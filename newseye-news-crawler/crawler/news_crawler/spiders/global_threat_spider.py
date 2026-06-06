import scrapy
from datetime import datetime
from config import Config

class GlobalThreatSpider(scrapy.Spider):
    """
    Simulates scraping foreign language (e.g., Russian, Chinese) threat forums
    and using an API to translate the content into English before ingestion.
    """
    name = 'global_threat_spider'
    
    # Mock URL
    start_urls = ['https://example.com/mock-ru-forum']

    def parse(self, response):
        self.logger.info("Scanning global threat sources...")
        
        # Mocking scraped foreign content
        mock_foreign_articles = [
            {
                "lang": "ru",
                "original_title": "Новый эксплойт для Windows LPE",
                "original_content": "Обнаружена новая уязвимость повышения привилегий в Windows. Эксплойт уже продается на форумах."
            },
            {
                "lang": "zh",
                "original_title": "针对金融部门的新的勒索软件活动",
                "original_content": "一个新的勒索软件团伙正在积极攻击亚洲的金融机构。他们使用钓鱼邮件进行初步访问。"
            }
        ]
        
        for article in mock_foreign_articles:
            # Simulate Translation API Call (e.g., DeepL or LLM translation)
            translated_title, translated_content = self._mock_translate(
                article["original_title"], 
                article["original_content"], 
                article["lang"]
            )
            
            yield {
                'title': f"[Translated - {article['lang'].upper()}] {translated_title}",
                'content': translated_content,
                'url': f"https://example.com/mock-forum/{article['lang']}/article1",
                'source': f"Global Forum ({article['lang'].upper()})",
                'published_at': datetime.utcnow().isoformat(),
                'crawled_at': datetime.utcnow().isoformat(),
                'trustability_score': 0.7,
                'crime_type': 'hacking', # Classification will happen in pipeline, but we set a default
                'risk_level': 8
            }

    def _mock_translate(self, title: str, content: str, lang: str) -> tuple:
        """
        Mocks a call to a translation API.
        """
        if lang == "ru":
            return ("New exploit for Windows LPE", "A new local privilege escalation vulnerability has been discovered in Windows. The exploit is already being sold on forums.")
        elif lang == "zh":
            return ("New ransomware campaign targeting financial sector", "A new ransomware gang is actively attacking financial institutions in Asia. They use phishing emails for initial access.")
        return (title, content)
