import logging
import os
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.error import TelegramError
from telegram import Update
from config import LOG_LEVEL

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment and initialize Telegram bot
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or ""
if TELEGRAM_BOT_TOKEN == "":
    raise RuntimeError("TELEGRAM_BOT_TOKEN is not set in environment.")


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.setup_handlers()

    async def start(self, update: Update, context: CallbackContext) -> None:
        """
        Start command handler.
        """
        await update.message.reply_text("Hello! I am your bot.")

    async def help(self, update: Update, context: CallbackContext) -> None:
        """
        Help command handler.
        """
        await update.message.reply_text("Here is how I can help you...")

    async def echo(self, update: Update, context: CallbackContext) -> None:
        """
        Echo handler for text messages.
        """
        await update.message.reply_text(update.message.text)

    def setup_handlers(self) -> None:
        """
        Setup command and message handlers.
        """
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_handler(MessageHandler(
            Filters.text & ~Filters.command, self.echo))

    def run(self) -> None:
        """
        Start the bot.
        """
        self.updater.start_polling()
        self.updater.idle()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    bot.run()