"""
Dashboard module for MAGUS PRIME X trading bot.

This module provides a web-based dashboard for monitoring and controlling the trading bot.
"""

import logging
import os
import threading
from typing import Any, Dict, List

import pandas as pd
from flask import Flask, jsonify, redirect, render_template_string, request

from dashboard.trade_history import TradeHistoryEntry


class Dashboard:
    """Web dashboard for the trading bot."""

    def __init__(self, bot_instance=None, dashboard_password: str = "magus"):
        """Initialize the dashboard.

        Args:
            bot_instance: Instance of the TradingBot
            dashboard_password: Password for dashboard access
        """
        self.app = Flask(__name__)
        self.bot = bot_instance
        self.password = dashboard_password
        self.trade_history_file = "trade_history.csv"
        self.equity_curve_file = "equity_curve.csv"

        # Set up routes
        self._setup_routes()

        # Dashboard state
        self.is_running = False
        self.server_thread = None

    def _setup_routes(self):
        """Set up Flask routes for the dashboard."""

        # Set up basic routes
        self.app.route("/")(self._home_route)
        self.app.route("/dashboard", methods=["GET", "POST"])(self._dashboard_route)
        self.app.route("/control", methods=["POST"])(self._control_route)
        self.app.route("/api/status", methods=["GET"])(self._api_status_route)

    def _home_route(self):
        """Home page route - redirects to dashboard."""
        return redirect("/dashboard")

    def _dashboard_route(self):
        """Main dashboard route."""
        # Check password
        if request.method == "POST":
            if not self._validate_password(request.form.get("password")):
                return self._render_invalid_password_page()

        # Load data
        trade_history = self.load_trade_history()
        bot_status = self._get_bot_status()

        # Render dashboard
        return self._render_dashboard_template(
            bot_status=bot_status["status"],
            active_trades=bot_status["active_trades"],
            daily_pl=bot_status["daily_pl"],
            trade_history=trade_history,
        )

    def _control_route(self):
        """Control route for bot actions."""
        action = request.form.get("action")

        if not self.bot:
            return jsonify({"error": "Bot not initialized"}), 500

        if action == "start":
            self._handle_start_bot()
        elif action == "stop":
            self._handle_stop_bot()
        elif action == "close_all":
            self._handle_close_all_trades()

        return redirect("/dashboard")

    def _api_status_route(self):
        """API endpoint for bot status."""
        if not self.bot:
            return jsonify({"error": "Bot not initialized"}), 500

        return jsonify(self._get_bot_status())

    def _handle_start_bot(self):
        """Handle start bot action."""
        if not getattr(self.bot, "is_running", False):
            # Start the bot in a separate thread
            threading.Thread(target=self.bot.run).start()

    def _handle_stop_bot(self):
        """Handle stop bot action."""
        if getattr(self.bot, "is_running", False):
            self.bot.stop()

    def _handle_close_all_trades(self):
        """Handle close all trades action."""
        if hasattr(self.bot, "close_all_trades"):
            self.bot.close_all_trades()

    def _validate_password(self, password):
        """Validate dashboard password.

        Args:
            password: Password to validate

        Returns:
            bool: True if password is valid
        """
        return password == self.password

    def _render_invalid_password_page(self):
        """Render invalid password page.

        Returns:
            str: Rendered HTML
        """
        return render_template_string(
            """
        <h1>Invalid password</h1>
        <a href="/dashboard">Try again</a>
        """
        )

    def _get_bot_status(self):
        """Get current bot status.

        Returns:
            dict: Bot status information
        """
        return {
            "status": (
                "Running"
                if self.bot and getattr(self.bot, "is_running", False)
                else "Stopped"
            ),
            "active_trades": (
                len(getattr(self.bot, "active_trades", [])) if self.bot else 0
            ),
            "daily_pl": getattr(self.bot, "daily_profit_loss", 0) if self.bot else 0,
        }

    def _render_dashboard_template(
        self, bot_status, active_trades, daily_pl, trade_history
    ):
        """Render the main dashboard template.

        Args:
            bot_status: Current bot status
            active_trades: Number of active trades
            daily_pl: Daily profit/loss
            trade_history: Trade history data

        Returns:
            str: Rendered HTML template
        """
        return render_template_string(
            self._get_dashboard_html_template(),
            bot_status=bot_status,
            active_trades=active_trades,
            daily_pl=daily_pl,
            trade_history=trade_history,
        )

    def _get_dashboard_html_template(self):
        """Get the HTML template for the dashboard.

        Returns:
            str: HTML template
        """
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MAGUS PRIME X Dashboard</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                tr:hover { background-color: #f5f5f5; }
                .card {
                          box-shadow: 0 4px 8px 0 rgba(
                                                        0,
                          0,
                          0,
                          0.2); padding: 16px; margin-bottom: 20px; }                .success { color: green; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <h1>MAGUS PRIME X Trading Dashboard</h1>
            
            <div class="card">
                <h2>Bot Status</h2>
                <p>Status: {{ bot_status }}</p>
                <p>Active Trades: {{ active_trades }}</p>
                <p>Daily P/L: {{ daily_pl }}</p>
                
                <form method="POST" action="/control">
                    <button type="submit" name="action" value="start">Start Bot</button>
                    <button type="submit" name="action" value="stop">Stop Bot</button>
                    <button type="submit" name="action" value="close_all">Close All Trades</button>
                </form>
            </div>
            
            <div class="card">
                <h2>Trade History</h2>
                <table>
                    <tr>
                        <th>Time</th>
                        <th>Symbol</th>
                        <th>Action</th>
                        <th>TP</th>
                        <th>SL</th>
                        <th>Result</th>
                    </tr>
                    {% for trade in trade_history %}
                    <tr>
                        <td>{{ trade.Time }}</td>
                        <td>{{ trade.Symbol }}</td>
                        <td>{{ trade.Action }}</td>
                        <td>{{ trade.TP }}</td>
                        <td>{{ trade.SL }}</td>
                        <td class=" "
{{ 'success' if trade.Result == 'WIN' else 'error' if trade.Result == 'LOSS' else '' }}">
                            {{ trade.Result }}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </body>
        </html>
        """

    def load_trade_history(self) -> List[Dict[str, Any]]:
        """Load trade history from CSV file.

        Returns:
            list: List of trade records
        """
        if os.path.exists(self.trade_history_file):
            try:
                return (
                    pd.read_csv(self.trade_history_file)
                    .tail(100)
                    .to_dict(orient="records")
                )
            except Exception as e:
                logging.error(f"Failed to load trade history: {e}")
                return []
        return []

    def clear_trade_history(self):
        """Clear the trade history file."""
        if os.path.exists(self.trade_history_file):
            os.remove(self.trade_history_file)
            logging.info("Trade history cleared.")

    def save_trade_to_history(self, entry: TradeHistoryEntry):
        """Save a trade record to history.

        Args:
            entry: Trade history entry
        """
        df = pd.DataFrame(
            [
                [
                    entry.timestamp,
                    entry.symbol,
                    entry.action,
                    entry.take_profit,
                    entry.stop_loss,
                    entry.result,
                ]
            ],
            columns=["Time", "Symbol", "Action", "TP", "SL", "Result"],
        )

        df.to_csv(
            self.trade_history_file,
            mode="a",
            header=not os.path.exists(self.trade_history_file),
            index=False,
        )

    def run(
        self,
        host: str = "0.0.0.0",
        port: int = 5000,
        debug: bool = False,
        use_thread: bool = True,
    ):
        """Run the dashboard server.

        Args:
            host: Server host
            port: Server port
            debug: Whether to run in debug mode
            use_thread: Whether to run in a separate thread
        """
        if use_thread:
            # Run in a separate thread
            self.server_thread = threading.Thread(
                target=self.app.run,
                kwargs={
                    "host": host,
                    "port": port,
                    "debug": debug,
                    "use_reloader": False,
                },
            )
            self.server_thread.daemon = True
            self.server_thread.start()
            self.is_running = True
            logging.info(f"Dashboard started on http://{host}:{port}")
        else:
            # Run in the main thread (blocking)
            self.is_running = True
            self.app.run(host=host, port=port, debug=debug)

    def stop(self):
        """Stop the dashboard server."""
        # Flask doesn't have a clean shutdown method when running in a thread
        # This is a limitation of Flask's development server
        self.is_running = False
        logging.info("Dashboard stopped")
