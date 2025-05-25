"""
Utility functions for asset type detection and classification.
"""

import json
import logging
import os
from typing import Dict, List

logger = logging.getLogger(__name__)

# Asset type mappings
COMMON_SYMBOLS = {
    # Cryptocurrencies
    "BTCUSD": "Crypto",
    "ETHUSD": "Crypto",
    "XRPUSD": "Crypto",
    "SOLUSD": "Crypto",
    "ADAUSD": "Crypto",
    "DOTUSD": "Crypto",
    "BNBUSD": "Crypto",
    "DOGEUSD": "Crypto",
    "LTCUSD": "Crypto",
    # Commodities
    "XAUUSD": "Commodity",
    "GOLD": "Commodity",
    "SILVER": "Commodity",
    "XAGUSD": "Commodity",
    "WTIUSD": "Commodity",
    "BRENTUSD": "Commodity",
    "NATGASUSD": "Commodity",
    # Indices
    "US30": "Index",
    "US100": "Index",
    "US500": "Index",
    "SPX500": "Index",
    "GER40": "Index",
    "UK100": "Index",
    # Forex Pairs
    "EURUSD": "Forex",
    "GBPUSD": "Forex",
    "USDJPY": "Forex",
    "AUDUSD": "Forex",
    "USDCAD": "Forex",
    "NZDUSD": "Forex",
}


def get_asset_type(symbol: str, markets_data: List[Dict] = None) -> str:
    """
    Determine the asset type based on the symbol.

    Args:
        symbol: Trading symbol to check
        markets_data: Optional list of market data dictionaries from API

    Returns:
        str: Asset type (Crypto, Forex, Stock, Index, Commodity)
    """
    if not symbol:
        return "Unknown"

    # Normalize the symbol
    symbol = symbol.upper().replace("/", "")

    # Check if symbol is in our common symbols dictionary
    if symbol in COMMON_SYMBOLS:
        return COMMON_SYMBOLS[symbol]

    # Try to determine from market data if provided
    if markets_data:
        for market in markets_data:
            if market.get("instrumentName") == symbol:
                market_type = market.get("instrumentType")
                if market_type:
                    return market_type

    # Categorize based on patterns in the symbol
    # Cryptocurrency detection
    if any(
        crypto in symbol
        for crypto in [
            "BTC",
            "ETH",
            "XRP",
            "LTC",
            "SOL",
            "ADA",
            "DOT",
            "DOGE",
            "AVAX",
            "LINK",
        ]
    ):
        return "Crypto"

    # Common forex pairs
    if len(symbol) == 6 and any(
        currency in symbol
        for currency in ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]
    ):
        return "Forex"

    # Common commodities
    if any(
        commodity in symbol
        for commodity in [
            "GOLD",
            "XAU",
            "SILVER",
            "XAG",
            "OIL",
            "BRENT",
            "WTI",
            "GAS",
            "NG",
        ]
    ):
        return "Commodity"

    # Common indices
    if any(
        index in symbol
        for index in [
            "SPX",
            "S&P",
            "DOW",
            "NASDAQ",
            "NDX",
            "US30",
            "US100",
            "DAX",
            "FTSE",
            "NKY",
        ]
    ):
        return "Index"

    # Default fallback
    return "Unknown"


def load_asset_types_from_config(
    config_path: str = "assets_config.json",
) -> Dict[str, str]:
    """
    Load asset types from configuration file

    Args:
        config_path: Path to the configuration file

    Returns:
        Dict[str, str]: Dictionary mapping symbols to asset types
    """
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_data = json.load(f)

            asset_types = {}

            # Handle different possible config formats
            if "assets" in config_data:
                for asset in config_data["assets"]:
                    if "symbol" in asset and "type" in asset:
                        asset_types[asset["symbol"]] = asset["type"]
            else:
                # Assume config is directly a mapping of symbols to their details
                for symbol, details in config_data.items():
                    if isinstance(details, dict) and "type" in details:
                        asset_types[symbol] = details["type"]

            return asset_types
    except Exception as e:
        logger.error(f"Error loading asset types from config: {e}")

    return {}


# When this module is imported, initialize with config file
ASSET_TYPES = load_asset_types_from_config()

# Update common symbols with loaded config
COMMON_SYMBOLS.update(ASSET_TYPES)
