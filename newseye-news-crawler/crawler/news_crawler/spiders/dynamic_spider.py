import scrapy
from scrapy_playwright.page import PageMethod
from datetime import datetime

class DynamicSpider(scrapy.Spider):
    name = 'dynamic_spider'
    
    # Example target: A security site that might use JS rendering
    # Using TheHackerNews as a representative example
    start_urls = ['https://thehackernews.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.body-post"), # Wait for posts to load
                    ],
                },
                callback=self.parse
            )

    def parse(self, response):
        self.logger.info(f"Successfully rendered {response.url} with Playwright")
        for post in response.css('div.body-post'):
            title = post.css('h2.home-title::text').get()
            link = post.css('a.story-link::attr(href)').get()
            summary = post.css('div.home-desc::text').get()
            
            if title and link:
                yield {
                    'title':              title.strip(),
                    'content':            summary.strip() if summary else "",
                    'url':                link,
                    'source':             'TheHackerNews (Dynamic)',
                    'published_at':       None, 
                    'crawled_at':         datetime.utcnow().isoformat(),
                    'trustability_score': 0.95,
                }
