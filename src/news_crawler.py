"""Schritt 2c (optional): Eigener Crawler für Schlagzeilen aus einer News-Sitemap.

Zeigt den Crawling-Teil der Vorlesung. Scrapy liest die robots.txt selbst
und hält sich daran (ROBOTSTXT_OBEY). Zusätzlich drosseln wir die Abrufe.

Start:   python src/news_crawler.py
Ergebnis: data/raw/crawler/<datum>.json

TODO (Gruppe): Seite auswählen (z.B. heise oder ZDF), deren
Nutzungsbedingungen lesen und die Sitemap-Adresse unten eintragen.
"""

from datetime import date

from scrapy.crawler import CrawlerProcess
from scrapy.spiders import SitemapSpider

from config import CRISIS_KEYWORDS_DE, RAW_DIR

# Platzhalter: hier die News-Sitemap der gewählten Seite eintragen.
SITEMAP_URLS = ["https://www.example.com/news-sitemap.xml"]


class HeadlineSpider(SitemapSpider):
    name = "headlines"
    sitemap_urls = SITEMAP_URLS

    def parse(self, response):
        """Wird für jede Artikelseite aus der Sitemap aufgerufen."""
        title = response.css("title::text").get(default="").strip()
        # Nur Artikel behalten, deren Titel einen Krisenbegriff enthält.
        if any(k.lower() in title.lower() for k in CRISIS_KEYWORDS_DE):
            yield {"url": response.url, "title": title, "crawled": date.today().isoformat()}


def main() -> None:
    out_file = RAW_DIR / "crawler" / f"{date.today()}.json"
    process = CrawlerProcess(
        settings={
            "ROBOTSTXT_OBEY": True,  # robots.txt beachten
            "DOWNLOAD_DELAY": 2,  # 2 Sekunden zwischen Abrufen
            "AUTOTHROTTLE_ENABLED": True,
            "CLOSESPIDER_ITEMCOUNT": 200,  # nach 200 Treffern aufhören
            "USER_AGENT": "Uni-Projekt Web Mining (Studierende, nicht kommerziell)",
            "FEEDS": {str(out_file): {"format": "json", "encoding": "utf8"}},
        }
    )
    process.crawl(HeadlineSpider)
    process.start()


if __name__ == "__main__":
    main()
