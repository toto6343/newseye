BOT_NAME = 'news_crawler'

SPIDER_MODULES = ['crawler.news_crawler.spiders']
NEWSPIDER_MODULE = 'crawler.news_crawler.spiders'

ITEM_PIPELINES = {
    'crawler.news_crawler.pipelines.NewsCleaningPipeline': 300,
    'crawler.news_crawler.pipelines.NewsValidationPipeline': 400,
    'crawler.news_crawler.pipelines.PostgresStorePipeline': 500,
}

ROBOTSTXT_OBEY = False
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
LOG_LEVEL = 'INFO'

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
}
