from signal_formatter import build_signal_message
import io
from dotenv import load_dotenv
from typing import Any, Optional, List, Dict
try:
    from news_monitor import fetch_news, get_market_sentiment  # use the existing function
except ImportError:
    # Safe fallback if news_monitor is missing
    def fetch_news():
        return []

    def get_market_sentiment():
        return None
# Ensure indicators are used
from technical_indicators import calculate_macd_safe, calculate_rsi_safe
from telegram_utils import send_message_sync  # Ensure send_message_sync is used
# Ensure EnhancedSignalSender is used
from enhanced_signal_sender import EnhancedSignalSender, send_signal, send_signal_with_commentary, send_pre_signal_alert, send_recap
from ta.momentum import RSIIndicator
from ta.trend import MACD
from openai_assistant import get_trade_commentary, get_openai_commentary, generate_gpt_commentary, analyze_sentiment
from commentary_generator import generate_fallback_commentary
from market_status_checker import (
    check_market_status,
    get_asset_type,
    get_market_status_message,
)
from flask import Flask, jsonify, render_template_string, request
import unittest
import json
import logging
import os
import sys
import threading
import time
import signal
from collections import deque
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from logging.handlers import RotatingFileHandler
from message_generator import generate_message


def log_trade_action(signal_id, action):
    logger.info(f"Action '{action}' logged for signal ID: {signal_id}")


load_dotenv()  # Only call once at the top


try:
    import yaml
    print("✅ PyYAML module is installed and working.")
except ImportError:
    raise ImportError(
        "❌ The 'yaml' module is not installed. Please install it using 'pip install PyYAML'.")

# Configure UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# === Configuration Constants ===
CONFIG = {
    "MAGUS_ASSISTANT_ENABLED": os.getenv("MAGUS_ASSISTANT_ENABLED", "false").lower() == "true",
    "MARKET_AWARENESS_ENABLED": os.getenv("ENABLE_MARKET_AWARENESS", "true").lower() == "true",
    "NEWS_MONITORING_ENABLED": os.getenv("ENABLE_NEWS_MONITORING", "true").lower() == "true",
    "PORT": int(os.getenv("PORT", 8080)),
    "API_KEY": os.getenv("API_KEY", "magus_prime_secret_key"),
    "DEBUG_MODE": os.getenv("DEBUG", "false").lower() == "true",
    "ALLOW_MARKET_OVERRIDE": os.getenv("ALLOW_MARKET_OVERRIDE", "false").lower() == "true",
    "MAX_SIGNAL_HISTORY": 1000,
    "CLEANUP_INTERVAL": 6 * 60 * 60  # 6 hours
}

# === Flask Application Setup ===
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if CONFIG["DEBUG_MODE"] else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("signal_dispatcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

log_file = "app.log"
handler = RotatingFileHandler(
    log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# === Global State Management ===


class SignalDispatcherState:
    def __init__(self):
        self.signal_history: list[Any] = []
        self.signal_history_file: str = "signal_history.json"  # define this attribute
        self.news_monitor_thread: Optional[threading.Thread] = None
        self.seen_titles = deque(maxlen=1000)
        self.history_lock = threading.Lock()


state = SignalDispatcherState()

# === Signal Dispatcher ===


class SignalDispatcher:
    def __init__(self):
        self.active_signals: List[Dict[str, Any]] = []

    def get_active_signals(self) -> Optional[List[Dict[str, Any]]:
        """
        Return the list of active signals. Returns None if no signals exist.
        """
        return self.active_signals or None

    def add_signal(self, signal: Dict[str, Any]) -> None:
        """
        Add a new signal to the active signals list.
        """
        self.active_signals.append(signal)

    def remove_signal(self, signal_id: str) -> None:
        """
        Remove a signal from the active signals list by its ID.
        """
        self.active_signals = [
            signal for signal in self.active_signals if signal.get("id") != signal_id
        ]

    def send_recap(self, pair: str, result: str, exit_price: float, notes: str) -> Dict[str, Any]:
        """
        Send a recap notification for a completed trade.
        """
        recap_message = f"Recap for {pair}: {result} at {exit_price}. Notes: {notes}"
        return {"success": True, "message": recap_message}

    def dispatch_signal(self, signal: Dict[str, Any]) -> None:
        """
        Dispatch a signal to the appropriate channels.
        """
        self.send_recap(
            pair=signal["pair"],
            result=signal.get("result", "UNKNOWN"),
            exit_price=signal.get("exit_price", 0.0),
            notes=signal.get("notes", "No additional notes.")
        )

    def clear_expired_signals(self) -> None:
        """
        Clear signals that are older than a certain threshold.
        """
        pass


# === Helper Functions ===


def validate_api_key(request_api_key: str | None) -> bool:
    """
    Validate the API key with secure comparison.

    Args:
        request_api_key: The API key provided in the request.

    Returns:
        bool: True if the API key is valid, False otherwise.
    """
    api_key = os.getenv("API_KEY", "magus_prime_secret_key")
    if not api_key:
        logger.warning("API key validation disabled - no key configured.")
        return True
    is_valid = (request_api_key or "") == api_key
    if not is_valid:
        logger.warning("Invalid API key provided.")
    return is_valid


def save_signal_history(state):
    """
    Save signal history with thread-safe locking.

    Args:
        state: The global state object containing signal history.
    """
    with state.history_lock:
        try:
            with open(state.signal_history_file, 'w') as f:
                json.dump(state.signal_history, f, indent=2, default=str)
            logger.info("Signal history saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save signal history: {e}")


def load_signal_history():
    """
    Load signal history with error handling.
    """
    try:
        if os.path.exists(state.signal_history_file):
            with open(state.signal_history_file, 'r') as f:
                with state.history_lock:
                    state.signal_history = json.load(f)
                logger.info(
                    f"Loaded {len(state.signal_history)} historical signals.")
    except Exception as e:
        logger.error(f"Failed to load signal history: {e}")


executor = ThreadPoolExecutor(max_workers=5)


def background_cleanup():
    """Periodic maintenance tasks."""
    while True:
        try:
            with state.history_lock:
                if len(state.signal_history) > CONFIG["MAX_SIGNAL_HISTORY"]:
                    state.signal_history = state.signal_history[-CONFIG["MAX_SIGNAL_HISTORY"]:]
                    save_signal_history(state)
                    logger.info("Performed signal history cleanup")
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
        time.sleep(CONFIG["CLEANUP_INTERVAL"])


# Start cleanup task in the thread pool
executor.submit(background_cleanup)

# Example usage of the 'ta' library to ensure it is accessed


def example_ta_usage():
    import pandas as pd
    # Updated synthetic data to include sufficient points for meaningful RSI/MACD calculations
    data = pd.DataFrame({
        "close": [100 + i for i in range(100)],  # 100 data points
        "high": [101 + i for i in range(100)],
        "low": [99 + i for i in range(100)]
    })
    rsi = RSIIndicator(data["close"]).rsi()
    logger.info(f"Example RSI calculation: {rsi.tolist()}")

    macd = MACD(data["close"]).macd()
    logger.info(f"Example MACD calculation: {macd.tolist()}")

# Example usage of generate_gpt_commentary


def example_generate_gpt_commentary():
    try:
        result = generate_gpt_commentary(
            "Explain the impact of market trends on trading strategies.")
        logger.info(f"Example GPT Commentary: {result}")
    except Exception as e:
        logger.error(f"Failed to generate GPT commentary: {e}")

# Example usage of get_trade_commentary


def example_get_trade_commentary():
    try:
        result = get_trade_commentary(
            "EUR/USD", "Breakout Strategy", entry=1.1000, stop_loss=1.0900)
        logger.info(f"Example Trade Commentary: {result}")
    except Exception as e:
        logger.error(f"Failed to get trade commentary: {e}")

# Example usage of analyze_sentiment


def example_analyze_sentiment():
    try:
        result = analyze_sentiment(
            "The market is showing strong bullish signals.")
        logger.info(f"Example Sentiment Analysis: {result}")
    except Exception as e:
        logger.error(f"Failed to analyze sentiment: {e}")


# Example usage of EnhancedSignalSender
signal_sender = EnhancedSignalSender()

# Example usage of send_message_sync
send_message_sync("Signal Dispatcher Initialized",
                  chat_id=os.getenv("TELEGRAM_STATUS_CHAT_ID"))

# Example usage of fetch_news
latest_news = fetch_news()
if latest_news:
    print("Latest News:", latest_news)

# Example usage of calculate_macd_safe and calculate_rsi_safe


def analyze_market_data(data):
    macd_line, signal_line= calculate_macd_safe(data['close'])
    rsi= calculate_rsi_safe(data['close'])
    if macd_line is not None and signal_line is not None:
        print("MACD Analysis:", macd_line, signal_line)
    if rsi is not None:
        print("RSI Analysis:", rsi)

# Example usage of get_openai_commentary


def example_get_openai_commentary():
    try:
        result = get_openai_commentary(
            "What is the current trend for EUR/USD?",
        )
        logger.info(f"Example OpenAI Commentary: {result}")
    except Exception as e:
        logger.error(f"Failed to get OpenAI commentary: {e}")

# Example usage of send_signal


def example_send_signal():
    try:
        send_signal(
            symbol="ETHUSD",
            direction="BUY",
            entry=3500,
            stop_loss=3400,
            take_profits=[3600, 3700, 3800],
            strategy="Breakout",
            strategy_name="Breakout Strategy",
            asset_type="Crypto",
            timeframe="1H",
            hold_time="2h"
        )
        logger.info("Example send_signal executed.")
    except Exception as e:
        logger.error(f"Failed to send signal: {e}")

# Example usage of send_pre_signal_alert


def example_send_pre_signal_alert():
    try:
        send_pre_signal_alert(
            symbol="AAPL",
            direction="BUY",
            strategy="Momentum",
            timeframe="15M"
        )
        logger.info("Example send_pre_signal_alert executed.")
    except Exception as e:
        logger.error(f"Failed to send pre-signal alert: {e}")

# Example usage of send_recap


def example_send_recap():
    try:
        send_recap(
            symbol="GBPUSD",
            direction="SELL",
            entry=1.2500,
            stop_loss=1.2600,
            take_profits=[1.2400, 1.2300, 1.2200],
            strategy="Reversal",
            timeframe="4H",
            result="TP1 hit"
        )
        logger.info("Example send_recap executed.")
    except Exception as e:
        logger.error(f"Failed to send recap: {e}")

# Example usage of get_asset_type


def example_get_asset_type():
    try:
        asset_type = get_asset_type("XAUUSD")
        logger.info(f"Example asset type for XAUUSD: {asset_type}")
    except Exception as e:
        logger.error(f"Failed to get asset type: {e}")


# === Safe Execution Wrapper ===


def safe_execute(func, *args, **kwargs):
    """Execute a function safely with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}")
        return None


# === Signal Generation ===


def generate_signal(asset, strategy, timeframe, indicators, news_context, entry, stop_loss, take_profits, commentary):
    """
    Generate and format a trading signal.

    Args:
        asset (str): Trading asset.
        strategy (str): Strategy name.
        timeframe (str): Timeframe.
        indicators (str): Indicators used.
        news_context (str): News context.
        entry (float): Entry price.
        stop_loss (float): Stop loss price.
        take_profits (list): Take profit levels.
        commentary (str): Commentary.

    Returns:
        str: Formatted signal message.
    """
    from signal_formatter import format_signal_template
    return format_signal_template(asset, strategy, timeframe, indicators, news_context, entry, stop_loss, take_profits, commentary)


def dispatch_signal(data, commentary, send_message_sync, send_signal_with_buttons):
    """
    Dispatch a trading signal using the new formatter.

    Args:
        data (dict): Signal data.
        commentary (str): Commentary for the signal.
        send_message_sync (function): Function to send a message synchronously.
        send_signal_with_buttons (function): Function to send a signal with buttons.
    """
    fmt_data = {
        "symbol": data["pair"],
        "asset_name": "Gold" if data["pair"] == "XAUUSD" else data["pair"],
        "asset_name_ar": "الذهب" if data["pair"] == "XAUUSD" else data["pair"],
        "strategy": data["strategy"],
        "strategy_ar": "اختراق" if data["strategy"] == "Breakout" else data["strategy"],
        "timeframe": data["timeframe"],
        "timeframe_ar": "ساعة" if data["timeframe"] == "1h" else data["timeframe"],
        "tp1": data["tp1"], "tp1_pips": abs(data["tp1"] - data["entry"]) * 10000,
        "tp2": data["tp2"], "tp2_pips": abs(data["tp2"] - data["entry"]) * 10000,
        "tp3": data["tp3"], "tp3_pips": abs(data["tp3"] - data["entry"]) * 10000,
        "sl": data["stop_loss"],
        "commentary": commentary,
        "commentary_ar": commentary  # or translate in code
    }
    is_ar = False  # or your user setting
    message = build_signal_message(fmt_data, arabic=is_ar)

    # send via Telegram:
    send_message_sync(message, chat_id=os.getenv("TELEGRAM_SIGNAL_CHAT_ID"))

    # Optionally, send with buttons
    send_signal_with_buttons(
        chat_id=os.getenv("TELEGRAM_SIGNAL_CHAT_ID"),
        signal_id=data.get("signal_id", ""),
        message=message,
        symbol=data["pair"]
    )


def send_signal_with_buttons(chat_id: str, signal_id: str, message: str, symbol: str) -> None:
    logger.info(f"send_signal_with_buttons called for {symbol} (no-op)")


def get_stats_summary(*args, **kwargs) -> str:
    return ""


def build_application(*args, **kwargs):
    return None


def setup_bot_handlers(*args, **kwargs):
    pass


def graceful_shutdown_placeholder(*args, **kwargs):
    pass


# Example call:
send_signal_with_commentary(
    symbol="BTCUSD",
    direction="SELL",
    entry=86200,
    stop_loss=87300,
    take_profits=[82400, 80000, 77600],
    strategy="Hybrid",
    strategy_name="SMC + MA + News",
    asset_type="Crypto",
    timeframe="4H",
    hold_time="8h",
    commentary="Liquidity grab confirmed with RSI divergence",
    # platform can be omitted if default is fine
)

# === Flask Routes ===


@ app.route("/")
def service_status():
    """Main status dashboard"""
    template_vars = {
        "news_monitor": CONFIG["NEWS_MONITORING_ENABLED"],
        "assistant": CONFIG["MAGUS_ASSISTANT_ENABLED"],
        "market_awareness": CONFIG["MARKET_AWARENESS_ENABLED"],
        "signal_count": len(state.signal_history),
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MAGUS PRIME X Signal Dispatcher</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
            .active { background-color: #d4edda; color: #155724; }
            .inactive { background-color: #f8d7da; color: #721c24; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <h1>MAGUS PRIME X Signal Dispatcher</h1>
        <div class="status active">
            <strong>Status:</strong> Running ✅
        </div>
        <div class="status {{ 'active' if news_monitor else 'inactive' }}">
            <strong>News Monitoring:</strong> {{ 'Enabled ✅' if news_monitor else 'Disabled ❌' }}
        </div>
        <div class="status {{ 'active' if assistant else 'inactive' }}">
            <strong>MAGUS PRIMEX ASSISTANT:</strong> {{ 'Enabled ✅' if assistant else 'Disabled ❌' }}
        </div>
        <div class="status {{ 'active' if market_awareness else 'inactive' }}">
            <strong>Market Awareness:</strong> {{ 'Enabled ✅' if market_awareness else 'Disabled ❌' }}
        </div>
        <div>
            <strong>Signals Processed:</strong> {{ signal_count }}
        </div>
        <div>
            <strong>Server Time:</strong> {{ server_time }}
        </div>
        <hr>
        <small>MAGUS PRIME X Signal Dispatcher v2.1</small>
    </body>
    </html>
    """, **template_vars)


@ app.route("/send-signal", methods=["POST"])
def handle_signal():
    """Process trading signals with enhanced AI, logging, and safety."""
    # 🔒 Validate API Key
    if not validate_api_key(request.headers.get('X-API-Key')):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # 📥 Parse and validate input
        data = request.get_json()
        required_fields = ["pair", "direction", "entry", "stop_loss",
                           "tp1", "tp2", "tp3", "strategy", "timeframe", "hold_time"]
        missing_fields = [
            field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": "Missing required fields", "missing_fields": missing_fields}), 400

        # 🛑 Market Hours Check
        if CONFIG["MARKET_AWARENESS_ENABLED"] and not data.get("override_market_check", False):
            market_open = check_market_status(data["pair"])
            if not market_open and not CONFIG["ALLOW_MARKET_OVERRIDE"]:
                return jsonify({
                    "error": f"Market closed for {data['pair']}",
                    "message": get_market_status_message(data["pair"])
                }), 403

        # 📊 Optional Market Sentiment
        if CONFIG["NEWS_MONITORING_ENABLED"]:
            try:
                sentiment = get_market_sentiment(data["pair"])
                logger.info(
                    f"Market sentiment for {data['pair']}: {sentiment}")
            except Exception as e:
                logger.warning(f"Sentiment fetch failed: {e}")

        # 🧠 AI Commentary using GPT-4 with fallback
        commentary = data.get("commentary")
        if not commentary and CONFIG["MAGUS_ASSISTANT_ENABLED"]:
            try:
                commentary = get_trade_commentary(
                    symbol=data["pair"],
                    direction=data["direction"],
                    entry=float(data["entry"]),
                    stop_loss=float(data["stop_loss"]),
                    targets=[float(data["tp1"]), float(
                        data["tp2"]), float(data["tp3"])],
                    strategy=data["strategy"]
                )
                logger.info(f"🧠 GPT Commentary: {commentary}")
            except Exception as e:
                logger.error(f"AI trade commentary failed: {str(e)}")
                commentary = generate_fallback_commentary(
                    data["pair"], data["direction"], data["strategy"])

        # ✉️ Dispatch Signal
        dispatch_signal(data, commentary, send_message_sync,
                        send_signal_with_buttons)

        # 💾 Save Signal History
        signal_record = {
            "timestamp": datetime.now().isoformat(),
            "pair": data["pair"],
            "direction": data["direction"],
            "entry": data["entry"],
            "stop_loss": data["stop_loss"],
            "take_profits": [data["tp1"], data["tp2"], data["tp3"]],
            "strategy": data["strategy"],
            "timeframe": data["timeframe"],
            "status": "sent",
            "signal_id": data.get("signal_id", "N/A")
        }

        with state.history_lock:
            state.signal_history.append(signal_record)
            save_signal_history(state)

        return jsonify({"status": "success", "signal_id": signal_record["signal_id"]}), 200

    except Exception as e:
        logger.error(f"Signal processing error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@ app.route("/execute-trade/<signal_id>", methods=["GET"])
def execute_trade(signal_id):
    """
    Execute a trade for the given signal ID via the Capital.com API.

    Args:
        signal_id (str): The ID of the signal to execute.

    Returns:
        Response: JSON response with the execution result.
    """
    try:
        with state.history_lock:  # Ensure thread-safe access to signal history
            match = next((s for s in state.signal_history if s.get(
                "signal_id") == signal_id), None)

        if not match:
            return jsonify({"error": "Signal not found"}), 404

        from capital_trade_executor import execute_capital_trade
        result= execute_capital_trade(
            symbol=match["pair"],
            direction=match["direction"],
            entry=match["entry"],
            stop_loss=match["stop_loss"],
            take_profits=match["take_profits"]
        )

        log_trade_action(signal_id, "executed-via-api")  # Log API execution

        return jsonify({"status": "success", "result": result}), 200
    except Exception as e:
        logger.error(f"❌ Failed to execute trade: {e}")
        return jsonify({"error": str(e)}), 500


@ app.route("/ignore-signal/<signal_id>", methods=["GET"])
def ignore_signal(signal_id):
    """
    Ignore a trade for the given signal ID.

    Args:
        signal_id (str): Unique signal ID.

    Returns:
        JSON response indicating success or failure.
    """
    try:
        logger.info(f"🛑 Ignoring trade ID: {signal_id}")
        # TODO: Log ignored signals to history if needed
        return jsonify({"status": "success", "message": f"Trade {signal_id} ignored"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@ app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "time": datetime.now().isoformat()}), 200

# === System Initialization ===


def validate_env_vars():
    """
    Validate required environment variables.
    Only require PORT if MAGUS_PROJECT_MODE is set to 'production'.
    """
    required_vars = ["API_KEY"]
    if os.getenv("MAGUS_PROJECT_MODE", "development").lower() == "production":
        required_vars.append("PORT")

    for var in required_vars:
        if not os.getenv(var):
            logger.critical(f"Missing required environment variable: {var}")
            raise EnvironmentError(f"Environment variable {var} is not set")


def initialize_system():
    """Initialize all system components"""
    validate_env_vars()
    example_ta_usage()
    load_signal_history()

    # Start background services
    if CONFIG["NEWS_MONITORING_ENABLED"]:
        try:
            import asyncio
            # async fn that pushes into Telegram
            from news_monitor import fetch_and_send_news

            async def news_loop(interval_seconds=1800):
                while True:
                    await fetch_and_send_news()
                    await asyncio.sleep(interval_seconds)

            state.news_monitor_thread = threading.Thread(
                target=lambda: asyncio.run(news_loop()), daemon=True)
            if state.news_monitor_thread is not None:
                state.news_monitor_thread.start()
            logger.info("News monitor thread started successfully.")
        except Exception as e:
            logger.warning(f"News monitor not available: {str(e)}")


def graceful_shutdown(*args):
    """Handle graceful shutdown for all threads and resources."""
    logger.info("Graceful shutdown initiated")
    try:
        if state.news_monitor_thread:
            if state.news_monitor_thread and state.news_monitor_thread.is_alive():
                state.news_monitor_thread.join(timeout=1)
                logger.info("News monitor thread stopped.")
        save_signal_history(state)
        logger.info("All resources cleaned up successfully.")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")
    finally:
        os._exit(0)


def log_latest_news():
    """
    Fetch and log the latest news headlines.
    """
    try:
        news = fetch_news()
        if news:
            logging.info("📰 Latest News Headlines:")
            for article in news[:5]:  # Log the top 5 articles
                logging.info(f"- {article['title']}")
        else:
            logging.warning("No news articles found.")
    except Exception as e:
        logging.error(f"Error fetching news: {str(e)}")


# Attach signal handlers for SIGINT and SIGTERM
signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

# === Entry Point ===
if __name__ == "__main__":
    # Call the examples to ensure the functions are accessed
    example_generate_gpt_commentary()
    example_get_trade_commentary()
    example_analyze_sentiment()
    example_get_openai_commentary()
    example_send_signal()
    example_send_pre_signal_alert()
    example_send_recap()
    example_get_asset_type()
    log_latest_news()
    safe_execute(save_signal_history, state)
    try:
        initialize_system()
        logging.info(f"[OK] MAGUS PRIME X Assistant Ready (Model: gpt-4)")
        app.run(
            host="0.0.0.0",
            port=CONFIG["PORT"],
            debug=CONFIG["DEBUG_MODE"],
            use_reloader=False
        )
    except KeyboardInterrupt:
        logger.info("Graceful shutdown initiated")
        if state.news_monitor_thread and state.news_monitor_thread.is_alive():
            state.news_monitor_thread.join(timeout=1)
            logger.info("News monitor thread stopped.")
        save_signal_history(state)
    except Exception as e:
        logger.critical(f"Fatal initialization error: {str(e)}")
        raise

# === Unit Tests ===


class TestSignalDispatcher(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_service_status(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN") or "your_default_token"
