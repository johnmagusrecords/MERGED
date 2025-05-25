import os
import requests
import logging
from textblob import TextBlob

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news():
    logging.info("Fetching news data...")
    url = f"https://newsapi.org/v2/everything?q=market&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        logging.info("News data fetched successfully.")
        return response.json().get("articles", [])
    else:
        logging.error(f"❌ Failed to fetch news: {response.json()}")
        return []

def analyze_sentiment(article):
    analysis = TextBlob(article["description"])
    return analysis.sentiment.polarity