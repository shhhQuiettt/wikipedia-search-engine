from queue import Empty, Queue
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
    def get_matrix(self) -> npt.NDArray:
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
            CREATE TABLE IF NOT EXISTS inverted_index (
                id INTEGER PRIMARY KEY,
                term TEXT UNIQUE,
                doc_ids TEXT
            )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                url TEXT,
                title TEXT
                )
            """
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS term_document (
                term TEXT PRIMARY KEY,
                doc_id INTEGER, 
                count INTEGER
                )
            """
        )

        self.connection.commit()

    def clean_db(self):
        self.cursor.execute(
            """
            DELETE FROM inverted_index
            """
        )
        self.cursor.execute(
            """
            DELETE FROM documents
            """
        )
        self.connection.commit()

    def build_from_dict(self, inverted_index_dict: dict[str, list[Posting]]):
        n_documents = max(
            [
                posting.document.id + 1
                for posting_list in inverted_index_dict.values()
                for posting in posting_list
            ]
        )

        for term, posting_list in inverted_index_dict.items():
            for posting in posting_list:
                self.cursor.execute(
                    """
                        INSERT OR IGNORE INTO documents (id, url, title) VALUES (?, ?, ?)
                    """,
                    (posting.document.id, posting.document.url, posting.document.title),
                )

                self.cursor.execute(
                    """
                    INSERT INTO term_document (term, doc_id, count) VALUES (?, ?, ?)
                    )""",
                    (term, posting.document.id, posting.bag_of_words),
                )

            max_count = max([posting.bag_of_words for posting in posting_list])
            idf = np.log(n_documents / (len(posting_list) + 1))

            posting_list_str = ";".join(
                [
                    f"{posting.document.id}:{ idf * posting.bag_of_words / max_count }"
                    for posting in posting_list
                ]
            )
            # start transaction
            self.cursor.execute(
                """
                INSERT INTO inverted_index (term, doc_ids) VALUES (?, ?)
                """,
                (term, posting_list_str),
            )

        self.connection.commit()

    def get_matrix(self) -> npt.NDArray:
        self.cursor.execute(
            """
                SELECT count(*) FROM documents
                """
        )

        no_of_documents = self.cursor.fetchone()[0]

        self.cursor.execute(
            """
                SELECT term, doc_ids FROM inverted_index ORDER BY term
            """
        )

        inverted_index = self.cursor.fetchall()

        matrix = np.zeros((no_of_documents, len(inverted_index)))

        for term_id, (term, posting_list) in enumerate(inverted_index):
            for posting in posting_list.split(";"):
                doc_id, bag_of_words = posting.split(":")
                matrix[int(doc_id), term_id] = bag_of_words

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
            SELECT id FROM inverted_index WHERE term = ?
            """,
            (term,),
        )

        result = self.cursor.fetchone()
        if result is None:
            return None

        return result[0]

    # def build_counter(self, counter: dict[str, int]):
    #     for term, count in counter.items():
    #         self.cursor.execute(
    #             """
    #             INSERT INTO term_counter (term, count) VALUES (?, ?)
    #             """,
    #             (term, count),
    #         )

    #     self.connection.commit()


def stopping_condition(inverted_index_dict):
    return True


def worker(
    documents: Queue,
    inverted_index_dict: dict[str, list[Posting]],
    inverted_index_dict_mutex: threading.Lock,
):
    while stopping_condition(inverted_index_dict):
        try:
            document = documents.get(timeout=10)

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
