"""
Technical indicators module for trading analysis
"""
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_macd_safe(prices: pd.Series):
    """
    Calculate MACD values for a price series.
    Returns (macd_line, signal_line) tuple or (None, None) on error.
    """
    try:
        # Calculate EMA-12 and EMA-26
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = ema12 - ema26
        
        # Calculate signal line (9-day EMA of MACD line)
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        
        return macd_line.iloc[-1], signal_line.iloc[-1]
    except Exception as e:
        logger.error(f"MACD calculation error: {e}")
        return None, None

def calculate_rsi_safe(prices: pd.Series, window: int = 14) -> float | None:
    """
    Calculate RSI value for a price series.
    Returns RSI value or None on error.
    """
    try:
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gain and loss
        avg_gain = gain.rolling(window=window).mean()
        avg_loss = loss.rolling(window=window).mean()
        
        # Calculate RS
        rs = avg_gain / avg_loss
        
        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    except Exception as e:
        logger.error(f"RSI calculation error: {e}")
        return None

def calculate_bbands_safe(prices: pd.Series, window: int = 20, std: int = 2):
    """
    Calculate Bollinger Bands for a price series.
    Returns (middle_band, upper_band, lower_band) tuple or (None, None, None) on error.
    """
    try:
        # Calculate middle band (SMA)
        middle_band = prices.rolling(window=window).mean()
        
        # Calculate standard deviation
        rolling_std = prices.rolling(window=window).std()
        
        # Calculate upper and lower bands
        upper_band = middle_band + (rolling_std * std)
        lower_band = middle_band - (rolling_std * std)
        
        return middle_band.iloc[-1], upper_band.iloc[-1], lower_band.iloc[-1]
    except Exception as e:
        logger.error(f"Bollinger Bands calculation error: {e}")
        return None, None, None