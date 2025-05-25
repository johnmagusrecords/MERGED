import pandas as pd
import logging
from ta.volume import VolumeWeightedAveragePrice
from ta.trend import ADXIndicator, IchimokuIndicator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def calculate_vwap_safe(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series, window: int = 14) -> float | None:
    """
    Compute the latest VWAP using ta.volume.VolumeWeightedAveragePrice.
    Returns VWAP value or None on insufficient data or error.
    """
    if len(close) < window:
        logger.warning(f"VWAP skipped: need at least {window} data points.")
        return None
    try:
        vwap = VolumeWeightedAveragePrice(high=high, low=low, close=close, volume=volume, window=window)
        return vwap.volume_weighted_average_price().iloc[-1]
    except Exception as e:
        logger.error(f"VWAP error: {e}")
        return None


def calculate_adx_safe(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> float | None:
    """
    Compute the latest ADX using ta.trend.ADXIndicator.
    Returns ADX value or None on insufficient data or error.
    """
    if len(close) < window:
        logger.warning(f"ADX skipped: need at least {window} data points.")
        return None
    try:
        adx = ADXIndicator(high=high, low=low, close=close, window=window)
        return adx.adx().iloc[-1]
    except Exception as e:
        logger.error(f"ADX error: {e}")
        return None


def calculate_ichimoku_safe(high: pd.Series, low: pd.Series, close: pd.Series) -> float | None:
    """
    Compute the latest Ichimoku indicator's conversion line (Tenkan-sen).
    Returns the value or None on insufficient data or error.
    """
    try:
        ichimoku = IchimokuIndicator(high=high, low=low, window1=9, window2=26, window3=52)
        return ichimoku.ichimoku_conversion_line().iloc[-1]
    except Exception as e:
        logger.error(f"Ichimoku error: {e}")
        return None


def calculate_macd_safe(prices: pd.Series):
    """
    Calculate MACD values for a price series.
    Returns (macd_line, signal_line) tuple or (None, None) on error.
    """
    try:
        from ta.trend import MACD
        macd_indicator = MACD(prices)
        macd_line = macd_indicator.macd().iloc[-1]
        signal_line = macd_indicator.macd_signal().iloc[-1]
        return macd_line, signal_line
    except Exception as e:
        logger.error(f"MACD calculation error: {e}")
        return None, None


def calculate_rsi_safe(prices: pd.Series, window: int = 14) -> float | None:
    """
    Calculate RSI value for a price series.
    Returns RSI value or None on error.
    """
    try:
        from ta.momentum import RSIIndicator
        rsi = RSIIndicator(prices, window=window)
        return rsi.rsi().iloc[-1]
    except Exception as e:
        logger.error(f"RSI calculation error: {e}")
        return None


def calculate_bbands_safe(prices: pd.Series, window: int = 20, std: int = 2):
    """
    Calculate Bollinger Bands for a price series.
    Returns (middle_band, upper_band, lower_band) tuple or (None, None, None) on error.
    """
    try:
        from ta.volatility import BollingerBands
        bbands = BollingerBands(prices, window=window, window_dev=std)
        middle = bbands.bollinger_mavg().iloc[-1]
        upper = bbands.bollinger_hband().iloc[-1]
        lower = bbands.bollinger_lband().iloc[-1]
        return middle, upper, lower
    except Exception as e:
        logger.error(f"Bollinger Bands calculation error: {e}")
        return None, None, None


def calculate_indicators(prices: pd.Series) -> dict:
    """
    Return a snapshot of the latest RSI, MACD, and Bollinger Bands values.
    """
    try:
        macd_line, macd_signal = calculate_macd_safe(prices)
        rsi_val = calculate_rsi_safe(prices)
        mavg, upper, lower = calculate_bbands_safe(prices)
        return {
            "RSI": rsi_val,
            "MACD": {"line": macd_line, "signal": macd_signal},
            "BollingerBands": {"mavg": mavg, "upper": upper, "lower": lower},
        }
    except Exception as e:
        logger.error(f"Error calculating indicators: {e}")
        return {}


def get_price_data(limit: int = 50) -> pd.DataFrame:
    """
    Placeholder function to simulate price data retrieval.
    Returns a DataFrame with 'close' prices.
    """
    dates = pd.date_range(end=pd.Timestamp.now(), periods=limit)
    prices = pd.Series([100 + i * 0.1 for i in range(limit)], index=dates)
    df = pd.DataFrame({"close": prices})
    return df


if __name__ == "__main__":
    # Demo execution
    df = get_price_data(limit=50)["close"]
    print("Indicators snapshot:", calculate_indicators(df))