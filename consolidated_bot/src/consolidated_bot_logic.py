import os
import time
import logging
from typing import List, Optional

import numpy as np
import pandas as pd
import requests

CAPITAL_API_URL = os.getenv("CAPITAL_API_URL", "https://api.capital.com/api/v1")
CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY", "")
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_IDENTIFIER", "")
CAPITAL_API_PASSWORD = os.getenv("CAPITAL_API_PASSWORD", "")
TRADE_INTERVAL = int(os.getenv("TRADE_INTERVAL", 300))
LOT_SIZE_DEFAULT = float(os.getenv("LOT_SIZE_DEFAULT", 1.0))


class CapitalAPI:
    """Minimal wrapper for Capital.com REST endpoints."""

    def __init__(self) -> None:
        self.cst: Optional[str] = None
        self.security: Optional[str] = None
        self.session = requests.Session()

    def authenticate(self) -> bool:
        url = f"{CAPITAL_API_URL}/session"
        payload = {"identifier": CAPITAL_IDENTIFIER, "password": CAPITAL_API_PASSWORD}
        headers = {"X-CAP-API-KEY": CAPITAL_API_KEY, "Content-Type": "application/json"}
        resp = self.session.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            self.cst = resp.headers.get("CST")
            self.security = resp.headers.get("X-SECURITY-TOKEN")
            logging.info("Authentication successful")
            return True
        logging.error("Authentication failed: %s", resp.text)
        return False

    def _auth_headers(self) -> dict:
        return {
            "X-CAP-API-KEY": CAPITAL_API_KEY,
            "CST": self.cst or "",
            "X-SECURITY-TOKEN": self.security or "",
        }

    def fetch_prices(self, symbol: str, count: int = 100) -> Optional[pd.DataFrame]:
        url = f"{CAPITAL_API_URL}/prices/{symbol}?resolution=MINUTE_5&max={count}"
        resp = self.session.get(url, headers=self._auth_headers())
        if resp.status_code != 200:
            logging.error("Failed to fetch prices for %s: %s", symbol, resp.text)
            return None
        data = resp.json().get("prices", [])
        df = pd.DataFrame(data)
        if df.empty:
            return None
        df["timestamp"] = pd.to_datetime(df["snapshotTime"], errors="coerce")
        df["close"] = df["closePrice"].apply(lambda x: x.get("bid"))
        df["high"] = df["highPrice"].apply(lambda x: x.get("bid"))
        df["low"] = df["lowPrice"].apply(lambda x: x.get("bid"))
        return df[["timestamp", "close", "high", "low"]].dropna()

    def place_order(
        self,
        symbol: str,
        direction: str,
        size: float,
        stop_loss: float,
        take_profit: float,
    ) -> bool:
        url = f"{CAPITAL_API_URL}/positions"
        data = {
            "epic": symbol,
            "direction": direction,
            "size": size,
            "orderType": "MARKET",
            "stopLevel": round(stop_loss, 2),
            "limitLevel": round(take_profit, 2),
        }
        headers = {**self._auth_headers(), "Content-Type": "application/json"}
        resp = self.session.post(url, json=data, headers=headers)
        if resp.status_code in (200, 201):
            logging.info("Trade executed: %s %s size %.2f", direction, symbol, size)
            return True
        logging.error("Trade failed: %s", resp.text)
        return False


def calculate_atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> np.ndarray:
    high = np.array(high)
    low = np.array(low)
    close = np.array(close)
    tr = np.maximum(high - low, np.maximum(np.abs(high - np.roll(close, 1)), np.abs(low - np.roll(close, 1))))
    tr[0] = high[0] - low[0]
    atr = np.zeros_like(tr)
    atr[0] = tr[0]
    for i in range(1, len(tr)):
        atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    return atr


def calculate_sma(prices: List[float], period: int) -> np.ndarray:
    return pd.Series(prices).rolling(window=period).mean().fillna(0).values


def calculate_rsi(prices: List[float], period: int = 14) -> np.ndarray:
    prices = np.array(prices)
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100 - 100 / (1 + rs)
    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        upval = max(delta, 0)
        downval = -min(delta, 0)
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100 - 100 / (1 + rs)
    return rsi


class TrendFollowingStrategy:
    def __init__(self) -> None:
        self.positions: dict[str, float] = {}
        self.sma_short = 10
        self.sma_long = 20
        self.rsi_period = 14
        self.atr_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30

    def generate_signal(self, symbol: str, df: pd.DataFrame) -> Optional[dict]:
        prices = df["close"].values
        highs = df["high"].values
        lows = df["low"].values
        if len(prices) < self.sma_long:
            return None
        sma_short = calculate_sma(prices, self.sma_short)
        sma_long = calculate_sma(prices, self.sma_long)
        rsi = calculate_rsi(prices, self.rsi_period)
        atr = calculate_atr(highs, lows, prices, self.atr_period)
        has_position = symbol in self.positions
        price = prices[-1]
        if not has_position and sma_short[-1] > sma_long[-1] and rsi[-1] < self.rsi_overbought:
            qty = LOT_SIZE_DEFAULT
            stop = price - 2 * atr[-1]
            tp = price + atr[-1]
            return {"action": "BUY", "quantity": qty, "stop": stop, "tp": tp}
        if has_position and (sma_short[-1] < sma_long[-1] or rsi[-1] > self.rsi_overbought):
            qty = self.positions.pop(symbol)
            stop = price + 2 * atr[-1]
            tp = price - atr[-1]
            return {"action": "SELL", "quantity": qty, "stop": stop, "tp": tp}
        return None


class TradingBot:
    def __init__(self, symbols: List[str]) -> None:
        self.api = CapitalAPI()
        self.symbols = symbols
        self.strategy = TrendFollowingStrategy()

    def run(self) -> None:
        if not self.api.authenticate():
            return
        while True:
            for sym in self.symbols:
                df = self.api.fetch_prices(sym)
                if df is None:
                    continue
                signal = self.strategy.generate_signal(sym, df)
                if not signal:
                    continue
                action = signal["action"]
                qty = signal["quantity"]
                stop = signal["stop"]
                tp = signal["tp"]
                if self.api.place_order(sym, action, qty, stop, tp):
                    if action == "BUY":
                        self.strategy.positions[sym] = qty
            time.sleep(TRADE_INTERVAL)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    symbols_env = os.getenv("TRADE_SYMBOLS", "BTCUSD")
    symbols = [s.strip() for s in symbols_env.split(",") if s.strip()]
    bot = TradingBot(symbols)
    bot.run()
