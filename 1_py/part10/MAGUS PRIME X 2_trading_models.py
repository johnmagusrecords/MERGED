"""
Trading Models Module

This module contains data models and structures used for trading operations.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# File paths for persistence
TRADE_HISTORY_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "trade_history.json"
)
EQUITY_CURVE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "equity_curve.csv"
)

# Ensure data directory exists
os.makedirs(os.path.dirname(TRADE_HISTORY_FILE), exist_ok=True)


class TradeParams:
    """Model for trade parameters."""

    def __init__(self, symbol: str, direction: str, **kwargs) -> None:
        """Initialize trade parameters.

        Args:
            symbol: Market symbol to trade
            direction: Trade direction ('BUY' or 'SELL')

        Keyword Args:
            quantity: Trade size (default: 1.0)
            take_profit: Take profit level
            stop_loss: Stop loss level

        Raises:
            ValueError: If required parameters are invalid
        """
        if not symbol:
            raise ValueError("Symbol must be specified")

        if direction not in ["BUY", "SELL"]:
            raise ValueError("Direction must be 'BUY' or 'SELL'")

        quantity = kwargs.get("quantity", 1.0)
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        self.symbol = symbol
        self.direction = direction
        self.quantity = quantity
        self.take_profit = kwargs.get("take_profit")
        self.stop_loss = kwargs.get("stop_loss")

    def to_dict(self) -> Dict[str, Any]:
        """Convert trade parameters to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of trade parameters
        """
        return {
            "symbol": self.symbol,
            "direction": self.direction,
            "quantity": self.quantity,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TradeParams":
        """Create TradeParams from dictionary.

        Args:
            data: Dictionary with trade parameters

        Returns:
            TradeParams: New instance
        """
        return cls(
            symbol=data.get("symbol"),
            direction=data.get("direction"),
            quantity=float(data.get("quantity", 1.0)),
            take_profit=data.get("take_profit"),
            stop_loss=data.get("stop_loss"),
        )


def get_trade_history() -> List[Dict[str, Any]]:
    """Load the trade history from file.

    Returns:
        List[Dict[str, Any]]: List of trade records or empty list if no history
    """
    if not os.path.exists(TRADE_HISTORY_FILE):
        return []

    try:
        with open(TRADE_HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load trade history: {e}")
        return []


def save_trade_history(trades: List[Dict[str, Any]]) -> bool:
    """Save the trade history to file.

    Args:
        trades: List of trade records

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(TRADE_HISTORY_FILE, "w") as f:
            json.dump(trades, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Failed to save trade history: {e}")
        return False


def add_trade_record(trade_data: Dict[str, Any]) -> bool:
    """Add a new trade record to the history.

    Args:
        trade_data: Trade record details

    Returns:
        bool: True if successful, False otherwise
    """
    trades = get_trade_history()

    # Add timestamp if not present
    if "Timestamp" not in trade_data:
        trade_data["Timestamp"] = datetime.now().isoformat()

    trades.append(trade_data)
    return save_trade_history(trades)


def clear_trade_history() -> None:
    """Clear all trade history data."""
    if os.path.exists(TRADE_HISTORY_FILE):
        os.remove(TRADE_HISTORY_FILE)
        logging.info("Trade history cleared.")


def calculate_trade_statistics(trades: List[Dict[str, Any]]) -> Tuple[float, float]:
    """Calculate trading statistics from trade history.

    Args:
        trades: List of trade records

    Returns:
        tuple: (win_rate, pnl) statistics
    """
    if not trades:
        return 0.0, 0.0

    win_rate = calculate_win_rate(trades)
    pnl = calculate_profit_loss(trades)

    return win_rate, pnl


def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
    """Calculate win rate percentage from trades.

    Args:
        trades: List of trade records

    Returns:
        float: Win rate as a percentage
    """
    wins = sum(1 for t in trades if t.get("Result") == "WIN")
    losses = sum(1 for t in trades if t.get("Result") == "LOSS")
    total = wins + losses

    return (wins / total * 100) if total > 0 else 0.0


def calculate_profit_loss(trades: List[Dict[str, Any]]) -> float:
    """Calculate total profit/loss from trades.

    Args:
        trades: List of trade records

    Returns:
        float: Total profit/loss
    """
    pnl = 0.0

    for trade in trades:
        result = trade.get("Result")
        if result not in ("WIN", "LOSS"):
            continue

        pnl += calculate_trade_pl(trade, result)

    return pnl


def calculate_trade_pl(trade: Dict[str, Any], result: str) -> float:
    """Calculate profit/loss for a single trade.

    Args:
        trade: Trade record
        result: Trade result ('WIN' or 'LOSS')

    Returns:
        float: Profit/loss amount for this trade
    """
    # Use direct PL value if available
    if "PL" in trade and trade["PL"] is not None:
        return float(trade["PL"])

    # Otherwise calculate based on TP and SL
    trade_value = abs(float(trade.get("TP", 0)) - float(trade.get("SL", 0)))

    return trade_value if result == "WIN" else -trade_value


def update_equity_curve(timestamp: datetime, balance: float) -> None:
    """Update the equity curve file with current balance.

    Args:
        timestamp: Timestamp for the equity point
        balance: Account balance at that time
    """
    df = pd.DataFrame([[timestamp, balance]], columns=["Time", "Balance"])
    df.to_csv(
        EQUITY_CURVE_FILE,
        mode="a",
        header=not os.path.exists(EQUITY_CURVE_FILE),
        index=False,
    )


def load_equity_curve() -> Optional[pd.DataFrame]:
    """Load the equity curve data.

    Returns:
        Optional[pd.DataFrame]: Equity curve data or None on error
    """
    if os.path.exists(EQUITY_CURVE_FILE):
        try:
            df = pd.read_csv(EQUITY_CURVE_FILE)
            df["Time"] = pd.to_datetime(df["Time"])
            return df
        except Exception as e:
            logging.error(f"Failed to load equity curve: {e}")
            return None
    return None
