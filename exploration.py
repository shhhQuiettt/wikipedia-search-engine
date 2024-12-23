r"""°°°
# Some statistics and exploration of the results
°°°"""

# |%%--%%| <5tJdZ3c28b|BKwtjaM3EH>
import matplotlib.pyplot as plt
from indexing import SqliteInvertedIndex
import recommender
from recommender import jacard_similarity, cosine_similarity
import numpy as np


# |%%--%%| <BKwtjaM3EH|acP0eTQMOW>

inverted_index = SqliteInvertedIndex("inverted_index.db")
inverted_index_matrix = inverted_index.get_tf_idf_matrix()

query = lambda query_text: inverted_index.cursor.execute(query_text)


# |%%--%%| <acP0eTQMOW|mzdCRVc0zz>
r"""°°°
## Number of documents
°°°"""
# |%%--%%| <mzdCRVc0zz|88v3KdgHkG>

query("select count(*) from documents").fetchone()

# |%%--%%| <88v3KdgHkG|OF5gpUBFki>
r"""°°°
### Number of terms
°°°"""
# |%%--%%| <OF5gpUBFki|tlDonAt6DD>
query("select count(*) from terms").fetchone()

# |%%--%%| <tlDonAt6DD|uDkOPumtEj>
r"""°°°
### Top 20 frequently occuring terms which length is greater than 3
°°°"""
# |%%--%%| <uDkOPumtEj|bq6KyOhPAv>

res = query(
    """
    select term, sum(count) 
    from postings p 
    join terms t on p.term_id = t.id 
    group by term 
    having length(term) > 3 
    order by sum(count) desc
    limit 10
            """
)
res.fetchall()

# |%%--%%| <bq6KyOhPAv|29HOlidCNL>
r"""°°°
Despite weirdness of _shrew_, and manually checking, it turns out that _shrew_ __indeed is__ a frequent word in the documents related to mammals and other animals
°°°"""
# |%%--%%| <29HOlidCNL|YnwfvTmBYU>
r"""°°°
### Terms with lowest entropy
°°°"""
# |%%--%%| <YnwfvTmBYU|7iVCUI0aWb>

query(
    """
        select term, idf from terms order by idf asc limit 10
        """
).fetchall()

# |%%--%%| <7iVCUI0aWb|heVO1aiSno>
r"""°°°
### Terms with highest entropy
°°°"""
# |%%--%%| <heVO1aiSno|2pSmidhWJs>

query(
    """
  select term, idf from terms order by idf desc limit 10
  """
).fetchall()
# |%%--%%| <2pSmidhWJs|PBeq7ZpcIw>
r"""°°°
### Distribution of terms occurance among all documents
°°°"""
# |%%--%%| <PBeq7ZpcIw|VPxjM0s195>

res = query(
    """
        select t.term, sum(p.count) 
        from terms t join postings p on t.id = p.term_id 
        group by t.term
        order by sum(p.count) desc
    """
).fetchall()

plt.plot([x[1] for x in res])

# |%%--%%| <VPxjM0s195|Mz3pWiVxLw>
r"""°°°
### Checking if corpus fulfills Zipf's law
°°°"""
# |%%--%%| <Mz3pWiVxLw|ZZsb7UgsYh>

res = query(
    """
    select t.term, sum(p.count)
    from terms t join postings p on t.id = p.term_id
    group by t.term
    order by sum(p.count) desc
    """
).fetchall()

ocurrances = np.array([x[1] for x in res])
N = len(ocurrances)
k = ocurrances[3] / N * 4
expected_zipf = k / np.arange(1, N + 1)

cut_off = 1000
plt.plot(ocurrances[:1000] / N)
plt.plot(expected_zipf[:1000])
plt.legend(["Actual frequency", "Expected from Zipf's law"])


# |%%--%%| <ZZsb7UgsYh|yTfKqUqIFM>

r"""°°°
### Document most similar to **Open set**
°°°"""
# |%%--%%| <yTfKqUqIFM|oyxhg3nskT>

url = "https://en.wikipedia.org/wiki/Open_set"
doc_id = inverted_index.get_document_id(url)
assert doc_id is not None

doc_vector = inverted_index_matrix[doc_id, :]

similarities = np.apply_along_axis(
    lambda x: cosine_similarity(doc_vector, x), 1, inverted_index_matrix
)

top_5_similarities = np.argsort(similarities, axis=0)[-6:-1]

for doc_id in top_5_similarities[::-1]:
    res = query(
        f"""
        select title from documents where id = {doc_id}
        """,
    ).fetchone()
    assert res is not None
    print(f"Title: {res[0]}")
    print(f"Cosine similarity: {similarities[doc_id]}\n")


# |%%--%%| <oyxhg3nskT|tfegEl31Qc>
r"""°°°
### Least similar document to **Open set**
°°°"""
# |%%--%%| <tfegEl31Qc|8LPlMdFam6>


url = "https://en.wikipedia.org/wiki/Open_set"
doc_id = inverted_index.get_document_id(url)
assert doc_id is not None

doc_vector = inverted_index_matrix[doc_id, :]

similarities = np.apply_along_axis(
    lambda x: cosine_similarity(doc_vector, x), 1, inverted_index_matrix
)

top_5_similarities = np.argsort(similarities, axis=0)[:5]

for doc_id in top_5_similarities:
    res = query(
        f"""
        select title from documents where id = {doc_id}
        """,
    ).fetchone()
    assert res is not None
    print(f"Title: {res[0]}")
    print(f"Cosine similarity: {similarities[doc_id]}\n")


# |%%--%%| <8LPlMdFam6|5qQpK8dZFl>
r"""°°°
These results make sense, as Open Set relates to topics like *topology* and *closed sets*, while do not relate to topics like *hedgehogs* or *Chacarero*

Open Set:
![Open Set](./reports/imgs/open-set.png)

Closed Set (similar):
![Closed Set](./reports/imgs/closed-set.png)

Eastern forest hedgehog (not similar):
![Eastern forest hedgehog]("./reports/imgs/eastern-forest-hedgehog.jpeg")
°°°"""
# |%%--%%| <5qQpK8dZFl|DUKR4HkT1D>
r"""°°°
## Comparing similiarities between various documents 
°°°"""
# |%%--%%| <DUKR4HkT1D|O3AiHggqL4>

hedghog_doc_url = "https://en.wikipedia.org/wiki/Hedgehog"
hedgehog_doc_id = inverted_index.get_document_id(hedghog_doc_url)
hedgehog_doc_vector = inverted_index_matrix[hedgehog_doc_id, :]
assert hedgehog_doc_vector is not None

calculus_doc_url = "https://en.wikipedia.org/wiki/Calculus"
calculus_doc_id = inverted_index.get_document_id(calculus_doc_url)
calculus_doc_vector = inverted_index_matrix[calculus_doc_id, :]
assert calculus_doc_vector is not None

derivatives_doc_url = "https://en.wikipedia.org/wiki/Derivative"
derivatives_doc_id = inverted_index.get_document_id(derivatives_doc_url)
derivatives_doc_vector = inverted_index_matrix[derivatives_doc_id, :]
assert derivatives_doc_vector is not None

# |%%--%%| <O3AiHggqL4|OJJuEbgXHQ>
r"""°°°
### Cosine similarity and Jacard similarity between hedgehog and calculus 
°°°"""
# |%%--%%| <OJJuEbgXHQ|PASWx1dFOx>
cosine_similarity_score = cosine_similarity(hedgehog_doc_vector, calculus_doc_vector)
jacard_similarity_score = jacard_similarity(hedgehog_doc_vector, calculus_doc_vector)

print("Hedgehog vs Calculus")
print(f"Cosine similarity: {cosine_similarity_score}")
print(f"Jacard similarity: {jacard_similarity_score}")


# |%%--%%| <PASWx1dFOx|fEuQuQsvN6>
r"""°°°
### Cosine similarity and Jacard similarity between calculus and derivatives
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
# |%%--%%| <W3JyCuLY4a|QgJ5R7EoO4>
