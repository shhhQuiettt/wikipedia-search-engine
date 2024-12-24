::: {#title-block-header}
# Wikipedia recommender system {#wikipedia-recommender-system .title}
:::

## ([Link to Github](https://github.com/shhhQuiettt/wikipedia-search-engine))

The aim of this project is to index the Wikipedia and build a
**recommender system** in a simplified form on top of it. Given a list
of previously read articles, the system should recommend the next
article to read.

In this simplified form we assume that the documents are related, for
example that they come from a **single session**, and we want to
recommend the next article(s) to read.

### Process consists of following steps:

1.  **Building the database**

    1.  Downloading the Wikipedia dump
    2.  Text Preprocessing
    3.  Indexing
    4.  Storing the index

2.  **Recommending**

    1.  Querying the read documents
    2.  Calculating similarities
    3.  Recommending the k-next articles

## Usage

1.  **Building the database**

Run this command to start the crawling and database building process:

    python build_db.py

2.  **Recommending**

Put visited links inside `previously_seen.txt` and run this command to
get 5 recommendations:

    python recommend.py 5 previously_seen.txt

# Implementation

## Building the database

The building and indexing is done **asynchronously**. The crawling
process is implemented in a coroutine model on a one thread
([`crawler.py`](https://github.com/shhhQuiettt/wikipedia-search-engine/blob/main/crawler.py)),
while the indexing is done in a separate thread with multiple workers
([`indexing.py`](https://github.com/shhhQuiettt/wikipedia-search-engine/blob/main/indexing.py)).

### Downloading the Wikipedia dump

The crawler start from **three initial urls** to:

-   An *important* mathematical theorem: [Hairy Ball
    Theorem](https://en.wikipedia.org/wiki/Hairy_ball_theorem)
-   Butterjelly sandwich: [Butterjelly
    sandwich](https://en.wikipedia.org/wiki/Butterjelly_sandwich)
-   Hedgehog: [Hedgehog](https://en.wikipedia.org/wiki/Hedgehog)

Then `BeautifulSoup` is used to parse the html and extract the text from
the body of the document. We also extract the title of the document. The
document gets inside a queue, where it will await **preprocessing and
indexing**, and we search for all urls in the body to apply the
procedure recursively.

### Text Preprocessing

The text is preprocessed in the following way:

1.  **Tokenization**

We tokenize the text using `nltk`'s `word_tokenize` function to obtain a
list of tokens.

2.  **Lemmatization**

We lemmatize the tokens using `nltk`'s `WordNetLemmatizer` to extract
the base word of the token. For example the word "running" will be
lemmatized to "run".

3.  **Stopwords removal**

We remove the stopwords using `nltk`'s `stopwords` list.

### Indexing

We want to store **TF-IDF** values for each word in document:

$$\text{TF}\left( \text{term},\text{document} \right) = \frac{\text{\#term appears in document}}{\text{\#the most frequent term in document}}$$

$$\text{IDF}\left( \text{term} \right) = \log\left( \frac{\text{total number of documents}}{\text{number of documents containing term}} \right)$$

$$\text{TF-IDF}\left( \text{term},\text{document} \right) = \text{TF}\left( \text{term},\text{document} \right) \times \text{IDF}\left( \text{term} \right)$$

The **IDF** is important in order to prioritize terms with **high
entropy** among other documents

### Storing the index

In the current implementation we store inverted index inside **sqlite**
database, but we abstract the index storage to an *abstract class*
`InvertedIndex` to possibly test other storage methods like **NoSQL**
databases like *mongoDB* or **RAM-base** like *Redis*

# Recommending

The read documents are queried from the database and the similarities
are calculated using the **cosine similarity**. The cosine similarity is
calculated as follows:

$$\text{cosine similarity}\left( \text{doc1},\text{doc2} \right) = \frac{\text{doc1} \cdot \text{doc2}}{\parallel \text{doc1} \parallel \times \parallel \text{doc2} \parallel}$$

Where document vector is a vector of **TF-IDF** values for each word in
the document.

The implementation allows for using other similarity measures which
fulfill the `similarity_function` interface (`recommender.py`), so we
also tested **Jaccard similarity** with binary vectors:

$$\text{Jaccard similarity}\left( \text{doc1},\text{doc2} \right) = \frac{\text{doc1} \cap \text{doc2}}{\text{doc1} \cup \text{doc2}}$$

In the currenct implementation we assume that the documents come from a
**single session** and we want to recommend the next `k` article(s) to
read.

We calculate the **centroid** of the read documents and recommend the
`k` closest documents to the centroid.

::: {#some-recommendations .section .cell .markdown}
# Some recommendations
:::

::: {#1-this-session-relates-to-mathematitics-and-pioneers-of-calculus .section .cell .markdown}
### 1. This session relates to **Mathematitics** and pioneers of **Calculus**
:::

::: {.cell .code execution_count="1"}
::: {#cb1 .sourceCode}
::: {#cb3 .sourceCode}
``` {.sourceCode .python}
!cat ./example_visited/previously_seen1.txt
```
:::
:::

::: {.output .stream .stdout}
    https://en.wikipedia.org/wiki/Leonhard_Euler
    https://en.wikipedia.org/wiki/Isaac_Newton
    https://en.wikipedia.org/wiki/Mathematics
    https://en.wikipedia.org/wiki/Functions_(mathematics)
    https://en.wikipedia.org/wiki/Real_number
:::
:::

::: {.cell .code execution_count="2"}
::: {#cb3 .sourceCode}
::: {#cb5 .sourceCode}
``` {.sourceCode .python}
!python recommender.py 5 ./example_visited/previously_seen1.txt
```
:::
:::

::: {.output .stream .stdout}
    https://en.wikipedia.org/wiki/Leonhard_Euler not found in the database. Calculating document vector...
    https://en.wikipedia.org/wiki/Isaac_Newton not found in the database. Calculating document vector...
    Best ids: [(240, 0.06210137608606608), (258, 0.0590626066522234), (79, 0.054672164284898996), (322, 0.05021229255088811), (184, 0.04862576791724621)]
    Recommended documents:
    (240, 'https://en.wikipedia.org/wiki/Hyperreal_numbers', 'Hyperreal number')
    Cosine similarity: 0.06210137608606608

    (258, 'https://en.wikipedia.org/wiki/Theorem', 'Theorem')
    Cosine similarity: 0.0590626066522234

    (79, 'https://en.wikipedia.org/wiki/Calculus', 'Calculus')
    Cosine similarity: 0.054672164284898996

    (322, 'https://en.wikipedia.org/wiki/Bijective', 'Bijection')
    Cosine similarity: 0.05021229255088811

    (184, 'https://en.wikipedia.org/wiki/Mathematical_analysis', 'Mathematical analysis')
    Cosine similarity: 0.04862576791724621
:::
:::

::: {.cell .markdown}
We see topics we would expect for someone interested in **Newton** and
**Euler** and **Mathematics**
:::

::: {#2-this-session-relates-sandwiches .section .cell .markdown}
### 2. This session relates sandwiches
:::

::: {.cell .code execution_count="3"}
::: {#cb5 .sourceCode}
::: {#cb7 .sourceCode}
``` {.sourceCode .python}
!cat ./example_visited/previously_seen2.txt
```
:::
:::

::: {.output .stream .stdout}
    https://en.wikipedia.org/wiki/Peanut_butter
    https://en.wikipedia.org/wiki/Lunch
    https://en.wikipedia.org/wiki/Sandwich
:::
:::

::: {.cell .code execution_count="4"}
::: {#cb7 .sourceCode}
::: {#cb9 .sourceCode}
``` {.sourceCode .python}
!python recommender.py 5 ./example_visited/previously_seen2.txt
```
:::
:::

::: {.output .stream .stdout}
    Best ids: [(560, 0.23502137689424202), (605, 0.20909613026041712), (599, 0.19268899828898028), (583, 0.19119226566432948), (800, 0.18548005955094318)]
    Recommended documents:
    (560, 'https://en.wikipedia.org/wiki/Bal%C4%B1k_ekmek', 'Balık ekmek')
    Cosine similarity: 0.23502137689424202

    (605, 'https://en.wikipedia.org/wiki/Roujiamo', 'Roujiamo')
    Cosine similarity: 0.20909613026041712

    (599, 'https://en.wikipedia.org/wiki/Panini_(sandwich)', 'Panini (sandwich)')
    Cosine similarity: 0.19268899828898028

    (583, 'https://en.wikipedia.org/wiki/Donkey_burger', 'Donkey burger')
    Cosine similarity: 0.19119226566432948

    (800, 'https://en.wikipedia.org/wiki/Bag_lunch', 'Packed lunch')
    Cosine similarity: 0.18548005955094318
:::
:::

::: {.cell .markdown}
Indeed, we see different types of sandwiches someone could be interested
in
:::

::: {#some-statistics-and-exploration-of-the-results .section .cell .markdown jukit_cell_id="5tJdZ3c28b"}
# Some statistics and exploration of the results
:::

::: {.cell .code execution_count="5" jukit_cell_id="BKwtjaM3EH"}
::: {#cb9 .sourceCode}
::: {#cb11 .sourceCode}
``` {.sourceCode .python}
import matplotlib.pyplot as plt
from indexing import SqliteInvertedIndex
import recommender
from recommender import jacard_similarity, cosine_similarity
import numpy as np
```
:::
:::
:::

::: {.cell .code execution_count="6" jukit_cell_id="acP0eTQMOW"}
::: {#cb10 .sourceCode}
::: {#cb12 .sourceCode}
``` {.sourceCode .python}
inverted_index = SqliteInvertedIndex("inverted_index.db")
inverted_index_matrix = inverted_index.get_tf_idf_matrix()

query = lambda query_text: inverted_index.cursor.execute(query_text)
```
:::
:::
:::

::: {#number-of-documents .section .cell .markdown jukit_cell_id="mzdCRVc0zz"}
## Number of documents
:::

::: {.cell .code execution_count="7" jukit_cell_id="88v3KdgHkG"}
::: {#cb11 .sourceCode}
::: {#cb13 .sourceCode}
``` {.sourceCode .python}
query("select count(*) from documents").fetchone()
```
:::
:::

::: {.output .execute_result execution_count="7"}
    (1000,)
:::
:::

::: {#number-of-terms .section .cell .markdown jukit_cell_id="OF5gpUBFki"}
### Number of terms
:::

::: {.cell .code execution_count="8" jukit_cell_id="tlDonAt6DD"}
::: {#cb13 .sourceCode}
::: {#cb15 .sourceCode}
``` {.sourceCode .python}
query("select count(*) from terms").fetchone()
```
:::
:::

::: {.output .execute_result execution_count="8"}
    (116470,)
:::
:::

::: {#top-20-frequently-occuring-terms .section .cell .markdown jukit_cell_id="uDkOPumtEj"}
### Top 20 frequently occuring terms
:::

::: {.cell .code execution_count="19" jukit_cell_id="bq6KyOhPAv"}
::: {#cb15 .sourceCode}
::: {#cb17 .sourceCode}
``` {.sourceCode .python}
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
```
:::
:::

::: {.output .execute_result execution_count="19"}
    [('shrew', 32304),
     ('function', 14177),
     ('retrieved', 12128),
     ('edit', 11623),
     ('space', 8069),
     ('isbn', 7562),
     ('also', 7100),
     ('archived', 6817),
     ('original', 6753),
     ('number', 6483)]
:::
:::

::: {.cell .markdown jukit_cell_id="29HOlidCNL"}
Despite weirdness of *shrew*, and manually checking, it turns out that
*shrew* **indeed is** a frequent word in the documents related to
mammals and other animals
:::

::: {#terms-with-lowest-entropy .section .cell .markdown jukit_cell_id="YnwfvTmBYU"}
### Terms with lowest entropy
:::

::: {.cell .code execution_count="10" jukit_cell_id="7iVCUI0aWb"}
::: {#cb17 .sourceCode}
::: {#cb19 .sourceCode}
``` {.sourceCode .python}
query(
    """
        select term, idf from terms order by idf asc limit 10
        """
).fetchall()
```
:::
:::

::: {.output .execute_result execution_count="10"}
    [('retrieved', 0.0),
     ('http', 0.0),
     ('1', 0.022245608947319737),
     ('reference', 0.03978087001184446),
     ('edit', 0.06935007813479324),
     ('2', 0.08773891430800689),
     ('also', 0.1266976530459575),
     ('3', 0.1636960926707897),
     ('see', 0.1779312084926618),
     ('new', 0.18632957819149354)]
:::
:::

::: {#terms-with-highest-entropy .section .cell .markdown jukit_cell_id="heVO1aiSno"}
### Terms with highest entropy
:::

::: {.cell .code execution_count="11" jukit_cell_id="2pSmidhWJs"}
::: {#cb19 .sourceCode}
::: {#cb21 .sourceCode}
``` {.sourceCode .python}
query(
    """
  select term, idf from terms order by idf desc limit 10
  """
).fetchall()
```
:::
:::

::: {.output .execute_result execution_count="11"}
    [('combable', 6.907755278982137),
     ('ℝ3', 6.907755278982137),
     ('idealizes', 6.907755278982137),
     ('meteorologically', 6.907755278982137),
     ('accomplishes', 6.907755278982137),
     ('gidea', 6.907755278982137),
     ('1584882530', 6.907755278982137),
     ('abbildung', 6.907755278982137),
     ('bormashenko', 6.907755278982137),
     ('kazachkov', 6.907755278982137)]
:::
:::

::: {#distribution-of-terms-occurance-among-all-documents .section .cell .markdown jukit_cell_id="PBeq7ZpcIw"}
### Distribution of terms occurance among all documents
:::

::: {.cell .code execution_count="12" jukit_cell_id="VPxjM0s195"}
::: {#cb21 .sourceCode}
::: {#cb23 .sourceCode}
``` {.sourceCode .python}
res = query(
    """
        select t.term, sum(p.count) 
        from terms t join postings p on t.id = p.term_id 
        group by t.term
        order by sum(p.count) desc
    """
).fetchall()

plt.plot([x[1] for x in res])
```
:::
:::

::: {.output .execute_result execution_count="12"}
    [<matplotlib.lines.Line2D at 0x7dc550188690>]
:::

::: {.output .display_data}
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAksAAAGdCAYAAAACMjetAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjAsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvlHJYcgAAAAlwSFlzAAAPYQAAD2EBqD+naQAAMxpJREFUeJzt3Xt0VPW9///XTJKZhMskXCRDJFwsSuQiSGLi1Et/HnMYPVltqaxKKdUcRKs0WCA9QFlVsD1tw8JjFRWw1nWE9TtVIOtbWwWEb064HSWCBINcIx6xocIkKmQmUEhC5vP9Q7PLSNgykCFMeD7W2qvM/rznsz/705XOq3v2/ozDGGMEAACANjk7egAAAACXM8ISAACADcISAACADcISAACADcISAACADcISAACADcISAACADcISAACAjcSOHkBHCofDOnz4sLp37y6Hw9HRwwEAAOfBGKOGhgZlZGTI6Yz9dZ8rOiwdPnxYmZmZHT0MAABwAQ4dOqR+/frF/DhXdFjq3r27pC8m2+PxdPBoAADA+QiFQsrMzLQ+x2Ptig5LrV+9eTwewhIAAHHmUt1Cww3eAAAANghLAAAANghLAAAANghLAAAANghLAAAANghLAAAANghLAAAANqIOS5988ol+9KMfqVevXkpJSdGIESO0fft2q90Yo7lz56pv375KSUlRfn6+Dhw4ENHH0aNHNXHiRHk8HqWlpWny5Mk6fvx4RM3777+v2267TcnJycrMzNSCBQvOGktpaamysrKUnJysESNGaM2aNdGeDgAAgK2owtKxY8d0yy23KCkpSW+++ab27t2rp556Sj169LBqFixYoGeffVYvvPCCtm7dqq5du8rv9+vUqVNWzcSJE7Vnzx6VlZVp1apV2rx5s3784x9b7aFQSGPGjNGAAQNUWVmpJ598Uk888YRefPFFq2bLli2aMGGCJk+erPfee09jx47V2LFjtXv37ouZDwAAgEgmCrNnzza33nrrOdvD4bDxer3mySeftPbV19cbt9ttXn31VWOMMXv37jWSzLvvvmvVvPnmm8bhcJhPPvnEGGPM4sWLTY8ePUxjY2PEsYcMGWK9vvfee01BQUHE8fPy8szDDz983ucTDAaNJBMMBs/7PQAAoGNd6s/vqK4svf7668rJydH3v/999enTRzfeeKP+8Ic/WO0HDx5UIBBQfn6+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)
:::
:::

::: {#checking-if-corpus-fulfills-zipfs-law .section .cell .markdown jukit_cell_id="Mz3pWiVxLw"}
### Checking if corpus fulfills Zipf\'s law
:::

::: {.cell .code execution_count="13" jukit_cell_id="ZZsb7UgsYh"}
::: {#cb23 .sourceCode}
::: {#cb25 .sourceCode}
``` {.sourceCode .python}
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
```
:::
:::

::: {.output .execute_result execution_count="13"}
    <matplotlib.legend.Legend at 0x7dc55018da90>
:::

::: {.output .display_data}
![](data:image/png;base64,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)
:::
:::

::: {#documents-most-similar-to-the-article-open-set .section .cell .markdown jukit_cell_id="yTfKqUqIFM"}
### Documents most similar to the article **Open Set**
:::

::: {.cell .code execution_count="14" jukit_cell_id="oyxhg3nskT"}
::: {#cb25 .sourceCode}
::: {#cb27 .sourceCode}
``` {.sourceCode .python}
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
```
:::
:::

::: {.output .stream .stdout}
    Title: Open set
    Cosine similarity: 1.0

    Title: Closed set
    Cosine similarity: 0.1670939050012435

    Title: Accumulation point
    Cosine similarity: 0.09399570728349808

    Title: Open and closed maps
    Cosine similarity: 0.09323925622985396

    Title: Open and closed maps
    Cosine similarity: 0.09323925622985396
:::
:::

::: {#documents-least-similar-document-to-the-article-open-set .section .cell .markdown jukit_cell_id="tfegEl31Qc"}
### Documents least similar document to the article **Open set**
:::

::: {.cell .code execution_count="15" jukit_cell_id="8LPlMdFam6"}
::: {#cb27 .sourceCode}
::: {#cb29 .sourceCode}
``` {.sourceCode .python}
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
```
:::
:::

::: {.output .stream .stdout}
    Title: Eastern forest hedgehog
    Cosine similarity: 4.099291536117715e-06

    Title: Chacarero
    Cosine similarity: 1.473436229790874e-05

    Title: Somali hedgehog
    Cosine similarity: 2.148079406048971e-05

    Title: Hemiechinus
    Cosine similarity: 2.2237134281189762e-05

    Title: Gaoligong forest hedgehog
    Cosine similarity: 2.259060627956648e-05
:::
:::

::: {.cell .markdown jukit_cell_id="5qQpK8dZFl"}
These results make sense, as Open Set relates to topics like *topology*
and *closed sets*, while do not relate to topics like *hedgehogs* or
*Chacarero*

**Open Set**:

![Open
Set](data:image/png;base64,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)

**Closed Set** (similar to Open Set):

![Closed
Set](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAcIAAAE3CAYAAAA5R0HvAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAhGVYSWZNTQAqAAAACAAFARIAAwAAAAEAAQAAARoABQAAAAEAAABKARsABQAAAAEAAABSASgAAwAAAAEAAgAAh2kABAAAAAEAAABaAAAAAAAAA7oAAAABAAADugAAAAEAA6ABAAMAAAABAAEAAKACAAQAAAABAAABwqADAAQAAAABAAABNwAAAABM4DyhAAAACXBIWXMAAJK3AACStwHA7gadAAABWWlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iWE1QIENvcmUgNi4wLjAiPgogICA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogICAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIgogICAgICAgICAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyI+CiAgICAgICAgIDx0aWZmOk9yaWVudGF0aW9uPjE8L3RpZmY6T3JpZW50YXRpb24+CiAgICAgIDwvcmRmOkRlc2NyaXB0aW9uPgogICA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgoZXuEHAABAAElEQVR4Ae2dB7hdVZn+35tGekJ6AiEJJSRAhBCCdAJIHxEBRXFAZP7AEEZQRBkRZ9TBYUTE8jwqijQVpCktUgRCEzEJJZQQIAnpjfRGCin/9e6PL/dwSbn37H3O2eVdz3POPmXvtdf6rb33u75vtbpNIUBBBERABERABApKoFlB861si4AIiIAIiEBEQEKoC0EEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEWhQ698q8CFSRwKZNdjLflp66rq7+W+nn+l/rP5UeX/rZ9/Djfeu/aysCIrBlAnWbQtjyX/pVBESgqQT8bvItj29WQ78L01GaFhdH3zY1f9pfBPJIQEKYx1JVnqpCwAXGt9sSvA8+AN5/H1i+HFi6FFi5Eli1Clixwl7LlgHr1tmL+65fD2zYYC9mpnlzoEXw3/DVsqW9WrcGOncG2rUDOna0bYcO9hu3bdvacVuDsXGj/eOi6Nut7a/fRSCvBCSEeS1Z5StxAqXWFUVjS8JBsVuyBJg3D5g5E5g1C5g/H1i0yISQgkbxat/+o+JFMaOwUeS4D0WV8bu4UrT4YhookhTLNWtMUCmmFFWKLD9zy315ju7dgR49gL597dWzp52f52oYGpO/hsfouwjkgYCEMA+lqDxUjICLw5aEj0L03nvA1KnA228D775rAsjEUHz69QN69wa6dgU6dTJhopXmYlcaJ8/jofSz/1a6LRVg/8xjXCzXrgVWrzZRpPVJEZ49G5gxA1i40KzKPn2A3XYD9twT6N/fBJPpKg2Mj6E0nfaL3kUgXwQkhPkqT+UmAQIufm6NeZQUl+nTgbfeAiZMACZNMtfl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tlRQWM81EgwOEaDlRCuKVhM727DdjO5D9kRlr0m2r3kcjNNfLpC+Zfyl4uXn29bWRdSFzrc8n794PM+5dq2J3uLFJuxcvYPiN3cu0LGjifrgwcCAAbbeI8cDloat8SjdR59FIKsEJIRZLTmlu2oEXKxcaEpPTLcoXYkcq8i2tGnTbMu2NVqJHMBPYeRYuq5drVMJ50Gl0FAkS620UmErPUfp51Kx5GcKlLdbslMPBW/5coCrOXBeT1p7TB+tWv7XpYsJdv/+NpaS7Z+0+Fys/VzbyrPvo60I5IWAhDAvJal8VIWACwRPtiVh5O90i3J4AQXIhYjrKFKMOOXYypX1rkoKIi1Hvjj5tFty3FIkKZY8p4sd4+Z3bil47OlK92bpfKq08Ci8FGG++JliTMHjOVxwmVYPbvHx+9by5ftqKwJ5IyAhzFuJKj9VJ9AYcfREUcAoXrTOVq82tyqFzAWNVl2p6HE/ChMFk+LI3pwUSBdQWp0U0datbQwkf+ewj4YWnp+f26akt/Q4fRaBvBKQEOa1ZJWvmhGg0DD41r5tW5x8n6S2pWLnccrScxLaisBHCUgIP8pD30SgogQaimPD7+WevNTdWfq53Ph0nAgUiYCEsEilrbyKgAiIgAh8jEBodVAQAREQAREQgeISkBAWt+yVcxEQAREQgUBAQqjLQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEREBCqGtABERABESg0AQkhIUufmVeBERABERAFjGnkgAAADhJREFUQqhrQAREQAREoNAEJISFLn5lXgREQAREQEKoa0AEREAERKDQBCSEhS5+ZV4EREAEROD/A5rGplivlB9PAAAAAElFTkSuQmCC)

**Eastern forest hedgehog** (not similar to Open Set):

![Eastern forest
hedgehog](data:image/jpeg;base64,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)
:::

::: {#comparing-similiarities-between-various-documents .section .cell .markdown jukit_cell_id="DUKR4HkT1D"}
# Comparing similiarities between various documents
:::

::: {.cell .code execution_count="16" jukit_cell_id="O3AiHggqL4"}
::: {#cb29 .sourceCode}
::: {#cb31 .sourceCode}
``` {.sourceCode .python}
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
```
:::
:::
:::

::: {#cosine-similarity-and-jacard-similarity-between-hedgehog-and-calculus .section .cell .markdown jukit_cell_id="OJJuEbgXHQ"}
### Cosine similarity and Jacard similarity between hedgehog and calculus
:::

::: {.cell .code execution_count="17" jukit_cell_id="PASWx1dFOx"}
::: {#cb30 .sourceCode}
::: {#cb32 .sourceCode}
``` {.sourceCode .python}
cosine_similarity_score = cosine_similarity(hedgehog_doc_vector, calculus_doc_vector)
jacard_similarity_score = jacard_similarity(hedgehog_doc_vector, calculus_doc_vector)

print("Hedgehog vs Calculus")
print(f"Cosine similarity: {cosine_similarity_score}")
print(f"Jacard similarity: {jacard_similarity_score}")
```
:::
:::

::: {.output .stream .stdout}
    Hedgehog vs Calculus
    Cosine similarity: 0.0036931801887427344
    Jacard similarity: 0.09270638525247128
:::
:::

::: {#cosine-similarity-and-jacard-similarity-between-calculus-and-derivatives .section .cell .markdown jukit_cell_id="fEuQuQsvN6"}
### Cosine similarity and Jacard similarity between calculus and derivatives
:::

::: {.cell .code execution_count="18" jukit_cell_id="ap4wb6WJ3s"}
::: {#cb32 .sourceCode}
::: {#cb34 .sourceCode}
``` {.sourceCode .python}
cosine_similarity_score = cosine_similarity(calculus_doc_vector, derivatives_doc_vector)
jacard_similarity_score = jacard_similarity(calculus_doc_vector, derivatives_doc_vector)
print("Calculus vs Derivatives")
print(f"Cosine similarity: {cosine_similarity_score}")
print(f"Jacard similarity: {jacard_similarity_score}")
```
:::
:::

::: {.output .stream .stdout}
    Calculus vs Derivatives
    Cosine similarity: 0.04768521737485992
    Jacard similarity: 0.27093206951026855
:::
:::

::: {.cell .markdown jukit_cell_id="W3JyCuLY4a"}
Cosine similarity between derivatives and hedgehog is almost **two order
of magnitude higher** than the cosine similarity between hedgehog and
calculus, what should be expected
:::

::: {#the-results-and-the-quality-of-recommender-would-be-higher-for-more-documents-than-only-1000-to-increase-this-number-before-building-the-db-one-could-change-total_pages-in-build_dbpy .section .cell .markdown jukit_cell_id="QgJ5R7EoO4"}
### The results and the quality of recommender would be higher for more documents than only 1000. To increase this number, before building the DB one could change `TOTAL_PAGES` in [`build_db.py`](https://github.com/shhhQuiettt/wikipedia-search-engine/blob/main/build_db.py)
:::
