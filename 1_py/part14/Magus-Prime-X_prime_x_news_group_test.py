# prime_x_news_group_test.py
import os
import logging
import asyncio
from typing import Optional
from telegram_utils import send_message_sync  # Adjust import if needed

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ConfigurationError(Exception):
    """Raised when required configuration is missing for Telegram integration."""
    pass


def _get_env_var(name: str) -> str:
    """
    Retrieve an environment variable or raise ConfigurationError if missing.

    Args:
        name (str): The environment variable name.

    Returns:
        str: The value of the environment variable.

    Raises:
        ConfigurationError: If the variable is not set.
    """
    value = os.getenv(name)
    if not value:
        raise ConfigurationError(
            f"Missing required environment variable: {name}")
    return value


async def send_test_news_async() -> None:
    """
    Asynchronously send a test news message to the configured Telegram news group.

    Raises:
        ConfigurationError: If required environment variables are missing.
    """
    token = _get_env_var("TELEGRAM_BOT_TOKEN")
    chat_id = _get_env_var("TELEGRAM_NEWS_CHAT_ID")
    message = "📰 *Test News*\nThis is a test message from MAGUS PRIME X."
    try:
        await send_message_sync(token, chat_id, message, parse_mode="Markdown")
        logger.info("Test news message sent successfully.")
    except Exception as exc:
        logger.error(f"Failed to send test news message: {exc}")


def send_test_news() -> None:
    """
    Synchronously send a test news message to the configured Telegram news group.

    Raises:
        ConfigurationError: If required environment variables are missing.
    """
    asyncio.run(send_test_news_async())


def main() -> None:
    """
    Main entry point for sending a test news message to the Telegram group.
    """
    try:
        send_test_news()
    except ConfigurationError as e:
        logger.error(str(e))


if __name__ == "__main__":
    main()
