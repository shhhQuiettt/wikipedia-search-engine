from indexing import SqliteInvertedIndex
from typing import Callable
import numpy as np
import numpy.typing as npt


SimilarityFunction = Callable[[npt.NDArray, npt.NDArray], float]


def cosine_similarity(doc1: npt.NDArray, doc2: npt.NDArray) -> float:
    return np.dot(doc1, doc2) / (np.linalg.norm(doc1) * np.linalg.norm(doc2))


def k_nearest_to_centroid(
    doc_ids: list[int],
    inverted_index_matrix: npt.NDArray,
    k: int,
    similarity: SimilarityFunction,
) -> list[tuple[int, float]]:
    centroid = np.mean(inverted_index_matrix[doc_ids], axis=0)
    similarities = np.apply_along_axis(
        lambda d: similarity(centroid, d), 1, inverted_index_matrix
    )

    rank = np.argsort(similarities)[::-1]
    rank_without_given = rank[~np.isin(rank, doc_ids)]

    top_k = rank_without_given[:k]
    scores = similarities[top_k]

    return list(zip(top_k.tolist(), scores.tolist()))


def main():
    inverted_index = SqliteInvertedIndex("inverted_index.db")

    m = inverted_index.get_matrix()
    print(f"No of terms: {m.shape[1]}")
    print(f"No of documents: {m.shape[0]}")

    given_ids = [1, 2, 3, 4, 5]

    best_ids = k_nearest_to_centroid(given_ids, m, 5, cosine_similarity)

    print(f"Best ids: {best_ids}")

    print("Seen documents:")
    for doc_id in given_ids:
        print(inverted_index.get_document(doc_id))

    print("Recommended documents:")
    for doc_id, score in best_ids:
        print(type(doc_id))
        print(inverted_index.get_document(int(doc_id)))
        print(f"Score: {score}")
        print()


if __name__ == "__main__":
    m = main()
