import requests
from dataclasses import dataclass
import bs4
from collections import Counter
from nltk.tokenize import word_tokenize


def tokenize(text):
    return [token for token in word_tokenize(text) if token.isalnum()]


def get_text(url):
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    content = soup.find("div", {"id": "bodyContent"})

    return content.get_text()


def get_term_couter(tokens) -> Counter:
    return Counter(tokens)


@dataclass
class Document:
    id: int
    url: str
    title: str
    text: str
