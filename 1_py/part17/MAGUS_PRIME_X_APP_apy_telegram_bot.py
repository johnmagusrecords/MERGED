import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configure logging
logging.basicConfig(
    level=logging.INFO,
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
        self.application = ApplicationBuilder().token(self.token).build()
        self.setup_handlers()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Start command handler.
        """
        if update.message:
            await update.message.reply_text("Hello! I am your bot.")

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Help command handler.
        """
        if update.message:
            await update.message.reply_text("Here is how I can help you...")

    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Echo handler for text messages.
        """
        if update.message and update.message.text:
            await update.message.reply_text(update.message.text)

    def setup_handlers(self) -> None:
        """
        Setup command and message handlers.
        """
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

    def run(self) -> None:
        """
        Start the bot.
        """
        self.application.run_polling()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    bot = TelegramBot(TELEGRAM_BOT_TOKEN)
    bot.run()
