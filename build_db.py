from queue import Queue
from indexing import perform_indexing, SqliteInvertedIndex
from crawler import crawl
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from nltk.corpus import wordnet
from nltk.corpus import stopwords


INITIAL_URL = "https://en.wikipedia.org/wiki/Hairy_ball_theorem"
INITIAL_URL2 = "https://en.wikipedia.org/wiki/Peanut_butter_and_jelly_sandwich"
INITIAL_URL3 = "https://en.wikipedia.org/wiki/Hedgehog"


def main():
    import nltk

    nltk.download("punkt_tab")
    nltk.download("stopwords")
    nltk.download("wordnet")

    stopwords.ensure_loaded()
    wordnet.ensure_loaded()

    documents = Queue()

    inverted_index = SqliteInvertedIndex("inverted_index.db")
    seen_urls = inverted_index.get_all_documents_urls()

    with ThreadPoolExecutor() as executor:
        crawling_future1 = executor.submit(
            crawl, documents, INITIAL_URL, seen_urls, 400, 5
        )
        crawling_future2 = executor.submit(
            crawl, documents, INITIAL_URL2, seen_urls, 300, 5
        )
        crawling_future3 = executor.submit(
            crawl, documents, INITIAL_URL3, seen_urls, 300, 5
        )
        indexing_future = executor.submit(perform_indexing, documents, no_of_threads=5)

        try:
            crawling_future1.result()
            crawling_future2.result()
            crawling_future3.result()
            indexing_future.result()
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Shutting down executor...")
            raise


if __name__ == "__main__":
    main()
