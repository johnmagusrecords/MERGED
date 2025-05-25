# config.py
from typing import Any, Dict, List, Optional
from newsapi import NewsApiClient
import requests
from requests.adapters import HTTPAdapter, Retry
from telegram import Bot
import telegram
import logging
import os
from capital_com_trader import CapitalComTrader
from dotenv import load_dotenv
load_dotenv()  # <-- Move this to the top, before any os.getenv calls


# Try importing constants from existing config, else use defaults
try:
    from config import CONFIG, TELEGRAM_BOT_TOKEN, LOG_LEVEL
except ImportError:
    CONFIG = {}
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    LOG_LEVEL = logging.INFO

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL if isinstance(LOG_LEVEL, int) else logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Credentials and API keys (from environment or defaults)
CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY", "")
CAPITAL_API_PASSWORD = os.getenv("CAPITAL_API_PASSWORD", "")
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_IDENTIFIER", "")
CAPITAL_API_URL = os.getenv(
    "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
STATUS_CHAT_ID = os.getenv("STATUS_CHAT_ID", TELEGRAM_CHAT_ID)
NEWS_CHAT_ID = os.getenv("TELEGRAM_NEWS_CHAT_ID", TELEGRAM_CHAT_ID)

# Trading configuration
TRADE_LOG: List[Dict[str, Any]] = []
TRADE_HISTORY_FILE = "trade_history.csv"
STRATEGY_MODE = os.getenv("STRATEGY_MODE", "Balanced")
DAILY_LOSS_LIMIT = float(os.getenv("DAILY_LOSS_LIMIT", "-500"))
DAILY_PROFIT_LIMIT = float(os.getenv("DAILY_PROFIT_LIMIT", "1000"))

if STRATEGY_MODE == "Safe":
    TRADE_INTERVAL = 600
    TP_MOVE_PERCENT = 0.003  # 0.3%
    BREAKEVEN_TRIGGER = 0.005  # 0.5%
    RISK_PERCENT = 1
elif STRATEGY_MODE == "Aggressive":
    TRADE_INTERVAL = 120
    TP_MOVE_PERCENT = 0.01  # 1%
    BREAKEVEN_TRIGGER = 0.015  # 1.5%
    RISK_PERCENT = 3
else:  # Balanced
    TRADE_INTERVAL = 300
    TP_MOVE_PERCENT = 0.005  # 0.5%
    BREAKEVEN_TRIGGER = 0.01  # 1%
    RISK_PERCENT = 2

USE_ALL_MARKETS = True
MARKET_CACHE: Dict[str, Any] = {}
MARKET_CACHE_TTL = 3600

# Initialize HTTP session with retries
session = requests.Session()
retry_strategy = Retry(total=5, backoff_factor=0.2)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Initialize external clients
if TELEGRAM_BOT_TOKEN:
    telegram_bot: Optional[telegram.Bot] = Bot(token=str(TELEGRAM_BOT_TOKEN))
else:
    telegram_bot: Optional[telegram.Bot] = None

newsapi = NewsApiClient(api_key=NEWS_API_KEY or "demo_key")

# Initialize trading API (Capital.com)
capital_trader = CapitalComTrader()
capital_trader.initialize()


def fetch_latest_news() -> list[str]:
    """Fetch latest news headlines using NewsAPI (fallback example)."""
    try:
        top_headlines = newsapi.get_top_headlines(language='en', page_size=5)
        articles = top_headlines.get('articles', [])
        return [article['title'] for article in articles if 'title' in article]
    except Exception as e:
        logger.error(f"Error fetching latest news: {e}")
        return []


class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    MIN_TRADE_INTERVAL = 60
    MAX_TRADE_INTERVAL = 300
    TRADE_INTERVAL: int = 300  # Allow reassignment to any int
    STRATEGY_MODE: str = os.getenv("STRATEGY_MODE", "Balanced")
    RISK_PERCENT: int = 2
    TRADE_HISTORY_FILE: str = "trade_history.csv"
    # ...add other config variables as needed...


CONFIG = Config()
# Make it available for direct import
TELEGRAM_BOT_TOKEN = CONFIG.TELEGRAM_BOT_TOKEN
