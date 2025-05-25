import sys
import os
from typing import List, Union, Tuple, Sequence, Any, Optional
from datetime import datetime
import logging
import asyncio
import random
import csv
import time
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pandas import Series
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv(override=True)

class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')
    STATUS_CHAT_ID: str = os.getenv('STATUS_CHAT_ID', TELEGRAM_CHAT_ID)
    NEWS_API_KEY: str = os.getenv('NEWS_API_KEY', '')
    TRADE_INTERVAL: int = int(os.getenv('TRADE_INTERVAL', '60'))  # seconds
    TRADE_HISTORY_FILE: str = os.getenv('TRADE_HISTORY_FILE', 'trade_history.csv')
    MARKETS: List[str] = os.getenv('MARKETS', 'XAUUSD,US100,GER40').split(',')
    RISK_PERCENT: float = float(os.getenv('RISK_PERCENT', '1.0'))
    STRATEGY_MODE: str = os.getenv('STRATEGY_MODE', 'Balanced')
    MIN_TRADE_INTERVAL: int = 10
    MAX_TRADE_INTERVAL: int = 3600
    API_URL: str = os.getenv('API_URL', 'https://api.example.com')

CONFIG = Config()

if CONFIG.TRADE_INTERVAL < CONFIG.MIN_TRADE_INTERVAL:
    CONFIG.TRADE_INTERVAL = CONFIG.MIN_TRADE_INTERVAL
elif CONFIG.TRADE_INTERVAL > CONFIG.MAX_TRADE_INTERVAL:
    CONFIG.TRADE_INTERVAL = CONFIG.MAX_TRADE_INTERVAL

logging.basicConfig(
    format='%(asctime)s | %(levelname)s | %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_retry_session() -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

http_session = get_retry_session()

try:
    from newsapi import NewsApiClient
except ImportError:
    class NewsApiClient:
        def __init__(self, api_key: str = ''):
            pass

        def get_top_headlines(self, language='en', page_size=5, **kwargs) -> dict:
            return {"articles": []}

try:
    from capital_com_trader import CapitalComTrader as ImportedCapitalComTrader
    CapitalComTrader: type = ImportedCapitalComTrader
except ImportError:
    class CapitalComTrader:
        def initialize(self):
            logging.getLogger(__name__).warning("StubCapitalComTrader initialized")

        def execute_trade(self, symbol: str, direction: str, tp: float, sl: float) -> bool:
            logging.getLogger(__name__).warning(f"Trade stub for {symbol} {direction}")
            return False

try:
    from market_status_checker import is_market_closed
except ImportError:
    def is_market_closed(symbol: str) -> bool:
        return False

try:
    from message_generator import generate_signal_message
except ImportError:
    def generate_signal_message(*args, **kwargs) -> str:
        return f"Signal: {kwargs.get('signal', {}).get('symbol', kwargs.get('signal', {}).get('pair', ''))} {kwargs.get('signal', {}).get('direction', '')}"

async def save_trade_to_csv(timestamp: str, symbol: str, action: str, tp: float, sl: float, result: str) -> None:
    try:
        await asyncio.to_thread(_write_trade_to_csv, timestamp, symbol, action, tp, sl, result)
    except Exception as e:
        logging.getLogger(__name__).error(f"CSV save failed: {e}")

def _write_trade_to_csv(timestamp: str, symbol: str, action: str, tp: float, sl: float, result: str) -> None:
    file_exists = os.path.isfile(CONFIG.TRADE_HISTORY_FILE)
    with open(CONFIG.TRADE_HISTORY_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Time', 'Symbol', 'Action', 'TP', 'SL', 'Result'])
        writer.writerow([timestamp, symbol, action, tp, sl, result])

async def fetch_latest_news() -> List[str]:
    try:
        loop = asyncio.get_running_loop()
        def sync_fetch():
            client = NewsApiClient(api_key=CONFIG.NEWS_API_KEY)
            top = client.get_top_headlines(language='en', page_size=5)
            return [a.get('title', '') for a in top.get('articles', [])]
        return await loop.run_in_executor(None, sync_fetch)
    except Exception as e:
        logging.getLogger(__name__).error(f"News fetch error: {e}")
        return []

async def send_signal(app: Optional[Application], text: str) -> None:
    if app is None:
        logger.error("send_signal called with app=None")
        return
    try:
        await app.bot.send_message(
            chat_id=CONFIG.TELEGRAM_CHAT_ID,
            text=text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.getLogger(__name__).error(f"Signal send failed: {e}")

class TradingBot:
    def __init__(self, app: Optional[Application] = None):
        self.app = app
        self.trader = CapitalComTrader()
        self.trader.initialize()
        self.interval = CONFIG.TRADE_INTERVAL
        self.markets = [m.strip() for m in CONFIG.MARKETS]

    def get_market_data(self, symbol: str):
        # This method is used by tests and should be patched or implemented
        raise NotImplementedError("get_market_data is not implemented")

    def analyze_market(self, symbol: str) -> dict:
        # This method is used by tests and should be patched or implemented
        raise NotImplementedError("analyze_market is not implemented")

    async def run(self):
        logger.info('Trading loop started')
        while True:
            for symbol in self.markets:
                if is_market_closed(symbol):
                    continue
                price = random.uniform(50, 150)
                direction = 'BUY' if price < 100 else 'SELL'
                tp = price * (1.01 if direction == 'BUY' else 0.99)
                sl = price * (0.99 if direction == 'BUY' else 1.01)
                success = self.trader.execute_trade(symbol, direction, tp, sl)
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                await save_trade_to_csv(ts, symbol, direction, tp, sl, 'DONE' if success else 'FAIL')
                sig = {'symbol': symbol, 'direction': direction, 'tp': tp, 'sl': sl}
                msg = generate_signal_message(sig, direction, tp, sl)
                await send_signal(self.app, msg)
                await asyncio.sleep(1)
            await asyncio.sleep(self.interval)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat:
        text = f"Magus-Prime-X Bot online! Mode: {CONFIG.STRATEGY_MODE}"
        await context.bot.send_message(chat_id=chat.id, text=text)


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat:
        info = (
            f"Interval={CONFIG.TRADE_INTERVAL}s, "
            f"Markets={','.join(CONFIG.MARKETS)}, "
            f"Risk={CONFIG.RISK_PERCENT}%"
        )
        await context.bot.send_message(chat_id=chat.id, text=info)
