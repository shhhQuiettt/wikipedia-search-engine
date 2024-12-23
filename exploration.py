import matplotlib.pyplot as plt
from indexing import SqliteInvertedIndex
import recommender
from recommender import jacard_similarity, cosine_similarity


inverted_index = SqliteInvertedIndex("inverted_index.db")
inverted_index_matrix = inverted_index.get_tf_idf_matrix()

# |%%--%%| <JJTU8YYM7y|VHZ33pkNnw>
r"""°°°
Let's compare similiarities between various documents 
°°°"""
# |%%--%%| <VHZ33pkNnw|O3AiHggqL4>

hedghog_doc_url = "https://en.wikipedia.org/wiki/Hedgehog"
hedgehog_doc_id = inverted_index.get_document_id(hedghog_doc_url)
hedgehog_doc_vector = inverted_index_matrix[hedgehog_doc_id, :]


calculus_doc_url = "https://en.wikipedia.org/wiki/Calculus"
calculus_doc_id = inverted_index.get_document_id(calculus_doc_url)
calculus_doc_vector = inverted_index_matrix[calculus_doc_id, :]

derivatives_doc_url = "https://en.wikipedia.org/wiki/Derivative"
derivatives_doc_id = inverted_index.get_document_id(derivatives_doc_url)
derivatives_doc_vector = inverted_index_matrix[derivatives_doc_id, :]

# |%%--%%| <O3AiHggqL4|OJJuEbgXHQ>
r"""°°°
Cosine similarity and Jacard similarity between hedgehog and calculus 
°°°"""
# |%%--%%| <OJJuEbgXHQ|PASWx1dFOx>
cosine_similarity_score = cosine_similarity(hedgehog_doc_vector, calculus_doc_vector)
jacard_similarity_score = jacard_similarity(hedgehog_doc_vector, calculus_doc_vector)

print("Hedgehog vs Calculus")
print(f"Cosine similarity: {cosine_similarity_score}")
print(f"Jacard similarity: {jacard_similarity_score}")


# |%%--%%| <PASWx1dFOx|fEuQuQsvN6>
r"""°°°
Cosine similarity and Jacard similarity between calculus and derivatives
°°°"""
# |%%--%%| <fEuQuQsvN6|ap4wb6WJ3s>

cosine_similarity_score = cosine_similarity(calculus_doc_vector, derivatives_doc_vector)
jacard_similarity_score = jacard_similarity(calculus_doc_vector, derivatives_doc_vector)
print("Calculus vs Derivatives")
print(f"Cosine similarity: {cosine_similarity_score}")
print(f"Jacard similarity: {jacard_similarity_score}")


# |%%--%%| <ap4wb6WJ3s|W3JyCuLY4a>
r"""°°°
Cosine similarity between derivatives and hedgehog is almost **two order of magnitude higher** than the cosine similarity between hedgehog and calculus, what should be expected
°°°"""


# |%%--%%| <W3JyCuLY4a|Lv6wgwWFZV>
r"""°°°
# Some statistics

Top 10 popular terms
°°°"""
# |%%--%%| <Lv6wgwWFZV|3AcKBfkEwY>
res = inverted_index.cursor.execute(
    """
        select term, sum(count) from term_document group by term order by sum(count) desc limit 10
        """
)
res
