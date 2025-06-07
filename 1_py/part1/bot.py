# --- Part 1: Imports, Config, Logging ---
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from dotenv import load_dotenv
from datetime import datetime
import logging
import asyncio
import sys
import os
import requests
from telegram.ext import ContextTypes
import random
import csv
from requests.adapters import HTTPAdapter, Retry
from typing import List, Optional
GLOBAL_Optional = Optional  # <-- make Optional globally accessible


load_dotenv()


class Config:
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')
    STATUS_CHAT_ID: str = os.getenv('STATUS_CHAT_ID', TELEGRAM_CHAT_ID)
    NEWS_API_KEY: str = os.getenv('NEWS_API_KEY', '')
    TRADE_INTERVAL: int = int(os.getenv('TRADE_INTERVAL', '60'))  # seconds
    TRADE_HISTORY_FILE: str = os.getenv(
        'TRADE_HISTORY_FILE', 'trade_history.csv')
    MARKETS: List[str] = os.getenv('MARKETS', 'XAUUSD,US100,GER40').split(',')
    RISK_PERCENT: float = float(os.getenv('RISK_PERCENT', '1.0'))
    STRATEGY_MODE: str = os.getenv('STRATEGY_MODE', 'Balanced')
    MIN_TRADE_INTERVAL: int = 10
    MAX_TRADE_INTERVAL: int = 3600


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

# --- Part 2: HTTP, Stubs, Helpers ---


def get_retry_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


http_session = get_retry_session()

try:
    from newsapi import NewsApiClient
except ImportError:
    class StubNewsApiClient:
        def __init__(self, api_key: str = ''):
            pass

        def get_top_headlines(self, **kwargs) -> dict:
            return {"articles": []}

try:
    from indicators import calculate_macd_safe, calculate_rsi_safe, calculate_ema_safe
    from technical_indicators import calculate_vwap_safe, calculate_adx_safe

    # Redefine calculate_ichimoku_safe with the correct signature
    from pandas import Series
    from typing import Union

    def calculate_ichimoku_safe(
        high: Series,
        low: Series,
        close: Series,
        window1: int = 9,
        window2: int = 26,
        window3: int = 52
    ) -> Union[float, None]:
        # Call the original function with only the first three parameters
        from technical_indicators import calculate_ichimoku_safe as original_calculate_ichimoku_safe
        return original_calculate_ichimoku_safe(high, low, close)
    # Patch: ensure calculate_ichimoku_safe has the correct signature
    import inspect
    if (
        "calculate_ichimoku_safe" in locals()
        and len(inspect.signature(calculate_ichimoku_safe).parameters) == 3
    ):
        # Redefine with correct signature if needed
        from pandas import Series
        from typing import Union

        def calculate_ichimoku_safe(
            high: Series,
            low: Series,
            close: Series,
            window1: int = 9,
            window2: int = 26,
            window3: int = 52
        ) -> Union[float, None]:
            # Call the original with only 3 params if needed, ignore extra
            return None
except ImportError:
    from typing import Sequence, Tuple, Optional
    from pandas import Series
    from typing import Union

    def calculate_macd_safe(prices: Sequence[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[Optional[float], Optional[float]]:
        return (None, None)

    def calculate_rsi_safe(prices: Sequence[float], period: int = 14) -> Optional[float]:
        return None

    def calculate_ema_safe(prices: Sequence[float], period: int = 14) -> Optional[float]:
        return None

    def calculate_vwap_safe(high: Series, low: Series, close: Series, volume: Series, window: int = 14) -> Union[float, None]:
        return None

    def calculate_adx_safe(high: Series, low: Series, close: Series, window: int = 14) -> Union[float, None]:
        return None

    def calculate_ichimoku_safe(
        high: Series,
        low: Series,
        close: Series,
        window1: int = 9,
        window2: int = 26,
        window3: int = 52
    ) -> Union[float, None]:
        return None

# Make indicator functions globally accessible
GLOBAL_calculate_macd_safe = calculate_macd_safe
GLOBAL_calculate_rsi_safe = calculate_rsi_safe
GLOBAL_calculate_ema_safe = calculate_ema_safe
GLOBAL_calculate_vwap_safe = calculate_vwap_safe
GLOBAL_calculate_adx_safe = calculate_adx_safe
GLOBAL_calculate_ichimoku_safe = calculate_ichimoku_safe

# Make stub function parameter names globally accessible
GLOBAL_high_param = "high"
GLOBAL_low_param = "low"
GLOBAL_close_param = "close"
GLOBAL_window1_param = "window1"
GLOBAL_window2_param = "window2"
GLOBAL_window3_param = "window3"

try:
    from market_status_checker import is_market_closed
except ImportError:
    def is_market_closed(symbol: str) -> bool:
        return False

try:
    from message_generator import generate_signal_message
except ImportError:
    def generate_signal_message(signal: dict, direction: str = '', tp: float = 0.0, sl: float = 0.0) -> str:
        return f"Signal: {signal.get('symbol', signal.get('pair', ''))} {signal.get('direction', direction)}"

try:
    from capital_com_trader import CapitalComTrader
except ImportError:
    class StubCapitalComTrader:
        def initialize(self):
            logging.getLogger(__name__).warning(
                "StubCapitalComTrader initialized")

        def execute_trade(self, symbol, direction, tp, sl) -> bool:
            logging.getLogger(__name__).warning(
                f"Trade stub for {symbol} {direction}")
            return False


async def save_trade_to_csv(timestamp: str, symbol: str, action: str, tp: float, sl: float, result: str) -> None:
    file_exists = os.path.isfile(CONFIG.TRADE_HISTORY_FILE)
    try:
        with open(CONFIG.TRADE_HISTORY_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(
                    ['Time', 'Symbol', 'Action', 'TP', 'SL', 'Result'])
            writer.writerow([timestamp, symbol, action, tp, sl, result])
    except Exception as e:
        logging.getLogger(__name__).error(f"CSV save failed: {e}")


async def fetch_latest_news() -> List[str]:
    try:
        loop = asyncio.get_running_loop()

        def sync_fetch():
            client = (NewsApiClient if 'NewsApiClient' in globals()
                      else StubNewsApiClient)(api_key=CONFIG.NEWS_API_KEY)
            top = client.get_top_headlines(language='en', page_size=5)
            return [a.get('title', '') for a in top.get('articles', [])]
        return await loop.run_in_executor(None, sync_fetch)
    except Exception as e:
        logging.getLogger(__name__).error(f"News fetch error: {e}")
        return []


async def send_signal(app: Application, text: str) -> None:
    try:
        await app.bot.send_message(
            chat_id=CONFIG.TELEGRAM_CHAT_ID,
            text=text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logging.getLogger(__name__).error(f"Signal send failed: {e}")

# --- Part 3: TradingBot and Command Handlers ---


class TradingBot:
    def __init__(self, app: Application):
        self.app = app
        self.trader = (
            CapitalComTrader if 'CapitalComTrader' in globals() else StubCapitalComTrader)()
        self.trader.initialize()
        self.interval = CONFIG.TRADE_INTERVAL
        self.markets = [m.strip() for m in CONFIG.MARKETS]

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
                sig = {'symbol': symbol,
                       'direction': direction, 'tp': tp, 'sl': sl}
                msg = generate_signal_message(sig)
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
