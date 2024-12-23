from queue import Empty, Queue
from time import sleep
from math import log
from typing import Any
import numpy as np
import numpy.typing as npt
from dataclasses import dataclass
import sqlite3
from abc import ABC, abstractmethod
import threading
from typing import Any
from crawler import Document
from text_processing import (
    tokenize,
    get_term_couter,
    remove_stopwords,
    lemmatize,
)


@dataclass
class Posting:
    document: Document
    bag_of_words: int

    def __str__(self):
        return f"{self.document.id}:{self.bag_of_words}"


class InvertedIndex(ABC):
    @abstractmethod
    def build_from_dict(self, inverted_index_dict: dict):
        pass

    @abstractmethod
    def get_tf_idf_matrix(self) -> npt.NDArray:
        pass

    @abstractmethod
    def get_document(self, doc_id: int) -> tuple:
        pass

    @abstractmethod
    def get_all_documents_urls(self) -> set[str]:
        pass

    @abstractmethod
    def get_document_id(self, url: str) -> Any:
        pass

    @abstractmethod
    def get_term_id(self, term: str) -> Any:
        pass

    # @abstractmethod
    # def build_counter(self, counter: dict[str, int]):
    #     pass


class SqliteInvertedIndex(InvertedIndex):
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                title TEXT
                )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS terms (
                id INTEGER PRIMARY KEY,
                term TEXT UNIQUE,
                idf REAL
                )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS postings (
                document_id INTEGER,
                term_id INTEGER,
                count INTEGER,
                tf INTEGER,
                tf_idf REAL
            )
            """
        )

        self.connection.commit()

    def build_from_dict(self, inverted_index_dict: dict[str, list[Posting]]):
        no_of_documents = len(
            set(
                [
                    posting.document.url
                    for posting_list in inverted_index_dict.values()
                    for posting in posting_list
                ]
            )
        )

        for term_id, (term, posting_list) in enumerate(inverted_index_dict.items()):
            idf = log(no_of_documents / len(posting_list))

            print(no_of_documents, len(posting_list), idf)

            self.cursor.execute(
                """
                    INSERT INTO terms (id, term, idf) VALUES (?, ?, ?)
                """,
                (term_id, term, idf),
            )

            doc_id = 0
            for posting in posting_list:
                max_ocurrences = max((posting.bag_of_words for posting in posting_list))
                tf = posting.bag_of_words / max_ocurrences
                tf_idf = tf * idf
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO documents (id, url, title) VALUES (?, ?, ?)
                    """,
                    (doc_id, posting.document.url, posting.document.title),
                )
                doc_id += 1

                self.cursor.execute(
                    """
                        INSERT INTO POSTINGS (document_id, term_id, count, tf, tf_idf) VALUES (?, ?, ?, ?, ?)
                    """,
                    (doc_id, term_id, posting.bag_of_words, tf, tf_idf),
                )
        self.connection.commit()

    def get_tf_idf_matrix(self) -> npt.NDArray:
        (no_of_documents,) = self.cursor.execute(
            """
            SELECT COUNT(*) FROM documents
            """
        ).fetchone()

        (no_of_terms,) = self.cursor.execute(
            """
            SELECT COUNT(*) FROM terms
            """
        ).fetchone()

        matrix = np.zeros((no_of_documents, no_of_terms))

        for doc_id, term_id, tf_idf in self.cursor.execute(
            """
            SELECT document_id, term_id, tf_idf FROM postings
            """
        ):
            matrix[doc_id, term_id] = tf_idf

        return matrix

    def get_document(self, doc_id: int) -> tuple:
        self.cursor.execute(
            """
            SELECT * FROM documents WHERE id = ?
            """,
            (doc_id,),
        )

        return self.cursor.fetchone()

    def get_all_documents_urls(self) -> set[str]:
        self.cursor.execute(
            """
            SELECT url FROM documents
            """
        )
        return set([url for url, in self.cursor.fetchall()])

    def get_document_id(self, url: str) -> Any:
        self.cursor.execute(
            """
            SELECT id FROM documents WHERE url = ?
            """,
            (url,),
        )

        result = self.cursor.fetchone()
        if result is None:
            return None

        return result[0]

    def get_term_id(self, term: str) -> Any:
        self.cursor.execute(
            """
            SELECT id FROM terms WHERE term = ?
            """,
            (term,),
        )

        result = self.cursor.fetchone()
        if result is None:
            return None

        return result[0]


def worker(
    documents: Queue,
    inverted_index_dict: dict[str, list[Posting]],
    inverted_index_dict_mutex: threading.Lock,
):
    while 0 == 0:
        try:
            document = documents.get(timeout=3)

        except Empty:
            print("No more documents to index")
            return

        tokens = tokenize(document.text)
        tokens = remove_stopwords(tokens)
        tokens = lemmatize(tokens)

        term_counter = get_term_couter(tokens)
        with inverted_index_dict_mutex:
            for term, count in term_counter.items():
                if term not in inverted_index_dict:
                    inverted_index_dict[term] = []

                inverted_index_dict[term].append(Posting(document, count))

        print(f"Indexed {document.url}")


def perform_indexing(documents: Queue, no_of_threads: int = 10):
    inverted_index = SqliteInvertedIndex("inverted_index.db")
    inverted_index_dict = {}
    inverted_index_dict_mutex = threading.Lock()
    threads = [
        threading.Thread(
            target=worker,
            args=(
                documents,
                inverted_index_dict,
                inverted_index_dict_mutex,
            ),
        )
        for _ in range(no_of_threads)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    inverted_index.build_from_dict(inverted_index_dict)
    return inverted_index
