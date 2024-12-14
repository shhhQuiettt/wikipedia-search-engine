from queue import Queue
from indexing import perform_indexing, SqliteInvertedIndex
from crawler import crawl
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


INITIAL_URL = "https://en.wikipedia.org/wiki/Hairy_ball_theorem"
INITIAL_URL2 = "https://en.wikipedia.org/wiki/Peanut_butter_and_jelly_sandwich"


def main():
    documents = Queue()

    # crawler_thread = Thread(target=crawl, args=(documents, 10, 30))
    # indexing_thread = Thread(target=perform_indexing, args=(documents,))

    inverted_index = SqliteInvertedIndex("inverted_index.db")
    seen_urls = inverted_index.get_all_documents_urls()
    print(seen_urls)

    with ThreadPoolExecutor() as executor:
        executor.submit(crawl, documents, INITIAL_URL, seen_urls, 50, 24)
        executor.submit(perform_indexing, documents)


if __name__ == "__main__":
    main()
