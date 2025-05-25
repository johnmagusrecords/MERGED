import os
import feedparser
import time
from datetime import datetime, timedelta

class Config:
    @staticmethod
    def load():
        # Only validate at runtime
        required = ["NEWS_RSS_URL"]
        missing = [k for k in required if not os.getenv(k)]
        if missing:
            raise RuntimeError(f"Missing config: {missing}")

class NewsFetcher:
    def __init__(self, rss_url):
        self.rss_url = rss_url
        self.seen_guids = set()

    def fetch_rss(self):
        feed = feedparser.parse(self.rss_url)
        new_items = []
        for entry in feed.entries:
            guid = entry.get("id") or entry.get("link")
            if guid and guid not in self.seen_guids:
                self.seen_guids.add(guid)
                new_items.append(entry)
        return new_items

def send_signal(message):
    # Implement or import actual Telegram send logic
    print(f"Sending to Telegram: {message}")

def monitor_news():
    Config.load()
    fetcher = NewsFetcher(os.getenv("NEWS_RSS_URL"))
    while True:
        new_items = fetcher.fetch_rss()
        for item in new_items:
            send_signal(f"News: {item.title}")
        time.sleep(60)

# ...existing code...
