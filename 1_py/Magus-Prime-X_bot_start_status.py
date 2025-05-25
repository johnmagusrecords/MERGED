import os
import logging
from dataclasses import dataclass
from typing import Optional

from telegram_utils import send_text_sync, escape_markdown

# Module-level logger
logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required bot configuration is missing."""


@dataclass(frozen=True)
class BotConfig:
    """Immutable configuration for the bot."""
    bot_token: str
    status_chat_id: str
    default_chat_id: str


def _get_env_var(name: str) -> str:
    """Fetch an environment variable or raise ConfigurationError if missing."""
    value = os.getenv(name)
    if not value:
        logger.error(f"Missing required environment variable: {name}")
        raise ConfigurationError(
            f"Missing required environment variable: {name}")
    return value


# Validate environment at import time
try:
    _BOT_TOKEN = _get_env_var("TELEGRAM_BOT_TOKEN")
    _STATUS_CHAT_ID = _get_env_var("STATUS_CHAT_ID")
    _DEFAULT_CHAT_ID = _get_env_var("TELEGRAM_CHAT_ID")
except ConfigurationError as e:
    raise

DEFAULT_CONFIG = BotConfig(
    bot_token=_BOT_TOKEN,
    status_chat_id=_STATUS_CHAT_ID,
    default_chat_id=_DEFAULT_CHAT_ID,
)


class BotStatusNotifier:
    """Notifier for bot status updates via Telegram."""

    def __init__(self, cfg: BotConfig = DEFAULT_CONFIG) -> None:
        """
        Initialize the notifier with the given configuration.

        Args:
            cfg (BotConfig): The bot configuration.
        """
        self.cfg = cfg

    def notify_start(self) -> bool:
        """
        Notify that the bot has started.

        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        return self._send_status("start")

    def notify_stop(self) -> bool:
        """
        Notify that the bot has stopped.

        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        return self._send_status("stop")

    def notify_online(self) -> bool:
        """
        Notify that the server is online.

        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        return self.notify_server_status(online=True)

    def notify_offline(self) -> bool:
        """
        Notify that the server is offline.

        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        return self.notify_server_status(online=False)

    def notify_server_status(self, online: bool) -> bool:
        """
        Notify about the server's online/offline status.

        Args:
            online (bool): True if the server is online, False if offline.

        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        status = "online" if online else "offline"
        return self._send_status(status)

    def _send_status(self, status: str) -> bool:
        """
        Send a status notification message.

        Args:
            status (str): The status to notify ("start", "stop", "online", "offline").

        Returns:
            bool: True if the notification was sent successfully, False otherwise.
        """
        message = self._format_message(status)
        chat_id = self.cfg.status_chat_id
        logger.info(f"Sending '{status}' notification to chat_id={chat_id}")
        try:
            success = send_text_sync(message, chat_id)
            if success:
                logger.info(f"Notification '{status}' sent successfully.")
            else:
                logger.error(f"Failed to send notification '{status}'.")
            return success
        except Exception as exc:
            logger.error(
                f"Exception while sending notification '{status}': {exc}")
            return False

    def _format_message(self, status: str) -> str:
        """
        Format the status message with emoji and escape for MarkdownV2.

        Args:
            status (str): The status ("start", "stop", "online", "offline").

        Returns:
            str: The formatted and escaped message.
        """
        emoji = self._status_to_emoji(status)
        text = f"{emoji} Bot status: *{status.capitalize()}*"
        return escape_markdown(text)

    def _status_to_emoji(self, status: str) -> str:
        """
        Map status to corresponding emoji.

        Args:
            status (str): The status string.

        Returns:
            str: The emoji representing the status.
        """
        mapping = {
            "start": "🚀",
            "stop": "🛑",
            "online": "✅",
            "offline": "❌",
        }
        return mapping.get(status, "ℹ️")


def log_escaped_message():
    """
    Log an escaped message for demonstration.
    """
    message = "This is a *bold* message with _italic_ text."
    escaped_message = escape_markdown(message)
    logger.info(f"Escaped Message: {escaped_message}")


# Example usage
if __name__ == "__main__":
    try:
        notifier = BotStatusNotifier()
        notifier.notify_start()
        # Simulate server status
        notifier.notify_online()
        log_escaped_message()
    except Exception as e:
        logger.error(f"Error in bot status notifier: {e}")
