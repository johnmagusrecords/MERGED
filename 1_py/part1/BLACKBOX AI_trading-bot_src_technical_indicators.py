import numpy as np
import pandas as pd

def calculate_atr(high, low, close, period=14):
    """Calculate Average True Range (ATR)"""
    try:
        high = np.array(high)
        low = np.array(low)
        close = np.array(close)
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - np.roll(close, 1))
        tr3 = abs(low - np.roll(close, 1))
        tr = np.maximum(np.maximum(tr1, tr2), tr3)
        tr[0] = tr1[0]  # First value
        
        # Calculate ATR
        atr = np.zeros_like(tr)
        atr[0] = tr[0]
        for i in range(1, len(tr)):
            atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
            
        return atr
        
    except Exception as e:
        print(f"Error calculating ATR: {str(e)}")
        return np.array([])

def calculate_moving_averages(prices, short_period=10, long_period=20):
    """Calculate Simple Moving Averages"""
    try:
        prices = np.array(prices)
        
        # Calculate SMAs
        sma_short = np.zeros_like(prices)
        sma_long = np.zeros_like(prices)
        
        for i in range(len(prices)):
            if i >= short_period:
                sma_short[i] = np.mean(prices[i-short_period:i])
            if i >= long_period:
                sma_long[i] = np.mean(prices[i-long_period:i])
                
        return sma_short, sma_long
        
    except Exception as e:
        print(f"Error calculating moving averages: {str(e)}")
        return np.array([]), np.array([])

def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    try:
        prices = np.array(prices)
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum()/period
        down = -seed[seed < 0].sum()/period
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100./(1. + rs)

        for i in range(period, len(prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(period-1) + upval)/period
            down = (down*(period-1) + downval)/period
            rs = up/down
            rsi[i] = 100. - 100./(1. + rs)

        return rsi
        
    except Exception as e:
        print(f"Error calculating RSI: {str(e)}")
        return np.array([])

def calculate_bollinger_bands(prices, period=20, num_std=2):
    """Calculate Bollinger Bands"""
    try:
        prices = np.array(prices)
        sma = pd.Series(prices).rolling(window=period).mean()
        std = pd.Series(prices).rolling(window=period).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        return sma, upper_band, lower_band
        
    except Exception as e:
        print(f"Error calculating Bollinger Bands: {str(e)}")
        return np.array([]), np.array([]), np.array([])

def calculate_macd(prices, fast_period=12, slow_period=26, signal_period=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    try:
        prices = np.array(prices)
        # Calculate EMAs
        ema_fast = pd.Series(prices).ewm(span=fast_period, adjust=False).mean()
        ema_slow = pd.Series(prices).ewm(span=slow_period, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        # Calculate Signal line
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        
        # Calculate MACD histogram
        macd_hist = macd_line - signal_line
        
        return macd_line, signal_line, macd_hist
        
    except Exception as e:
        print(f"Error calculating MACD: {str(e)}")
        return np.array([]), np.array([]), np.array([])
