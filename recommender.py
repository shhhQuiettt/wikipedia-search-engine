from indexing import SqliteInvertedIndex, InvertedIndex
import sys
from typing import Callable
import numpy as np
import numpy.typing as npt
import requests
import bs4
from collections import Counter
from text_processing import tokenize, get_term_couter


SimilarityFunction = Callable[[npt.NDArray, npt.NDArray], float]


def cosine_similarity(doc1: npt.NDArray, doc2: npt.NDArray) -> float:
    return np.dot(doc1, doc2) / (np.linalg.norm(doc1) * np.linalg.norm(doc2))


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


def calculate_document_vector(url: str, inverted_index: InvertedIndex) -> npt.NDArray:
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    document = soup.find("div", {"id": "bodyContent"}).get_text()
    assert document is not None, f"Failed to find content of link {url}"

    inverted_index_matrix = inverted_index.get_matrix()

    tokens = tokenize(document)
    term_counter = get_term_couter(tokens)

    document_vector = np.zeros(inverted_index_matrix.shape[1])
    for term, count in term_counter.items():
        term_id = inverted_index.get_term_id(term)
        if term_id is None:
            continue
        term_matrix_id = term_id - 1

        idf = np.log(
            inverted_index_matrix.shape[0]
            / np.count_nonzero(inverted_index_matrix[:, term_matrix_id])
        )
        max_count = max(term_counter.values())
        document_vector[term_matrix_id] = count * idf / max_count

    return document_vector


def main():
    print("asdf")
    print(sys.argv)
    if len(sys.argv) != 2:
        print("Usage: python recommender.py <visited_urls_filename>")
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename, "r") as f:
        visited_urls = f.read().splitlines()

    print("Seen documents:")
    for url in visited_urls:
        print(url)

    inverted_index = SqliteInvertedIndex("inverted_index.db")
    inverted_index_matrix = inverted_index.get_matrix()

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

    m = inverted_index.get_matrix()

    best_ids = k_nearest_to_centroid(document_vectors, m, 5, cosine_similarity)

    print(f"Best ids: {best_ids}")

    print("Recommended documents:")
    for doc_id, score in best_ids:
        print(inverted_index.get_document(int(doc_id)))
        print(f"Score: {score}")
        print()


if __name__ == "__main__":
    main()
