import requests
import time
import numpy as np
import pandas as pd
import talib
import backtrader as bt
from newsapi import NewsApiClient
from sklearn.preprocessing import MinMaxScaler

# 🔑 Capital.com API Credentials (Replace with Your Real Keys)
CAPITAL_API_KEY = "MFjNMipztEELvdrV"
NEWS_API_KEY = "ea16bacd51c7462abcde520271143bf8"

BASE_URL = "https://api-capital.backend-capital.com/api/v1"
HEADERS = {
    "X-API-KEY": CAPITAL_API_KEY,
    "Content-Type": "application/json"
}

# Trading Configuration
SYMBOL = "XAU/USD"  # Example: Gold
LOT_SIZE = 0.01
RISK_PERCENT = 1  # Stop Loss 1%
TP_RATIO = 1.5  # Take Profit Ratio (1.5x Risk)
TRAILING_STOP_MULTIPLIER = 1.2  # Move Stop Loss if trade is in profit

# 📌 Authenticate with Capital.com API
def authenticate():
    url = f"{BASE_URL}/session"
    payload = {"identifier": CAPITAL_API_KEY, "password": ""}  # API Key auth
    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        token = response.json().get("clientToken")
        HEADERS["Authorization"] = f"Bearer {token}"
        print("✅ Authentication Successful!")
        return True
    else:
        print(f"❌ Authentication Failed: {response.text}")
        return False

# 📊 Fetch Market Data from Capital.com
def get_historical_data(epic, resolution="HOUR_1", count=500):
    url = f"{BASE_URL}/prices/{epic}/{resolution}/{count}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        prices = [entry['closePrice']['bid'] for entry in data['prices']]
        return np.array(prices)
    
    print(f"❌ Error Fetching Data: {response.text}")
    return None

# 📈 Calculate Technical Indicators
def calculate_indicators(prices):
    rsi = talib.RSI(prices, timeperiod=14)[-1]
    macd, signal, _ = talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)
    atr = talib.ATR(prices, prices, prices, timeperiod=14)[-1]
    upper, middle, lower = talib.BBANDS(prices, timeperiod=20)
    vwap = np.mean(prices)
    
    return rsi, macd[-1], signal[-1], atr, upper[-1], middle[-1], lower[-1], vwap

# 📰 Get News Sentiment (Positive/Negative)
def get_news_sentiment():
    url = f"https://newsapi.org/v2/everything?q=gold&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    
    sentiment_score = sum(1 for article in response['articles'] if 'bullish' in article['title'].lower())
    sentiment_score -= sum(1 for article in response['articles'] if 'bearish' in article['title'].lower())
    
    return sentiment_score

# 📌 Open Trade on Capital.com
def open_trade(direction, sl, tp):
    url = f"{BASE_URL}/positions"
    payload = {
        "epic": SYMBOL,
        "direction": direction,
        "size": LOT_SIZE,
        "stopLevel": sl,
        "limitLevel": tp
    }
    
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"✅ Trade Opened: {direction} at {tp}")
        return response.json().get("dealId")
    
    print(f"❌ Error Opening Trade: {response.text}")
    return None

# 📌 Update Stop Loss when trade is in profit
def update_stop_loss(order_id, new_sl):
    url = f"{BASE_URL}/positions/{order_id}"
    payload = {"stopLevel": new_sl}
    
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code == 200:
        print(f"✅ Stop Loss Updated: {new_sl}")
    else:
        print(f"❌ Error Updating Stop Loss: {response.text}")

# 🔁 Main Trading Loop
def main():
    if not authenticate():
        return
    
    open_trades = {}  # Store open trades and stop loss levels
    
    while True:
        prices = get_historical_data(SYMBOL)
        if prices is None:
            time.sleep(10)
            continue
        
        rsi, macd, signal, atr, upper, middle, lower, vwap = calculate_indicators(prices)
        sentiment = get_news_sentiment()
        last_close = prices[-1]
        
        # ✅ Buy Condition
        if sentiment > 0 and last_close > upper:
            sl = last_close - (atr * TRAILING_STOP_MULTIPLIER)
            tp = last_close + (atr * TP_RATIO)
            order_id = open_trade("BUY", sl, tp)
            if order_id:
                open_trades[order_id] = sl

        # ✅ Sell Condition
        elif sentiment < 0 and last_close < lower:
            sl = last_close + (atr * TRAILING_STOP_MULTIPLIER)
            tp = last_close - (atr * TP_RATIO)
            order_id = open_trade("SELL", sl, tp)
            if order_id:
                open_trades[order_id] = sl

        # ✅ Adjust Stop Loss if Trade is in Profit
        for order_id, sl in list(open_trades.items()):
            if last_close > sl and "BUY" in order_id:
                new_sl = last_close - (atr * 0.5)  # Tighten Stop Loss
                update_stop_loss(order_id, new_sl)
                open_trades[order_id] = new_sl
            elif last_close < sl and "SELL" in order_id:
                new_sl = last_close + (atr * 0.5)
                update_stop_loss(order_id, new_sl)
                open_trades[order_id] = new_sl

        time.sleep(60)  # Wait 1 min before next check

# 🚀 Run the Bot
if __name__ == "__main__":
    main()
