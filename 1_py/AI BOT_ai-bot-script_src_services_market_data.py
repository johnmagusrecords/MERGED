import os
import requests
import pandas as pd
import talib
import logging

CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
CAPITAL_API_URL = os.getenv("CAPITAL_API_URL")

def get_market_data(symbol, cst, x_security):
    logging.info(f"Fetching market data for {symbol}...")
    url = f"{CAPITAL_API_URL}/prices/{symbol}?resolution=MINUTE_5&max=100"
    headers = {"X-CAP-API-KEY": CAPITAL_API_KEY, "CST": cst, "X-SECURITY-TOKEN": x_security}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data.get("prices", []))
        
        if not df.empty:
            try:
                df["timestamp"] = pd.to_datetime(df["snapshotTime"], format='%Y-%m-%dT%H:%M:%S.%fZ', errors="coerce")
                df["close"] = df["closePrice"].apply(lambda x: x.get("bid", None))
                df["high"] = df["highPrice"].apply(lambda x: x.get("bid", None))
                df["low"] = df["lowPrice"].apply(lambda x: x.get("bid", None))
            except Exception as e:
                logging.warning(f"⚠️ Error processing data for {symbol}: {e}")
                return None

            logging.info(f"Market data for {symbol} fetched successfully.")
            return df[["timestamp", "close", "high", "low"]].dropna()
    logging.warning(f"⚠️ Error fetching data for {symbol}")
    return None

def analyze_market(symbol, cst, x_security):
    df = get_market_data(symbol, cst, x_security)
    if df is None or len(df) < 14:
        return None

    df["ATR"] = talib.ATR(df["high"], df["low"], df["close"], timeperiod=14)
    df["RSI"] = talib.RSI(df["close"], timeperiod=14)
    df["MACD"], _, _ = talib.MACD(df["close"], fastperiod=12, slowperiod=26, signalperiod=9)

    last_close = df["close"].iloc[-1]
    atr = df["ATR"].iloc[-1]
    rsi = df["RSI"].iloc[-1]
    macd = df["MACD"].iloc[-1]

    if rsi < 30 and macd > 0:
        return "BUY", last_close, atr
    elif rsi > 70 and macd < 0:
        return "SELL", last_close, atr
    return None