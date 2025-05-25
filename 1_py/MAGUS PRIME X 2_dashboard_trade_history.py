"""
Trade history module for the dashboard.

This module provides classes for managing trade history records.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TradeHistoryEntry:
    """A single trade history entry."""

    timestamp: str
    symbol: str
    action: str
    take_profit: float
    stop_loss: float
    result: Optional[str] = None
