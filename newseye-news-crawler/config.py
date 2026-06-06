import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME", "newseye_dev")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

    # Use SQLite if DB_TYPE is set to sqlite or as a fallback
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    if DB_TYPE == "sqlite":
        DATABASE_URL = f"sqlite:///./{DB_NAME}.db"
    else:
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    CRAWL_DELAY = int(os.getenv("CRAWL_DELAY", 2))
    CONCURRENT_REQUESTS = int(os.getenv("CONCURRENT_REQUESTS", 8))

    NEWS_SOURCES = {
        'google_news': {'url': 'https://news.google.com/rss/search?q=cybersecurity&hl=ko&gl=KR&ceid=KR:ko', 'source': 'GoogleNews'},
        'the_hacker_news': {'url': 'https://feeds.feedburner.com/TheHackersNews', 'source': 'TheHackerNews'},
        'bleeping_computer': {'url': 'https://www.bleepingcomputer.com/feed/', 'source': 'BleepingComputer'},
        'dark_reading': {'url': 'https://www.darkreading.com/rss.xml', 'source': 'DarkReading'},
    }

    TELEGRAM_CHANNELS = [
        'bad_packets',
        'malwrhunterteam',
        'pwnallthethings',
        'checkpoint_research',
        'darknetstats'
    ]

    CRIME_TYPES = ['phishing', 'ransomware', 'hacking', 'fraud', 'malware', 'stalking', 'crypto_crime']
