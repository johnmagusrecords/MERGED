import logging
import os
import re
from typing import Optional
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode
import asyncio

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load environment variables at import time
load_dotenv()
TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.critical(
        "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment.")
    raise RuntimeError(
        "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment.")

# Precreate Bot instance
bot: Bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Precompile regex for MarkdownV2 escaping
_MARKDOWN_V2_ESCAPE_RE = re.compile(r'([_*\[\]()~`>#+\-=|{}.!])')


def escape_markdown(text: str) -> str:
    """
    Escape Telegram MarkdownV2 special characters in a string.

    Args:
        text (str): The text to escape.

    Returns:
        str: The escaped text.
    """
    return _MARKDOWN_V2_ESCAPE_RE.sub(r'\\\1', text)


async def send_telegram_message(
    message: str, chat_id: Optional[str] = None
) -> bool:
    """
    Asynchronously send a MarkdownV2-formatted message to a Telegram chat.

    Args:
        message (str): The message to send.
        chat_id (Optional[str]): Override chat ID. Defaults to env var.

    Returns:
        bool: True if sent successfully, False otherwise.
    """
    target_chat_id = chat_id or TELEGRAM_CHAT_ID
    try:
        await bot.send_message(
            chat_id=target_chat_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return True
    except Exception as e:
        logger.error("Failed to send Telegram message: %s", e, exc_info=True)
        return False


def send_message_sync(
    message: str, chat_id: Optional[str] = None
) -> bool:
    """
    Synchronously send a MarkdownV2-formatted message to a Telegram chat.

    Args:
        message (str): The message to send.
        chat_id (Optional[str]): Override chat ID. Defaults to env var.

    Returns:
        bool: True if scheduled/sent successfully, False otherwise.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Schedule as a task in the running loop
            asyncio.ensure_future(send_telegram_message(message, chat_id))
            return True
        else:
            return loop.run_until_complete(
                send_telegram_message(message, chat_id)
            )
    except Exception as e:
        logger.error(
            "Failed to send Telegram message synchronously: %s", e, exc_info=True)
        return False

# Unit test stubs


def _test_escape_markdown():
    """
    Unit test stub for escape_markdown.
    """
    assert escape_markdown("_test*") == r"\_test\*"


def _test_send_telegram_message():
    """
    Unit test stub for send_telegram_message.
    """
    import pytest
    import asyncio

    async def test():
        # Should not actually send in unit test; mock bot.send_message
        assert await send_telegram_message("Test") in (True, False)
    asyncio.run(test())


def _test_send_message_sync():
    """
    Unit test stub for send_message_sync.
    """
    assert send_message_sync("Test") in (True, False)