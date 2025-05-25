import re
from typing import List, Callable


class NewsMonitor:
    def __init__(self, callback: Callable[[str, str, str], None], assets: List[str]):
        self.callback = callback
        self.assets = assets
        # Expanded asset keyword mapping
        self.asset_keywords = {
            "BTC": ["bitcoin", "btc"],
            "ETH": ["ethereum", "eth"],
            "OIL": ["oil", "crude"],
            "USD": ["usd", "dollar", "us dollar"],
            "EUR": ["eur", "euro"],
            "GOLD": ["gold"],
            "JPY": ["jpy", "yen", "japanese yen"],
        }

    def fetch_headlines(self):
        # stub returning empty list
        return []

    def _detect_assets_in_headline(self, headline: str) -> List[str]:
        detected_assets = set()
        headline_lower = headline.lower()
        for asset, keywords in self.asset_keywords.items():
            for kw in keywords:
                # Use regex to match whole words only
                if re.search(rf'\b{re.escape(kw)}\b', headline_lower):
                    detected_assets.add(asset)
        return list(detected_assets)

    def _detect_headline_sentiment(self, headline: str) -> str:
        headline_lower = headline.lower()
        # Expanded bullish and bearish keywords
        bullish_keywords = [
            "surge", "surges", "rally", "rallies", "gain", "gains", "climb", "climbs", "jump", "jumps", "soar", "soars",
            "rise", "rises", "advance", "advances", "recovery", "optimism", "grow", "grows", "growth", "bullish", "high", "record high", "all-time high", "increase", "increases"
        ]
        bearish_keywords = [
            "plunge", "plunges", "tumble", "tumbles", "fall", "falls", "drop", "drops", "decline", "declines", "selloff", "sell-off",
            "weak", "weakens", "bearish", "low", "record low", "decrease", "decreases", "slowdown", "pessimism", "loss", "losses"
        ]

        bullish_count = 0
        bearish_count = 0

        for word in bearish_keywords:
            if re.search(rf'\b{re.escape(word)}\b', headline_lower):
                bearish_count += 1

        for word in bullish_keywords:
            if re.search(rf'\b{re.escape(word)}\b', headline_lower):
                bullish_count += 1

        print(f"DEBUG: Headline: {headline}")
        print(f"DEBUG: Bearish count: {bearish_count}, Bullish count: {bullish_count}")

        if bearish_count > bullish_count:
            return "bearish"
        elif bullish_count > bearish_count:
            return "bullish"
        elif bearish_count == bullish_count and bearish_count > 0:
            # If equal counts but non-zero, prioritize bearish
            return "bearish"
        else:
            return "neutral"

    def _create_signals_for_assets(self, assets: List[str], sentiment: str, headline: str):
        if sentiment == "neutral":
            return
        direction = "BUY" if sentiment == "bullish" else "SELL"
        for asset in assets:
            self.callback(asset, direction, headline)

    def _process_news_headline(self, headline: str, lang: str = "en"):
        sentiment = self._detect_headline_sentiment(headline)
        assets = self._detect_assets_in_headline(headline)
        self._create_signals_for_assets(assets, sentiment, headline)
