import os
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Add current directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from crawler.news_crawler.spiders.rss_spider import RSSSpider

def run():
    settings = {
        'ITEM_PIPELINES': {
            'crawler.news_crawler.pipelines.NewsCleaningPipeline': 300,
            'crawler.news_crawler.pipelines.NewsValidationPipeline': 400,
            'crawler.news_crawler.pipelines.PostgresStorePipeline': 500,
        },
        'LOG_LEVEL': 'INFO',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
    }
    
    process = CrawlerProcess(settings)
    process.crawl(RSSSpider)
    process.start()

if __name__ == "__main__":
    run()
