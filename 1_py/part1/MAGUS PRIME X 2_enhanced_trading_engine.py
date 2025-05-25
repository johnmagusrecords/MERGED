import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import talib

from market_regime import EnhancedMarketRegimeDetector
from ml_predictor import EnhancedMLPredictor
from risk_manager import EnhancedRiskManager


@dataclass
class TradeParameters:
    entry_price: float
    stop_loss: float
    take_profit: float
    direction: str
    size: float
    symbol: str
    timestamp: datetime


@dataclass
class Position:
    id: str
    symbol: str
    direction: str
    size: float
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    entry_time: datetime
    pnl: float
    pnl_percent: float
    status: str
    timeframe: str
    strategy: str


class EnhancedTradingEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.market_data = {}
        self.active_trades = {}
        self.risk_manager = EnhancedRiskManager()
        self.regime_detector = EnhancedMarketRegimeDetector()
        self.ml_predictor = EnhancedMLPredictor()

        # Trading parameters
        self.min_volatility = 0.001  # Minimum volatility for trading
        self.max_spread = 0.003  # Maximum allowed spread
        self.min_volume = 1000  # Minimum volume requirement
        self.trend_strength = 25  # Minimum ADX for trend following

    def calculate_indicators(self, data: pd.DataFrame) -> Dict:
        """Calculate enhanced technical indicators"""
        close = data["close"].values
        high = data["high"].values
        low = data["low"].values
        volume = data["volume"].values

        indicators = {}

        # Trend Indicators
        indicators["sma_20"] = talib.SMA(close, timeperiod=20)
        indicators["sma_50"] = talib.SMA(close, timeperiod=50)
        indicators["sma_200"] = talib.SMA(close, timeperiod=200)
        indicators["ema_20"] = talib.EMA(close, timeperiod=20)

        # Momentum Indicators
        indicators["rsi"] = talib.RSI(close)
        indicators["macd"], indicators["macd_signal"], _ = talib.MACD(close)
        indicators["stoch_k"], indicators["stoch_d"] = talib.STOCH(high, low, close)

        # Volatility Indicators
        indicators["atr"] = talib.ATR(high, low, close)
        (
            indicators["bbands_upper"],
            indicators["bbands_middle"],
            indicators["bbands_lower"],
        ) = talib.BBANDS(close)

        # Volume Indicators
        indicators["obv"] = talib.OBV(close, volume)
        indicators["mfi"] = talib.MFI(high, low, close, volume)

        # Trend Strength
        indicators["adx"] = talib.ADX(high, low, close)
        indicators["cci"] = talib.CCI(high, low, close)

        # Additional Advanced Indicators
        (
            indicators["keltner_upper"],
            indicators["keltner_middle"],
            indicators["keltner_lower"],
        ) = self._calculate_keltner(high, low, close)
        indicators["vwap"] = self._calculate_vwap(high, low, close, volume)

        return indicators

    def _calculate_keltner(self, high, low, close, period=20, atr_multiplier=2.0):
        """Calculate Keltner Channels"""
        typical_price = (high + low + close) / 3
        middle = talib.EMA(typical_price, timeperiod=period)
        atr = talib.ATR(high, low, close, timeperiod=period)

        upper = middle + (atr * atr_multiplier)
        lower = middle - (atr * atr_multiplier)

        return upper, middle, lower

    def _calculate_vwap(self, high, low, close, volume):
        """Calculate Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        return np.cumsum(typical_price * volume) / np.cumsum(volume)

    def analyze_market(self, symbol: str) -> Tuple[str, Optional[Dict]]:
        """Enhanced market analysis with multiple confirmations"""
        try:
            if symbol not in self.market_data or "1h" not in self.market_data[symbol]:
                return "HOLD", None

            data = self.market_data[symbol]["1h"]

            # Calculate all indicators
            indicators = self.calculate_indicators(data)

            # Get market regime and ML prediction
            regime, confidence = self.regime_detector.detect_regime(symbol, data)
            prediction = self.ml_predictor.predict(symbol, data)

            if prediction is None:
                return "HOLD", None

            current_price = data["close"].iloc[-1]
            current_spread = data["high"].iloc[-1] - data["low"].iloc[-1]

            # Check trading conditions
            if (current_spread / current_price) > self.max_spread:
                return "HOLD", None

            if indicators["atr"][-1] < self.min_volatility:
                return "HOLD", None

            if data["volume"].iloc[-1] < self.min_volume:
                return "HOLD", None

            # Long setup conditions
            long_conditions = (
                prediction.direction == "long"
                and prediction.confidence > 0.6
                and indicators["rsi"][-1] < 70
                and indicators["macd"][-1] > indicators["macd_signal"][-1]
                and current_price > indicators["sma_20"][-1]
                and indicators["adx"][-1] > self.trend_strength
                and indicators["mfi"][-1] < 80
                and current_price > indicators["vwap"][-1]
                and indicators["cci"][-1] > -100
                and confidence > 0.6
            )

            # Short setup conditions
            short_conditions = (
                prediction.direction == "short"
                and prediction.confidence > 0.6
                and indicators["rsi"][-1] > 30
                and indicators["macd"][-1] < indicators["macd_signal"][-1]
                and current_price < indicators["sma_20"][-1]
                and indicators["adx"][-1] > self.trend_strength
                and indicators["mfi"][-1] > 20
                and current_price < indicators["vwap"][-1]
                and indicators["cci"][-1] < 100
                and confidence > 0.6
            )

            signal = "HOLD"
            params = None

            if long_conditions:
                signal = "LONG"
                # Dynamic stop loss based on ATR and support levels
                atr = indicators["atr"][-1]
                support_level = min(
                    indicators["bbands_lower"][-1],
                    indicators["keltner_lower"][-1],
                    data["low"].iloc[-5:],
                )
                stop_loss = max(current_price - 2.5 * atr, support_level)
                take_profit = current_price + 3.0 * (current_price - stop_loss)

                params = {
                    "entry_price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "direction": "long",
                }

            elif short_conditions:
                signal = "SHORT"
                # Dynamic stop loss based on ATR and resistance levels
                atr = indicators["atr"][-1]
                resistance_level = max(
                    indicators["bbands_upper"][-1],
                    indicators["keltner_upper"][-1],
                    data["high"].iloc[-5:],
                )
                stop_loss = min(current_price + 2.5 * atr, resistance_level)
                take_profit = current_price - 3.0 * (stop_loss - current_price)

                params = {
                    "entry_price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "direction": "short",
                }

            return signal, params

        except Exception as e:
            self.logger.error(f"Error in analyze_market: {str(e)}")
            return "HOLD", None

    def update_market_data(self, symbol: str, timeframe: str, data: pd.DataFrame):
        """Update market data for a symbol and timeframe"""
        if symbol not in self.market_data:
            self.market_data[symbol] = {}
        self.market_data[symbol][timeframe] = data

    def place_trade(
        self,
        symbol: str,
        direction: str,
        size: float,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
    ) -> bool:
        """Place a new trade"""
        try:
            # Create trade parameters
            trade = TradeParameters(
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                direction=direction,
                size=size,
                symbol=symbol,
                timestamp=datetime.now(),
            )

            # Store trade
            self.active_trades[symbol] = trade

            # Update risk manager
            self.risk_manager.update_position(symbol, size, entry_price, direction)

            self.logger.info(f"Placed {direction} trade for {symbol}")
            return True

        except Exception as e:
            self.logger.error(f"Error placing trade: {str(e)}")
            return False

    def close_trade(self, symbol: str, reason: str = ""):
        """Close an active trade"""
        try:
            if symbol in self.active_trades:
                trade = self.active_trades[symbol]
                self.logger.info(
                    f"Closing {trade.direction} trade for {symbol}. Reason: {reason}"
                )

                # Remove from active trades
                del self.active_trades[symbol]

                # Update risk manager
                self.risk_manager.remove_position(symbol)

        except Exception as e:
            self.logger.error(f"Error closing trade: {str(e)}")

    def update_trade(self, symbol: str, current_price: float):
        """Update and manage active trade"""
        try:
            if symbol not in self.active_trades:
                return

            trade = self.active_trades[symbol]

            # Check stop loss
            if trade.direction == "long":
                if current_price <= trade.stop_loss:
                    self.close_trade(symbol, "Stop Loss Hit")
                elif current_price >= trade.take_profit:
                    self.close_trade(symbol, "Take Profit Hit")

            else:  # Short trade
                if current_price >= trade.stop_loss:
                    self.close_trade(symbol, "Stop Loss Hit")
                elif current_price <= trade.take_profit:
                    self.close_trade(symbol, "Take Profit Hit")

        except Exception as e:
            self.logger.error(f"Error updating trade: {str(e)}")
