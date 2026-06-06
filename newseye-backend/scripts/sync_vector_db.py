import asyncio
import sys
import os

# Add parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.news import News
from app.services.rag_service import rag_service

async def sync_news_to_vector_db():
    print("🚀 Starting sync: SQL Database -> ChromaDB Vector Store")
    db = SessionLocal()
    try:
        # Get all analyzed news
        news_list = db.query(News).filter(News.is_analyzed == True).all()
        print(f"📊 Found {len(news_list)} analyzed news articles.")
        
        count = 0
        for news in news_list:
            await rag_service.add_news(
                news_id=news.id,
                title=news.title,
                content=news.content,
                metadata={
                    "source": news.source,
                    "url": news.url,
                    "published_at": str(news.published_at) if news.published_at else "",
                    "crime_type": news.crime_type or "unknown"
                }
            )
            count += 1
            if count % 10 == 0:
                print(f"✅ Processed {count}/{len(news_list)} articles...")
        
        print(f"🎉 Sync complete! Total {count} articles indexed in Vector DB.")
    except Exception as e:
        print(f"❌ Error during sync: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(sync_news_to_vector_db())
