import requests
from dataclasses import dataclass
import bs4
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

_stop_words = set(stopwords.words("english"))
_lemmatizer = WordNetLemmatizer()


def tokenize(text):
    return [token.lower() for token in word_tokenize(text) if token.isalnum()]


def remove_stopwords(tokens):
    return [token for token in tokens if token not in _stop_words]


def lemmatize(tokens):
    return [_lemmatizer.lemmatize(token) for token in tokens]


def get_term_couter(tokens) -> Counter:
    return Counter(tokens)


def get_text(url):
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    content = soup.find("div", {"id": "bodyContent"})

    return content.get_text()
