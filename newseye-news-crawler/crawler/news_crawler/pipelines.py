import scrapy
from scrapy.exceptions import DropItem
from datetime import datetime
import os
import sys

# Add parent directory to sys.path to import local modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from database import SessionLocal, News
from ml.crime_classifier import CrimeClassifier
from ml.text_analyzer import TextAnalyzer
from ml.ner_extractor import NERExtractor

class NewsCleaningPipeline:
    def __init__(self):
        self.text_analyzer = TextAnalyzer()

    def process_item(self, item, spider):
        if not item.get('title') or not item.get('url'):
            raise DropItem("Missing required fields")

        item['title'] = self.text_analyzer.clean_text(item['title'])
        item['content'] = self.text_analyzer.clean_text(item.get('content', ''))

        if len(item['title']) < 5:
            raise DropItem("Title too short")

        return item

import requests

class NewsValidationPipeline:
    def __init__(self):
        self.classifier = CrimeClassifier()
        self.ner_extractor = NERExtractor()

    def process_item(self, item, spider):
        full_text = f"{item['title']} {item.get('content', '')}"
        classification = self.classifier.classify(full_text)

        item['crime_type'] = classification['crime_type']
        item['is_analyzed'] = True
        item['keywords'] = self.classifier.extract_keywords(full_text)
        item['entities'] = self.ner_extractor.extract_entities(full_text)
        item['risk_level'] = int(classification['confidence'] * 10)

        return item

class PostgresStorePipeline:
    def __init__(self):
        self.api_url = os.getenv("BACKEND_API_URL", "http://localhost:8000/api/v1/news/ingest")

    def process_item(self, item, spider):
        try:
            # Parse crawled_at
            crawled_at = item.get('crawled_at')
            if isinstance(crawled_at, str):
                crawled_at = datetime.fromisoformat(crawled_at)
            else:
                crawled_at = datetime.utcnow()

            # Parse published_at
            published_at = item.get('published_at')
            if published_at and not isinstance(published_at, str):
                published_at = published_at.isoformat()

            payload = {
                "title": item['title'],
                "content": item.get('content', ''),
                "source": item['source'],
                "url": item['url'],
                "published_at": published_at,
                "crime_type": item.get('crime_type'),
                "keywords": item.get('keywords', []),
                "trustability_score": item.get('trustability_score', 0.7),
                "risk_level": item.get('risk_level')
            }
            
            response = requests.post(self.api_url, json=payload)
            if response.status_code not in [200, 201, 202]:
                raise DropItem(f"API rejected item: {response.status_code} - {response.text}")
                
            return item
        except Exception as e:
            raise DropItem(f"API request error: {e}")
