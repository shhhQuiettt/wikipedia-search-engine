## ([Link to Github](https://github.com/shhhQuiettt/wikipedia-search-engine))

The aim of this project is to index the Wikipedia and build a **recommender system** in a simplified form on top of it.
Given a list of previously read articles, the system should recommend the next article to read.

In this simplified form we assume that the documents are related, for example that they come from a **single session**, and we want to recommend the next article(s) to read.

### Process consists of following steps:

1. **Building the database**

   1. Downloading the Wikipedia dump
   2. Text Preprocessing
   3. Indexing
   4. Storing the index

2. **Recommending**
   1. Querying the read documents
   2. Calculating similarities
   3. Recommending the k-next articles

## Usage

1. **Building the database**

Run this command to start the crawling and database building process:

```
python build_db.py
```

2. **Recommending**

Put visited links inside `previously_seen.txt` and run this command to get 5 recommendations:

```
python recommend.py 5 previously_seen.txt
```

# Implementation

## Building the database

The building and indexing is done **asynchronously**. The crawling process is implemented in a coroutine model on a one thread ([`crawler.py`](https://github.com/shhhQuiettt/wikipedia-search-engine/blob/main/crawler.py)), while the indexing is done in a separate thread with multiple workers ([`indexing.py`](https://github.com/shhhQuiettt/wikipedia-search-engine/blob/main/indexing.py)).

### Downloading the Wikipedia dump

The crawler start from **three initial urls** to:

- An _important_ mathematical theorem: [Hairy Ball Theorem](https://en.wikipedia.org/wiki/Hairy_ball_theorem)
- Butterjelly sandwich: [Butterjelly sandwich](https://en.wikipedia.org/wiki/Butterjelly_sandwich)
- Hedgehog: [Hedgehog](https://en.wikipedia.org/wiki/Hedgehog)

Then `BeautifulSoup` is used to parse the html and extract the text from the body of the document. We also extract the title of the document. The document gets inside a queue, where it will await **preprocessing and indexing**, and we search for all urls in the body to apply the procedure recursively.

### Text Preprocessing

The text is preprocessed in the following way:

1. **Tokenization**

We tokenize the text using `nltk`'s `word_tokenize` function to obtain a list of tokens.

2. **Lemmatization**

We lemmatize the tokens using `nltk`'s `WordNetLemmatizer` to extract the base word of the token.
For example the word "running" will be lemmatized to "run".

3. **Stopwords removal**

We remove the stopwords using `nltk`'s `stopwords` list.

### Indexing

We want to store **TF-IDF** values for each word in document:

$$ \text{TF}(\text{term}, \text{document}) = \frac{\#\text{ term appears in document}}{\#\text{ the most frequent term in document}} $$

$$ \text{IDF}(\text{term}) = \log \left( \frac{\text{total number of documents}}{\text{number of documents containing term}} \right) $$

$$ \text{TF-IDF}(\text{term}, \text{document}) = \text{TF}(\text{term}, \text{document}) \times \text{IDF}(\text{term}) $$

The **IDF** is important in order to prioritize terms with **high entropy** among other documents

### Storing the index

In the current implementation we store inverted index inside **sqlite** database, but we abstract the index storage to an _abstract class_ `InvertedIndex` to possibly test other storage methods like **NoSQL** databases like _mongoDB_ or **RAM-base** like _Redis_

# Recommending

The read documents are queried from the database and the similarities are calculated using the **cosine similarity**. The cosine similarity is calculated as follows:

$$ \text{cosine similarity}(\text{doc1}, \text{doc2}) = \frac{\text{doc1} \cdot \text{doc2}}{\| \text{doc1} \| \times \| \text{doc2} \|} $$

Where document vector is a vector of **TF-IDF** values for each word in the document.

The implementation allows for using other similarity measures which fulfill the `similarity_function` interface (`recommender.py`), so we also tested **Jaccard similarity** with binary vectors:

$$ \text{Jaccard similarity}(\text{doc1}, \text{doc2}) = \frac{\text{doc1} \cap \text{doc2}}{\text{doc1} \cup \text{doc2}} $$

In the currenct implementation we assume that the documents come from a **single session** and we want to recommend the next `k` article(s) to read.

We calculate the **centroid** of the read documents and recommend the `k` closest documents to the centroid.
