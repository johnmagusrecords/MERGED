import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get Telegram token
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN:
    logger.error("Telegram token not found in environment variables")
    exit(1)


# Command handlers
async def start(update, context):
    await update.message.reply_text("MAGUS PRIME X Trading Bot is active")


async def status(update, context):
    await update.message.reply_text(
        "Bot is online and running\nUse /help to see available commands"
    )


async def help(update, context):
    await update.message.reply_text(
        "Available commands:\n"
        "/status - Check bot status\n"
        "/pause - Pause trading\n"
        "/resume - Resume trading\n"
        "/forcebuy SYMBOL [TP] [SL] - Force buy\n"
        "/forcesell SYMBOL [TP] [SL] - Force sell\n"
        "/signal SYMBOL - Get signal for symbol"
    )


async def test_message(update, context):
    await update.message.reply_text(
        "This is a test message to verify bot functionality"
    )


async def init_message():
    """Send initialization message"""
    try:
        if TELEGRAM_CHAT_ID:
            app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
            await app.bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text="🤖 Telegram Bot started in standalone mode",
            )
    except Exception as e:
        logger.error(f"Failed to send init message: {e}")


def main():
    # Initialize the Application
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("test", test_message))

    # Start the bot
    logger.info("Starting Telegram bot")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    # On startup, send an initialization message
    asyncio.run(init_message())

    # Then start the bot
    main()
