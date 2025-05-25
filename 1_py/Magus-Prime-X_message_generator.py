"""
message_generator.py — Refactored
- Unified MarkdownV2 escaping
- Consolidated signal message building
- Robust fallback for missing templates
- Clean imports, no unused code
"""
import logging
from typing import Any, Dict
from telegram.helpers import escape_markdown as _escape

from config import CONFIG

logger = logging.getLogger(__name__)

__all__ = [
    "escape_markdown",
    "generate_message",
    "get_signal_message",
    "generate_signal_message",
    "get_recovery_message"
]


def escape_markdown(text: str) -> str:
    """Escape MarkdownV2 special characters for Telegram."""
    try:
        return _escape(text, version=2)
    except Exception:
        return text


def generate_message(template: str, **kwargs: Any) -> str:
    """Format a template string with provided kwargs."""
    try:
        return template.format(**kwargs)
    except Exception as e:
        logger.error(f"generate_message formatting error: {e}")
        return template


def get_signal_message(signal: Dict[str, Any]) -> str:
    """Construct a detailed MarkdownV2 signal message."""
    parts = []
    pair = signal.get('pair') or signal.get('symbol', '')
    if pair:
        parts.append(f"*Signal for:* {pair}")

    direction = signal.get('direction')
    if direction:
        parts.append(f"*Direction:* {direction}")

    entry = signal.get('entry') or signal.get('entry_price')
    if entry is not None:
        parts.append(f"*Entry:* {entry}")

    tps = signal.get('take_profits') or signal.get('tp_levels') or []
    for i, tp in enumerate(tps, start=1):
        parts.append(f"*TP{i}:* {tp}")

    sl = signal.get('stop_loss') or signal.get('sl_level')
    if sl is not None:
        parts.append(f"*SL:* {sl}")

    asset_type = signal.get('asset_type')
    if asset_type:
        parts.append(f"*Asset Type:* {asset_type}")

    strategy = signal.get('strategy_name') or signal.get('strategy')
    if strategy:
        parts.append(f"*Strategy:* {strategy}")

    hold_time = signal.get('hold_time') or signal.get('timeframe')
    if hold_time:
        parts.append(f"*Hold Time:* {hold_time}")

    commentary = signal.get('commentary')
    if commentary:
        parts.append(f"*Commentary:* {commentary}")

    text = "\n".join(parts)
    return escape_markdown(text)


def generate_signal_message(**kwargs: Any) -> str:
    """Alias to build a signal message from kwargs."""
    return get_signal_message(kwargs)


def get_recovery_message(*args: Any, **kwargs: Any) -> str:
    """Produce a recovery message via template or fallback."""
    try:
        from templates import get_recovery_message as _tmpl
        return _tmpl(*args, **kwargs)
    except ImportError:
        return "*Recovery:* No template available"
