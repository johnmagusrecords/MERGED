"""
signal_formatter.py

Provides functions to format trading signals into human-readable messages
for different platforms (e.g., generic Telegram and MetaTrader 5).
"""

from typing import Dict, Any, List


def format_signal(signal: Dict[str, Any], **kwargs) -> str:
    """
    Convert a signal dictionary into a multi-line text message.

    Expected keys in `signal`:
      - symbol: str       # trading symbol, e.g. "BTCUSD"
      - direction: str    # "BUY" or "SELL"
      - entry: float      # entry price
      - stop_loss: float  # stop loss price
      - take_profits: List[float]  # list of TP levels
      - timeframe: str    # e.g. "1h", "4h"

    Behavior:
      1. Always include:
         • Signal: <symbol>
         • Action: <direction>
         • Entry: <entry price>
         • SL: <stop loss>
      2. If `take_profits` is non-empty, append:
         • TPs: comma-separated list of each take profit
      3. If `timeframe` is provided, append:
         • Timeframe: <timeframe>
      4. On any exception or missing data, return "Invalid signal data."

    Returns:
      A formatted string with each field on its own line.
    """
    try:
        symbol = signal.get("symbol", "")
        direction = signal.get("direction", "")
        entry = signal.get("entry", "")
        stop_loss = signal.get("stop_loss", "")
        take_profits = signal.get("take_profits", []) or []
        timeframe = signal.get("timeframe", "")

        lines: List[str] = [
            f"Signal: {symbol}",
            f"Action: {direction}",
            f"Entry: {entry}",
            f"SL: {stop_loss}"
        ]

        if take_profits:
            profits = ", ".join(str(tp) for tp in take_profits)
            lines.append(f"TPs: {profits}")

        if timeframe:
            lines.append(f"Timeframe: {timeframe}")

        return "\n".join(lines)

    except Exception:
        return "Invalid signal data."


def format_signal_mt5(signal: Dict[str, Any], **kwargs) -> str:
    """
    Alias for format_signal with MT5-specific adjustments if needed.
    Currently identical to format_signal.
    """
    return format_signal(signal, **kwargs)
