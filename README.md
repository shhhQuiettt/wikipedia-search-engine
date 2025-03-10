# Wikipedia Search Engine

## Authors:
- [Krzysztof Skrobała](https://github.com/shhhQuiettt)
- [Wojciech Bogacz](https://github.com/wojbog)

 
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

- **1. Cloning the repository**

```
git clone --depth 1 https://github.com/shhhQuiettt/wikipedia-search-engine.git
cd wikipedia-search-engine

```

- **2. Creating virtual environment and downloading necessary packages**

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- **2. Building the database**

Run this command to start the crawling and database building process:

```
python build_db.py
```

- **3. Recommending**

Put visited links inside `previously_seen.txt` and run this command to get 5 recommendations:

```
python recommender.py 5 previously_seen.txt
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

$$ \text{TF}(\text{term}, \text{document}) = \frac{\text{number of term appears in document}}{\text{number of the most frequent term in document}} $$

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

<section id="some-recommendations" class="cell markdown">
<h1>Some recommendations</h1>
</section>
<section
id="1-this-session-relates-to-mathematitics-and-pioneers-of-calculus"
class="cell markdown">
<h3>1. This session relates to <strong>Mathematitics</strong> and
pioneers of <strong>Calculus</strong></h3>
</section>
<div class="cell code" data-execution_count="1">
<div class="sourceCode" id="cb1"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb1-1"><a href="#cb1-1" aria-hidden="true" tabindex="-1"></a><span class="op">!</span>cat .<span class="op">/</span>example_visited<span class="op">/</span>previously_seen1.txt</span></code></pre></div>
<div class="output stream stdout">
<pre><code>https://en.wikipedia.org/wiki/Leonhard_Euler
https://en.wikipedia.org/wiki/Isaac_Newton
https://en.wikipedia.org/wiki/Mathematics
https://en.wikipedia.org/wiki/Functions_(mathematics)
https://en.wikipedia.org/wiki/Real_number


</code></pre>
</div>
</div>
<div class="cell code" data-execution_count="2">
<div class="sourceCode" id="cb3"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb3-1"><a href="#cb3-1" aria-hidden="true" tabindex="-1"></a><span class="op">!</span>python recommender.py <span class="dv">5</span> .<span class="op">/</span>example_visited<span class="op">/</span>previously_seen1.txt</span></code></pre></div>
<div class="output stream stdout">
<pre><code>https://en.wikipedia.org/wiki/Leonhard_Euler not found in the database. Calculating document vector...
https://en.wikipedia.org/wiki/Isaac_Newton not found in the database. Calculating document vector...
Recommended documents:
(240, &#39;https://en.wikipedia.org/wiki/Hyperreal_numbers&#39;, &#39;Hyperreal number&#39;)
Cosine similarity: 0.06210137608606608

(258, &#39;https://en.wikipedia.org/wiki/Theorem&#39;, &#39;Theorem&#39;)
Cosine similarity: 0.0590626066522234

(79, &#39;https://en.wikipedia.org/wiki/Calculus&#39;, &#39;Calculus&#39;)
Cosine similarity: 0.054672164284898996

(322, &#39;https://en.wikipedia.org/wiki/Bijective&#39;, &#39;Bijection&#39;)
Cosine similarity: 0.05021229255088811

(184, &#39;https://en.wikipedia.org/wiki/Mathematical_analysis&#39;, &#39;Mathematical analysis&#39;)
Cosine similarity: 0.04862576791724621

</code></pre>
</div>
</div>
<div class="cell markdown">
<p>We see topics we would expect for someone interested in
<strong>Newton</strong> and <strong>Euler</strong> and
<strong>Mathematics</strong></p>
</div>
<section id="2-this-session-relates-sandwiches" class="cell markdown">
<h3>2. This session relates sandwiches</h3>
</section>
<div class="cell code" data-execution_count="3">
<div class="sourceCode" id="cb5"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb5-1"><a href="#cb5-1" aria-hidden="true" tabindex="-1"></a><span class="op">!</span>cat .<span class="op">/</span>example_visited<span class="op">/</span>previously_seen2.txt</span></code></pre></div>
<div class="output stream stdout">
<pre><code>https://en.wikipedia.org/wiki/Peanut_butter
https://en.wikipedia.org/wiki/Lunch
https://en.wikipedia.org/wiki/Sandwich
</code></pre>
</div>
</div>
<div class="cell code" data-execution_count="4">
<div class="sourceCode" id="cb7"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb7-1"><a href="#cb7-1" aria-hidden="true" tabindex="-1"></a><span class="op">!</span>python recommender.py <span class="dv">5</span> .<span class="op">/</span>example_visited<span class="op">/</span>previously_seen2.txt</span></code></pre></div>
<div class="output stream stdout">
<pre><code>Recommended documents:
(560, &#39;https://en.wikipedia.org/wiki/Bal%C4%B1k_ekmek&#39;, &#39;Balık ekmek&#39;)
Cosine similarity: 0.23502137689424202

(605, &#39;https://en.wikipedia.org/wiki/Roujiamo&#39;, &#39;Roujiamo&#39;)
Cosine similarity: 0.20909613026041712

(599, &#39;https://en.wikipedia.org/wiki/Panini_(sandwich)&#39;, &#39;Panini (sandwich)&#39;)
Cosine similarity: 0.19268899828898028

(583, &#39;https://en.wikipedia.org/wiki/Donkey_burger&#39;, &#39;Donkey burger&#39;)
Cosine similarity: 0.19119226566432948

(800, &#39;https://en.wikipedia.org/wiki/Bag_lunch&#39;, &#39;Packed lunch&#39;)
Cosine similarity: 0.18548005955094318

</code></pre>
</div>
</div>
<div class="cell markdown">
<p>Indeed, we see different types of sandwiches someone could be
interested in</p>
</div>
<section id="some-statistics-and-exploration-of-the-results"
class="cell markdown" data-jukit_cell_id="5tJdZ3c28b">
<h1>Some statistics and exploration of the results</h1>
</section>
<div class="cell code" data-execution_count="5"
data-jukit_cell_id="BKwtjaM3EH">
<div class="sourceCode" id="cb9"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb9-1"><a href="#cb9-1" aria-hidden="true" tabindex="-1"></a><span class="im">import</span> matplotlib.pyplot <span class="im">as</span> plt</span>
<span id="cb9-2"><a href="#cb9-2" aria-hidden="true" tabindex="-1"></a><span class="im">from</span> indexing <span class="im">import</span> SqliteInvertedIndex</span>
<span id="cb9-3"><a href="#cb9-3" aria-hidden="true" tabindex="-1"></a><span class="im">import</span> recommender</span>
<span id="cb9-4"><a href="#cb9-4" aria-hidden="true" tabindex="-1"></a><span class="im">from</span> recommender <span class="im">import</span> jacard_similarity, cosine_similarity</span>
<span id="cb9-5"><a href="#cb9-5" aria-hidden="true" tabindex="-1"></a><span class="im">import</span> numpy <span class="im">as</span> np</span></code></pre></div>
</div>
<div class="cell code" data-execution_count="6"
data-jukit_cell_id="acP0eTQMOW">
<div class="sourceCode" id="cb10"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb10-1"><a href="#cb10-1" aria-hidden="true" tabindex="-1"></a>inverted_index <span class="op">=</span> SqliteInvertedIndex(<span class="st">&quot;inverted_index.db&quot;</span>)</span>
<span id="cb10-2"><a href="#cb10-2" aria-hidden="true" tabindex="-1"></a>inverted_index_matrix <span class="op">=</span> inverted_index.get_tf_idf_matrix()</span>
<span id="cb10-3"><a href="#cb10-3" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb10-4"><a href="#cb10-4" aria-hidden="true" tabindex="-1"></a>query <span class="op">=</span> <span class="kw">lambda</span> query_text: inverted_index.cursor.execute(query_text)</span></code></pre></div>
</div>
<section id="number-of-documents" class="cell markdown"
data-jukit_cell_id="mzdCRVc0zz">
<h2>Number of documents</h2>
</section>
<div class="cell code" data-execution_count="7"
data-jukit_cell_id="88v3KdgHkG">
<div class="sourceCode" id="cb11"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb11-1"><a href="#cb11-1" aria-hidden="true" tabindex="-1"></a>query(<span class="st">&quot;select count(*) from documents&quot;</span>).fetchone()</span></code></pre></div>
<div class="output execute_result" data-execution_count="7">
<pre><code>(1000,)</code></pre>
</div>
</div>
<section id="number-of-terms" class="cell markdown"
data-jukit_cell_id="OF5gpUBFki">
<h3>Number of terms</h3>
</section>
<div class="cell code" data-execution_count="8"
data-jukit_cell_id="tlDonAt6DD">
<div class="sourceCode" id="cb13"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb13-1"><a href="#cb13-1" aria-hidden="true" tabindex="-1"></a>query(<span class="st">&quot;select count(*) from terms&quot;</span>).fetchone()</span></code></pre></div>
<div class="output execute_result" data-execution_count="8">
<pre><code>(116470,)</code></pre>
</div>
</div>
<section id="top-20-frequently-occuring-terms" class="cell markdown"
data-jukit_cell_id="uDkOPumtEj">
<h3>Top 20 frequently occuring terms</h3>
</section>
<div class="cell code" data-execution_count="9"
data-jukit_cell_id="bq6KyOhPAv">
<div class="sourceCode" id="cb15"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb15-1"><a href="#cb15-1" aria-hidden="true" tabindex="-1"></a>res <span class="op">=</span> query(</span>
<span id="cb15-2"><a href="#cb15-2" aria-hidden="true" tabindex="-1"></a>    <span class="st">&quot;&quot;&quot;</span></span>
<span id="cb15-3"><a href="#cb15-3" aria-hidden="true" tabindex="-1"></a><span class="st">    select term, sum(count) </span></span>
<span id="cb15-4"><a href="#cb15-4" aria-hidden="true" tabindex="-1"></a><span class="st">    from postings p </span></span>
<span id="cb15-5"><a href="#cb15-5" aria-hidden="true" tabindex="-1"></a><span class="st">    join terms t on p.term_id = t.id </span></span>
<span id="cb15-6"><a href="#cb15-6" aria-hidden="true" tabindex="-1"></a><span class="st">    group by term </span></span>
<span id="cb15-7"><a href="#cb15-7" aria-hidden="true" tabindex="-1"></a><span class="st">    having length(term) &gt; 3 </span></span>
<span id="cb15-8"><a href="#cb15-8" aria-hidden="true" tabindex="-1"></a><span class="st">    order by sum(count) desc</span></span>
<span id="cb15-9"><a href="#cb15-9" aria-hidden="true" tabindex="-1"></a><span class="st">    limit 10</span></span>
<span id="cb15-10"><a href="#cb15-10" aria-hidden="true" tabindex="-1"></a><span class="st">            &quot;&quot;&quot;</span></span>
<span id="cb15-11"><a href="#cb15-11" aria-hidden="true" tabindex="-1"></a>)</span>
<span id="cb15-12"><a href="#cb15-12" aria-hidden="true" tabindex="-1"></a>res.fetchall()</span></code></pre></div>
<div class="output execute_result" data-execution_count="9">
<pre><code>[(&#39;shrew&#39;, 32304),
 (&#39;function&#39;, 14177),
 (&#39;retrieved&#39;, 12128),
 (&#39;edit&#39;, 11623),
 (&#39;space&#39;, 8069),
 (&#39;isbn&#39;, 7562),
 (&#39;also&#39;, 7100),
 (&#39;archived&#39;, 6817),
 (&#39;original&#39;, 6753),
 (&#39;number&#39;, 6483)]</code></pre>
</div>
</div>
<div class="cell markdown" data-jukit_cell_id="29HOlidCNL">
<p>Despite weirdness of <em>shrew</em>, and manually checking, it turns
out that <em>shrew</em> <strong>indeed is</strong> a frequent word in
the documents related to mammals and other animals</p>
</div>
<section id="terms-with-lowest-entropy" class="cell markdown"
data-jukit_cell_id="YnwfvTmBYU">
<h3>Terms with lowest entropy</h3>
</section>
<div class="cell code" data-execution_count="10"
data-jukit_cell_id="7iVCUI0aWb">
<div class="sourceCode" id="cb17"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb17-1"><a href="#cb17-1" aria-hidden="true" tabindex="-1"></a>query(</span>
<span id="cb17-2"><a href="#cb17-2" aria-hidden="true" tabindex="-1"></a>    <span class="st">&quot;&quot;&quot;</span></span>
<span id="cb17-3"><a href="#cb17-3" aria-hidden="true" tabindex="-1"></a><span class="st">        select term, idf from terms order by idf asc limit 10</span></span>
<span id="cb17-4"><a href="#cb17-4" aria-hidden="true" tabindex="-1"></a><span class="st">        &quot;&quot;&quot;</span></span>
<span id="cb17-5"><a href="#cb17-5" aria-hidden="true" tabindex="-1"></a>).fetchall()</span></code></pre></div>
<div class="output execute_result" data-execution_count="10">
<pre><code>[(&#39;retrieved&#39;, 0.0),
 (&#39;http&#39;, 0.0),
 (&#39;1&#39;, 0.022245608947319737),
 (&#39;reference&#39;, 0.03978087001184446),
 (&#39;edit&#39;, 0.06935007813479324),
 (&#39;2&#39;, 0.08773891430800689),
 (&#39;also&#39;, 0.1266976530459575),
 (&#39;3&#39;, 0.1636960926707897),
 (&#39;see&#39;, 0.1779312084926618),
 (&#39;new&#39;, 0.18632957819149354)]</code></pre>
</div>
</div>
<section id="terms-with-highest-entropy" class="cell markdown"
data-jukit_cell_id="heVO1aiSno">
<h3>Terms with highest entropy</h3>
</section>
<div class="cell code" data-execution_count="11"
data-jukit_cell_id="2pSmidhWJs">
<div class="sourceCode" id="cb19"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb19-1"><a href="#cb19-1" aria-hidden="true" tabindex="-1"></a>query(</span>
<span id="cb19-2"><a href="#cb19-2" aria-hidden="true" tabindex="-1"></a>    <span class="st">&quot;&quot;&quot;</span></span>
<span id="cb19-3"><a href="#cb19-3" aria-hidden="true" tabindex="-1"></a><span class="st">  select term, idf from terms order by idf desc limit 10</span></span>
<span id="cb19-4"><a href="#cb19-4" aria-hidden="true" tabindex="-1"></a><span class="st">  &quot;&quot;&quot;</span></span>
<span id="cb19-5"><a href="#cb19-5" aria-hidden="true" tabindex="-1"></a>).fetchall()</span></code></pre></div>
<div class="output execute_result" data-execution_count="11">
<pre><code>[(&#39;combable&#39;, 6.907755278982137),
 (&#39;ℝ3&#39;, 6.907755278982137),
 (&#39;idealizes&#39;, 6.907755278982137),
 (&#39;meteorologically&#39;, 6.907755278982137),
 (&#39;accomplishes&#39;, 6.907755278982137),
 (&#39;gidea&#39;, 6.907755278982137),
 (&#39;1584882530&#39;, 6.907755278982137),
 (&#39;abbildung&#39;, 6.907755278982137),
 (&#39;bormashenko&#39;, 6.907755278982137),
 (&#39;kazachkov&#39;, 6.907755278982137)]</code></pre>
</div>
</div>
<section id="distribution-of-terms-occurance-among-all-documents"
class="cell markdown" data-jukit_cell_id="PBeq7ZpcIw">
<h3>Distribution of terms occurance among all documents</h3>
</section>
<div class="cell code" data-execution_count="12"
data-jukit_cell_id="VPxjM0s195">
<div class="sourceCode" id="cb21"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb21-1"><a href="#cb21-1" aria-hidden="true" tabindex="-1"></a>res <span class="op">=</span> query(</span>
<span id="cb21-2"><a href="#cb21-2" aria-hidden="true" tabindex="-1"></a>    <span class="st">&quot;&quot;&quot;</span></span>
<span id="cb21-3"><a href="#cb21-3" aria-hidden="true" tabindex="-1"></a><span class="st">        select t.term, sum(p.count) </span></span>
<span id="cb21-4"><a href="#cb21-4" aria-hidden="true" tabindex="-1"></a><span class="st">        from terms t join postings p on t.id = p.term_id </span></span>
<span id="cb21-5"><a href="#cb21-5" aria-hidden="true" tabindex="-1"></a><span class="st">        group by t.term</span></span>
<span id="cb21-6"><a href="#cb21-6" aria-hidden="true" tabindex="-1"></a><span class="st">        order by sum(p.count) desc</span></span>
<span id="cb21-7"><a href="#cb21-7" aria-hidden="true" tabindex="-1"></a><span class="st">    &quot;&quot;&quot;</span></span>
<span id="cb21-8"><a href="#cb21-8" aria-hidden="true" tabindex="-1"></a>).fetchall()</span>
<span id="cb21-9"><a href="#cb21-9" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb21-10"><a href="#cb21-10" aria-hidden="true" tabindex="-1"></a>plt.plot([x[<span class="dv">1</span>] <span class="cf">for</span> x <span class="kw">in</span> res])</span></code></pre></div>
<div class="output execute_result" data-execution_count="12">
<pre><code>[&lt;matplotlib.lines.Line2D at 0x7ff29a850690&gt;]</code></pre>
</div>
<div class="output display_data">
<p><img src="a3a5147a407b6e537d935838d4fef9c8279d6429.png" /></p>
</div>
</div>
<section id="checking-if-corpus-fulfills-zipfs-law"
class="cell markdown" data-jukit_cell_id="Mz3pWiVxLw">
<h3>Checking if corpus fulfills Zipf's law</h3>
</section>
<div class="cell code" data-execution_count="13"
data-jukit_cell_id="ZZsb7UgsYh">
<div class="sourceCode" id="cb23"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb23-1"><a href="#cb23-1" aria-hidden="true" tabindex="-1"></a>res <span class="op">=</span> query(</span>
<span id="cb23-2"><a href="#cb23-2" aria-hidden="true" tabindex="-1"></a>    <span class="st">&quot;&quot;&quot;</span></span>
<span id="cb23-3"><a href="#cb23-3" aria-hidden="true" tabindex="-1"></a><span class="st">    select t.term, sum(p.count)</span></span>
<span id="cb23-4"><a href="#cb23-4" aria-hidden="true" tabindex="-1"></a><span class="st">    from terms t join postings p on t.id = p.term_id</span></span>
<span id="cb23-5"><a href="#cb23-5" aria-hidden="true" tabindex="-1"></a><span class="st">    group by t.term</span></span>
<span id="cb23-6"><a href="#cb23-6" aria-hidden="true" tabindex="-1"></a><span class="st">    order by sum(p.count) desc</span></span>
<span id="cb23-7"><a href="#cb23-7" aria-hidden="true" tabindex="-1"></a><span class="st">    &quot;&quot;&quot;</span></span>
<span id="cb23-8"><a href="#cb23-8" aria-hidden="true" tabindex="-1"></a>).fetchall()</span>
<span id="cb23-9"><a href="#cb23-9" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb23-10"><a href="#cb23-10" aria-hidden="true" tabindex="-1"></a>ocurrances <span class="op">=</span> np.array([x[<span class="dv">1</span>] <span class="cf">for</span> x <span class="kw">in</span> res])</span>
<span id="cb23-11"><a href="#cb23-11" aria-hidden="true" tabindex="-1"></a>N <span class="op">=</span> <span class="bu">len</span>(ocurrances)</span>
<span id="cb23-12"><a href="#cb23-12" aria-hidden="true" tabindex="-1"></a>k <span class="op">=</span> ocurrances[<span class="dv">3</span>] <span class="op">/</span> N <span class="op">*</span> <span class="dv">4</span></span>
<span id="cb23-13"><a href="#cb23-13" aria-hidden="true" tabindex="-1"></a>expected_zipf <span class="op">=</span> k <span class="op">/</span> np.arange(<span class="dv">1</span>, N <span class="op">+</span> <span class="dv">1</span>)</span>
<span id="cb23-14"><a href="#cb23-14" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb23-15"><a href="#cb23-15" aria-hidden="true" tabindex="-1"></a>cut_off <span class="op">=</span> <span class="dv">1000</span></span>
<span id="cb23-16"><a href="#cb23-16" aria-hidden="true" tabindex="-1"></a>plt.plot(ocurrances[:<span class="dv">1000</span>] <span class="op">/</span> N)</span>
<span id="cb23-17"><a href="#cb23-17" aria-hidden="true" tabindex="-1"></a>plt.plot(expected_zipf[:<span class="dv">1000</span>])</span>
<span id="cb23-18"><a href="#cb23-18" aria-hidden="true" tabindex="-1"></a>plt.legend([<span class="st">&quot;Actual frequency&quot;</span>, <span class="st">&quot;Expected from Zipf&#39;s law&quot;</span>])</span></code></pre></div>
<div class="output execute_result" data-execution_count="13">
<pre><code>&lt;matplotlib.legend.Legend at 0x7ff29a84dbe0&gt;</code></pre>
</div>
<div class="output display_data">
<p><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAksAAAGdCAYAAAACMjetAAAAOnRFWHRTb2Z0d2FyZQBNYXRwbG90bGliIHZlcnNpb24zLjEwLjAsIGh0dHBzOi8vbWF0cGxvdGxpYi5vcmcvlHJYcgAAAAlwSFlzAAAPYQAAD2EBqD+naQAAMxpJREFUeJzt3Xt0VPW9///XTJKZhMskXCRDJFwsSuQiSGLi1Et/HnMYPVltqaxKKdUcRKs0WCA9QFlVsD1tw8JjFRWw1nWE9TtVIOtbWwWEb064HSWCBINcIx6xocIkKmQmUEhC5vP9Q7PLSNgykCFMeD7W2qvM/rznsz/705XOq3v2/ozDGGMEAACANjk7egAAAACXM8ISAACADcISAACADcISAACADcISAACADcISAACADcISAACADcISAACAjcSOHkBHCofDOnz4sLp37y6Hw9HRwwEAAOfBGKOGhgZlZGTI6Yz9dZ8rOiwdPnxYmZmZHT0MAABwAQ4dOqR+/frF/DhXdFjq3r27pC8m2+PxdPBoAADA+QiFQsrMzLQ+x2Ptig5LrV+9eTwewhIAAHHmUt1Cww3eAAAANghLAAAANghLAAAANghLAAAANghLAAAANghLAAAANghLAAAANqIOS5988ol+9KMfqVevXkpJSdGIESO0fft2q90Yo7lz56pv375KSUlRfn6+Dhw4ENHH0aNHNXHiRHk8HqWlpWny5Mk6fvx4RM3777+v2267TcnJycrMzNSCBQvOGktpaamysrKUnJysESNGaM2aNdGeDgAAgK2owtKxY8d0yy23KCkpSW+++ab27t2rp556Sj169LBqFixYoGeffVYvvPCCtm7dqq5du8rv9+vUqVNWzcSJE7Vnzx6VlZVp1apV2rx5s3784x9b7aFQSGPGjNGAAQNUWVmpJ598Uk888YRefPFFq2bLli2aMGGCJk+erPfee09jx47V2LFjtXv37ouZDwAAgEgmCrNnzza33nrrOdvD4bDxer3mySeftPbV19cbt9ttXn31VWOMMXv37jWSzLvvvmvVvPnmm8bhcJhPPvnEGGPM4sWLTY8ePUxjY2PEsYcMGWK9vvfee01BQUHE8fPy8szDDz983ucTDAaNJBMMBs/7PQAAoGNd6s/vqK4svf7668rJydH3v/999enTRzfeeKP+8Ic/WO0HDx5UIBBQfn6+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" /></p>
</div>
</div>
<section id="documents-most-similar-to-the-article-open-set"
class="cell markdown" data-jukit_cell_id="yTfKqUqIFM">
<h3>Documents most similar to the article <strong>Open Set</strong></h3>
</section>
<div class="cell code" data-execution_count="14"
data-jukit_cell_id="oyxhg3nskT">
<div class="sourceCode" id="cb25"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb25-1"><a href="#cb25-1" aria-hidden="true" tabindex="-1"></a>url <span class="op">=</span> <span class="st">&quot;https://en.wikipedia.org/wiki/Open_set&quot;</span></span>
<span id="cb25-2"><a href="#cb25-2" aria-hidden="true" tabindex="-1"></a>doc_id <span class="op">=</span> inverted_index.get_document_id(url)</span>
<span id="cb25-3"><a href="#cb25-3" aria-hidden="true" tabindex="-1"></a><span class="cf">assert</span> doc_id <span class="kw">is</span> <span class="kw">not</span> <span class="va">None</span></span>
<span id="cb25-4"><a href="#cb25-4" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb25-5"><a href="#cb25-5" aria-hidden="true" tabindex="-1"></a>doc_vector <span class="op">=</span> inverted_index_matrix[doc_id, :]</span>
<span id="cb25-6"><a href="#cb25-6" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb25-7"><a href="#cb25-7" aria-hidden="true" tabindex="-1"></a>similarities <span class="op">=</span> np.apply_along_axis(</span>
<span id="cb25-8"><a href="#cb25-8" aria-hidden="true" tabindex="-1"></a>    <span class="kw">lambda</span> x: cosine_similarity(doc_vector, x), <span class="dv">1</span>, inverted_index_matrix</span>
<span id="cb25-9"><a href="#cb25-9" aria-hidden="true" tabindex="-1"></a>)</span>
<span id="cb25-10"><a href="#cb25-10" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb25-11"><a href="#cb25-11" aria-hidden="true" tabindex="-1"></a>top_5_similarities <span class="op">=</span> np.argsort(similarities, axis<span class="op">=</span><span class="dv">0</span>)[<span class="op">-</span><span class="dv">6</span>:<span class="op">-</span><span class="dv">1</span>]</span>
<span id="cb25-12"><a href="#cb25-12" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb25-13"><a href="#cb25-13" aria-hidden="true" tabindex="-1"></a><span class="cf">for</span> doc_id <span class="kw">in</span> top_5_similarities[::<span class="op">-</span><span class="dv">1</span>]:</span>
<span id="cb25-14"><a href="#cb25-14" aria-hidden="true" tabindex="-1"></a>    res <span class="op">=</span> query(</span>
<span id="cb25-15"><a href="#cb25-15" aria-hidden="true" tabindex="-1"></a>        <span class="ss">f&quot;&quot;&quot;</span></span>
<span id="cb25-16"><a href="#cb25-16" aria-hidden="true" tabindex="-1"></a><span class="ss">        select title from documents where id = </span><span class="sc">{</span>doc_id<span class="sc">}</span></span>
<span id="cb25-17"><a href="#cb25-17" aria-hidden="true" tabindex="-1"></a><span class="ss">        &quot;&quot;&quot;</span>,</span>
<span id="cb25-18"><a href="#cb25-18" aria-hidden="true" tabindex="-1"></a>    ).fetchone()</span>
<span id="cb25-19"><a href="#cb25-19" aria-hidden="true" tabindex="-1"></a>    <span class="cf">assert</span> res <span class="kw">is</span> <span class="kw">not</span> <span class="va">None</span></span>
<span id="cb25-20"><a href="#cb25-20" aria-hidden="true" tabindex="-1"></a>    <span class="bu">print</span>(<span class="ss">f&quot;Title: </span><span class="sc">{</span>res[<span class="dv">0</span>]<span class="sc">}</span><span class="ss">&quot;</span>)</span>
<span id="cb25-21"><a href="#cb25-21" aria-hidden="true" tabindex="-1"></a>    <span class="bu">print</span>(<span class="ss">f&quot;Cosine similarity: </span><span class="sc">{</span>similarities[doc_id]<span class="sc">}</span><span class="ch">\n</span><span class="ss">&quot;</span>)</span></code></pre></div>
<div class="output stream stdout">
<pre><code>Title: Open set
Cosine similarity: 1.0

Title: Closed set
Cosine similarity: 0.1670939050012435

Title: Accumulation point
Cosine similarity: 0.09399570728349808

Title: Open and closed maps
Cosine similarity: 0.09323925622985396

Title: Open and closed maps
Cosine similarity: 0.09323925622985396

</code></pre>
</div>
</div>
<section id="documents-least-similar-document-to-the-article-open-set"
class="cell markdown" data-jukit_cell_id="tfegEl31Qc">
<h3>Documents least similar document to the article <strong>Open
set</strong></h3>
</section>
<div class="cell code" data-execution_count="15"
data-jukit_cell_id="8LPlMdFam6">
<div class="sourceCode" id="cb27"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb27-1"><a href="#cb27-1" aria-hidden="true" tabindex="-1"></a>url <span class="op">=</span> <span class="st">&quot;https://en.wikipedia.org/wiki/Open_set&quot;</span></span>
<span id="cb27-2"><a href="#cb27-2" aria-hidden="true" tabindex="-1"></a>doc_id <span class="op">=</span> inverted_index.get_document_id(url)</span>
<span id="cb27-3"><a href="#cb27-3" aria-hidden="true" tabindex="-1"></a><span class="cf">assert</span> doc_id <span class="kw">is</span> <span class="kw">not</span> <span class="va">None</span></span>
<span id="cb27-4"><a href="#cb27-4" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb27-5"><a href="#cb27-5" aria-hidden="true" tabindex="-1"></a>doc_vector <span class="op">=</span> inverted_index_matrix[doc_id, :]</span>
<span id="cb27-6"><a href="#cb27-6" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb27-7"><a href="#cb27-7" aria-hidden="true" tabindex="-1"></a>similarities <span class="op">=</span> np.apply_along_axis(</span>
<span id="cb27-8"><a href="#cb27-8" aria-hidden="true" tabindex="-1"></a>    <span class="kw">lambda</span> x: cosine_similarity(doc_vector, x), <span class="dv">1</span>, inverted_index_matrix</span>
<span id="cb27-9"><a href="#cb27-9" aria-hidden="true" tabindex="-1"></a>)</span>
<span id="cb27-10"><a href="#cb27-10" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb27-11"><a href="#cb27-11" aria-hidden="true" tabindex="-1"></a>top_5_similarities <span class="op">=</span> np.argsort(similarities, axis<span class="op">=</span><span class="dv">0</span>)[:<span class="dv">5</span>]</span>
<span id="cb27-12"><a href="#cb27-12" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb27-13"><a href="#cb27-13" aria-hidden="true" tabindex="-1"></a><span class="cf">for</span> doc_id <span class="kw">in</span> top_5_similarities:</span>
<span id="cb27-14"><a href="#cb27-14" aria-hidden="true" tabindex="-1"></a>    res <span class="op">=</span> query(</span>
<span id="cb27-15"><a href="#cb27-15" aria-hidden="true" tabindex="-1"></a>        <span class="ss">f&quot;&quot;&quot;</span></span>
<span id="cb27-16"><a href="#cb27-16" aria-hidden="true" tabindex="-1"></a><span class="ss">        select title from documents where id = </span><span class="sc">{</span>doc_id<span class="sc">}</span></span>
<span id="cb27-17"><a href="#cb27-17" aria-hidden="true" tabindex="-1"></a><span class="ss">        &quot;&quot;&quot;</span>,</span>
<span id="cb27-18"><a href="#cb27-18" aria-hidden="true" tabindex="-1"></a>    ).fetchone()</span>
<span id="cb27-19"><a href="#cb27-19" aria-hidden="true" tabindex="-1"></a>    <span class="cf">assert</span> res <span class="kw">is</span> <span class="kw">not</span> <span class="va">None</span></span>
<span id="cb27-20"><a href="#cb27-20" aria-hidden="true" tabindex="-1"></a>    <span class="bu">print</span>(<span class="ss">f&quot;Title: </span><span class="sc">{</span>res[<span class="dv">0</span>]<span class="sc">}</span><span class="ss">&quot;</span>)</span>
<span id="cb27-21"><a href="#cb27-21" aria-hidden="true" tabindex="-1"></a>    <span class="bu">print</span>(<span class="ss">f&quot;Cosine similarity: </span><span class="sc">{</span>similarities[doc_id]<span class="sc">}</span><span class="ch">\n</span><span class="ss">&quot;</span>)</span></code></pre></div>
<div class="output stream stdout">
<pre><code>Title: Eastern forest hedgehog
Cosine similarity: 4.099291536117715e-06

Title: Chacarero
Cosine similarity: 1.473436229790874e-05

Title: Somali hedgehog
Cosine similarity: 2.148079406048971e-05

Title: Hemiechinus
Cosine similarity: 2.2237134281189762e-05

Title: Gaoligong forest hedgehog
Cosine similarity: 2.259060627956648e-05

</code></pre>
</div>
</div>
<div class="cell markdown" data-jukit_cell_id="5qQpK8dZFl">
<p>These results make sense, as Open Set relates to topics like
<em>topology</em> and <em>closed sets</em>, while do not relate to
topics like <em>hedgehogs</em> or <em>Chacarero</em></p>
<p><strong>Open Set</strong>:</p>
<p><img src="./reports/imgs/open-set.png" alt="Open Set" /></p>
<p><strong>Closed Set</strong> (similar to Open Set):</p>
<p><img src="./reports/imgs/closed-set.png" alt="Closed Set" /></p>
<p><strong>Eastern forest hedgehog</strong> (not similar to Open
Set):</p>
<p><img src="./reports/imgs/eastern-forest-hedgehog.jpeg"
alt="Eastern forest hedgehog" /></p>
</div>
<section id="comparing-similiarities-between-various-documents"
class="cell markdown" data-jukit_cell_id="DUKR4HkT1D">
<h1>Comparing similiarities between various documents</h1>
</section>
<div class="cell code" data-execution_count="16"
data-jukit_cell_id="O3AiHggqL4">
<div class="sourceCode" id="cb29"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb29-1"><a href="#cb29-1" aria-hidden="true" tabindex="-1"></a>hedghog_doc_url <span class="op">=</span> <span class="st">&quot;https://en.wikipedia.org/wiki/Hedgehog&quot;</span></span>
<span id="cb29-2"><a href="#cb29-2" aria-hidden="true" tabindex="-1"></a>hedgehog_doc_id <span class="op">=</span> inverted_index.get_document_id(hedghog_doc_url)</span>
<span id="cb29-3"><a href="#cb29-3" aria-hidden="true" tabindex="-1"></a>hedgehog_doc_vector <span class="op">=</span> inverted_index_matrix[hedgehog_doc_id, :]</span>
<span id="cb29-4"><a href="#cb29-4" aria-hidden="true" tabindex="-1"></a><span class="cf">assert</span> hedgehog_doc_vector <span class="kw">is</span> <span class="kw">not</span> <span class="va">None</span></span>
<span id="cb29-5"><a href="#cb29-5" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb29-6"><a href="#cb29-6" aria-hidden="true" tabindex="-1"></a>calculus_doc_url <span class="op">=</span> <span class="st">&quot;https://en.wikipedia.org/wiki/Calculus&quot;</span></span>
<span id="cb29-7"><a href="#cb29-7" aria-hidden="true" tabindex="-1"></a>calculus_doc_id <span class="op">=</span> inverted_index.get_document_id(calculus_doc_url)</span>
<span id="cb29-8"><a href="#cb29-8" aria-hidden="true" tabindex="-1"></a>calculus_doc_vector <span class="op">=</span> inverted_index_matrix[calculus_doc_id, :]</span>
<span id="cb29-9"><a href="#cb29-9" aria-hidden="true" tabindex="-1"></a><span class="cf">assert</span> calculus_doc_vector <span class="kw">is</span> <span class="kw">not</span> <span class="va">None</span></span>
<span id="cb29-10"><a href="#cb29-10" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb29-11"><a href="#cb29-11" aria-hidden="true" tabindex="-1"></a>derivatives_doc_url <span class="op">=</span> <span class="st">&quot;https://en.wikipedia.org/wiki/Derivative&quot;</span></span>
<span id="cb29-12"><a href="#cb29-12" aria-hidden="true" tabindex="-1"></a>derivatives_doc_id <span class="op">=</span> inverted_index.get_document_id(derivatives_doc_url)</span>
<span id="cb29-13"><a href="#cb29-13" aria-hidden="true" tabindex="-1"></a>derivatives_doc_vector <span class="op">=</span> inverted_index_matrix[derivatives_doc_id, :]</span>
<span id="cb29-14"><a href="#cb29-14" aria-hidden="true" tabindex="-1"></a><span class="cf">assert</span> derivatives_doc_vector <span class="kw">is</span> <span class="kw">not</span> <span class="va">None</span></span></code></pre></div>
</div>
<section
id="cosine-similarity-and-jacard-similarity-between-hedgehog-and-calculus"
class="cell markdown" data-jukit_cell_id="OJJuEbgXHQ">
<h3>Cosine similarity and Jacard similarity between hedgehog and
calculus</h3>
</section>
<div class="cell code" data-execution_count="17"
data-jukit_cell_id="PASWx1dFOx">
<div class="sourceCode" id="cb30"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb30-1"><a href="#cb30-1" aria-hidden="true" tabindex="-1"></a>cosine_similarity_score <span class="op">=</span> cosine_similarity(hedgehog_doc_vector, calculus_doc_vector)</span>
<span id="cb30-2"><a href="#cb30-2" aria-hidden="true" tabindex="-1"></a>jacard_similarity_score <span class="op">=</span> jacard_similarity(hedgehog_doc_vector, calculus_doc_vector)</span>
<span id="cb30-3"><a href="#cb30-3" aria-hidden="true" tabindex="-1"></a></span>
<span id="cb30-4"><a href="#cb30-4" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span>(<span class="st">&quot;Hedgehog vs Calculus&quot;</span>)</span>
<span id="cb30-5"><a href="#cb30-5" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span>(<span class="ss">f&quot;Cosine similarity: </span><span class="sc">{</span>cosine_similarity_score<span class="sc">}</span><span class="ss">&quot;</span>)</span>
<span id="cb30-6"><a href="#cb30-6" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span>(<span class="ss">f&quot;Jacard similarity: </span><span class="sc">{</span>jacard_similarity_score<span class="sc">}</span><span class="ss">&quot;</span>)</span></code></pre></div>
<div class="output stream stdout">
<pre><code>Hedgehog vs Calculus
Cosine similarity: 0.0036931801887427344
Jacard similarity: 0.09270638525247128
</code></pre>
</div>
</div>
<section
id="cosine-similarity-and-jacard-similarity-between-calculus-and-derivatives"
class="cell markdown" data-jukit_cell_id="fEuQuQsvN6">
<h3>Cosine similarity and Jacard similarity between calculus and
derivatives</h3>
</section>
<div class="cell code" data-execution_count="18"
data-jukit_cell_id="ap4wb6WJ3s">
<div class="sourceCode" id="cb32"><pre
class="sourceCode python"><code class="sourceCode python"><span id="cb32-1"><a href="#cb32-1" aria-hidden="true" tabindex="-1"></a>cosine_similarity_score <span class="op">=</span> cosine_similarity(calculus_doc_vector, derivatives_doc_vector)</span>
<span id="cb32-2"><a href="#cb32-2" aria-hidden="true" tabindex="-1"></a>jacard_similarity_score <span class="op">=</span> jacard_similarity(calculus_doc_vector, derivatives_doc_vector)</span>
<span id="cb32-3"><a href="#cb32-3" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span>(<span class="st">&quot;Calculus vs Derivatives&quot;</span>)</span>
<span id="cb32-4"><a href="#cb32-4" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span>(<span class="ss">f&quot;Cosine similarity: </span><span class="sc">{</span>cosine_similarity_score<span class="sc">}</span><span class="ss">&quot;</span>)</span>
<span id="cb32-5"><a href="#cb32-5" aria-hidden="true" tabindex="-1"></a><span class="bu">print</span>(<span class="ss">f&quot;Jacard similarity: </span><span class="sc">{</span>jacard_similarity_score<span class="sc">}</span><span class="ss">&quot;</span>)</span></code></pre></div>
<div class="output stream stdout">
<pre><code>Calculus vs Derivatives
Cosine similarity: 0.04768521737485992
Jacard similarity: 0.27093206951026855
</code></pre>
</div>
</div>
<div class="cell markdown" data-jukit_cell_id="W3JyCuLY4a">
<p>Cosine similarity between derivatives and hedgehog is almost
<strong>two order of magnitude higher</strong> than the cosine
similarity between hedgehog and calculus, what should be expected</p>
</div>
<section
id="the-results-and-the-quality-of-recommender-would-be-higher-for-more-documents-than-only-1000-to-increase-this-number-before-building-the-db-one-could-change-total_pages-in-build_dbpy"
class="cell markdown" data-jukit_cell_id="QgJ5R7EoO4">
<h3>The results and the quality of recommender would be higher for more
documents than only 1000. To increase this number, before building the
DB one could change <code>TOTAL_PAGES</code> in <a
href="https://github.com/shhhQuiettt/wikipedia-search-engine/blob/main/build_db.py"><code>build_db.py</code></a></h3>
</section>
