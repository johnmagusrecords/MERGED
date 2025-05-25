import os
import time
import threading
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Correct import paths
from src.services.authentication import authenticate
from src.services.market_data import get_market_data, analyze_market
from src.services.news import fetch_news, analyze_sentiment
from src.services.trading import execute_trade, fetch_assets

# Load environment variables
load_dotenv()

# Trading Settings
TRADE_INTERVAL = int(os.getenv("TRADE_INTERVAL", 300))

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Flask Webhook
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    logging.info(f"Incoming Webhook Data: {data}")

    symbol = data.get("symbol")
    price = float(data.get("price"))
    action = data.get("action")

    if symbol and action:
        cst, x_security = authenticate()
        if not cst or not x_security:
            return jsonify({"status": "error", "message": "Authentication failed"}), 500

        market_data = get_market_data(symbol, cst, x_security)
        if market_data is not None:
            atr_value = market_data["ATR"].iloc[-1]
            execute_trade(symbol, action, price, atr_value, fetch_assets())
        else:
            logging.error(f"Failed to fetch market data for {symbol}")
            return jsonify({"status": "error", "message": "Failed to fetch market data"}), 500

    return jsonify({"status": "success"}), 200

# Main Bot Loop
def main():
    logging.info("🚀 Trading Bot Started!")
    while True:
        cst, x_security = authenticate()
        if not cst or not x_security:
            logging.error("❌ Authentication failed. Retrying...")
            time.sleep(TRADE_INTERVAL)
            continue

        logging.info("📊 Fetching market data...")
        assets = fetch_assets()
        if assets is None:
            logging.error("❌ Exiting due to missing assets.json.")
            break

        for symbol in assets.keys():
            trend = analyze_market(symbol, cst, x_security)
            if trend:
                execute_trade(symbol, *trend, assets)

        logging.info("📰 Fetching news data...")
        news_articles = fetch_news()
        for article in news_articles:
            sentiment = analyze_sentiment(article)
            if sentiment > 0.5:
                logging.info(f"📈 Positive news detected: {article['title']}")
                market_data = get_market_data("BTCUSD", cst, x_security)
                if market_data is not None:
                    current_price = market_data["close"].iloc[-1]
                    atr_value = market_data["ATR"].iloc[-1]
                    execute_trade("BTCUSD", "BUY", current_price, atr_value, assets)
            elif sentiment < -0.5:
                logging.info(f"📉 Negative news detected: {article['title']}")
                market_data = get_market_data("BTCUSD", cst, x_security)
                if market_data is not None:
                    current_price = market_data["close"].iloc[-1]
                    atr_value = market_data["ATR"].iloc[-1]
                    execute_trade("BTCUSD", "SELL", current_price, atr_value, assets)

        time.sleep(TRADE_INTERVAL)

if __name__ == "__main__":
    threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 80, "threaded": True}).start()
    main()