import scrapy
import feedparser
from datetime import datetime
from config import Config

class RSSSpider(scrapy.Spider):
    name = 'rss_spider'
    allowed_domains = ['news.google.com']

    def start_requests(self):
        self.logger.info(f"Starting requests for {len(Config.NEWS_SOURCES)} sources")
        for key, info in Config.NEWS_SOURCES.items():
            self.logger.info(f"Yielding request for {info['url']}")
            yield scrapy.Request(
                info['url'], 
                callback=self.parse_rss, 
                cb_kwargs={'source_name': info['source']}
            )

    def parse_rss(self, response, source_name):
        self.logger.info(f"Parsing RSS from {response.url}")
        feed = feedparser.parse(response.text)
        for entry in feed.entries:
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6])

            yield {
                'title':              entry.get('title', ''),
                'content':            entry.get('summary', '') or entry.get('description', ''),
                'url':                entry.get('link', ''),
                'source':             source_name,
                'published_at':       published_at,
                'crawled_at':         datetime.utcnow().isoformat(),
                'trustability_score': 0.98,
            }
