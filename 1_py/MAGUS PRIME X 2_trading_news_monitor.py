"""
News monitoring module for MAGUS PRIME X trading bot.

This module handles fetching and processing news from various sources
to help identify potential trading opportunities.
"""

import logging
import threading
import time
from typing import Callable, Dict, Optional

from newsapi import NewsApiClient


class NewsMonitor:
    """Monitor news sources for trading signals."""

    def __init__(
        self,
        news_api_key: Optional[str] = None,
        arabic_news_url: Optional[str] = None,
        news_check_interval: int = 300,
        signal_callback: Optional[Callable] = None,
    ):
        """Initialize the news monitor.

        Args:
            news_api_key: API key for NewsAPI (for English headlines)
            arabic_news_url: URL for Arabic news RSS feed
            news_check_interval: Seconds between news checks
            signal_callback: Function to call when a trading signal is detected
        """
        self.news_api_key = news_api_key
        self.arabic_news_url = arabic_news_url
        self.news_check_interval = news_check_interval
        self.signal_callback = signal_callback

        # State tracking
        self.last_english_headline = ""
        self.last_arabic_headline = ""
        self.news_api = None
        self.monitoring_thread = None
        self.is_running = False

        # Initialize NewsAPI if key provided
        if self.news_api_key:
            try:
                self.news_api = NewsApiClient(api_key=self.news_api_key)
                logging.info("NewsAPI client initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize NewsAPI client: {e}")
                self.news_api = None

    def start_monitoring(self):
        """Start the news monitoring thread."""
        if self.is_running:
            logging.warning("News monitoring already running")
            return

        if not self.news_api_key and not self.arabic_news_url:
            logging.warning("No news sources configured, monitoring not started")
            return

        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._news_loop, daemon=True)
        self.monitoring_thread.start()
        logging.info("News monitoring thread started")

    def stop_monitoring(self):
        """Stop the news monitoring thread."""
        self.is_running = False
        logging.info("News monitoring thread signaled to stop")

    def _news_loop(self):
        """Background thread that continuously monitors for news events."""
        logging.info("Starting news monitoring loop...")

        while self.is_running:
            try:
                if self.arabic_news_url:
                    self._check_arabic_news()

                if self.news_api:
                    self._check_english_news()

                # Sleep between news checks
                time.sleep(self.news_check_interval)
            except Exception as e:
                logging.error(f"Error in news monitoring: {e}")
                time.sleep(60)  # Sleep after error

    def _check_arabic_news(self):
        """Check Arabic news source for trading-relevant headlines."""
        try:
            # Placeholder for Arabic news checking logic
            # This would typically involve fetching an RSS feed or similar
            # and extracting headlines for processing

            # Example placeholder:
            # response = requests.get(self.arabic_news_url)
            # feed = feedparser.parse(response.content)
            # if feed.entries:
            #     latest_headline = feed.entries[0].title
            #     if latest_headline != self.last_arabic_headline:
            #         self.last_arabic_headline = latest_headline
            #         self._process_news_headline(latest_headline, 'ar')

            pass  # Placeholder until implementation
        except Exception as e:
            logging.error(f"Error checking Arabic news: {e}")

    def _check_english_news(self):
        """Check English news via NewsAPI for trading-relevant headlines."""
        try:
            if not self.news_api:
                logging.warning("NewsAPI client not initialized")
                return

            # Get top business headlines
            headlines = self.news_api.get_top_headlines(
                category="business", language="en", page_size=5
            )

            if headlines.get("articles"):
                for article in headlines["articles"]:
                    title = article.get("title", "")

                    # Skip if we've seen this headline already
                    if title == self.last_english_headline:
                        continue

                    # Update last seen headline
                    self.last_english_headline = title

                    # Process headline for trading signals
                    self._process_news_headline(title, "en")
        except Exception as e:
            logging.error(f"Error checking English news: {e}")

    def _process_news_headline(self, headline: str, language: str):
        """Process a news headline for potential trading signals.

        Args:
            headline: The news headline text
            language: Language code of the headline (e.g., 'en', 'ar')
        """
        logging.info(f"Processing {language} headline: {headline}")

        # Analyze headline sentiment
        sentiment = self._analyze_headline_sentiment(headline)

        # Extract mentioned assets
        assets = self._extract_mentioned_assets(headline.lower())

        # Generate trading signals if conditions are met
        self._generate_signals_from_headline(headline, sentiment, assets)

    def _analyze_headline_sentiment(self, headline: str) -> str:
        """Analyze the sentiment of a headline.

        Args:
            headline: The news headline text

        Returns:
            str: 'bullish', 'bearish', or 'neutral'
        """
        # Perform sentiment analysis or keyword matching
        # This is a simplistic example - production systems would use NLP
        bullish_keywords = ["surge", "rally", "jump", "gain", "positive", "up"]
        bearish_keywords = ["plunge", "drop", "fall", "down", "negative", "crisis"]

        headline_lower = headline.lower()

        # Determine sentiment
        if any(keyword in headline_lower for keyword in bullish_keywords):
            return "bullish"
        elif any(keyword in headline_lower for keyword in bearish_keywords):
            return "bearish"

        return "neutral"

    def _generate_signals_from_headline(
        self, headline: str, sentiment: str, assets: list
    ):
        """Generate trading signals from a processed headline.

        Args:
            headline: The original headline text
            sentiment: Analyzed sentiment ('bullish', 'bearish', 'neutral')
            assets: List of detected asset symbols
        """
        # Skip if neutral sentiment or no assets detected
        if sentiment == "neutral" or not assets:
            return

        # Skip if no callback function is registered
        if not self.signal_callback:
            return

        # Generate signal for each detected asset
        for symbol in assets:
            signal = {
                "symbol": symbol,
                "action": "BUY" if sentiment == "bullish" else "SELL",
                "confidence": 0.6,  # Moderate confidence for news-based signals
                "source": "news",
                "headline": headline,
            }

            # Call the callback function with the signal
            self.signal_callback(signal)
            logging.info(f"Generated news-based signal: {signal}")

    def _extract_mentioned_assets(self, text: str) -> list:
        """Extract mentioned assets/symbols from text.

        Args:
            text: Text to analyze for asset mentions

        Returns:
            list: Asset symbols mentioned in the text
        """
        # This is a simplistic implementation
        # Real systems would use NLP entity recognition
        common_assets = self._get_common_asset_mapping()

        mentioned_assets = []
        for keyword, symbol in common_assets.items():
            if keyword in text:
                mentioned_assets.append(symbol)

        return mentioned_assets

    def _get_common_asset_mapping(self) -> Dict[str, str]:
        """Get mapping of common asset names to trading symbols.

        Returns:
            dict: Mapping of common asset names to trading symbols
        """
        return {
            "bitcoin": "BTCUSD",
            "ethereum": "ETHUSD",
            "gold": "XAUUSD",
            "oil": "USOIL",
            "sp500": "US500",
            "dow": "US30",
            "nasdaq": "USTEC",
        }
