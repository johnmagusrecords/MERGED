import logging
import os
import re
import threading
import time
from collections import deque

import aiohttp  # Make sure to install this with: pip install aiohttp
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)  # Define logger before using it

# Import BeautifulSoup for handling HTML parsing
try:
    from bs4 import BeautifulSoup

    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BeautifulSoup = None
    BEAUTIFULSOUP_AVAILABLE = False
    logger.warning(
        "BeautifulSoup not installed. HTML parsing will be skipped if required."
    )

# Import NewsApiClient for fetching news
try:
    from newsapi import NewsApiClient

    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False
    logger.warning(
        "NewsApiClient not installed. Run fix_dependencies.py to fix news fetching."
    )

# Add Telegram markdown escaping functionality


def escape_markdown(text: str) -> str:
    """
    Escape Telegram Markdown special characters in the given text.
    """
    if not text:
        return ""
    # Characters to escape in Markdown to avoid formatting issues
    special_chars = (
        r"[*_`]"  # escaping *, _, and backtick; brackets are handled separately
    )
    # Use regex to prefix special characters with a backslash
    return re.sub(special_chars, r"\\\g<0>", text)


# Add format_news_data function
def format_news_data(news_item):
    """Format news data into a properly escaped Markdown message"""
    try:
        title = escape_markdown(news_item.get("title", "No title"))
        source = escape_markdown(
            news_item.get("source", {}).get("name", "Unknown source")
        )
        description = escape_markdown(news_item.get("description", ""))
        url = news_item.get("url", "#")

        formatted_message = (
            f"📰 *{title}*\n📡 _{source}_\n\n{description}\n🔗 [Read more]({url})"
        )
        return formatted_message
    except Exception as e:
        print(f"Formatting error: {e}")
        return "⚠️ Failed to format news article."


# Add send_telegram_news function
async def send_telegram_news(news_item, bot_token, chat_id):
    """Send news to Telegram with proper markdown escaping"""
    try:
        message = format_news_data(news_item)
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "MarkdownV2",
                "disable_web_page_preview": False,
            }
            async with session.post(url, data=payload) as resp:
                if resp.status != 200:
                    print(
                        f"Failed to send news to Telegram: {resp.status} - {await resp.text()}"
                    )
    except Exception as e:
        print(f"send_telegram_news error: {e}")


# Load environment variables
load_dotenv()

# API Keys and Telegram configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_GROUP_ID")
GROUP_ID = os.getenv(
    "TELEGRAM_GROUP_ID", CHAT_ID
)  # Default to CHAT_ID if GROUP_ID not set
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY") or os.getenv(
    "ALPHA_VANTAGE_API_KEY"
)
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY") or os.getenv("NEWS_API_KEY")
NEWS_UPDATE_INTERVAL = int(
    os.getenv("NEWS_UPDATE_INTERVAL", "1800")
)  # 30 minutes default

# API URLs
ALPHAVANTAGE_URL = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={ALPHAVANTAGE_API_KEY}"
NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"

# RSS Feeds for additional news sources
RSS_FEEDS = {
    "forex": ["https://www.forexlive.com/feed", "https://www.fxstreet.com/news/feed"],
    "crypto": ["https://cointelegraph.com/rss", "https://news.bitcoin.com/feed/"],
    "stocks": [
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",  # CNBC Market News
        "https://www.investing.com/rss/news.rss",
    ],
    "arabic": [
        "https://arabic.cnn.com/api/v1/rss/business/rss.xml",  # CNN Arabic Business
        "https://www.mubasher.info/api/1.0/news/get-by-category/82/rss",  # Arabic Financial News
    ],
}

# User-Agent for API requests
HEADERS = {"User-Agent": "MagusPrimeX NewsBot/1.0"}

# Cache for news articles and sentiment data
NEWS_CACHE = deque(maxlen=500)  # Store up to 500 recent articles
SENTIMENT_CACHE = {}  # Symbol -> sentiment score

# Asset keywords for categorization
ASSET_KEYWORDS = {
    "crypto": [
        "bitcoin",
        "btc",
        "eth",
        "ethereum",
        "crypto",
        "blockchain",
        "defi",
        "nft",
        "altcoin",
        "binance",
        "coinbase",
    ],
    "forex": [
        "forex",
        "eur",
        "usd",
        "jpy",
        "gbp",
        "currency",
        "exchange rate",
        "dollar",
        "euro",
        "pound",
        "yen",
    ],
    "gold": ["gold", "xau", "precious metal", "bullion"],
    "oil": ["oil", "crude", "wti", "brent", "petroleum"],
    "indices": [
        "s&p",
        "nasdaq",
        "dow",
        "index",
        "dax",
        "ftse",
        "nikkei",
        "stock market",
    ],
}

# High impact news keywords
HIGH_IMPACT_KEYWORDS = [
    "rate hike",
    "fed",
    "federal reserve",
    "ecb",
    "boe",
    "interest rate",
    "inflation",
    "gdp",
    "nfp",
    "non-farm payroll",
    "recession",
    "crash",
    "surge",
    "plunge",
    "unemployment",
]

# Runtime flags
news_monitor_running = False
stop_news_monitor = threading.Event()

# Begin monitoring if this file is run directly
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting news monitoring as main module")

    # Test sending a news message
    test_message = {
        "title": "TEST MESSAGE",
        "source": {"name": "News Monitoring System"},
        "description": "This is a test of the news monitoring system. The system is working correctly if you can see this message.",
        "url": "https://example.com/test-message",
    }

    print("Testing news monitoring system...")
    print("Sending test message to Telegram...")

    result = send_telegram_news(test_message, BOT_TOKEN, CHAT_ID)
    if result.get("ok"):
        print("✅ Test message sent successfully!")
    else:
        print(f"❌ Failed to send test message: {result}")

    # Start the news monitor
    monitor_thread = threading.Thread(
        target=lambda: None, daemon=True
    )  # Placeholder for actual monitoring function
    monitor_thread.start()

    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping news monitor...")
        stop_news_monitor.set()
        monitor_thread.join(timeout=5)
        print("News monitor stopped.")

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

# Configuration from environment
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
ENABLE_NEWS_MONITORING = os.getenv("ENABLE_NEWS_MONITORING", "true").lower() == "true"
ENABLE_PRE_NEWS_EXIT = os.getenv("ENABLE_PRE_NEWS_EXIT", "true").lower() == "true"
NEWS_CHECK_INTERVAL = int(os.getenv("NEWS_CHECK_INTERVAL", "300"))  # Default: 5 minutes
NEWS_LOOKBACK_HOURS = int(os.getenv("NEWS_LOOKBACK_HOURS", "2"))  # Default: 2 hours

# Import bot functions - avoid circular imports by using local imports when needed
def get_open_positions():
    """
    Get current open positions - implement based on your bot's structure
    This is a placeholder that would be replaced with actual implementation
    """
    try:
        # In a real implementation, you would get this from your trading platform
        # For now, return a sample list
        from bot_dev_backup import active_signals
        return list(active_signals.keys())
    except (ImportError, Exception):
        # Fallback
        return []

def check_trade_exit_due_to_news(symbol, headline, description=None):
    """
    Check if a trade should exit based on news content
    
    Args:
        symbol: Trading symbol
        headline: News headline
        description: News description (optional)
    
    Returns:
        bool: True if exit is recommended, False otherwise
    """
    # Risk keywords that indicate potential market volatility
    risk_keywords = [
        "rate hike", "inflation", "fed decision", "interest rate", 
        "war", "conflict", "emergency", "crash", "sell-off",
        "breaking", "collapse", "crisis", "plunge", "tumble",
        "recession", "bankruptcy", "default", "disaster",
        "investigation", "stimulus", "bailout", "ban", "sanction"
    ]
    
    # Extra high risk keywords that always trigger exit
    critical_keywords = [
        "market crash", "bank failure", "financial crisis", "circuit breaker",
        "trading halt", "black swan", "emergency meeting", "flash crash"
    ]
    
    # Asset-specific keywords
    asset_keywords = {
        "BTC": ["bitcoin", "crypto", "cryptocurrency", "digital currency", "blockchain"],
        "ETH": ["ethereum", "crypto", "cryptocurrency", "digital currency", "blockchain"],
        "XAU": ["gold", "precious metal", "safe haven", "bullion"],
        "OIL": ["crude", "petroleum", "barrel", "opec", "energy crisis"],
        "SPX": ["s&p", "index", "wall street", "stock market", "dow"],
        "USD": ["dollar", "fed", "treasury", "greenback", "currency"]
    }
    
    # Determine which asset keywords to use
    relevant_asset_keywords = []
    for asset_prefix, keywords in asset_keywords.items():
        if asset_prefix in symbol.upper():
            relevant_asset_keywords.extend(keywords)
    
    # If we don't have specific asset keywords, default to generic
    if not relevant_asset_keywords:
        relevant_asset_keywords = ["market", "trading", "economy", "finance"]
    
    # Check combined text for risks
    combined_text = (headline + " " + (description or "")).lower()
    
    # Check for critical keywords first (always exit)
    if any(keyword in combined_text for keyword in critical_keywords):
        logger.warning(f"Critical risk keyword detected for {symbol} in news: {headline}")
        
        # Import locally to avoid circular imports
        async def notify_and_exit():
            try:
                from bot_dev_backup import close_position_due_to_news
                await close_position_due_to_news(symbol, headline)
            except Exception as e:
                logger.error(f"Failed to process emergency exit: {e}")
                
        # Create task to handle the exit
        asyncio.create_task(notify_and_exit())
        return True
    
    # Check if both risk keywords and asset relevance
    has_risk_keyword = any(keyword in combined_text for keyword in risk_keywords)
    has_asset_keyword = any(keyword in combined_text for keyword in relevant_asset_keywords)
    
    if has_risk_keyword and has_asset_keyword:
        logger.warning(f"Risk keywords detected for {symbol} in news: {headline}")
        
        # Import locally to avoid circular imports
        async def notify_and_exit():
            try:
                # Send a Telegram notification
                message = (
                    f"⚠️ *Emergency Exit Alert*\n\n"
                    f"High-impact news detected related to *{symbol}*:\n\n"
                    f"📰 _{headline}_\n\n"
                    f"💡 Evaluating position closure to protect capital."
                )
                
                # Import locally to avoid circular imports
                try:
                    from bot_dev_backup import send_telegram_message_async, is_telegram_async, send_telegram_message_sync
                    
                    if is_telegram_async:
                        await send_telegram_message_async(message)
                    else:
                        send_telegram_message_sync(message)
                except ImportError:
                    # Fallback if telegram functions aren't available
                    logger.warning("Couldn't import Telegram functions")
                
                # Trigger position close if enabled
                from bot_dev_backup import close_position_due_to_news
                await close_position_due_to_news(symbol, headline)
            except Exception as e:
                logger.error(f"Failed to process news alert: {e}")
        
        # Create task to handle the alert and exit
        asyncio.create_task(notify_and_exit())
        return True
    
    return False

async def fetch_latest_news():
    """Fetch latest market news from various sources"""
    if not NEWS_API_KEY:
        logger.warning("News API key not set, cannot fetch news")
        return []
    
    try:
        # Calculate time range - look back a few hours
        from_date = (datetime.now() - timedelta(hours=NEWS_LOOKBACK_HOURS)).strftime('%Y-%m-%d')
        
        # Fetch financial news using NewsAPI
        url = f"https://newsapi.org/v2/everything"
        params = {
            'apiKey': NEWS_API_KEY,
            'q': '(stock OR market OR trading OR forex OR crypto OR finance) AND (crash OR surge OR plunge OR rally)',
            'language': 'en',
            'from': from_date,
            'sortBy': 'publishedAt'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('articles', [])
            
            # Format the results
            results = []
            for article in articles[:15]:  # Top 15 articles
                results.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'publishedAt': article.get('publishedAt', '')
                })
            
            return results
        else:
            logger.error(f"News API error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return []

async def monitor_news_for_open_positions():
    """Monitor news for impact on open positions"""
    try:
        # Load pre-news exit settings
        ENABLE_PRENEWS_EXIT = os.getenv("ENABLE_PRENEWS_EXIT", "false").lower() == "true"
        
        if ENABLE_PRENEWS_EXIT:
            try:
                import json
                IMPORTANT_EVENTS = json.loads(os.getenv("IMPORTANT_EVENTS", '[]'))
                PRENEWS_EXIT_BEFORE_MINUTES = int(os.getenv("PRENEWS_EXIT_BEFORE_MINUTES", "10"))
            except (json.JSONDecodeError, ValueError):
                logger.error("Error parsing pre-news exit settings, using defaults")
                IMPORTANT_EVENTS = ["CPI", "FOMC", "Powell", "NFP", "Jobs Report", "Rate Decision", "Interest Rate"]
                PRENEWS_EXIT_BEFORE_MINUTES = 10
        
        # Get open positions
        open_positions = get_open_positions()
        if not open_positions:
            return
        
        # Fetch latest news
        news_articles = await fetch_latest_news()
        if not news_articles:
            return
        
        # First check for important upcoming events that require closing all positions
        if ENABLE_PRENEWS_EXIT:
            for article in news_articles:
                if should_exit_due_to_news(article, IMPORTANT_EVENTS, PRENEWS_EXIT_BEFORE_MINUTES):
                    logger.warning(f"⚠️ Exiting all trades due to upcoming event: {article.get('title', 'Unknown event')}")
                    
                    try:
                        # Close all positions
                        async def close_all_due_to_news():
                            try:
                                # Import bot functions locally to avoid circular imports
                                from bot_dev_backup import close_all_positions
                                await close_all_positions()
                                
                                # Send notification
                                event_title = article.get('title', 'Unknown event')
                                message = (
                                    f"⚠️ *Pre-News Auto Exit*\n\n"
                                    f"Closed all positions due to upcoming high-impact event:\n\n"
                                    f"📰 _{event_title}_\n\n"
                                    f"This is an automated protective measure to avoid high volatility."
                                )
                                
                                try:
                                    from bot_dev_backup import send_telegram_message_async, is_telegram_async, send_telegram_message_sync
                                    
                                    if is_telegram_async:
                                        await send_telegram_message_async(message)
                                    else:
                                        send_telegram_message_sync(message)
                                except ImportError:
                                    logger.warning("Couldn't import Telegram functions for notification")
                            except Exception as e:
                                logger.error(f"Failed to close positions for pre-news exit: {e}")
                        
                        # Execute the closure
                        asyncio.create_task(close_all_due_to_news())
                        # Only exit once - no need to process multiple events
                        return
                    except Exception as e:
                        logger.error(f"Error in pre-news exit: {e}")
        
        # Then check each position against news (existing code)
        for symbol in open_positions:
            symbol_str = str(symbol).upper()
            
            # Extract the base asset name for better matching
            base_asset = symbol_str
            if "USD" in symbol_str and symbol_str != "USD":
                base_asset = symbol_str.replace("USD", "")
            
            # Check each news article for relevance to this asset
            for article in news_articles:
                headline = article.get('title', '')
                description = article.get('description', '')
                
                # Check both the full symbol and base asset
                if (symbol_str in headline.upper() or base_asset in headline.upper() or
                    symbol_str in description.upper() or base_asset in description.upper()):
                    
                    # Check if this news indicates we should exit
                    check_trade_exit_due_to_news(symbol, headline, description)
    
    except Exception as e:
        logger.error(f"Error in news monitoring for positions: {e}")

async def run_news_monitoring():
    """Main news monitoring loop"""
    if not ENABLE_NEWS_MONITORING:
        logger.info("News monitoring is disabled")
        return
    
    logger.info("Starting news monitoring service")
    
    while True:
        try:
            # Only check for news impacts to open positions if pre-exit is enabled
            if ENABLE_PRE_NEWS_EXIT:
                await monitor_news_for_open_positions()
            
            # Wait for next check
            await asyncio.sleep(NEWS_CHECK_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in news monitoring: {e}")
            await asyncio.sleep(60)  # Wait a minute before retrying

def start_news_monitoring():
    """Start the news monitoring service in background"""
    if not ENABLE_NEWS_MONITORING:
        logger.info("News monitoring is disabled")
        return
    
    # Create and start the event loop
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.create_task(run_news_monitoring())
        loop.run_forever()
    except Exception as e:
        logger.error(f"Failed to start news monitoring: {e}")

# For direct execution testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("Testing news monitoring...")
    
    async def test():
        news = await fetch_latest_news()
        for article in news[:3]:  # Show first 3 articles
            print(f"Title: {article['title']}")
            print(f"Description: {article['description']}")
            print(f"URL: {article['url']}")
            print("-" * 80)
            
        # Test exit detection
        test_headline = "BREAKING: Fed announces emergency rate hike causing market chaos"
        should_exit = check_trade_exit_due_to_news("BTCUSD", test_headline)
        print(f"Should exit based on test headline: {should_exit}")
    
    asyncio.run(test())

# Add the should_exit_due_to_news function
def should_exit_due_to_news(news_item, important_events, minutes_before):
    """
    Check if a news item matches an important event and is within the pre-exit window
    
    Args:
        news_item: The news article data
        important_events: List of important event keywords
        minutes_before: How many minutes before the event to exit
        
    Returns:
        bool: True if trades should be closed, False otherwise
    """
    now = datetime.utcnow()
    
    # Check if title contains any important event keywords
    if not any(event.lower() in news_item.get('title', '').lower() for event in important_events):
        return False
        
    # Get news time, default to current time if not available
    news_time = news_item.get("publishedAt")
    if not news_time:
        news_time = news_item.get("datetime", now)
    
    # Convert string time to datetime if needed
    if isinstance(news_time, str):
        try:
            # Try different formats
            try:
                news_time = datetime.fromisoformat(news_time.replace('Z', '+00:00'))
            except ValueError:
                news_time = datetime.strptime(news_time, "%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, TypeError):
            logger.warning(f"Could not parse news datetime: {news_time}")
            news_time = now
            
    # Check if we're in the pre-event window
    time_until_event = news_time - now
    minutes_until_event = time_until_event.total_seconds() / 60
    
    # Exit if event is coming up within the specified window
    return 0 <= minutes_until_event <= minutes_before
