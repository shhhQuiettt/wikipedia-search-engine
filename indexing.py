from queue import Queue
from typing import Any
from pprint import pprint
from dataclasses import dataclass
import sqlite3
from abc import ABC, abstractmethod
import threading
from typing import Any
from crawler import Document
from text_processing import (
    tokenize,
    get_term_couter,
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


class SqliteInvertedIndex(InvertedIndex):
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inverted_index (
                term TEXT PRIMARY KEY,
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
        for term, posting_list in inverted_index_dict.items():
            for posting in posting_list:
                self.cursor.execute(
                    """
                        INSERT OR IGNORE INTO documents (id, url, title) VALUES (?, ?, ?)
                    """,
                    (posting.document.id, posting.document.url, posting.document.title),
                )

            posting_list_str = ";".join([str(posting) for posting in posting_list])
            self.cursor.execute(
                """
                INSERT INTO inverted_index (term, doc_ids) VALUES (?, ?)
                """,
                (term, posting_list_str),
            )

        self.connection.commit()

        self.connection.commit()

    def fetch_all(self):
        self.cursor.execute(
            """
            SELECT * FROM inverted_index
            """
        )
        return self.cursor.fetchall()


def stopping_condition(inverted_index_dict):
    return True


def worker(
    documents: Queue,
    inverted_index_dict: dict[str, list[Posting]],
    inverted_index_dict_mutex: threading.Lock,
):
    while stopping_condition(inverted_index_dict):
        document = documents.get(timeout=10)
        tokens = tokenize(document.text)
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
