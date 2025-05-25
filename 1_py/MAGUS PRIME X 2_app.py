import hashlib
import hmac
import json
import logging
import os
import threading
import time
from functools import wraps

import pandas as pd
import requests
import websocket
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit

from ai_learning_system import AILearningSystem
from chart_analyzer import ChartAnalyzer
from chatgpt_analyst import ChatGPTAnalyst
from enhanced_trading_engine import EnhancedTradingEngine
from hedging_strategy import HedgingStrategy
from news_analyzer import NewsAnalyzer
from pine_script_integration import PineScriptIntegration
from signal_sender import SignalSender
from telegram_notifier import TelegramNotifier

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(
    __name__,
    template_folder=os.path.abspath("templates"),
    static_folder=os.path.abspath("static"),
    static_url_path="/static",
)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_KEY = os.getenv("CAPITAL_API_KEY")
API_SECRET = os.getenv("CAPITAL_API_PASSWORD")
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_IDENTIFIER")
CAPITAL_WS_URL = "wss://api-streaming.capital.com/api/v1/streaming"
CAPITAL_API_URL = os.getenv(
    "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
)

# Initialize components
trading_engine = EnhancedTradingEngine()
news_analyzer = NewsAnalyzer()
hedging_strategy = HedgingStrategy()
ai_learning_system = AILearningSystem()
chatgpt_analyst = ChatGPTAnalyst()
chart_analyzer = ChartAnalyzer()
telegram_notifier = TelegramNotifier()
pine_script_integration = PineScriptIntegration()
signal_sender = SignalSender()

# Global variables
ws_client = None
subscribed_symbols = set()
market_data = {}
active_positions = []
connection_retry_count = 0
MAX_RETRIES = 5
RETRY_DELAY = 5
bot_running = False
bot_start_time = None


def generate_signature(secret, message):
    return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def capital_api_request(method, endpoint, data=None):
    try:
        timestamp = str(int(time.time() * 1000))
        signature = generate_signature(
            API_SECRET,
            timestamp + method + endpoint + (json.dumps(data) if data else ""),
        )

        headers = {
            "X-CAP-API-KEY": API_KEY,
            "X-CAP-API-TIMESTAMP": timestamp,
            "X-CAP-API-SIGNATURE": signature,
            "Content-Type": "application/json",
        }

        url = f"{CAPITAL_API_URL}{endpoint}"
        response = requests.request(method, url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
        return {"error": str(e), "status": "failed"}


def get_account_info():
    """Fetch account information from Capital.com"""
    try:
        endpoint = "/accounts"
        response = capital_api_request("GET", endpoint)
        if "accounts" in response:
            account = response["accounts"][0]  # Get the first account
            return {
                "totalBalance": account.get("balance", 0),
                "availableMargin": account.get("available", 0),
                "usedMargin": account.get("margin", 0),
                "openPnL": account.get("unrealizedPL", 0),
                "dailyPnL": account.get("dayPL", 0),
                "positions": account.get("positions", []),
                "currency": account.get("currency", "USD"),
            }
        return {}
    except Exception as e:
        logging.error(f"Error fetching account info: {str(e)}")
        return {}


@app.route("/api/account")
def get_account_data():
    """API endpoint to get account information"""
    account_info = get_account_info()
    return jsonify(account_info)


def fetch_available_symbols():
    """Fetch all available trading symbols from Capital.com"""
    try:
        endpoint = "/markets"
        response = capital_api_request("GET", endpoint)
        symbols = []
        if "markets" in response:
            for market in response["markets"]:
                symbol_info = {
                    "symbol": market["symbol"],
                    "name": market["name"],
                    "type": market["type"],
                    "leverage": market.get("leverageRatio", 1),
                    "minSize": market.get("minDealSize", 0.01),
                    "maxSize": market.get("maxDealSize", 1000),
                    "precision": market.get("decimalPlaces", 2),
                }
                symbols.append(symbol_info)
        return symbols
    except Exception as e:
        logging.error(f"Error fetching symbols: {str(e)}")
        return []


@app.route("/api/symbols")
def get_symbols():
    """API endpoint to get available symbols"""
    symbols = fetch_available_symbols()
    return jsonify(symbols)


@app.route("/api/trade", methods=["POST"])
def execute_trade():
    """Execute a trade with Capital.com"""
    try:
        data = request.json
        trade_params = {
            "symbol": data["symbol"],
            "direction": data["direction"],
            "size": data["size"],
            "stopLoss": data.get("stopLoss"),
            "takeProfit": data.get("takeProfit"),
            "leverage": data.get("leverage", 1),
        }

        endpoint = "/positions"
        response = capital_api_request("POST", endpoint, trade_params)

        # Send signal to Telegram for manual trades
        if response and "dealId" in response:
            # Trade was successful, send signal
            send_trading_signal(
                symbol=data["symbol"],
                direction=data["direction"],
                entry=data.get("entry", 0),
                stop_loss=data.get("stopLoss", 0),
                take_profits=[
                    data.get("takeProfit", 0),
                    data.get("takeProfit2", 0) if "takeProfit2" in data else 0,
                    data.get("takeProfit3", 0) if "takeProfit3" in data else 0,
                ],
                timeframe=data.get("timeframe", "30m"),
                signal_type="Manual Trade",
            )

        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/position/<position_id>", methods=["PUT"])
def modify_position(position_id):
    """Modify an existing position (stop loss, take profit)"""
    try:
        data = request.json
        modify_params = {
            "stopLoss": data.get("stopLoss"),
            "takeProfit": data.get("takeProfit"),
        }

        endpoint = f"/positions/{position_id}"
        response = capital_api_request("PUT", endpoint, modify_params)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/position/<position_id>", methods=["DELETE"])
def close_position(position_id):
    """Close a position"""
    try:
        endpoint = f"/positions/{position_id}"
        response = capital_api_request("DELETE", endpoint)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


def send_trading_signal(
    symbol,
    direction,
    entry,
    stop_loss,
    take_profits,
    timeframe="30m",
    signal_type="Breakout",
):
    """
    Send a trading signal to Telegram through the Signal Sender API.

    Args:
        symbol (str): The trading symbol (e.g., "GOLD", "BTCUSD")
        direction (str): "BUY" or "SELL"
        entry (float): Entry price
        stop_loss (float): Stop loss price
        take_profits (list): List of take profit targets [tp1, tp2, tp3]
        timeframe (str): Timeframe of the signal (e.g., "15m", "1h", "4h")
        signal_type (str): Type of signal (e.g., "Breakout", "Reversal")

    Returns:
        bool: True if signal was sent successfully, False otherwise
    """
    try:
        logger.info(f"Sending {direction} signal for {symbol} at {entry}")

        # Ensure we have at least one take profit level
        if not take_profits or len(take_profits) == 0:
            logger.error("No take profit levels provided")
            return False

        # Get up to 3 take profit levels
        tp1 = take_profits[0]
        tp2 = take_profits[1] if len(take_profits) > 1 else tp1 * 1.5
        tp3 = take_profits[2] if len(take_profits) > 2 else tp1 * 2

        # Add direction to signal type
        signal_type_with_direction = f"{direction} {signal_type}"

        # Send the signal
        response = signal_sender.send_signal(
            pair=symbol,
            entry=entry,
            stop_loss=stop_loss,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            timeframe=timeframe,
            mode="SAFE_RECOVERY",
            signal_type=signal_type_with_direction,
        )

        if "error" in response:
            logger.error(f"Failed to send signal: {response.get('error')}")
            return False

        logger.info(f"Signal sent successfully for {symbol}")
        return True

    except Exception as e:
        logger.error(f"Error sending trading signal: {str(e)}")
        return False


def start_websocket():
    """Start the WebSocket connection to Capital.com"""
    global ws_client, bot_running

    def on_message(ws, message):
        try:
            data = json.loads(message)
            if "marketData" in data:
                symbol = data["marketData"]["symbol"]
                timeframe = data["marketData"]["timeframe"]

                if symbol not in market_data:
                    market_data[symbol] = {}
                if timeframe not in market_data[symbol]:
                    market_data[symbol][timeframe] = pd.DataFrame()

                # Update market data
                new_data = pd.DataFrame([data["marketData"]])
                market_data[symbol][timeframe] = pd.concat(
                    [market_data[symbol][timeframe], new_data]
                )

                # Update indicators
                if bot_running:
                    trading_engine.market_data = market_data
                    trading_engine.calculate_indicators(
                        market_data[symbol][timeframe], timeframe
                    )

                    # Check for trading signals
                    signal, params = trading_engine.analyze_market(symbol)

                    if signal != "HOLD":
                        # Check news before trading
                        should_pause, reason = news_analyzer.should_pause_trading(
                            symbol
                        )
                        if should_pause:
                            logging.info(f"Trading paused for {symbol}: {reason}")
                            return

                        # Execute trade if conditions are met
                        position = execute_trade(symbol, signal, params)

                        # Send signal to Telegram if a trade will be executed
                        if signal in ["BUY", "SELL"] and params:
                            send_trading_signal(
                                symbol=symbol,
                                direction=signal,
                                entry=params.get("entry", 0),
                                stop_loss=params.get("stop_loss", 0),
                                take_profits=[
                                    params.get("tp1", 0),
                                    params.get("tp2", 0),
                                    params.get("tp3", 0),
                                ],
                                timeframe=timeframe,
                                signal_type=params.get("signal_type", "Breakout"),
                            )

                        # Check for hedging opportunities
                        if position:
                            should_hedge, reason, ratio = (
                                hedging_strategy.check_hedge_conditions(
                                    position, market_data, trading_engine.indicators
                                )
                            )
                            if should_hedge:
                                hedge_position = hedging_strategy.create_hedge(
                                    position, ratio, reason
                                )
                                if hedge_position:
                                    execute_trade(
                                        symbol, "HEDGE", {"position": hedge_position}
                                    )

                    # Manage existing positions
                    trading_engine.manage_positions()
                    hedging_strategy.manage_hedged_positions(
                        market_data, trading_engine.indicators
                    )

                # Emit updated data to clients
                socketio.emit(
                    "market_update", {"symbol": symbol, "data": data["marketData"]}
                )

        except Exception as e:
            logging.error(f"Error processing WebSocket message: {str(e)}")

    def on_error(ws, error):
        logging.error(f"WebSocket error: {str(error)}")

    def on_close(ws, close_status_code, close_msg):
        logging.info(f"WebSocket connection closed: {close_status_code} - {close_msg}")
        reconnect_websocket()

    def on_open(ws):
        logging.info("WebSocket connection established")
        # Authenticate
        auth_message = {
            "action": "auth",
            "token": API_KEY,
            "identifier": CAPITAL_IDENTIFIER,
        }
        ws.send(json.dumps(auth_message))
        # Subscribe to initial symbols
        subscribe_symbols(["BTCUSD", "EURUSD", "US100"])

    # Create WebSocket connection
    ws_client = websocket.WebSocketApp(
        CAPITAL_WS_URL,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open,
        header={"Content-Type": "application/json", "X-CAP-API-KEY": API_KEY},
    )

    ws_thread = threading.Thread(target=ws_client.run_forever)
    ws_thread.daemon = True
    ws_thread.start()


def reconnect_websocket():
    """Attempt to reconnect the WebSocket"""
    global connection_retry_count

    if connection_retry_count < MAX_RETRIES:
        time.sleep(RETRY_DELAY * (2**connection_retry_count))
        connection_retry_count += 1
        start_websocket()
    else:
        logging.error("Max reconnection attempts reached")
        socketio.emit("connection_status", {"status": "disconnected"})


def subscribe_symbols(symbols):
    """Subscribe to market data for given symbols"""
    if not ws_client:
        return

    for symbol in symbols:
        message = {
            "action": "subscribe",
            "symbols": [symbol],
            "granularity": ["5m", "1h", "4h"],  # Multiple timeframes
        }
        ws_client.send(json.dumps(message))
        subscribed_symbols.add(symbol)


# WebSocket event handlers
@socketio.on("connect")
def handle_connect():
    emit("connection_status", {"status": "connected"})
    # Send initial data
    emit("market_data", {"data": market_data})
    emit("positions_update", {"positions": active_positions})


@socketio.on("subscribe")
def handle_subscribe(data):
    if "symbols" in data:
        subscribe_symbols(data["symbols"])


# API key authentication
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if api_key and api_key == API_KEY:
            return f(*args, **kwargs)
        return jsonify({"error": "Invalid API key"}), 401

    return decorated_function


@app.route("/")
def index():
    """Serve the main page"""
    return render_template("dashboard.html")


@app.route("/static/<path:path>")
def serve_static(path):
    """Serve static files"""
    return send_from_directory("static", path)


if __name__ == "__main__":
    start_websocket()
    socketio.run(app, debug=True, host="0.0.0.0", port=8000)
