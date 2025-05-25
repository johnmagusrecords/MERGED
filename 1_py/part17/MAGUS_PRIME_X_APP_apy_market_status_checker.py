"""
market_status_checker.py

Provides stubbed utilities for checking market status.

Functions:
  - is_market_closed(symbol: str) -> bool
      Returns True if the market for the given symbol is closed; stub always returns False.
  - get_available_assets() -> list
      Returns a list of currently tradeable assets; stub always returns an empty list.
"""


def is_market_closed(symbol: str) -> bool:
    """
    Stub function to check if the market for a given symbol is closed.

    Args:
        symbol: The market symbol to check (e.g., "BTCUSD").

    Returns:
        False (stub indicating that the market is always open).
    """
    return False


def get_available_assets() -> list:
    """
    Stub function to return a list of assets available for trading.

    Returns:
        An empty list (stub).
    """
    return []
