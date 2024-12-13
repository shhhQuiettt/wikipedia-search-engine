import bs4
import asyncio
import httpx
from time import perf_counter

INITIAL_URL = "https://en.wikipedia.org/wiki/Hairy_ball_theorem"


class WikiCrawler:
    def __init__(self, client: httpx.AsyncClient, *, total_pages: int, workers: int):
        self.total_pages = total_pages
        self.client = client
        self.workers = workers

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

            urls = self.get_urls(response.text)
            for url in urls:
                await self.to_visit.put(url)

    def get_urls(self, body: str):
        soup = bs4.BeautifulSoup(body, "html.parser")

        content = soup.find("div", class_="mw-page-container")
        if content is None:
            print("Failed to find content of link")

        return [
            f"https://en.wikipedia.org{a['href'].split('#')[0]}"
            for a in content.find_all("a", href=True)
            if a["href"].startswith("/wiki/") and ":" not in a["href"]
        ]


crawler = WikiCrawler(httpx.AsyncClient(), total_pages=1000, workers=30)
print("Starting crawler")
start = perf_counter()
asyncio.run(crawler.run())
end = perf_counter()
print(f"Finished in {end - start:.2f} seconds")
print(f"Sucessfully extracted {crawler.sucessfully_extracted} pages")
