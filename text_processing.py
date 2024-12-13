import requests
from dataclasses import dataclass
import sqlite3
import bs4
from abc import ABC, abstractmethod
from nltk.tokenize import word_tokenize


class InvertedIndex(ABC):
    @abstractmethod
    def build_from_dict(self, dictionary: dict):
        pass

    @abstractmethod
    def search(self, term: str) -> set:
        pass


class SqliteInvertedIndex(InvertedIndex):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS inverted_index (
                term TEXT PRIMARY KEY,
                documents TEXT
            )
            """
        )

    def build_from_dict(self, dictionary: dict): ...

    def search(self, term: str) -> set: ...


def tokenize(text):
    return [token for token in word_tokenize(text) if token.isalnum()]


def get_text(url):
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    content = soup.find("div", {"id": "bodyContent"})

    return content.get_text()


inverted_index = SqliteInvertedIndex("inverted_index.db")


text = get_text("https://en.wikipedia.org/wiki/Hairy_ball_theorem")
tokens = tokenize(text)

inverted_index_dict = {}


for token in tokens:
    if token not in inverted_index_dict:
        inverted_index_dict[token] = set()

    inverted_index_dict[token].add("1")

print(inverted_index_dict)
