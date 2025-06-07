import os
import json
import requests
import logging
from services.authentication import authenticate

CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
CAPITAL_API_URL = os.getenv("CAPITAL_API_URL")
DEFAULT_LOT_SIZE = float(os.getenv("LOT_SIZE_DEFAULT", 0.01))
TRAILING_SL_ATR_MULTIPLIER = float(os.getenv("TRAILING_SL_ATR_MULTIPLIER", 1.5))
TP_RATIO = float(os.getenv("TP_RATIO", 1))

def execute_trade(symbol, direction, price, atr, lot_sizes):
    cst, x_security = authenticate()
    if not cst or not x_security:
        return

    lot_size = lot_sizes.get(symbol, DEFAULT_LOT_SIZE)
    stop_loss = price - (atr * TRAILING_SL_ATR_MULTIPLIER) if direction == "BUY" else price + (atr * TRAILING_SL_ATR_MULTIPLIER)
    take_profit = price + (atr * TP_RATIO) if direction == "BUY" else price - (atr * TP_RATIO)

    url = f"{CAPITAL_API_URL}/positions"
    headers = {
        "X-CAP-API-KEY": CAPITAL_API_KEY,
        "CST": cst,
        "X-SECURITY-TOKEN": x_security,
        "Content-Type": "application/json",
    }
    data = {
        "epic": symbol,
        "direction": direction,
        "size": lot_size,
        "orderType": "MARKET",
        "stopLevel": round(stop_loss, 2),
        "limitLevel": round(take_profit, 2),
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logging.info(f"✅ Trade Executed: {direction} {symbol} at {price} | TP: {take_profit} | SL: {stop_loss}")
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Trade Execution Failed for {symbol}: {e}")

def fetch_assets():
    
    assets_path = os.path.join(os.path.dirname(__file__), '..', 'assets.json')
    if not os.path.exists(assets_path):
        logging.error("❌ assets.json file is missing. Please ensure it exists.")
        return None

    with open(assets_path, "r") as f:
        assets_data = json.load(f)["assets"]
        assets = {asset["symbol"]: asset["lot_size"] for asset in assets_data}
        return assets
