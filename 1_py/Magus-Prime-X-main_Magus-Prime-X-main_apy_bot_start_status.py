import os
from dotenv import load_dotenv

# Ensure .env overrides and clear inherited token
os.environ.pop("TELEGRAM_BOT_TOKEN", None)
load_dotenv(override=True)

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info(f"Using TELEGRAM_BOT_TOKEN={os.getenv('TELEGRAM_BOT_TOKEN')}")
logging.info(f"Using STATUS_CHAT_ID={os.getenv('STATUS_CHAT_ID')}")

from dataclasses import dataclass
from telegram import Bot
import asyncio
import telegram.error

def send_text_sync(message: str, chat_id: str) -> bool:
    async def send_message():
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set.")
        bot = Bot(token=bot_token)
        try:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
            return True
        except telegram.error.InvalidToken as e:
            logging.error(f"Invalid Telegram bot token: {e}")
            return False
        except telegram.error.TelegramError as e:
            logging.error(f"Telegram API error: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error sending message: {e}")
            return False

    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(send_message())
    except Exception as e:
        logging.error(f"Exception in send_text_sync: {e}")
        return False

def escape_markdown(text: str) -> str:
    escape_chars = '_*[]()~`>#+-=|{}.!'
    return ''.join('\\' + char if char in escape_chars else char for char in text)

# Module-level logger
logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Raised when required bot configuration is missing."""

@dataclass
class BotConfig:
    bot_token: str
    status_chat_id: str
    default_chat_id: str

def _get_env_var(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        logger.error(f"Missing required environment variable: {name}")
        raise ConfigurationError(f"Missing required environment variable: {name}")
    return value

def _load_config() -> BotConfig:
    try:
        bot_token = _get_env_var("TELEGRAM_BOT_TOKEN")
        status_chat_id = _get_env_var("STATUS_CHAT_ID")
        default_chat_id = _get_env_var("TELEGRAM_CHAT_ID")
    except ConfigurationError as e:
        raise

    return BotConfig(
        bot_token=bot_token,
        status_chat_id=status_chat_id,
        default_chat_id=default_chat_id,
    )

DEFAULT_CONFIG = _load_config()

class BotStatusNotifier:
    """Notifier for bot status updates via Telegram."""

    def __init__(self, cfg: BotConfig = DEFAULT_CONFIG) -> None:
        self.cfg = cfg

    def notify_start(self) -> bool:
        try:
            return self._send_status("start")
        except Exception as exc:
            logger.error(f"Exception in notify_start: {exc}")
            return False

    def notify_stop(self) -> bool:
        try:
            return self._send_status("stop")
        except Exception as exc:
            logger.error(f"Exception in notify_stop: {exc}")
            return False

    def notify_online(self) -> bool:
        return self.notify_server_status(online=True)

    def notify_offline(self) -> bool:
        return self.notify_server_status(online=False)

    def notify_server_status(self, online: bool) -> bool:
        status = "online" if online else "offline"
        try:
            return self._send_status(status)
        except Exception as exc:
            logger.error(f"Exception in notify_server_status: {exc}")
            return False

    def _send_status(self, status: str) -> bool:
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
            logger.error(f"Exception while sending notification '{status}': {exc}")
            return False

    def _format_message(self, status: str) -> str:
        emoji = self._status_to_emoji(status)
        text = f"{emoji} Bot status: *{status.capitalize()}*"
        return escape_markdown(text)

    def _status_to_emoji(self, status: str) -> str:
        mapping = {
            "start": "🚀",
            "stop": "🛑",
            "online": "✅",
            "offline": "❌",
        }
        return mapping.get(status, "ℹ️")

def log_escaped_message():
    message = "This is a *bold* message with _italic_ text."
    escaped_message = escape_markdown(message)
    logger.info(f"Escaped Message: {escaped_message}")

def start_bot():
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    status_chat_id = os.environ.get('STATUS_CHAT_ID')
    default_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not status_chat_id or not default_chat_id:
        logging.error("Environment variables for bot configuration are not set.")
        return
    
    config = BotConfig(
        bot_token=bot_token,
        status_chat_id=status_chat_id,
        default_chat_id=default_chat_id
    )
    
    bot = Bot(token=config.bot_token)
    # Your bot logic here

# Example usage
if __name__ == "__main__":
    notifier = BotStatusNotifier()
    success = notifier.notify_start()
    if success:
        logging.info("✅ Startup notification sent!")
        print("✅ Startup notification sent!")
    else:
        logging.error("❌ Failed to send startup notification.")
        print("❌ Failed to send startup notification.")