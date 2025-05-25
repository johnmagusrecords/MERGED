"""
Parameter classes for trading operations.

This module provides parameter classes for various trading operations to reduce function argument count
and improve code maintainability.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Union


@dataclass
class TradeParameters:
    """Parameters for opening a trade."""

    symbol: str
    action: str
    take_profit: float
    stop_loss: float
    confidence: float
    source: str = "analysis"
    risk_percent: Optional[float] = None


@dataclass
class NotificationParameters:
    """Parameters for trade notifications."""

    symbol: str
    action: str
    entry_price: float
    take_profit: float
    stop_loss: float
    confidence: float


@dataclass
class ExitLevelParameters:
    """Parameters for exit level calculations."""

    action: str
    current_price: float
    support_resistance: Optional[Dict[str, List[Union[str, float]]]] = None


@dataclass
class TradeExecutionParameters:
    """Parameters for trade execution and tracking."""

    symbol: str
    action: str
    position_size: float
    take_profit: float
    stop_loss: float
    current_price: float
    confidence: float
    source: str
