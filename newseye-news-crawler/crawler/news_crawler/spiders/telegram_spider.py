import scrapy
from datetime import datetime
from config import Config

class TelegramSpider(scrapy.Spider):
    name = 'telegram_spider'

    def start_requests(self):
        for channel in Config.TELEGRAM_CHANNELS:
            url = f"https://t.me/s/{channel}"
            yield scrapy.Request(url=url, callback=self.parse, meta={'channel': channel})

    def parse(self, response):
        # Telegram web preview uses .tgme_widget_message_wrap for messages
        messages = response.css('.tgme_widget_message_wrap')
        
        for msg in messages:
            content = msg.css('.tgme_widget_message_text').xpath('string()').get()
            if not content:
                continue

            # Title is first few words or first line
            lines = content.strip().split('\n')
            title = lines[0][:100] if lines else "Telegram Update"
            
            # URL for the specific message
            msg_id = msg.css('.tgme_widget_message::attr(data-post)').get()
            url = f"https://t.me/{msg_id}" if msg_id else response.url

            # Date
            date_str = msg.css('time::attr(datetime)').get()
            published_at = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if date_str else datetime.utcnow()

            yield {
                'title': title,
                'content': content,
                'url': url,
                'source': f"Telegram (@{response.meta['channel']})",
                'published_at': published_at,
                'crawled_at': datetime.utcnow().isoformat(),
                'trustability_score': 0.85,
            }
