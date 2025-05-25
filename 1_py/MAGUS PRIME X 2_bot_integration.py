import logging
import os

from dotenv import load_dotenv
from flask import Flask, jsonify

from bot_dev_backup import (  # Fixed import (was 'bot1')
    analyze_market,
    authenticate,
    get_market_data,
    get_position_details,
)
from strategies import TrendFollowingStrategy

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize strategy
strategy = TrendFollowingStrategy()


@app.route("/api/dashboard/positions", methods=["GET"])
def get_positions():
    """Get all open positions with their details"""
    try:
        cst, x_security = authenticate()
        if not cst or not x_security:
            return jsonify({"error": "Authentication failed"}), 401

        url = f"{os.getenv('CAPITAL_API_URL')}/positions"
        headers = {
            "X-CAP-API-KEY": os.getenv("CAPITAL_API_KEY"),
            "CST": cst,
            "X-SECURITY-TOKEN": x_security,
            "Content-Type": "application/json",
        }

        # Define positions_data before using it
        positions_data = get_position_details(url, headers)

        positions = []
        for position in positions_data.get("positions", []):
            symbol = position.get("epic")
            direction = position.get("direction")
            entry_price = float(position.get("level", 0))
            current_price = float(position.get("marketPrice", 0))
            profit_loss = float(position.get("profit", 0))

            # Get market data for signal analysis
            get_market_data(symbol)
            _, _, mode = analyze_market(symbol)

            positions.append(
                {
                    "symbol": symbol,
                    "direction": direction,
                    "entry_price": entry_price,
                    "current_price": current_price,
                    "profit_loss": profit_loss,
                    "trading_mode": mode,
                    "take_profit": position.get("limitLevel"),
                    "stop_loss": position.get("stopLevel"),
                }
            )

        return jsonify({"positions": positions})
    except Exception as e:
        logging.error(f"Error fetching positions: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/dashboard/signals", methods=["GET"])
def get_signals():
    """Get current trading signals for all symbols"""
    try:
        signals = []
        for symbol in ["BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "ADAUSD"]:
            market_data = get_market_data(symbol)
            if market_data:
                trend, price, mode = analyze_market(symbol)
                signal = strategy.get_signal(
                    symbol, price, market_data, 10000
                )  # Example account balance

                if signal:
                    signals.append(
                        {
                            "symbol": symbol,
                            "action": signal["action"],
                            "price": price,
                            "reason": signal["reason"],
                            "mode": mode,
                        }
                    )

        return jsonify({"signals": signals})
    except Exception as e:
        logging.error(f"Error getting signals: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/dashboard/market_news", methods=["GET"])
def get_market_news():
    """Get relevant market news for traded assets"""
    try:
        # This would be replaced with actual news API integration
        news = [
            {
                "title": "Fed Announces Rate Hold",
                "content": "Federal Reserve maintains interest rates amid inflation concerns",
                "sentiment": "neutral",
                "symbol": "USD",
                "timestamp": "2024-03-19T14:00:00Z",
            },
            {
                "title": "Ethereum Network Upgrade",
                "content": "ETH 2.0 upgrade completes successfully, price surges 8%",
                "sentiment": "positive",
                "symbol": "ETHUSD",
                "timestamp": "2024-03-19T15:30:00Z",
            },
            {
                "title": "Coinbase Outage Report",
                "content": "Exchange experiences partial outage during high volatility",
                "sentiment": "negative",
                "symbol": "COIN",
                "timestamp": "2024-03-19T16:45:00Z",
            },
        ]
        return jsonify({"news": news})
    except Exception as e:
        logging.error(f"Error fetching news: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001)
