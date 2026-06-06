import sqlite3
import requests
import json
import time

CRAWLER_DB = 'newseye-news-crawler/newseye_dev.db'
BACKEND_API = 'http://127.0.0.1:8000/api/v1/news/ingest'

def sync_data():
    conn = sqlite3.connect(CRAWLER_DB)
    cursor = conn.cursor()
    
    # Fetch news that might be relevant
    cursor.execute('SELECT title, content, source, url, crime_type, risk_level FROM news ORDER BY id DESC LIMIT 20')
    rows = cursor.fetchall()
    
    print(f"Found {len(rows)} items in crawler DB. Starting sync to backend...")
    
    success_count = 0
    for row in rows:
        payload = {
            "title": row[0],
            "content": row[1],
            "source": row[2],
            "url": row[3],
            "crime_type": row[4],
            "risk_level": row[5] or 5, # Default to 5 if 0 or None
            "trustability_score": 0.9,
            "keywords": []
        }
        
        try:
            response = requests.post(BACKEND_API, json=payload, timeout=5)
            if response.status_code in [200, 201, 202]:
                print(f"✅ Synced: {row[0][:30]}...")
                success_count += 1
            else:
                print(f"❌ Failed ({response.status_code}): {row[0][:30]}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        time.sleep(0.5) # Avoid overwhelming the backend
    
    print(f"\nSync complete. {success_count} items successfully sent to backend.")
    conn.close()

if __name__ == "__main__":
    sync_data()
