import requests
from bs4 import BeautifulSoup
from datetime import datetime


class WebsiteScraper:

    def __init__(self):

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0.0.0 "
                "Safari/537.36"
            )
        }



    def fetch_page(self, url):

        try:

            response = requests.get(
                url,
                headers=self.headers,
                timeout=20
            )

            response.raise_for_status()

            return response.text

        except requests.RequestException as e:

            print(
                f"Error fetching {url}: {e}"
            )

            return None



    def fetch_dynamic_page(self, url):

        try:

            from playwright.sync_api import (
                sync_playwright
            )

            print(
                "Using Playwright for dynamic page..."
            )

            with sync_playwright() as p:

                browser = p.chromium.launch(
                    headless=True
                )

                page = browser.new_page(
                    user_agent=self.headers[
                        "User-Agent"
                    ]
                )

                page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=60000
                )

                # Give JavaScript additional time
                page.wait_for_timeout(5000)

                html = page.content()

                browser.close()

                return html

        except Exception as e:

            print(
                f"Playwright error: {e}"
            )

            return None

    def extract_text(self, html):

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header"
        ]):

            tag.decompose()

        return soup.get_text(
            separator=" ",
            strip=True
        )


    def scrape_static_page(self, url):

        html = self.fetch_page(
            url
        )

        if not html:
            return None

        text = self.extract_text(
            html
        )

        return {
            "source": url,
            "text": text,
            "type": "website",
            "fetched_at": datetime.now().isoformat()
        }


    def scrape_dynamic_page(self, url):

        html = self.fetch_dynamic_page(
            url
        )

        if not html:
            return None

        text = self.extract_text(
            html
        )

        return {
            "source": url,
            "text": text,
            "type": "website",
            "fetched_at": datetime.now().isoformat()
        }



    def scrape_page(self, url):

        print(
            f"\nScraping: {url}"
        )



        if "parakh.itmuniversity.ac.in" in url:

            document = (
                self.scrape_dynamic_page(
                    url
                )
            )

            if document:

                print(
                    "Characters:",
                    len(
                        document["text"]
                    )
                )

                # Debug checks
                text_lower = document[
                    "text"
                ].lower()

                print(
                    "Campus Achievers:",
                    "campus achievers"
                    in text_lower
                )

                print(
                    "Aman Sharma:",
                    "aman sharma"
                    in text_lower
                )

                return document



        document = (
            self.scrape_static_page(
                url
            )
        )

        if document:

            print(
                "Characters:",
                len(
                    document["text"]
                )
            )

        return document



    def scrape_urls(self, urls):

        documents = []

        for url in urls:

            document = self.scrape_page(
                url
            )

            if document:

                documents.append(
                    document
                )

        return documents




if __name__ == "__main__":

    from app.website_sources import (
        OFFICIAL_WEBSITE_URLS
    )

    scraper = WebsiteScraper()

    documents = scraper.scrape_urls(
        OFFICIAL_WEBSITE_URLS
    )

    print(
        f"\nTotal pages scraped: "
        f"{len(documents)}"
    )

    for document in documents:

        print(
            "\n-------------------------"
        )

        print(
            "Source:",
            document["source"]
        )

        print(
            "Characters:",
            len(
                document["text"]
            )
        )

        text = document[
            "text"
        ].lower()

        if "parakh.itmuniversity.ac.in" in document[
            "source"
        ].lower():

            print(
                "Campus Achievers:",
                "campus achievers"
                in text
            )

            print(
                "Aman Sharma:",
                "aman sharma"
                in text
            )