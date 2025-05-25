import json
import logging
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("magus_prime.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# API Configuration
CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY", "").strip()
CAPITAL_API_PASSWORD = os.getenv("CAPITAL_API_PASSWORD", "").strip()
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_API_IDENTIFIER", "").strip()
CAPITAL_API_URL = os.getenv(
    "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
).strip()

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
TELEGRAM_SIGNAL_CHAT_ID = os.getenv("TELEGRAM_SIGNAL_CHAT_ID", TELEGRAM_CHAT_ID).strip()
TELEGRAM_GROUP_CHAT_ID = os.getenv(
    "TELEGRAM_GROUP_CHAT_ID", ""
).strip()  # Added group chat ID
TELEGRAM_PRIVATE_GROUP = os.getenv(
    "TELEGRAM_PRIVATE_GROUP", "https://t.me/+5WUzX7eNzDRkZjBk"
).strip()

# News API Configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "ea16bacd51c7462abcde520271143bf8").strip()
ALPHAVANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "34BQ9ZZ40GRAHF21").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# Signal Dispatcher Configuration
SIGNAL_DISPATCHER_URL = os.getenv(
    "SIGNAL_DISPATCHER_URL", "https://magus-prime-x.onrender.com"
).strip()
SIGNAL_API_KEY = os.getenv("SIGNAL_API_KEY", "magus_prime_secret_key").strip()

# Trading Configuration
STRATEGY_MODE = os.getenv(
    "STRATEGY_MODE", "Balanced"
)  # Options: Safe, Balanced, Aggressive
RISK_PERCENT = float(os.getenv("RISK_PERCENT", "2"))
RECOVERY_ENABLED = os.getenv("RECOVERY_ENABLED", "True").lower() == "true"
WEEKEND_CRYPTO_ONLY = os.getenv("WEEKEND_CRYPTO_ONLY", "True").lower() == "true"
PRE_SIGNAL_ALERTS = os.getenv("PRE_SIGNAL_ALERTS", "True").lower() == "true"

# Languages & Localization
ENABLE_ARABIC = os.getenv("ENABLE_ARABIC", "False").lower() == "true"

# Feature toggles
PRE_SIGNALS_ENABLED = os.getenv("ENABLE_PRE_SIGNALS", "True").lower() == "true"
RECOVERY_MODE_ENABLED = os.getenv("ENABLE_RECOVERY_MODE", "True").lower() == "true"
NEWS_MONITORING_ENABLED = os.getenv("ENABLE_NEWS_MONITORING", "True").lower() == "true"
MARKET_AWARENESS_ENABLED = (
    os.getenv("ENABLE_MARKET_AWARENESS", "True").lower() == "true"
)
COMMENTARY_ENABLED = os.getenv("ENABLE_COMMENTARY", "True").lower() == "true"


# Assets Configuration
def load_asset_config():
    try:
        with open("assets_config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading assets_config.json: {e}")
        return {}


ASSET_CONFIG = load_asset_config()

# Strategy Descriptions
STRATEGY_DESCRIPTIONS = {
    "Breakout": "A breakout occurs when price moves beyond a defined support or resistance level with increased volume.",
    "Trend Following": "Following the established market direction, entering after a pullback or consolidation.",
    "Mean Reversion": "Trading the return to average price after extreme moves away from the trend.",
    "Support/Resistance": "Trading bounces off key structural levels where price has historically reversed.",
    "Gap Trading": "Trading the spaces or 'gaps' created when price moves sharply between trading sessions.",
    "Range Trading": "Trading between established support and resistance levels in sideways markets.",
    "FVG": "Fair Value Gap - An imbalance in price created by a quick, strong movement that often gets filled later.",
    "Swing": "Medium-term trades aiming to capture 'swings' in price over several days.",
}

# Market Hours & Status
FOREX_MARKET_HOURS = {
    "open_weekdays": [0, 1, 2, 3, 4],  # Monday to Friday
    "close_weekdays": [5, 6],  # Saturday and Sunday
    "open_hours": (0, 24),  # 24-hour market
}

STOCK_MARKET_HOURS = {
    "open_weekdays": [0, 1, 2, 3, 4],  # Monday to Friday
    "close_weekdays": [5, 6],  # Saturday and Sunday
    "open_hours": (9, 16),  # 9:00 AM to 4:00 PM
}

CRYPTO_MARKET_HOURS = {
    "open_weekdays": [0, 1, 2, 3, 4, 5, 6],  # All days
    "close_weekdays": [],  # No closed days
    "open_hours": (0, 24),  # 24-hour market
}

COMMODITY_MARKET_HOURS = {
    "open_weekdays": [0, 1, 2, 3, 4],  # Monday to Friday
    "close_weekdays": [5, 6],  # Saturday and Sunday
    "open_hours": (9, 17),  # 9:00 AM to 5:00 PM
}

# Asset Categories
CRYPTO_ASSETS = [
    symbol for symbol, data in ASSET_CONFIG.items() if data.get("type") == "Crypto"
]
FOREX_ASSETS = [
    symbol for symbol, data in ASSET_CONFIG.items() if data.get("type") == "Forex"
]
STOCK_ASSETS = [
    symbol for symbol, data in ASSET_CONFIG.items() if data.get("type") == "Stock"
]
COMMODITY_ASSETS = [
    symbol for symbol, data in ASSET_CONFIG.items() if data.get("type") == "Commodity"
]
INDEX_ASSETS = [
    symbol for symbol, data in ASSET_CONFIG.items() if data.get("type") == "Index"
]

# News Keywords to Watch (High Impact)
HIGH_IMPACT_KEYWORDS = [
    "fed",
    "powell",
    "fomc",
    "rate hike",
    "interest rate",
    "inflation",
    "recession",
    "gdp",
    "unemployment",
    "jobs report",
    "non-farm payroll",
    "central bank",
    "ecb",
    "boe",
    "bank of japan",
    "reserve bank",
]

# Export config as dictionary for easy access
config = {
    "capital": {
        "api_key": CAPITAL_API_KEY,
        "api_password": CAPITAL_API_PASSWORD,
        "identifier": CAPITAL_IDENTIFIER,
        "api_url": CAPITAL_API_URL,
    },
    "telegram": {
        "token": TELEGRAM_TOKEN,
        "chat_id": TELEGRAM_CHAT_ID,
        "signal_chat_id": TELEGRAM_SIGNAL_CHAT_ID,
        "group_chat_id": TELEGRAM_GROUP_CHAT_ID,  # Added group chat ID
        "private_group": True,
    },
    "news": {
        "news_api_key": NEWS_API_KEY,
        "alphavantage_key": ALPHAVANTAGE_API_KEY,
        "openai_key": OPENAI_API_KEY,
    },
    "signals": {"dispatcher_url": SIGNAL_DISPATCHER_URL, "api_key": SIGNAL_API_KEY},
    "trading": {
        "strategy_mode": STRATEGY_MODE,
        "risk_percent": RISK_PERCENT,
        "recovery_enabled": RECOVERY_ENABLED,
        "weekend_crypto_only": WEEKEND_CRYPTO_ONLY,
        "pre_signal_alerts": PRE_SIGNAL_ALERTS,
    },
    "localization": {"enable_arabic": ENABLE_ARABIC},
    "features": {
        "pre_signals": PRE_SIGNALS_ENABLED,
        "recovery_mode": RECOVERY_MODE_ENABLED,
        "news_monitoring": NEWS_MONITORING_ENABLED,
        "market_awareness": MARKET_AWARENESS_ENABLED,
        "commentary": COMMENTARY_ENABLED,
    },
    "assets": ASSET_CONFIG,
    "strategies": STRATEGY_DESCRIPTIONS,
    "market_hours": {
        "forex": FOREX_MARKET_HOURS,
        "stock": STOCK_MARKET_HOURS,
        "crypto": CRYPTO_MARKET_HOURS,
        "commodity": COMMODITY_MARKET_HOURS,
    },
    "asset_categories": {
        "crypto": CRYPTO_ASSETS,
        "forex": FOREX_ASSETS,
        "stock": STOCK_ASSETS,
        "commodity": COMMODITY_ASSETS,
        "index": INDEX_ASSETS,
    },
    "news_keywords": HIGH_IMPACT_KEYWORDS,
}
