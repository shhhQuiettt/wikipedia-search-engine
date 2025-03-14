from indexing import SqliteInvertedIndex, InvertedIndex
import sys
from math import log
from typing import Callable
import numpy as np
import numpy.typing as npt
import requests
import bs4
from collections import Counter
from text_processing import tokenize, get_term_couter, remove_stopwords, lemmatize


SimilarityFunction = Callable[[npt.NDArray, npt.NDArray], float]


def cosine_similarity(doc1: npt.NDArray, doc2: npt.NDArray) -> float:
    return np.dot(doc1, doc2) / (np.linalg.norm(doc1) * np.linalg.norm(doc2))


def jacard_similarity(doc1: npt.NDArray, doc2: npt.NDArray) -> float:
    bin_doc1 = doc1 > 0
    bin_doc2 = doc2 > 0
    return np.sum(bin_doc1 & bin_doc2) / np.sum(bin_doc1 | bin_doc2)


def pearson_similarity(doc1: npt.NDArray, doc2: npt.NDArray) -> float:
    return np.corrcoef(doc1, doc2)[0, 1]


def k_nearest_to_centroid(
    document_vectors: list[npt.NDArray],
    inverted_index_matrix: npt.NDArray,
    k: int,
    similarity: SimilarityFunction,
) -> list[tuple[int, float]]:
    centroid = np.mean(document_vectors, axis=0)
    similarities = np.apply_along_axis(
        lambda d: similarity(centroid, d), 1, inverted_index_matrix
    )

    document_vectors_mask = np.zeros(inverted_index_matrix.shape[0], dtype=bool)
    for doc_vector in document_vectors:
        document_vectors_mask |= np.all(inverted_index_matrix == doc_vector, axis=1)

    similarities[document_vectors_mask] = -1

    top_k = np.argsort(similarities)[-k:][::-1]
    scores = similarities[top_k]

    return list(zip(top_k.tolist(), scores.tolist()))


# Calculating the document vector for url not inside the database
def calculate_document_vector(url: str, inverted_index: InvertedIndex) -> npt.NDArray:
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    document = soup.find("div", {"id": "bodyContent"}).get_text()
    assert document is not None, f"Failed to find content of link {url}"

    inverted_index_matrix = inverted_index.get_tf_idf_matrix()

    tokens = tokenize(document)
    tokens = lemmatize(tokens)
    tokens = remove_stopwords(tokens)
    term_counter = get_term_couter(tokens)

    document_vector = np.zeros(inverted_index_matrix.shape[1])
    for term, count in term_counter.items():
        term_id = inverted_index.get_term_id(term)
        if term_id is None:
            continue

        idf = inverted_index.get_term_idf(term)
        max_count = max(term_counter.values())

        document_vector[term_id] = count * idf / max_count

    return document_vector


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python recommender.py <number of articles to recommend> <visited_urls_filename>"
        )
        sys.exit(1)

    k = int(sys.argv[1])
    filename = sys.argv[2]

    with open(filename, "r") as f:
        visited_urls = f.read().splitlines()

    inverted_index = SqliteInvertedIndex("inverted_index.db")
    inverted_index_matrix = inverted_index.get_tf_idf_matrix()

    document_vectors = []
    for url in visited_urls:
        if url == "":
            continue
        doc_id = inverted_index.get_document_id(url)
        if doc_id is None:
            print(f"{url} not found in the database. Calculating document vector...")
            document_vectors.append(calculate_document_vector(url, inverted_index))

        else:
            document_vectors.append(inverted_index_matrix[doc_id])

    m = inverted_index.get_tf_idf_matrix()

    best_ids = k_nearest_to_centroid(document_vectors, m, k, cosine_similarity)

    print("Recommended documents:")
    for doc_id, score in best_ids:
        print(inverted_index.get_document(int(doc_id)))
        print(f"Cosine similarity: {score}")
        print()


if __name__ == "__main__":
    main()
