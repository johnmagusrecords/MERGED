"""
Dashboard routes and handlers for MAGUS PRIME X web interface.

This module contains Flask routes and utility functions for the trading bot dashboard.
"""

import logging
import os

from flask import flash, jsonify, redirect, render_template, request

# Import constants and utils from the main application
from config import DASHBOARD_PASSWORD, STRATEGY_MODE
from utils.trade_utils import clear_trade_history, load_trade_history


def get_bot_status(bot):
    """Get the current status of the trading bot.

    Args:
        bot: TradingBot instance

    Returns:
        dict: Status information about the bot
    """
    return {
        "running": os.environ.get("BOT_PAUSED") != "1",
        "strategy": os.environ.get("STRATEGY_MODE", STRATEGY_MODE),
        "active_trades": len(bot.active_trades) if bot else 0,
        "last_trade": bot.last_trade_outcome if bot else None,
    }


def validate_webhook_request(data):
    """Validate webhook request data.

    Args:
        data: JSON data from webhook request

    Returns:
        tuple: (is_valid, error_message)
    """
    # Check API key
    if data.get("api_key") != DASHBOARD_PASSWORD:
        return False, "Invalid API key"

    # Check required fields
    if "symbol" not in data:
        return False, "Missing required parameter: symbol"

    if "action" not in data:
        return False, "Missing required parameter: action"

    # Validate action
    if data["action"].upper() not in ["BUY", "SELL"]:
        return False, f"Invalid action: {data['action']}"

    return True, ""


def create_trade_signal(data):
    """Create a trade signal from webhook data.

    Args:
        data: JSON data from webhook request

    Returns:
        TradeSignal: Trade signal object
    """
    from trading.models import TradeSignal

    return TradeSignal(
        symbol=data["symbol"],
        action=data["action"].upper(),
        confidence=float(data.get("confidence", 0.7)),
    )


def calculate_trade_statistics(trades):
    """Calculate trading statistics from trade history.

    Args:
        trades: List of trade records

    Returns:
        tuple: (win_rate, pnl) statistics
    """
    if not trades:
        return 0, 0

    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t.result == "WIN")
    losing_trades = sum(1 for t in trades if t.result == "LOSS")

    # Calculate win rate
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
    else:
        win_rate = 0

    # Calculate PnL (simplified)
    pnl = winning_trades * 1.5 - losing_trades  # Assuming average R:R of 1.5

    return round(win_rate, 1), round(pnl, 2)


def handle_dashboard_commands(form_data):
    """Process dashboard form commands.

    Args:
        form_data: Form data from the dashboard POST request

    Returns:
        bool: True if any command was processed
    """
    if form_data.get("password") != DASHBOARD_PASSWORD:
        return False

    commands_processed = False

    if form_data.get("reset"):
        clear_trade_history()
        commands_processed = True

    if form_data.get("pause"):
        os.environ["BOT_PAUSED"] = "1"
        commands_processed = True

    if form_data.get("resume"):
        os.environ["BOT_PAUSED"] = "0"
        commands_processed = True

    if form_data.get("strategy"):
        mode = form_data.get("strategy")
        os.environ["STRATEGY_MODE"] = mode
        commands_processed = True

    return commands_processed


def setup_dashboard_route(app, bot):
    """Set up the main dashboard route.

    Args:
        app: Flask application instance
        bot: TradingBot instance
    """

    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        """Render the trading bot dashboard with statistics and controls."""
        if request.method == "POST":
            if handle_dashboard_commands(request.form):
                flash("Command processed successfully")
            else:
                flash("Invalid password or command")

            return redirect("/dashboard")

        # Get trading history for display
        trades = load_trade_history()

        # Calculate statistics
        win_rate, pnl = calculate_trade_statistics(trades)

        # Get bot status information
        bot_status = get_bot_status(bot)

        return render_template(
            "dashboard.html",
            trades=trades,
            win_rate=win_rate,
            pnl=pnl,
            status=bot_status,
        )


def setup_root_route(app):
    """Set up the root route.

    Args:
        app: Flask application instance
    """

    @app.route("/", methods=["GET"])
    def root():
        """Redirect root to dashboard."""
        return redirect("/dashboard")


def setup_webhook_route(app, bot):
    """Set up the webhook route for external trade signals.

    Args:
        app: Flask application instance
        bot: TradingBot instance
    """

    @app.route("/webhook", methods=["POST"])
    def webhook():
        """Webhook for external trade signals."""
        try:
            data = request.json

            # Validate request
            is_valid, error_message = validate_webhook_request(data)
            if not is_valid:
                return jsonify({"status": "error", "message": error_message})

            if not bot:
                return jsonify({"status": "error", "message": "Bot not initialized"})

            # Create and process signal
            signal = create_trade_signal(data)
            bot._process_trade_signal(signal)

            return jsonify(
                {
                    "status": "success",
                    "message": f"{data['action'].upper()} signal for {data['symbol']} processed",
                }
            )

        except Exception as e:
            logging.error(f"Webhook error: {e}")
            return jsonify({"status": "error", "message": str(e)})


def init_dashboard_routes(app, bot):
    """Initialize dashboard routes with the Flask app and trading bot instance.

    Args:
        app: Flask application instance
        bot: TradingBot instance for controlling the bot
    """
    # Set up individual routes
    setup_dashboard_route(app, bot)
    setup_root_route(app)
    setup_webhook_route(app, bot)
