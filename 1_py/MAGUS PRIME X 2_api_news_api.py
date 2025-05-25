"""
News API Integration Module

This module provides functionality for monitoring news sources
and processing news headlines for trading signals.
"""

import asyncio
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import feedparser
from newsapi import NewsApiClient

# Import environment variables if available
try:
    from config import ARABIC_NEWS_RSS_URL, NEWS_API_KEY, NEWS_CHECK_INTERVAL
except ImportError:
    # Fallback to environment variables
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    ARABIC_NEWS_RSS_URL = os.getenv("ARABIC_NEWS_RSS_URL", "")
    NEWS_CHECK_INTERVAL = int(os.getenv("NEWS_CHECK_INTERVAL", 300))


class SentimentAnalyzer:
    """Handles sentiment analysis of news headlines."""

    @staticmethod
    async def analyze_headline(headline: str) -> str:
        """Analyze headline sentiment.

        Args:
            headline: News headline text

        Returns:
            str: 'bullish', 'bearish', or 'neutral'
        """
        # Check each pattern type
        is_bullish = SentimentAnalyzer._matches_bullish_patterns(headline)
        is_bearish = SentimentAnalyzer._matches_bearish_patterns(headline)

        # Check for currency-specific bearish patterns
        currency_bearish_match = SentimentAnalyzer._matches_currency_bearish_patterns(
            headline
        )
        is_bearish = is_bearish or currency_bearish_match

        # Determine sentiment
        if is_bullish and not is_bearish:
            return "bullish"
        elif is_bearish and not is_bullish:
            return "bearish"
        else:
            return "neutral"  # Mixed or no clear signals

    @staticmethod
    def _matches_bullish_patterns(headline: str) -> bool:
        """Check if headline matches bullish patterns."""
        bullish_patterns = [
            r"rise|rally|jump|surge|climb|gain|positive|beat|exceed|recovery|stronger",
            r"economic growth|market optimism|bullish|strong earnings",
        ]

        return any(
            re.search(pattern, headline, re.IGNORECASE) for pattern in bullish_patterns
        )

    @staticmethod
    def _matches_bearish_patterns(headline: str) -> bool:
        """Check if headline matches bearish patterns."""
        bearish_patterns = [
            r"fall|drop|decline|slip|plunge|crash|tumble|weak|miss|recession|fear",
            r"economic slowdown|market pessimism|bearish|weak earnings|weaken",
        ]

        return any(
            re.search(pattern, headline, re.IGNORECASE) for pattern in bearish_patterns
        )

    @staticmethod
    def _matches_currency_bearish_patterns(headline: str) -> bool:
        """Check if headline matches currency-specific bearish patterns."""
        currency_bearish = [
            r"(dollar|euro|pound|yen|franc|currency)\s+(weaken|depreciate|fall|drop)",
            r"weaken(s|ing|ed)?\s+against",
        ]

        return any(
            re.search(pattern, headline, re.IGNORECASE) for pattern in currency_bearish
        )


class AssetDetector:
    """Handles detection of assets mentioned in news headlines."""

    @staticmethod
    async def detect_assets(headline: str) -> List[str]:
        """Detect mentioned assets in a headline.

        Args:
            headline: News headline text

        Returns:
            list: List of detected asset symbols
        """
        asset_patterns = AssetDetector._get_asset_patterns()

        # Extract mentioned assets
        detected_assets = []
        for asset, pattern in asset_patterns.items():
            if re.search(pattern, headline, re.IGNORECASE):
                detected_assets.append(asset)

        return detected_assets

    @staticmethod
    def _get_asset_patterns() -> Dict[str, str]:
        """Get dictionary of asset patterns for detection."""
        return {
            "BTC": r"bitcoin|btc",
            "ETH": r"ethereum|eth",
            "USD": r"dollar|usd",
            "EUR": r"euro|eur",
            "GBP": r"pound|sterling|gbp",
            "JPY": r"yen|jpy",
            "GOLD": r"gold|xau",
            "OIL": r"oil|crude|brent|wti",
        }


class NewsMonitor:
    """Monitor news sources for trading signals."""

    def __init__(
        self, signal_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """Initialize the news monitor.

        Args:
            signal_callback: Optional callback for trading signals
        """
        self.news_api = NewsApiClient(api_key=NEWS_API_KEY) if NEWS_API_KEY else None
        self.signal_callback = signal_callback
        self.headlines_seen = set()  # Track already processed headlines
        self._last_check_time = 0
        self._running = False
        self._initialized = False

        # Validate API key availability
        if not NEWS_API_KEY:
            logging.warning("NEWS_API_KEY not set. English news monitoring disabled.")

        if not ARABIC_NEWS_RSS_URL:
            logging.warning(
                "ARABIC_NEWS_RSS_URL not set. Arabic news monitoring disabled."
            )

    async def start_monitoring(self) -> None:
        """Start the news monitoring loop."""
        if not self.news_api and not ARABIC_NEWS_RSS_URL:
            logging.warning("No news sources configured. Monitoring disabled.")
            return

        self._running = True
        self._initialized = True
        logging.info("Starting news monitoring...")

        while self._running:
            try:
                await self._process_news_cycle()
            except Exception as e:
                logging.error(f"Error in news monitoring: {str(e)}")

            # Sleep between cycles
            await asyncio.sleep(60)  # Check every minute

    async def _process_news_cycle(self) -> None:
        """Process a complete news monitoring cycle."""
        try:
            # Check for news at defined interval
            current_time = time.time()
            if current_time - self._last_check_time >= NEWS_CHECK_INTERVAL:
                self._last_check_time = current_time

                # Check English news sources if available
                if self.news_api:
                    await self.check_english_news()

                # Check Arabic news sources if available
                if ARABIC_NEWS_RSS_URL:
                    await self.check_arabic_news()

        except Exception as e:
            logging.error(f"Error processing news: {str(e)}")

    def stop_monitoring(self) -> None:
        """Stop the news monitoring loop."""
        if not self._running:
            return

        self._running = False
        logging.info("Stopping news monitoring...")

    async def check_arabic_news(self) -> None:
        """Check Arabic news sources for relevant headlines."""
        if not ARABIC_NEWS_RSS_URL:
            return

        try:
            logging.info("Checking Arabic news sources...")
            # Parse the RSS feed
            feed = feedparser.parse(ARABIC_NEWS_RSS_URL)

            # Process recent entries
            cutoff_time = datetime.now() - timedelta(hours=24)  # Last 24 hours

            for entry in feed.entries:
                try:
                    # Check if entry is recent
                    pub_date = datetime(*entry.published_parsed[:6])
                    if pub_date < cutoff_time:
                        continue

                    # Get headline and avoid duplicates
                    title = entry.title
                    if title in self.headlines_seen:
                        continue

                    # Mark as processed
                    self.headlines_seen.add(title)

                    # Process headline for trading signals
                    await self._process_news_headline(title, "ar")
                except Exception as e:
                    logging.error(f"Error processing Arabic news entry: {e}")

        except Exception as e:
            logging.error(f"Error checking Arabic news: {e}")

    async def check_english_news(self) -> None:
        """Check English news sources for trading signals."""
        if not self.news_api:
            return

        try:
            logging.info("Checking English news sources...")
            # Get top business headlines
            headlines = self.news_api.get_top_headlines(
                category="business", language="en", page_size=5
            )

            if headlines.get("articles"):
                for article in headlines["articles"]:
                    title = article.get("title", "")

                    # Skip if we've seen this headline already
                    if title in self.headlines_seen:
                        continue

                    # Mark as processed
                    self.headlines_seen.add(title)

                    # Process headline for trading signals
                    await self._process_news_headline(title, "en")
        except Exception as e:
            logging.error(f"Error checking English news: {e}")

    async def _process_news_headline(self, headline: str, language: str) -> None:
        """Process a news headline for potential trading signals.

        Args:
            headline: News headline text
            language: Language code ('en' for English, 'ar' for Arabic)
        """
        logging.info(f"Processing {language} headline: {headline}")

        # First determine sentiment
        sentiment = await SentimentAnalyzer.analyze_headline(headline)
        if sentiment == "neutral":
            return

        # Then identify mentioned assets
        detected_assets = await AssetDetector.detect_assets(headline)
        if not detected_assets:
            return

        # Create signals for each detected asset
        await self._create_signals_for_assets(detected_assets, sentiment, headline)

    async def _create_signals_for_assets(
        self, assets: List[str], sentiment: str, headline: str
    ) -> None:
        """Create trading signals for detected assets based on sentiment.

        Args:
            assets: List of asset symbols
            sentiment: 'bullish' or 'bearish'
            headline: Original headline for reference
        """
        if not self.signal_callback or not assets:
            return

        for asset in assets:
            signal = await self._create_signal_for_asset(asset, sentiment, headline)
            if signal:
                self.signal_callback(signal)

    async def _create_signal_for_asset(
        self, asset: str, sentiment: str, headline: str
    ) -> Optional[Dict[str, str]]:
        """Create a trading signal for a single asset.

        Args:
            asset: Asset symbol
            sentiment: 'bullish' or 'bearish'
            headline: Original headline

        Returns:
            Signal dictionary or None if sentiment is neutral
        """
        if sentiment == "bullish":
            signal = {"asset": asset, "direction": "BUY", "source": headline}
            logging.info(f"Bullish signal detected for {asset}: {headline}")
            return signal
        elif sentiment == "bearish":
            signal = {"asset": asset, "direction": "SELL", "source": headline}
            logging.info(f"Bearish signal detected for {asset}: {headline}")
            return signal
        return None


def get_market_sentiment_from_news(symbol: str) -> float:
    """Analyze recent news to determine market sentiment for a symbol.

    Args:
        symbol: Market symbol to check sentiment for

    Returns:
        float: Sentiment score between -1 (bearish) and 1 (bullish)
    """
    # This is a placeholder for a more sophisticated sentiment analysis
    # In a real implementation, you would analyze recent news and social media
    try:
        if not NEWS_API_KEY:
            return 0.0

        news_api = NewsApiClient(api_key=NEWS_API_KEY)

        # Extract keywords from symbol
        keywords = symbol.replace("/", " ").replace("-", " ")

        # Get recent news about the symbol
        news = news_api.get_everything(
            q=keywords, language="en", sort_by="relevancy", page_size=10
        )

        if not news.get("articles"):
            return 0.0

        # Simple sentiment scoring based on keywords
        bullish_words = ["rise", "gain", "bullish", "positive", "up", "rally", "growth"]
        bearish_words = [
            "fall",
            "drop",
            "bearish",
            "negative",
            "down",
            "decline",
            "recession",
        ]

        bullish_count = 0
        bearish_count = 0

        for article in news.get("articles", []):
            title = article.get("title", "").lower()
            description = article.get("description", "").lower()
            content = title + " " + description

            for word in bullish_words:
                bullish_count += content.count(word)

            for word in bearish_words:
                bearish_count += content.count(word)

        # Calculate sentiment score between -1 and 1
        total_count = bullish_count + bearish_count
        if total_count == 0:
            return 0.0

        sentiment = (bullish_count - bearish_count) / total_count
        return sentiment

    except Exception as e:
        logging.error(f"Error getting market sentiment for {symbol}: {e}")
        return 0.0
