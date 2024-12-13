from queue import Queue
from indexing import perform_indexing, SqliteInvertedIndex
from crawler import crawl
from threading import Thread


def main():
    documents = Queue()

    crawler_thread = Thread(target=crawl, args=(documents, 1000, 30))
    indexing_thread = Thread(target=perform_indexing, args=(documents,))

    crawler_thread.start()
    indexing_thread.start()

    crawler_thread.join()
    indexing_thread.join()


if __name__ == "__main__":
    main()
