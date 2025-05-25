import os
import logging
import asyncio
from dataclasses import dataclass
from typing import List, Optional, Set, Any
from datetime import datetime
import aiohttp

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None
import re

from telegram_utils import send_telegram_message  # Assumed to be async


class ConfigurationError(Exception):
    """Raised when required configuration is missing."""
    pass


@dataclass(frozen=True)
class Config:
    """Configuration loaded from environment variables."""
    TELEGRAM_TOKEN: str
    TELEGRAM_CHAT_ID: str
    NEWSAPI_KEY: str
    RSS_FEEDS: str  # Comma-separated URLs

    @staticmethod
    def load() -> "Config":
        missing = []
        env = os.environ
        keys = ["TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID",
                "NEWSAPI_KEY", "RSS_FEEDS"]
        values = {}
        for k in keys:
            v = env.get(k)
            if not v:
                missing.append(k)
            else:
                values[k] = v
        if missing:
            raise ConfigurationError(
                f"Missing environment variables: {', '.join(missing)}")
        return Config(**values)


CONFIG = Config.load()


@dataclass
class NewsArticle:
    """Represents a news article."""
    title: str
    summary: str
    link: str
    published: datetime
    sentiment: Optional[str] = None


class SentimentAnalyzer:
    """Interface for sentiment analysis."""

    def analyze(self, text: str) -> str:
        """Return sentiment label for the given text."""
        raise NotImplementedError


class SimpleSentimentAnalyzer(SentimentAnalyzer):
    """A trivial sentiment analyzer for demonstration."""

    def analyze(self, text: str) -> str:
        return "neutral"


def clean_html_summary(html: str) -> str:
    """Remove HTML tags from summary using BeautifulSoup if available, else regex."""
    if BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()
    return re.sub(r"<[^>]+>", "", html)


class NewsFetcher:
    """Fetches news from RSS feeds and NewsAPI."""

    def __init__(self, config: Config, sentiment_analyzer: SentimentAnalyzer):
        self.config = config
        self.sentiment_analyzer = sentiment_analyzer
        self.logger = logging.getLogger("NewsFetcher")

    async def fetch_rss(self) -> List[NewsArticle]:
        """Fetch articles from configured RSS feeds."""
        articles: List[NewsArticle] = []
        feeds = [url.strip()
                 for url in self.config.RSS_FEEDS.split(",") if url.strip()]
        async with aiohttp.ClientSession() as session:
            for url in feeds:
                try:
                    async with session.get(url, timeout=10) as resp:
                        text = await resp.text()
                        # ...parse RSS XML, extract items...
                        # For brevity, parsing is omitted; replace with actual parsing logic.
                        # Example:
                        # for item in parsed_items:
                        #     articles.append(NewsArticle(...))
                except Exception as e:
                    self.logger.error(f"Failed to fetch RSS feed {url}: {e}")
        return articles

    async def fetch_newsapi(self) -> List[NewsArticle]:
        """Fetch articles from NewsAPI."""
        url = f"https://newsapi.org/v2/top-headlines?apiKey={self.config.NEWSAPI_KEY}&language=en"
        articles: List[NewsArticle] = []
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    data = await resp.json()
                    for item in data.get("articles", []):
                        published = item.get("publishedAt")
                        dt = datetime.fromisoformat(published.replace(
                            "Z", "+00:00")) if published else datetime.utcnow()
                        summary = clean_html_summary(
                            item.get("description") or "")
                        sentiment = self.sentiment_analyzer.analyze(summary)
                        articles.append(NewsArticle(
                            title=item.get("title", ""),
                            summary=summary,
                            link=item.get("url", ""),
                            published=dt,
                            sentiment=sentiment
                        ))
        except Exception as e:
            self.logger.error(f"Failed to fetch NewsAPI: {e}")
        return articles

    async def fetch_all(self) -> List[NewsArticle]:
        """Fetch and merge articles from all sources, de-duplicated by link."""
        rss, newsapi = await asyncio.gather(self.fetch_rss(), self.fetch_newsapi())
        seen: Set[str] = set()
        merged: List[NewsArticle] = []
        for article in rss + newsapi:
            if article.link not in seen:
                seen.add(article.link)
                merged.append(article)
        return merged


async def notify_status(message: str) -> None:
    """Send a status message via Telegram."""
    try:
        await send_telegram_message(CONFIG.TELEGRAM_TOKEN, CONFIG.TELEGRAM_CHAT_ID, message)
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")


def notify_status_sync(message: str) -> None:
    """Synchronous wrapper for notify_status."""
    asyncio.run(notify_status(message))


async def main_loop(poll_interval: int = 300) -> None:
    """Main async loop for periodic news fetching and notification."""
    logging.basicConfig(level=logging.INFO)
    sentiment = SimpleSentimentAnalyzer()
    fetcher = NewsFetcher(CONFIG, sentiment)
    while True:
        try:
            articles = await fetcher.fetch_all()
            # ...process/filter articles as needed...
            # ...send notifications if new articles...
            logging.info(f"Fetched {len(articles)} articles.")
        except Exception as e:
            logging.exception(f"Error in main loop: {e}")
        await asyncio.sleep(poll_interval)


def run() -> None:
    """Entrypoint to run the news monitor."""
    asyncio.run(main_loop())


if __name__ == "__main__":
    run()
