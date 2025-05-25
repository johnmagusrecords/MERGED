import os
import time
import requests
import ccxt
import numpy as np
import pandas as pd
import talib
from dotenv import load_dotenv

# Load API Keys from .env
load_dotenv()
CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
CAPITAL_PASSWORD = os.getenv("CAPITAL_PASSWORD")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Capital.com Authentication Setup
exchange = ccxt.capitalcom({
    'apiKey': CAPITAL_API_KEY,
    'password': CAPITAL_PASSWORD
})

# Trading Constants
SYMBOL = "XAU/USD"  # Example: Gold (Change to any asset)
LOT_SIZE = 0.01
STOP_LOSS_PERCENT = 1  # 1% Stop Loss
TAKE_PROFIT_RATIO = 1  # 1:1 Risk-Reward
ATR_MULTIPLIER = 1.5  # Trailing Stop ATR Multiplier
ATR_PERIOD = 14
BBANDS_PERIOD = 20

# Fetch Market Data
def fetch_data():
    try:
        ohlcv = exchange.fetch_ohlcv(SYMBOL, timeframe='1h', limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

# Calculate Indicators
def calculate_indicators(df):
    df['ATR'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=ATR_PERIOD)
    df['upper_band'], df['middle_band'], df['lower_band'] = talib.BBANDS(df['close'], timeperiod=BBANDS_PERIOD)
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)
    return df

# Fetch News Sentiment
def get_news_sentiment():
    try:
        url = f'https://newsapi.org/v2/everything?q=gold&apiKey={NEWS_API_KEY}'
        response = requests.get(url).json()
        sentiment_score = sum(1 for article in response['articles'] if 'bullish' in article['title'].lower()) - \
                          sum(1 for article in response['articles'] if 'bearish' in article['title'].lower())
        return sentiment_score
    except Exception as e:
        print(f"❌ Error fetching news sentiment: {e}")
        return 0

# Open Trade
def open_trade(direction, sl, tp):
    try:
        order = exchange.create_market_order(SYMBOL, direction, LOT_SIZE, params={'stopLoss': sl, 'takeProfit': tp})
        return order['id']
    except Exception as e:
        print(f"❌ Error opening trade: {e}")
        return None

# Adjust Stop Loss Dynamically
def update_stop_loss(order_id, new_sl):
    try:
        exchange.edit_order(order_id, SYMBOL, 'market', LOT_SIZE, None, {'stopLoss': new_sl})
    except Exception as e:
        print(f"❌ Error updating stop loss: {e}")

# Main Bot Logic
def main():
    while True:
        df = fetch_data()
        if df is None:
            time.sleep(60)
            continue

        df = calculate_indicators(df)
        sentiment = get_news_sentiment()
        last_close = df['close'].iloc[-1]
        atr = df['ATR'].iloc[-1]

        # Buy Condition: Positive Sentiment + Price Breaks Upper Bollinger Band
        if sentiment > 0 and last_close > df['upper_band'].iloc[-1]:
            sl = last_close - (atr * ATR_MULTIPLIER)
            tp = last_close + (atr * TAKE_PROFIT_RATIO)
            order_id = open_trade('buy', sl, tp)
            if order_id:
                print(f"✅ Buy Order Opened (ID: {order_id})")

        # Sell Condition: Negative Sentiment + Price Drops Below Lower Bollinger Band
        elif sentiment < 0 and last_close < df['lower_band'].iloc[-1]:
            sl = last_close + (atr * ATR_MULTIPLIER)
            tp = last_close - (atr * TAKE_PROFIT_RATIO)
            order_id = open_trade('sell', sl, tp)
            if order_id:
                print(f"✅ Sell Order Opened (ID: {order_id})")

        # Adjust Stop Loss for Winning Trades
        open_orders = exchange.fetch_open_orders(SYMBOL)
        for order in open_orders:
            if order['side'] == 'buy' and last_close > order['price'] + atr:
                update_stop_loss(order['id'], last_close - (atr * 0.5))
            elif order['side'] == 'sell' and last_close < order['price'] - atr:
                update_stop_loss(order['id'], last_close + (atr * 0.5))

        time.sleep(60)  # Wait 1 minute before next check

if __name__ == "__main__":
    main()
