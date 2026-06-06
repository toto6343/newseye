import os
import requests
import time
from dotenv import load_dotenv

# Note: In a real scenario, you would use python-telegram-bot
# Here we mock the behavior of a bot interacting with our API

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "mock_token")
API_BASE_URL = "http://localhost:8000/api/v1"

def simulate_bot():
    print(f"🤖 Starting NewsEye Security Bot (Mock Mode)")
    
    # 1. User asks for the latest high-risk news
    print("\n[User]: /latest")
    time.sleep(1)
    
    try:
        response = requests.get(f"{API_BASE_URL}/news/latest?count=3")
        if response.status_code == 200:
            news_items = response.json().get("data", [])
            print("[Bot]: Here are the top 3 latest security threats:")
            for item in news_items:
                print(f"- 🔴 Risk {item.get('risk_level', 'N/A')}/10: {item['title']}")
        else:
            print("[Bot]: Failed to fetch news.")
    except Exception as e:
        print(f"[Bot]: API connection error: {e}")

    # 2. User asks a specific question (using RAG)
    query = "What are the latest ransomware tactics?"
    print(f"\n[User]: /ask {query}")
    time.sleep(1)
    
    try:
        response = requests.post(f"{API_BASE_URL}/analytics/chat", json={"query": query})
        if response.status_code == 200:
            data = response.json()
            print(f"[Bot]: {data['answer']}")
            if data.get('sources'):
                print("Sources:")
                for src in data['sources']:
                    print(f"- {src['url']}")
        else:
            print("[Bot]: I couldn't process your question at the moment.")
    except Exception as e:
         print(f"[Bot]: API connection error: {e}")

if __name__ == "__main__":
    simulate_bot()
