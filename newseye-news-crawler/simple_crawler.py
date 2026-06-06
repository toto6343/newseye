import requests
import feedparser
from datetime import datetime
import os
import sys

# Add directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database import SessionLocal, News
from ml.crime_classifier import CrimeClassifier
from ml.text_analyzer import TextAnalyzer
from config import Config

def run_simple_crawler():
    classifier = CrimeClassifier()
    analyzer = TextAnalyzer()
    db = SessionLocal()
    
    print(f"Starting simple crawler for {len(Config.NEWS_SOURCES)} sources...")
    
    for key, info in Config.NEWS_SOURCES.items():
        url = info['url']
        source_name = info['source']
        print(f"Fetching {url}...")
        
        try:
            r = requests.get(url, timeout=10)
            feed = feedparser.parse(r.text)
            
            items_added = 0
            for entry in feed.entries:
                title = entry.get('title', '')
                url = entry.get('link', '')
                content = entry.get('summary', '') or entry.get('description', '')
                
                # Check for duplicates
                existing = db.query(News).filter(News.url == url).first()
                if existing:
                    continue
                
                # Clean and classify
                clean_title = analyzer.clean_text(title)
                clean_content = analyzer.clean_text(content)
                
                classification = classifier.classify(f"{clean_title} {clean_content}")
                
                news = News(
                    title=clean_title,
                    content=clean_content,
                    source=source_name,
                    url=url,
                    crime_type=classification['crime_type'],
                    keywords=classifier.extract_keywords(f"{clean_title} {clean_content}"),
                    risk_level=int(classification['confidence'] * 10),
                    is_analyzed=True,
                    trustability_score=0.98,
                    crawled_at=datetime.utcnow()
                )
                db.add(news)
                items_added += 1
            
            db.commit()
            print(f"✅ Added {items_added} items from {source_name}")
            
        except Exception as e:
            print(f"❌ Error crawling {source_name}: {e}")
            db.rollback()
            
    db.close()

if __name__ == "__main__":
    run_simple_crawler()
