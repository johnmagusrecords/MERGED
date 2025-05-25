import datetime
import json
import logging
import os
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Market hours config (UTC)
MARKET_HOURS = {
    "Commodities": {"open": 22, "close": 20, "days": [0, 1, 2, 3, 4]},  # Sunday–Friday
    "Indices": {"open": 22, "close": 20, "days": [0, 1, 2, 3, 4]},
    "Forex": {"open": 22, "close": 20, "days": [0, 1, 2, 3, 4]},
    "Crypto": {"open": 0, "close": 24, "days": [0, 1, 2, 3, 4, 5, 6]},  # 24/7
}

# Enhanced market hours with more detail (UTC)
DETAILED_MARKET_HOURS = {
    "Crypto": {
        "sessions": [{"open": 0, "close": 24}],  # 24/7
        "days": [0, 1, 2, 3, 4, 5, 6],  # All days
        "exceptions": [],  # No exceptions
    },
    "Forex": {
        "sessions": [
            {"open": 22, "close": 24},  # Sunday open
            {"open": 0, "close": 20},  # Monday-Thursday full day
            {"open": 0, "close": 20},  # Friday close
        ],
        "days": [0, 1, 2, 3, 4],  # Sunday-Friday
        "exceptions": ["New Year", "Christmas"],
    },
    "Commodity": {
        "sessions": [
            {"open": 22, "close": 24},  # Sunday open
            {"open": 0, "close": 20},  # Weekday
            {"open": 0, "close": 20},  # Friday close
        ],
        "days": [0, 1, 2, 3, 4],  # Sunday-Friday
        "exceptions": ["New Year", "Christmas"],
    },
    "Index": {
        "sessions": [
            {"open": 22, "close": 24},  # Sunday open
            {"open": 0, "close": 20},  # Monday-Thursday
            {"open": 0, "close": 20},  # Friday
        ],
        "days": [0, 1, 2, 3, 4],  # Sunday-Friday
        "exceptions": ["New Year", "Christmas", "Good Friday"],
    },
    "Stock": {
        "sessions": [{"open": 13, "close": 20}],  # Regular trading hours (9am-4pm EST)
        "days": [1, 2, 3, 4, 5],  # Monday-Friday
        "exceptions": [
            "New Year",
            "Martin Luther King Day",
            "Presidents Day",
            "Good Friday",
            "Memorial Day",
            "Juneteenth",
            "Independence Day",
            "Labor Day",
            "Thanksgiving",
            "Christmas",
        ],
    },
}

# Commonly used symbols with their asset types for quick lookup
COMMON_SYMBOLS = {
    "BTCUSD": "Crypto",
    "ETHUSD": "Crypto",
    "BTC": "Crypto",
    "ETH": "Crypto",
    "XAUUSD": "Commodity",
    "GOLD": "Commodity",
    "SILVER": "Commodity",
    "XAGUSD": "Commodity",
    "OIL": "Commodity",
    "WTI": "Commodity",
    "NATGAS": "Commodity",
    "US30": "Index",
    "US100": "Index",
    "SPX500": "Index",
    "GER40": "Index",
    "DAX": "Index",
    "EURUSD": "Forex",
    "GBPUSD": "Forex",
    "USDJPY": "Forex",
    "USDCHF": "Forex",
    "AUDUSD": "Forex",
    "NZDUSD": "Forex",
    "USDCAD": "Forex",
}


def get_asset_type(symbol: str, config_path: str = "assets_config.json") -> str:
    """
    Get asset type from configuration file.

    Args:
        symbol: Trading symbol to check
        config_path: Path to assets configuration file

    Returns:
        str: Asset type (Crypto, Forex, etc.) or "Unknown" if not found
    """
    symbol = symbol.upper()

    # First check the quick lookup dictionary
    if symbol in COMMON_SYMBOLS:
        return COMMON_SYMBOLS[symbol]

    # Otherwise, try to load from config file
    try:
        if not os.path.exists(config_path):
            logger.warning(f"Asset config file not found: {config_path}")
            return "Unknown"

        with open(config_path, "r") as f:
            data = json.load(f)

            # Check if symbol exists in config
            if symbol in data:
                # Handle newer nested structure
                if isinstance(data[symbol], dict) and "type" in data[symbol]:
                    return data[symbol]["type"]
                # Handle older flat structure
                else:
                    return data.get(symbol, "Unknown")

            return "Unknown"
    except Exception as e:
        logger.error(f"Error getting asset type for {symbol}: {e}")
        return "Unknown"


def check_market_status(symbol: str) -> bool:
    """
    Check if the market for a specific symbol is currently open.

    Args:
        symbol: Trading symbol to check

    Returns:
        bool: True if market is open, False if closed
    """
    now = datetime.datetime.utcnow()
    hour = now.hour
    weekday = now.weekday()

    # Get asset type from config
    asset_type = get_asset_type(symbol)

    # For backward compatibility, map newer type names to older categories in MARKET_HOURS
    type_map = {
        "Crypto": "Crypto",
        "Commodity": "Commodities",
        "Index": "Indices",
        "Forex": "Forex",
        "Stock": "Indices",  # Default stocks to indices trading hours
    }

    mapped_type = type_map.get(asset_type, asset_type)

    # First try using the detailed market hours
    if asset_type in DETAILED_MARKET_HOURS:
        rules = DETAILED_MARKET_HOURS[asset_type]

        # Check if day is a trading day
        if weekday not in rules["days"]:
            logger.debug(
                f"Market for {symbol} ({asset_type}) is closed - weekend/holiday"
            )
            return False

        # Check if current hour is in any session
        for session in rules["sessions"]:
            if session["open"] <= hour < session["close"] or session["close"] == 24:
                return True

        logger.debug(
            f"Market for {symbol} ({asset_type}) is closed - outside trading hours"
        )
        return False

    # Fall back to legacy market hours if type not in detailed config
    if mapped_type not in MARKET_HOURS:
        logger.warning(f"Unknown asset type for {symbol}: {asset_type}")
        return True  # Default to allow if unknown

    rules = MARKET_HOURS[mapped_type]

    # Check trading day
    if weekday not in rules["days"]:
        return False

    # Handle markets that are open overnight/span across days
    if rules["open"] > rules["close"]:  # e.g. open at 22, close at 20 next day
        if hour >= rules["open"] or hour < rules["close"]:
            return True
    elif rules["close"] == 24:  # Special case for 24-hour markets
        return True
    else:  # Regular market hours
        if rules["open"] <= hour < rules["close"]:
            return True

    return False


def get_market_hours(symbol: str) -> Dict:
    """
    Get market hours for a specific symbol.

    Args:
        symbol: Trading symbol

    Returns:
        dict: Market hours configuration for this asset type
    """
    asset_type = get_asset_type(symbol)

    # Check detailed hours first
    if asset_type in DETAILED_MARKET_HOURS:
        return DETAILED_MARKET_HOURS[asset_type]

    # Fall back to basic hours
    type_map = {
        "Crypto": "Crypto",
        "Commodity": "Commodities",
        "Index": "Indices",
        "Forex": "Forex",
        "Stock": "Indices",
    }
    mapped_type = type_map.get(asset_type, "Unknown")

    if mapped_type in MARKET_HOURS:
        return MARKET_HOURS[mapped_type]

    # Default to 24/7 if unknown
    return {"open": 0, "close": 24, "days": [0, 1, 2, 3, 4, 5, 6]}


def get_market_reopen_time(symbol: str) -> Optional[Tuple[int, int]]:
    """
    Calculate when the market will reopen for a specific symbol.

    Args:
        symbol: Trading symbol

    Returns:
        tuple: (hours, minutes) until market reopens, or None if market is open
    """
    if check_market_status(symbol):
        return None  # Market is already open

    now = datetime.datetime.utcnow()
    asset_type = get_asset_type(symbol)

    # Get detailed market hours if available
    if asset_type in DETAILED_MARKET_HOURS:
        rules = DETAILED_MARKET_HOURS[asset_type]

        # Find the next trading day and session
        for days_ahead in range(7):  # Check up to 7 days ahead
            future_date = now + datetime.timedelta(days=days_ahead)
            future_weekday = future_date.weekday()

            # Skip non-trading days
            if future_weekday not in rules["days"]:
                continue

            # Check each session for this day
            for session in rules["sessions"]:
                session_start = future_date.replace(
                    hour=session["open"], minute=0, second=0, microsecond=0
                )

                # If this session starts in the future
                if session_start > now:
                    time_diff = session_start - now
                    hours = time_diff.days * 24 + time_diff.seconds // 3600
                    minutes = (time_diff.seconds % 3600) // 60
                    return (hours, minutes)

    # Fallback for simpler rules
    type_map = {
        "Crypto": "Crypto",
        "Commodity": "Commodities",
        "Index": "Indices",
        "Forex": "Forex",
    }
    mapped_type = type_map.get(asset_type, "Unknown")

    if mapped_type in MARKET_HOURS:
        rules = MARKET_HOURS[mapped_type]

        # Find the next trading day
        for days_ahead in range(7):
            future_date = now + datetime.timedelta(days=days_ahead)
            future_weekday = future_date.weekday()

            if future_weekday in rules["days"]:
                # Create datetime for market open time
                reopen_time = future_date.replace(
                    hour=rules["open"], minute=0, second=0, microsecond=0
                )

                # If market opens today but later
                if days_ahead == 0 and reopen_time < now:
                    # Add a day to get the next opening time
                    reopen_time = reopen_time + datetime.timedelta(days=1)

                time_diff = reopen_time - now
                hours = time_diff.days * 24 + time_diff.seconds // 3600
                minutes = (time_diff.seconds % 3600) // 60
                return (hours, minutes)

    # Default fallback
    return (24, 0)  # Return 24 hours as default


def get_market_status_message(symbol: str) -> str:
    """
    Generate a friendly message about market status for a symbol.

    Args:
        symbol: Trading symbol

    Returns:
        str: Message about market status, or empty string if market is open
    """
    if check_market_status(symbol):
        return ""  # Market is open

    reopen = get_market_reopen_time(symbol)
    asset_type = get_asset_type(symbol)

    if reopen:
        hours, minutes = reopen
        time_str = f"{hours} hours"
        if minutes > 0:
            time_str += f" and {minutes} minutes"

        if asset_type == "Crypto":
            return f"⚠️ Unexpected issue: {symbol} markets should be open 24/7"

        # Different messages for weekends vs after hours
        now = datetime.datetime.utcnow()
        weekday = now.weekday()

        if weekday in [5, 6]:  # Weekend
            return f"⛔ {symbol} market is closed for the weekend. Will reopen in {time_str}."
        else:
            return f"⛔ {symbol} market is currently closed. Will reopen in {time_str}."

    return f"⛔ {symbol} market is currently closed."


def get_available_assets(config_path: str = "assets_config.json") -> Dict:
    """
    Get all available assets from configuration file.

    Args:
        config_path: Path to assets configuration file

    Returns:
        dict: Dictionary of all available assets
    """
    try:
        if not os.path.exists(config_path):
            logger.warning(f"Asset config file not found: {config_path}")
            return {}

        with open(config_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading assets config: {e}")
        return {}


def get_assets_by_type(
    asset_type: str, config_path: str = "assets_config.json"
) -> List[str]:
    """
    Get all assets of a specific type.

    Args:
        asset_type: Asset type to filter by (Crypto, Forex, etc.)
        config_path: Path to assets configuration file

    Returns:
        list: List of symbols matching the requested asset type
    """
    assets = get_available_assets(config_path)
    matching_assets = []

    # Handle newer nested structure in config
    for symbol, data in assets.items():
        if isinstance(data, dict) and "type" in data:
            if data["type"] == asset_type:
                matching_assets.append(symbol)
        # Handle older flat structure
        elif data == asset_type:
            matching_assets.append(symbol)

    return matching_assets


def check_all_markets(asset_types: List[str] = None) -> Dict[str, bool]:
    """
    Check status of all markets by asset type.

    Args:
        asset_types: List of asset types to check, or None for all types

    Returns:
        dict: Dictionary with asset types as keys and boolean status as values
    """
    if asset_types is None:
        asset_types = ["Crypto", "Forex", "Commodity", "Index", "Stock"]

    status = {}
    for asset_type in asset_types:
        # Use a representative symbol for each asset type
        symbols = {
            "Crypto": "BTCUSD",
            "Forex": "EURUSD",
            "Commodity": "XAUUSD",
            "Index": "US30",
            "Stock": "AAPL",
        }

        symbol = symbols.get(asset_type)
        if symbol:
            status[asset_type] = check_market_status(symbol)
        else:
            status[asset_type] = False

    return status


if __name__ == "__main__":
    # Set up logging for direct script execution
    logging.basicConfig(level=logging.INFO)

    print("Market Status Checker - Test Mode")
    print("=" * 50)

    # Test common symbols
    test_symbols = ["BTCUSD", "EURUSD", "XAUUSD", "US30", "GER40"]

    now = datetime.datetime.utcnow()
    print(f"Current UTC time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    print("Testing individual symbols:")
    for symbol in test_symbols:
        asset_type = get_asset_type(symbol)
        status = check_market_status(symbol)
        status_text = "🟢 OPEN" if status else "🔴 CLOSED"

        print(f"{symbol} ({asset_type}): {status_text}")

        if not status:
            reopen = get_market_reopen_time(symbol)
            if reopen:
                hours, minutes = reopen
                print(f"  Reopens in: {hours}h {minutes}m")

            msg = get_market_status_message(symbol)
            print(f"  Status message: {msg}")

    print("-" * 50)
    print("Testing market-wide status:")

    market_status = check_all_markets()
    for market, status in market_status.items():
        status_text = "🟢 OPEN" if status else "🔴 CLOSED"
        print(f"{market}: {status_text}")

    print("-" * 50)
    print("Available assets by type:")

    for asset_type in ["Crypto", "Forex", "Commodity", "Index"]:
        assets = get_assets_by_type(asset_type)
        print(
            f"{asset_type}: {', '.join(assets[:5])}{'...' if len(assets) > 5 else ''}"
        )
