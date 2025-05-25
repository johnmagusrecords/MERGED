# telegram_utils.py
"""
Telegram Notification Utilities

This module provides functionality for sending notifications to Telegram.
"""
import asyncio
import logging
import os
import re
from typing import Optional, Union

from telegram import Bot, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Precompiled regex for MarkdownV2 escaping
_MARKDOWN_V2_ESCAPE_RE = re.compile(r'([_*\[\]()~`>#+\-=|{}.!])')


def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2.
    """
    return _MARKDOWN_V2_ESCAPE_RE.sub(r'\\\1', text)


class TelegramSender:
    """
    Handles sending messages via the Telegram Bot API.

    Depends on an injected telegram.Bot instance.
    """
    def __init__(self, bot: Bot, default_chat_id: Optional[str] = None):
        """
        Initializes the TelegramSender.

        Args:
            bot: An instance of telegram.Bot.
            default_chat_id: The default chat ID to use if none is provided
                             when sending a message.
        """
        if not isinstance(bot, Bot):
             raise TypeError("bot must be an instance of telegram.Bot")
        self._bot = bot
        self._default_chat_id = default_chat_id

    async def _send_internal(
        self,
        text: str,
        chat_id: Optional[str] = None,
        parse_mode: str = ParseMode.MARKDOWN_V2
    ) -> bool:
        """
        Core coroutine to send a message via Telegram Bot API.
        """
        cid = chat_id or self._default_chat_id
        if not cid:
            logger.error("No chat_id specified for Telegram message.")
            return False
        try:
            await self._bot.send_message(
                chat_id=cid,
                text=text,
                parse_mode=parse_mode,
            )
            logger.info(f"Sent Telegram message to {cid}")
            return True
        except TelegramError as e:
            logger.error(f"Telegram send failed: {e}")
            return False
        except Exception as e:
             # Catch other potential exceptions during send
             logger.error(f"An unexpected error occurred while sending Telegram message: {e}")
             return False

    def send_text_sync(
        self,
        message: str,
        chat_id: Optional[str] = None,
        parse_mode: str = ParseMode.MARKDOWN_V2
    ) -> bool:
        """
        Synchronous wrapper for sending a Telegram message.
        Detects running event loop and schedules accordingly.
        """
        async def runner():
            return await self._send_internal(message, chat_id, parse_mode)

        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                fut = asyncio.run_coroutine_threadsafe(runner(), loop)
                return fut.result()
        except RuntimeError:
            pass
        
        return asyncio.run(runner())

    async def send_text(
        self,
        message: str,
        chat_id: Optional[str] = None,
        parse_mode: str = ParseMode.MARKDOWN_V2
    ) -> bool:
        """
        Async function to send a Telegram message.
        """
        return await self._send_internal(message, chat_id, parse_mode)


def test_escape_markdown():
    """
    Unit test stub for escape_markdown.
    """
    assert escape_markdown("test*text_") == "test\\*text\\_"
    assert escape_markdown("`code`") == "\\`code\\`"
    assert escape_markdown("[link](url)") == "\\[link\\]\\(url\\)"


# Define a command handler function for the /start command
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Hello! I am your friendly Telegram bot. How can I assist you today?')

# Define a command handler function for the /help command
def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('You can control me by using these commands:\n'
                              '/start - Welcome message\n'
                              '/help - List available commands\n'
                              'You can also send me a message and I will echo it back!')

# Define a message handler function for echoing text messages
def echo(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

def main() -> None:
    # Initialize the bot with the token from the environment variable
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found. Exiting...")
        return

    updater = Updater(bot_token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the command handlers (e.g., /start, /help)
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Register a message handler for echoing all received messages
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    logger.info("Bot started polling. Waiting for commands and messages...")

    # Run the bot until you stop it with Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
