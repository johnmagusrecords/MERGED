import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
from dotenv import load_dotenv
from newsapi import NewsApiClient
from textblob import TextBlob

# Load environment variables
load_dotenv()


@dataclass
class MarketEvent:
    name: str
    date: datetime
    impact: str  # High, Medium, Low
    actual: Optional[float] = None
    forecast: Optional[float] = None
    previous: Optional[float] = None


class NewsAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("NEWS_API_KEY")
        self.newsapi = NewsApiClient(api_key=self.api_key)
        self.sentiment_cache = {}
        self.event_cache = {}
        self.event_impact_words = {
            "high": ["FOMC", "NFP", "CPI", "GDP", "Rate Decision", "Powell"],
            "medium": ["PMI", "Retail Sales", "Trade Balance", "Employment"],
            "low": ["Building Permits", "Housing Starts", "Inventory"],
        }

    def get_news(self, symbol: str, days: int = 1) -> List[Dict]:
        """Get news articles for a symbol"""
        try:
            # Convert trading symbol to search terms
            search_terms = {
                "BTCUSD": "Bitcoin OR BTC",
                "ETHUSD": "Ethereum OR ETH",
                "US100": "NASDAQ OR US100",
                "EURUSD": "EUR/USD OR Euro Dollar",
                "GBPUSD": "GBP/USD OR British Pound",
                "USDJPY": "USD/JPY OR Dollar Yen",
                "XAUUSD": "Gold OR XAUUSD",
                "US500": "S&P 500 OR SPX",
                "USDCHF": "USD/CHF OR Swiss Franc",
                "AUDUSD": "AUD/USD OR Australian Dollar",
                "NZDUSD": "NZD/USD OR New Zealand Dollar",
                "USDCAD": "USD/CAD OR Canadian Dollar",
                "LTCUSD": "Litecoin OR LTC",
                "XRPUSD": "Ripple OR XRP",
            }

            query = search_terms.get(symbol, symbol)
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            articles = self.newsapi.get_everything(
                q=query, from_param=from_date, language="en", sort_by="relevancy"
            )

            # Process and score articles
            processed_articles = []
            for article in articles["articles"]:
                if article["title"] and article["description"]:
                    sentiment_data = self._analyze_sentiment(
                        article["title"] + " " + article["description"]
                    )
                    processed_articles.append(
                        {
                            "title": article["title"],
                            "description": article["description"],
                            "url": article["url"],
                            "publishedAt": article["publishedAt"],
                            "sentiment": sentiment_data["score"],
                            "confidence": sentiment_data["confidence"],
                            "impact": self._assess_news_impact(
                                article["title"], article["description"]
                            ),
                        }
                    )

            return processed_articles

        except Exception as e:
            self.logger.error(f"Error getting news for {symbol}: {str(e)}")
            return []

    def _analyze_sentiment(self, text: str) -> Dict:
        """Advanced sentiment analysis using TextBlob and custom rules"""
        try:
            # Cache check
            if text in self.sentiment_cache:
                return self.sentiment_cache[text]

            # Use TextBlob for base sentiment
            blob = TextBlob(text)
            base_sentiment = blob.sentiment.polarity

            # Custom word lists
            positive_words = {
                "bullish": 1.5,
                "surge": 1.3,
                "gain": 1.2,
                "rally": 1.4,
                "breakthrough": 1.5,
                "outperform": 1.3,
                "upgrade": 1.2,
                "growth": 1.2,
                "strong": 1.1,
                "beat": 1.2,
                "exceed": 1.3,
            }

            negative_words = {
                "bearish": -1.5,
                "crash": -1.5,
                "plunge": -1.4,
                "downgrade": -1.3,
                "recession": -1.4,
                "crisis": -1.3,
                "default": -1.2,
                "miss": -1.1,
                "warning": -1.1,
                "risk": -1.0,
                "concern": -1.0,
                "weak": -1.1,
            }

            # Intensifiers and their multipliers
            intensifiers = {
                "very": 1.3,
                "highly": 1.3,
                "extremely": 1.5,
                "significantly": 1.4,
                "substantially": 1.4,
                "strongly": 1.3,
                "major": 1.3,
                "sharp": 1.3,
            }

            # Negators
            negators = {"not", "no", "n't", "never", "none", "neither", "nor"}

            # Convert to lowercase and split
            words = text.lower().split()

            # Calculate weighted sentiment
            sentiment = base_sentiment
            confidence = blob.sentiment.subjectivity
            negation = False

            for i, word in enumerate(words):
                if word in negators:
                    negation = True
                    continue

                if word in intensifiers and i + 1 < len(words):
                    next_word = words[i + 1]
                    if next_word in positive_words:
                        sentiment += positive_words[next_word] * intensifiers[word]
                    elif next_word in negative_words:
                        sentiment += negative_words[next_word] * intensifiers[word]

                if word in positive_words:
                    mod = -1 if negation else 1
                    sentiment += positive_words[word] * mod
                elif word in negative_words:
                    mod = -1 if negation else 1
                    sentiment += negative_words[word] * mod

                negation = False

            # Normalize sentiment to [-1, 1] range
            sentiment = np.clip(sentiment / 5, -1, 1)

            # Cache the result
            result = {
                "score": sentiment,
                "confidence": confidence,
                "base_score": base_sentiment,
            }
            self.sentiment_cache[text] = result

            return result

        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {str(e)}")
            return {"score": 0, "confidence": 0, "base_score": 0}

    def _assess_news_impact(self, title: str, description: str) -> str:
        """Assess the potential market impact of news"""
        text = (title + " " + description).lower()

        # Check for high impact events
        for word in self.event_impact_words["high"]:
            if word.lower() in text:
                return "high"

        # Check for medium impact events
        for word in self.event_impact_words["medium"]:
            if word.lower() in text:
                return "medium"

        # Check for low impact events
        for word in self.event_impact_words["low"]:
            if word.lower() in text:
                return "low"

        return "neutral"

    def get_upcoming_events(self, days: int = 7) -> List[MarketEvent]:
        """Get upcoming market events"""
        try:
            today = datetime.now().date()
            events = []

            # Major central bank meetings
            fomc_dates = ["2025-01-29", "2025-03-19", "2025-04-30", "2025-06-11"]
            ecb_dates = ["2025-01-23", "2025-03-06", "2025-04-17", "2025-06-05"]
            boe_dates = ["2025-02-06", "2025-03-20", "2025-05-08", "2025-06-19"]

            for date_str in fomc_dates:
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if 0 <= (event_date - today).days <= days:
                    events.append(
                        MarketEvent(
                            name="FOMC Meeting",
                            date=datetime.combine(event_date, datetime.min.time()),
                            impact="high",
                        )
                    )

            for date_str in ecb_dates:
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if 0 <= (event_date - today).days <= days:
                    events.append(
                        MarketEvent(
                            name="ECB Meeting",
                            date=datetime.combine(event_date, datetime.min.time()),
                            impact="high",
                        )
                    )

            for date_str in boe_dates:
                event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if 0 <= (event_date - today).days <= days:
                    events.append(
                        MarketEvent(
                            name="BOE Meeting",
                            date=datetime.combine(event_date, datetime.min.time()),
                            impact="high",
                        )
                    )

            return sorted(events, key=lambda x: x.date)

        except Exception as e:
            self.logger.error(f"Error getting upcoming events: {str(e)}")
            return []

    def get_latest_news(self) -> List[Dict]:
        """Get latest market-moving news"""
        try:
            # Get news for major markets
            markets = ["EURUSD", "US500", "BTCUSD", "XAUUSD"]
            all_news = []

            for market in markets:
                news = self.get_news(market, days=1)
                all_news.extend(news)

            # Sort by impact and recency
            all_news.sort(
                key=lambda x: (
                    (
                        0
                        if x["impact"] == "high"
                        else (
                            1
                            if x["impact"] == "medium"
                            else 2 if x["impact"] == "low" else 3
                        )
                    ),
                    x["publishedAt"],
                ),
                reverse=True,
            )

            # Return top 5 most impactful news
            return all_news[:5]

        except Exception as e:
            self.logger.error(f"Error getting latest news: {str(e)}")
            return []
