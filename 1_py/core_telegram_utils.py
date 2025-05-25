# telegram_utils.py
"""
Telegram Notification Utilities

This module provides functionality for sending notifications to Telegram.
"""
import asyncio
import logging
import os
import re
from typing import Optional

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Config object for defaults


class TelegramConfig:
    default_chat_id: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")
    bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")


config = TelegramConfig()

# Ensure exactly one Bot instance
_bot_instance = Bot(token=config.bot_token)

# Precompiled regex for MarkdownV2 escaping
_MARKDOWN_V2_ESCAPE_RE = re.compile(r'([_*\[\]()~`>#+\-=|{}.!])')


def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2.
    """
    return _MARKDOWN_V2_ESCAPE_RE.sub(r'\\\1', text)


async def _send_internal(
    text: str,
    chat_id: Optional[str] = None,
    parse_mode: str = ParseMode.MARKDOWN_V2
) -> bool:
    """
    Core coroutine to send a message via Telegram Bot API.
    """
    cid = chat_id or config.default_chat_id
    if not cid:
        logger.error("No chat_id specified for Telegram message.")
        return False
    try:
        await _bot_instance.send_message(
            chat_id=cid,
            text=text,
            parse_mode=parse_mode,
        )
        logger.info(f"Sent Telegram message to {cid}")
        return True
    except TelegramError as e:
        logger.error(f"Telegram send failed: {e}")
        return False


def send_text_sync(
    message: str,
    chat_id: Optional[str] = None,
    parse_mode: str = ParseMode.MARKDOWN_V2
) -> bool:
    """
    Synchronous wrapper for sending a Telegram message.
    Detects running event loop and schedules accordingly.
    """
    async def runner():
        return await _send_internal(message, chat_id, parse_mode)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        fut = asyncio.run_coroutine_threadsafe(runner(), loop)
        return fut.result()
    else:
        return asyncio.run(runner())


async def send_text(
    message: str,
    chat_id: Optional[str] = None,
    parse_mode: str = ParseMode.MARKDOWN_V2
) -> bool:
    """
    Async function to send a Telegram message.
    """
    return await _send_internal(message, chat_id, parse_mode)


class TradeNotification:
    """
    Utility for sending trade notifications via Telegram.
    """
    @staticmethod
    async def send_trade_async(
        trade_msg: str,
        chat_id: Optional[str] = None
    ) -> bool:
        """
        Send a trade notification asynchronously.
        """
        escaped = escape_markdown(trade_msg)
        return await send_text(escaped, chat_id)

    @staticmethod
    def send_trade_sync(
        trade_msg: str,
        chat_id: Optional[str] = None
    ) -> bool:
        """
        Send a trade notification synchronously.
        """
        escaped = escape_markdown(trade_msg)
        return send_text_sync(escaped, chat_id)

# Unit test stubs


def test_escape_markdown():
    """
    Unit test stub for escape_markdown.
    """
    assert escape_markdown("test*text_") == "test\\*text\\_"


def test_send_text_sync():
    """
    Unit test stub for send_text_sync.
    """
    # Should mock _bot_instance.send_message for real tests
    assert isinstance(send_text_sync("Hello", "12345"), bool)


def test_send_text():
    """
    Unit test stub for send_text.
    """
    # Should mock _bot_instance.send_message for real tests
    async def run():
        result = await send_text("Hello", "12345")
        assert isinstance(result, bool)
    asyncio.run(run())


def test_trade_notification_sync():
    """
    Unit test stub for TradeNotification.send_trade_sync.
    """
    assert isinstance(TradeNotification.send_trade_sync(
        "Trade *executed*", "12345"), bool)


def test_trade_notification_async():
    """
    Unit test stub for TradeNotification.send_trade_async.
    """
    async def run():
        result = await TradeNotification.send_trade_async("Trade *executed*", "12345")
        assert isinstance(result, bool)
    asyncio.run(run())
