from typing import Sequence, Optional, Tuple


def calculate_rsi_safe(prices: Sequence[float], period: int = 14) -> Optional[float]:
    """
    Safely calculates the RSI (Relative Strength Index).

    Args:
        prices: Sequence of price floats.
        period: RSI period.

    Returns:
        RSI value or None if not enough data.
    """
    if len(prices) < period:
        return None
    # ...actual RSI calculation...
    return 50.0  # stub


def calculate_macd_safe(prices: Sequence[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[Optional[float], Optional[float]]:
    """
    Safely calculates the MACD.

    Args:
        prices: Sequence of price floats.
        fast: Fast EMA period.
        slow: Slow EMA period.
        signal: Signal line period.

    Returns:
        Tuple of MACD value and signal line value or (None, None) if not enough data.
    """
    if len(prices) < slow + signal:
        return (None, None)
    # ...actual MACD calculation...
    return (0.0, 0.0)  # stub


def calculate_ema_safe(prices: Sequence[float], period: int = 21) -> Optional[float]:
    """
    Safely calculates the EMA (Exponential Moving Average).

    Args:
        prices: Sequence of price floats.
        period: EMA period.

    Returns:
        EMA value or None if not enough data.
    """
    if len(prices) < period:
        return None
    # ...actual EMA calculation...
    return sum(prices[-period:]) / period  # stub


def calculate_bbands_safe(prices: Sequence[float], period: int = 20, stddev: int = 2) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Stub for Bollinger Bands calculation.

    Args:
        prices: Sequence of price floats.
        period: Period for moving average.
        stddev: Number of standard deviations.

    Returns:
        Tuple of (moving average, upper band, lower band) or (None, None, None).
    """
    if len(prices) < period:
        return (None, None, None)
    # ...actual BBands calculation...
    return (0.0, 0.0, 0.0)  # stub
