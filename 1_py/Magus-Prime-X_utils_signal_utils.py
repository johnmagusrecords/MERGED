"""
signal_utils.py — Refactored
- Unified imports
- Clear `dispatch_signal` interface
- Robust fallback for external senders
- No unused code or imports
"""
import logging
from typing import Any, Dict, List, Optional

from message_generator import get_signal_message
from send_signal_helper import send_signal

logger = logging.getLogger(__name__)

__all__ = ["dispatch_signal"]


def dispatch_signal(
    symbol: str,
    direction: str,
    entry_price: float,
    tp_levels: List[float],
    sl_level: float,
    strategy_name: Optional[str] = None,
    holding_time: Optional[str] = None,
    commentary: Optional[str] = None,
    asset_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format and dispatch a trade signal.

    Builds the payload, generates the message, and calls the helper.
    Returns the helper's response dict.
    """
    # Build base signal dict
    signal = {
        'symbol': symbol,
        'direction': direction,
        'entry': entry_price,
        'take_profits': tp_levels,
        'stop_loss': sl_level,
    }

    if strategy_name:
        signal['strategy_name'] = strategy_name
    if holding_time:
        signal['hold_time'] = holding_time
    if commentary:
        signal['commentary'] = commentary
    if asset_type:
        signal['asset_type'] = asset_type

    # Generate message for logging
    try:
        msg = get_signal_message(signal)
        logger.info(f"Dispatching signal: {msg}")
    except Exception as e:
        logger.error(f"Message generation failed: {e}")

    # Dispatch via HTTP/Enhanced
    try:
        response = send_signal(
            pair=symbol,
            entry=entry_price,
            stop_loss=sl_level,
            tp1=tp_levels[0] if tp_levels else 0,
            tp2=tp_levels[1] if len(tp_levels) > 1 else None,
            tp3=tp_levels[2] if len(tp_levels) > 2 else None,
            timeframe=holding_time or '',
            type_=strategy_name or '',
            direction=direction,
            platform=asset_type or ''
        )
        logger.info(f"dispatch_signal response: {response}")
        return response
    except Exception as e:
        logger.error(f"dispatch_signal error: {e}")
        return {}
