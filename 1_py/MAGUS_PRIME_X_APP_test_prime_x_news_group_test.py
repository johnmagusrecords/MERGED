import os
import sys
import logging
import asyncio
from typing import Optional

# Add project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.telegram_utils import send_plain_message  # Use the new plain message function

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
    # Use Optional[str] for a custom message from environment
    custom_message: Optional[str] = os.getenv("TELEGRAM_TEST_MESSAGE")
    message = custom_message if custom_message is not None else "📰 *Test News*\nThis is a test message from MAGUS PRIME X."
    try:
        # The send_plain_message function is synchronous, so run it in executor
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, lambda: send_plain_message(chat_id, message))
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
