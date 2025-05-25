import json
import logging
import os
import threading
import time
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request

from commentary_generator import generate_fallback_commentary
from enhanced_signal_sender import send_pre_signal_alert, send_recap, send_signal

# Import market status checker
from market_status_checker import (
    check_market_status,
    get_asset_type,
    get_market_status_message,
)
from send_signal_helper import should_trigger_recovery

# Try to import optional components with graceful fallback
try:
    from news_monitor import start_news_monitor, stop_news_monitor_thread

    NEWS_MONITOR_AVAILABLE = True
except ImportError:
    NEWS_MONITOR_AVAILABLE = False
    logging.warning(
        "News monitor not available. Install with pip install feedparser newsapi-python"
    )

try:
    from openai_assistant import get_trade_commentary

    ASSISTANT_AVAILABLE = True
except ImportError:
    ASSISTANT_AVAILABLE = False
    logging.warning("MAGUS PRIMEX ASSISTANT integration not available")

# Load environment variables
load_dotenv()

# === Configuration ===
MAGUS_ASSISTANT_ENABLED = (
    os.getenv("MAGUS_ASSISTANT_ENABLED", "false").lower() == "true"
)
MARKET_AWARENESS_ENABLED = (
    os.getenv("ENABLE_MARKET_AWARENESS", "true").lower() == "true"
)
NEWS_MONITORING_ENABLED = os.getenv("ENABLE_NEWS_MONITORING", "true").lower() == "true"
PORT = int(os.getenv("PORT", 8080))
API_KEY = os.getenv("API_KEY", "magus_prime_secret_key")
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
ALLOW_MARKET_OVERRIDE = os.getenv("ALLOW_MARKET_OVERRIDE", "false").lower() == "true"

# === Setup Flask App ===
app = Flask(__name__)
logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Storage for signal history
signal_history = []
signal_history_file = "signal_history.json"


# === Helper Functions ===
def validate_api_key(request_api_key):
    """Validate the provided API key against the configured key"""
    if not API_KEY:
        logger.warning("No API key configured. All requests will be accepted.")
        return True

    return request_api_key == API_KEY


def save_signal_history():
    """Save signal history to a JSON file"""
    try:
        with open(signal_history_file, "w") as f:
            json.dump(signal_history, f, indent=2, default=str)
    except Exception as e:
        logger.error(f"Failed to save signal history: {e}")


def load_signal_history():
    """Load signal history from JSON file if it exists"""
    global signal_history
    try:
        if os.path.exists(signal_history_file):
            with open(signal_history_file, "r") as f:
                signal_history = json.load(f)
                logger.info(f"Loaded {len(signal_history)} signals from history file")
    except Exception as e:
        logger.error(f"Failed to load signal history: {e}")
        signal_history = []


def send_signal_to_telegram(signal_data, tag=""):
    """Send a formatted signal to Telegram"""
    try:
        # Import the correct function from enhanced_signal_sender
        from enhanced_signal_sender import send_telegram_message
        
        # Format signal data into a message
        message = f"{tag} SIGNAL\n\n"
        message += f"Pair: {signal_data.get('pair')}\n"
        message += f"Direction: {signal_data.get('direction')}\n"
        message += f"Entry: {signal_data.get('entry')}\n"
        message += f"SL: {signal_data.get('stop_loss')}\n"

        # Add TPs
        take_profits = signal_data.get("take_profits", [])
        if take_profits and len(take_profits) > 0:
            message += f"TP1: {take_profits[0]}\n"
        if take_profits and len(take_profits) > 1:
            message += f"TP2: {take_profits[1]}\n"
        if take_profits and len(take_profits) > 2:
            message += f"TP3: {take_profits[2]}\n"

        message += f"\nStrategy: {signal_data.get('strategy', 'Recovery')}"

        if signal_data.get("commentary"):
            message += f"\n\n{signal_data.get('commentary')}"

        # Send using the correct function
        return send_telegram_message(message, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error sending recovery signal to Telegram: {e}")
        return None


def generate_recovery_signal(original_trade_data):
    """
    Generate a recovery signal based on the original trade data.
    This creates a counter-trade when a stop loss has been hit.

    Args:
        original_trade_data: Data from the original trade that hit SL

    Returns:
        dict: Recovery signal data or None if not possible
    """
    try:
        # Extract key information from original trade
        pair = original_trade_data.get("pair")
        original_direction = original_trade_data.get("direction", "").upper()
        original_entry = float(original_trade_data.get("entry", 0))
        original_sl = float(original_trade_data.get("stop_loss", 0))

        # Validate required data
        if not pair or not original_direction or not original_entry or not original_sl:
            logging.error("Missing required data for recovery signal generation")
            return None

        # Invert the direction for recovery
        new_direction = "SELL" if original_direction == "BUY" else "BUY"

        # Calculate the risk distance from the original trade
        risk_distance = abs(original_entry - original_sl)

        # Use the original SL as entry for recovery trade
        new_entry = original_sl

        # Set new SL using similar risk distance but in opposite direction
        new_sl = (
            new_entry - risk_distance
            if new_direction == "BUY"
            else new_entry + risk_distance
        )

        # Set TP levels at 1.5R, 2R, and 3R
        if new_direction == "BUY":
            new_tp1 = new_entry + (risk_distance * 1.5)
            new_tp2 = new_entry + (risk_distance * 2.0)
            new_tp3 = new_entry + (risk_distance * 3.0)
        else:
            new_tp1 = new_entry - (risk_distance * 1.5)
            new_tp2 = new_entry - (risk_distance * 2.0)
            new_tp3 = new_entry - (risk_distance * 3.0)

        # Create recovery signal with original metadata
        recovery_signal = {
            "pair": pair,
            "direction": new_direction,
            "entry": new_entry,
            "stop_loss": new_sl,
            "take_profits": [new_tp1, new_tp2, new_tp3],
            "timeframe": original_trade_data.get("timeframe", "30m"),
            "strategy": f"Recovery ({original_direction} SL)",
            "commentary": f"Recovery signal after {original_direction} hit SL at {original_sl}. Looking for reversal momentum in {new_direction} direction.",
        }

        return recovery_signal

    except Exception as e:
        logging.error(f"Error generating recovery signal: {e}")
        return None


# === Flask Routes ===
@app.route("/")
def home():
    """Home route that shows a simple status page"""
    return render_template_string(
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MAGUS PRIME X Signal Dispatcher</title>
        <style>
            body {
                     font-family: Arial,
                     sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }            .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
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
        <small>MAGUS PRIME X Signal Dispatcher v2.0</small>
    </body>
    </html>
    """,
        news_monitor=NEWS_MONITORING_ENABLED,
        assistant=MAGUS_ASSISTANT_ENABLED,
        market_awareness=MARKET_AWARENESS_ENABLED,
        signal_count=len(signal_history),
        server_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/status")
def status():
    """JSON status endpoint for monitoring"""
    return jsonify(
        {
            "status": "running",
            "news_monitor": NEWS_MONITORING_ENABLED,
            "assistant": MAGUS_ASSISTANT_ENABLED,
            "market_awareness": MARKET_AWARENESS_ENABLED,
            "signals_processed": len(signal_history),
            "server_time": datetime.now().isoformat(),
            "version": "2.0",
        }
    )


@app.route("/signals", methods=["GET"])
def get_signals():
    """Return signal history"""
    # Check API key in headers or query params
    api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
    if not validate_api_key(api_key):
        return jsonify({"error": "Invalid API key"}), 401

    limit = request.args.get("limit", default=10, type=int)
    return jsonify(signal_history[-limit:])


@app.route("/send-signal", methods=["POST"])
def handle_send_signal():
    """Handle incoming signal requests"""
    # Check API key
    api_key = request.headers.get("X-API-Key")
    if not validate_api_key(api_key):
        return jsonify({"error": "Invalid API key"}), 401

    # Parse request data
    try:
        data = request.get_json()
    except Exception as e:
        logger.error(f"Invalid JSON: {e}")
        return jsonify({"error": "Invalid JSON data"}), 400

    # Validate required fields
    required = [
        "pair",
        "direction",
        "entry",
        "stop_loss",
        "tp1",
        "tp2",
        "tp3",
        "strategy",
        "timeframe",
        "hold_time",
    ]
    if not all(field in data for field in required):
        logger.warning(f"Missing required fields in request: {data}")
        return jsonify({"error": "Missing required signal fields"}), 400

    # Extract signal parameters
    pair = data["pair"]
    direction = data["direction"]
    entry = data["entry"]
    stop_loss = data["stop_loss"]
    take_profits = [data["tp1"], data["tp2"], data["tp3"]]
    strategy = data["strategy"]
    timeframe = data["timeframe"]
    hold_time = data["hold_time"]
    commentary = data.get("commentary")
    override_market_check = data.get("override_market_check", False)

    # Check market status if market awareness is enabled
    if MARKET_AWARENESS_ENABLED and not override_market_check:
        market_open = check_market_status(pair)
        if not market_open and not ALLOW_MARKET_OVERRIDE:
            market_message = get_market_status_message(pair)
            logger.warning(
                f"Market closed for {pair}. Signal not sent. {market_message}"
            )
            return (
                jsonify(
                    {
                        "error": f"Market closed for {pair}. Signal not sent.",
                        "message": market_message,
                    }
                ),
                403,
            )
        elif not market_open and ALLOW_MARKET_OVERRIDE:
            logger.warning(
                f"Market appears closed for {pair}, but override is enabled. Sending signal anyway."
            )

    # Get asset type for the signal
    try:
        asset_type = get_asset_type(pair)
        logger.info(f"Asset type for {pair}: {asset_type}")
    except Exception as e:
        logger.error(f"Error getting asset type: {e}")
        asset_type = "Unknown"

    # Send pre-signal alert
    try:
        pre_signal_result = send_pre_signal_alert(pair, direction, strategy, timeframe)
        logger.info(f"Pre-signal alert sent: {pre_signal_result}")
    except Exception as e:
        logger.error(f"Error sending pre-signal alert: {e}")

    # Generate commentary if not provided and AI is disabled
    if not commentary:
        if MAGUS_ASSISTANT_ENABLED and ASSISTANT_AVAILABLE:
            try:
                # Get AI-generated commentary
                logger.info(f"Generating AI commentary for {pair} {direction}")
                commentary = get_trade_commentary(
                    symbol=pair,
                    direction=direction,
                    entry=entry,
                    stop_loss=stop_loss,
                    targets=take_profits,
                    strategy=strategy,
                )
                logger.info("AI commentary generated successfully")
            except Exception as e:
                logger.error(f"Error generating AI commentary: {e}")
                commentary = generate_fallback_commentary(pair, direction, strategy)
        else:
            # Use fallback commentary
            commentary = generate_fallback_commentary(pair, direction, strategy)
            logger.info(f"Using fallback commentary for {pair}")

    # Send the actual signal
    try:
        send_signal(
            pair=pair,
            direction=direction,
            entry=entry,
            stop_loss=stop_loss,
            take_profits=take_profits,
            asset_type=asset_type,
            strategy=strategy,
            timeframe=timeframe,
            hold_time=hold_time,
            commentary=commentary,
        )

        # Record signal in history
        signal_record = {
            "timestamp": datetime.now().isoformat(),
            "pair": pair,
            "direction": direction,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profits": take_profits,
            "strategy": strategy,
            "timeframe": timeframe,
            "asset_type": asset_type,
            "status": "sent",
        }
        signal_history.append(signal_record)
        save_signal_history()

        logger.info(f"Signal sent successfully for {pair}")
        return (
            jsonify(
                {
                    "status": "signal_sent",
                    "signal_id": signal_record.get("id", "unknown"),
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Error sending signal: {e}")
        return jsonify({"error": f"Error sending signal: {str(e)}"}), 500


@app.route("/send-recap", methods=["POST"])
def handle_send_recap():
    """Handle recap requests"""
    # Check API key
    api_key = request.headers.get("X-API-Key")
    if not validate_api_key(api_key):
        return jsonify({"error": "Invalid API key"}), 401

    # Parse request data
    try:
        data = request.get_json()
    except Exception as e:
        logger.error(f"Invalid JSON: {e}")
        return jsonify({"error": "Invalid JSON data"}), 400

    # Validate required fields
    required = ["pair", "result", "exit_price"]
    if not all(field in data for field in required):
        logger.warning(f"Missing required fields in recap request: {data}")
        return jsonify({"error": "Missing required recap fields"}), 400

    # Extract recap parameters
    pair = data["pair"]
    result = data["result"]  # tp1, tp2, tp3, sl, closed
    exit_price = data["exit_price"]
    notes = data.get("notes")
    signal_id = data.get("signal_id")

    # Send the recap
    try:
        send_recap(pair, result, exit_price, notes, signal_id)

        # Update signal history
        for signal in signal_history:
            if signal.get("pair") == pair and signal.get("status") == "sent":
                signal["status"] = "completed"
                signal["result"] = result
                signal["exit_price"] = exit_price
                signal["recap_time"] = datetime.now().isoformat()
        save_signal_history()

        logger.info(f"Recap sent for {pair}, result: {result}")

        # After processing the recap, check if we should trigger recovery
        if should_trigger_recovery(result):
            logging.warning("📉 SL hit - triggering recovery mode...")

            # Get original trade data from the request or result
            original_trade_data = request.json.get("signal_data", {})

            # Generate recovery signal
            recovery_signal = generate_recovery_signal(original_trade_data)

            # Send recovery signal
            if recovery_signal:
                send_signal_to_telegram(recovery_signal, tag="🧪 Recovery")

        return jsonify({"status": "recap_sent"}), 200
    except Exception as e:
        logger.error(f"Error sending recap: {e}")
        return jsonify({"error": f"Error sending recap: {str(e)}"}), 500


@app.route("/market-status/<symbol>", methods=["GET"])
def get_market_status(symbol):
    """Check market status for a specific symbol"""
    try:
        market_open = check_market_status(symbol)
        market_message = (
            get_market_status_message(symbol) if not market_open else "Market is open"
        )
        asset_type = get_asset_type(symbol)

        return jsonify(
            {
                "symbol": symbol,
                "is_open": market_open,
                "status_message": market_message,
                "asset_type": asset_type,
            }
        )
    except Exception as e:
        logger.error(f"Error checking market status: {e}")
        return jsonify({"error": f"Error checking market status: {str(e)}"}), 500


@app.route("/assistant", methods=["POST"])
def assistant_respond():
    try:
        data = request.json
        message = data.get("message", "")
        TELEGRAM_SIGNAL_CHAT_ID = os.getenv("TELEGRAM_SIGNAL_CHAT_ID", "default_chat_id")
        chat_id = data.get("chat_id", TELEGRAM_SIGNAL_CHAT_ID)

        if not message:
            return jsonify({"error": "Empty message"}), 400

        # Use GPT to generate assistant response
        from gpt_commentary import generate_commentary_from_text

        response = generate_commentary_from_text(message)

        if response:
            # Replace this with the correct function
            from enhanced_signal_sender import send_telegram_message
            send_telegram_message(response)
            return jsonify({"success": True, "response": response}), 200
        else:
            return jsonify({"error": "No response generated"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/test", methods=["GET"])
def test_connection():
    return "MAGUS PRIME X Assistant is live!", 200


# === Background Tasks ===
news_monitor_thread = None


def start_background_tasks():
    """Start all background services"""
    global news_monitor_thread
    logger.info(f"Starting MAGUS PRIME X Signal Dispatcher on port {PORT}")

    # Load signal history
    load_signal_history()

    # Start News Monitor if enabled
    if NEWS_MONITORING_ENABLED and NEWS_MONITOR_AVAILABLE:
        try:
            logger.info("Starting news monitoring thread")
            news_monitor_thread = start_news_monitor()
            logger.info("News monitoring thread started successfully")
        except Exception as e:
            logger.error(f"Failed to start news monitor: {e}")
    else:
        if not NEWS_MONITOR_AVAILABLE:
            logger.warning("News monitoring not available - module not found")
        else:
            logger.info("News monitoring disabled by configuration")

    # Start signal history cleanup thread
    def cleanup_signal_history():
        """Periodically cleanup old signal history"""
        global signal_history
        while True:
            try:
                # Keep only the latest 1000 signals
                if len(signal_history) > 1000:
                    signal_history = signal_history[-1000:]
                    save_signal_history()
                    logger.info("Signal history cleaned up")
            except Exception as e:
                logger.error(f"Error in signal history cleanup: {e}")

            # Sleep for 6 hours
            time.sleep(6 * 60 * 60)

    threading.Thread(target=cleanup_signal_history, daemon=True).start()
    logger.info("Signal history cleanup thread started")

    # Log assistant status
    if MAGUS_ASSISTANT_ENABLED and ASSISTANT_AVAILABLE:
        logger.info("MAGUS PRIMEX ASSISTANT integration enabled ✅")
    elif MAGUS_ASSISTANT_ENABLED and not ASSISTANT_AVAILABLE:
        logger.warning("MAGUS PRIMEX ASSISTANT integration requested but not available")
    else:
        logger.info("MAGUS PRIMEX ASSISTANT integration not enabled")


# === Shutdown Handler ===
def shutdown_handler():
    """Handle graceful shutdown"""
    logger.info("Shutting down MAGUS PRIME X Signal Dispatcher")

    # Stop news monitor
    if news_monitor_thread:
        try:
            stop_news_monitor_thread()
            logger.info("News monitor stopped")
        except Exception as e:
            logger.error(f"Error stopping news monitor: {e}")

    # Save signal history
    save_signal_history()
    logger.info("Signal history saved")


# === Start Flask App ===
if __name__ == "__main__":
    try:
        start_background_tasks()
        app.run(host="0.0.0.0", port=PORT, debug=DEBUG_MODE)
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
        shutdown_handler()
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        shutdown_handler()
