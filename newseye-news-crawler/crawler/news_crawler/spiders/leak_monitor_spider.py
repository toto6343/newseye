import scrapy
from datetime import datetime
from config import Config

class LeakMonitorSpider(scrapy.Spider):
    """
    Monitors public paste sites or developer feeds (e.g., GitHub public gists, Pastebin) 
    for leaked API keys, credentials, or mentions of targeted assets.
    """
    name = 'leak_monitor'
    
    # Mocking a public feed URL
    start_urls = ['https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-100.txt']

    def parse(self, response):
        self.logger.info("Scanning potential leak source...")
        content = response.text
        
        # Mock detection logic
        keywords_to_monitor = ["password", "admin", "secret", "api_key", "token"]
        
        leaked_items_found = False
        for kw in keywords_to_monitor:
            if kw in content.lower():
                leaked_items_found = True
                break
                
        if leaked_items_found:
            yield {
                'title': f"Potential Credential Leak Detected from Public Source",
                'content': "Automated monitor detected potential credential exposure or sensitive keywords in a public code repository or paste site. Immediate review is recommended.",
                'url': response.url,
                'source': 'Leak Monitor',
                'published_at': datetime.utcnow().isoformat(),
                'crawled_at': datetime.utcnow().isoformat(),
                'trustability_score': 0.6,
                'crime_type': 'hacking',
                'risk_level': 9
            }
