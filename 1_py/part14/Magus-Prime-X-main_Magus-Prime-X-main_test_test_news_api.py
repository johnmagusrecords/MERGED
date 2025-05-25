"""
Unit tests for the news API integration and headline analysis.
"""

import os
import sys
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apy.news_api import NewsMonitor


class TestNewsMonitor(unittest.TestCase):
    """Test cases for the NewsMonitor class."""

    def setUp(self):
        """Set up test environment."""
        self.callback_results = []

        def mock_callback(asset, direction, headline):
            self.callback_results.append({"asset": asset, "direction": direction, "headline": headline})

        self.monitor = NewsMonitor(mock_callback, assets=["BTC", "ETH", "OIL", "USD", "EUR"])

    def test_detect_headline_sentiment(self):
        """Test sentiment detection in headlines."""
        # Test bullish headlines
        bullish_headlines = [
            "Bitcoin surges past $50,000 as institutional investors jump in",
            "Oil prices rally on strong economic growth forecast",
            "Dollar gains against euro as US economy shows recovery",
            "Gold climbs on inflation concerns and market optimism",
        ]

        for headline in bullish_headlines:
            sentiment = self.monitor._detect_headline_sentiment(headline)
            self.assertEqual(sentiment, "bullish", f"Failed on '{headline}'")

        # Test bearish headlines
        bearish_headlines = [
            "Bitcoin plunges below $40,000 amid market selloff",
            "Oil prices tumble on economic slowdown fears",
            "Dollar weakens against major currencies as market pessimism grows",
            "Gold falls after poor earnings reports from mining sector",
        ]

        for headline in bearish_headlines:
            sentiment = self.monitor._detect_headline_sentiment(headline)
            self.assertEqual(sentiment, "bearish", f"Failed on '{headline}'")

        # Test neutral headlines
        neutral_headlines = [
            "Central bank maintains current policy",
            "Markets closed for holiday",
            "Investors await economic data release",
            "Company announces new product launch",
        ]

        for headline in neutral_headlines:
            sentiment = self.monitor._detect_headline_sentiment(headline)
            self.assertEqual(sentiment, "neutral", f"Failed on '{headline}'")

    def test_detect_assets_in_headline(self):
        """Test asset detection in headlines."""
        # Test asset detection
        test_cases = [
            {
                "headline": "Bitcoin reaches new all-time high as institutional adoption grows",
                "expected": ["BTC"],
            },
            {
                "headline": "Dollar and Euro exchange rates remain stable after Fed announcement",
                "expected": ["USD", "EUR"],
            },
            {
                "headline": "Gold and oil prices fluctuate amid geopolitical tensions",
                "expected": ["GOLD", "OIL"],
            },
            {
                "headline": "Ethereum follows Bitcoin higher in crypto rally",
                "expected": ["ETH", "BTC"],
            },
            {
                "headline": "Japanese Yen weakens against US Dollar after policy announcement",
                "expected": ["JPY", "USD"],
            },
            {
                "headline": "Company launches new smartphone with innovative features",
                "expected": [],  # No relevant assets
            },
        ]

        for case in test_cases:
            assets = self.monitor._detect_assets_in_headline(case["headline"])
            self.assertEqual(
                sorted(assets),
                sorted(case["expected"]),
                f"Failed on '{case['headline']}'",
            )

    def test_create_signals_for_assets(self):
        """Test signal creation for detected assets."""
        # Reset callback results
        self.callback_results = []

        # Create signals for bullish sentiment
        self.monitor._create_signals_for_assets(
            assets=["BTC", "ETH"],
            sentiment="bullish",
            headline="Crypto markets rally as institutional interest grows",
        )

        # Check results
        self.assertEqual(len(self.callback_results), 2)
        self.assertEqual(self.callback_results[0]["asset"], "BTC")
        self.assertEqual(self.callback_results[0]["direction"], "BUY")
        self.assertEqual(self.callback_results[1]["asset"], "ETH")
        self.assertEqual(self.callback_results[1]["direction"], "BUY")

        # Reset and test bearish sentiment
        self.callback_results = []
        self.monitor._create_signals_for_assets(
            assets=["OIL"],
            sentiment="bearish",
            headline="Oil prices drop on oversupply concerns",
        )

        # Check results
        self.assertEqual(len(self.callback_results), 1)
        self.assertEqual(self.callback_results[0]["asset"], "OIL")
        self.assertEqual(self.callback_results[0]["direction"], "SELL")

        # Test neutral sentiment (should not generate signals)
        self.callback_results = []
        self.monitor._create_signals_for_assets(
            assets=["USD"], sentiment="neutral", headline="Dollar holds steady"
        )

        # Check that no signals were generated
        self.assertEqual(len(self.callback_results), 0)

    def test_process_news_headline(self):
        """Test the full headline processing pipeline."""
        # Reset callback results
        self.callback_results = []

        # Process a headline with clear sentiment and asset
        self.monitor._process_news_headline(
            "Bitcoin surges 10% as institutional adoption accelerates", "en"
        )

        # Check results
        self.assertEqual(len(self.callback_results), 1)
        self.assertEqual(self.callback_results[0]["asset"], "BTC")
        self.assertEqual(self.callback_results[0]["direction"], "BUY")

        # Process a headline with no clear sentiment
        self.callback_results = []
        self.monitor._process_news_headline(
            "Bitcoin trading volume remains steady", "en"
        )

        # Check that no signals were generated
        self.assertEqual(len(self.callback_results), 0)

        # Process a headline with sentiment but no relevant assets
        self.callback_results = []
        self.monitor._process_news_headline("Markets rally on economic optimism", "en")

        # Check that no signals were generated
        self.assertEqual(len(self.callback_results), 0)


if __name__ == "__main__":
    unittest.main()
