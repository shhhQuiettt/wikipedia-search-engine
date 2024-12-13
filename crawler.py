import bs4
from queue import Queue
from dataclasses import dataclass
import asyncio
import httpx
from time import perf_counter

INITIAL_URL = "https://en.wikipedia.org/wiki/Hairy_ball_theorem"


class Document:
    id = 0

    def __init__(self, url, title, text):
        self.url = url
        self.title = title
        self.text = text
        self.id = Document.id
        Document.id += 1


class WikiCrawler:
    def __init__(
        self,
        client: httpx.AsyncClient,
        documents: Queue,
        *,
        total_pages: int,
        workers: int,
    ):
        self.total_pages = total_pages
        self.client = client
        self.workers = workers
        self.documents = documents

        self.seen = set()
        self.to_visit = asyncio.Queue()
        self.sucessfully_extracted = 0

    async def run(self):
        await self.to_visit.put(INITIAL_URL)
        coroutines = [self.worker() for _ in range(self.workers)]
        await asyncio.gather(*coroutines)

    async def worker(self):
        while True:
            url = await self.to_visit.get()

            if url in self.seen:
                continue
            self.seen.add(url)

            print(f"Fetching {url}...")
            try:
                response = await self.client.get(url)
            except httpx.ConnectTimeout as e:
                print(f"Warining: Failed to fetch {url} due to connection timeout")
                print(f"{self.sucessfully_extracted=}")
                print(f"{self.to_visit.qsize()=}")

                continue

            if response.status_code != 200:
                print(f"Failed to fetch {url} (status code: {response.status_code})")

            if self.sucessfully_extracted >= self.total_pages:
                break

            self.sucessfully_extracted += 1

            soup = bs4.BeautifulSoup(response.text, "html.parser")
            content = soup.find("div", {"id": "bodyContent"})
            if content is None:
                print(f"Failed to find content of link {url}")
                continue

            urls = self.get_urls(content)

            self.documents.put(Document(url, response.url.path, content.get_text()))

            for url in urls:
                await self.to_visit.put(url)

    def get_urls(self, content):
        if content is None:
            print("Failed to find content of link")
            return []

        return [
            f"https://en.wikipedia.org{a['href'].split('#')[0]}"
            for a in content.find_all("a", href=True)
            if a["href"].startswith("/wiki/") and ":" not in a["href"]
        ]


def crawl(documents: Queue, total_pages: int = 1000, workers: int = 30):
    crawler = WikiCrawler(
        httpx.AsyncClient(), documents, total_pages=total_pages, workers=workers
    )
    print("Starting crawler")
    start = perf_counter()
    asyncio.run(crawler.run())
    end = perf_counter()
    print(f"Finished crawling in {end - start:.2f} seconds")
    print(f"Sucessfully extracted {crawler.sucessfully_extracted} pages")
