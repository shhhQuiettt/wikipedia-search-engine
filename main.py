from queue import Queue
from indexing import perform_indexing, SqliteInvertedIndex
from crawler import crawl
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


def main():
    documents = Queue()

    # crawler_thread = Thread(target=crawl, args=(documents, 10, 30))
    # indexing_thread = Thread(target=perform_indexing, args=(documents,))

    with ThreadPoolExecutor() as executor:
        executor.submit(crawl, documents, 800, 30)
        executor.submit(perform_indexing, documents)


if __name__ == "__main__":
    main()
