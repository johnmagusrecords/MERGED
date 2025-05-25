import asyncio
import logging
import os

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Make sure to load .env variables FIRST, before importing Telegram
load_dotenv(override=True)

# Get token from environment variables
token = os.getenv("TELEGRAM_BOT_TOKEN")
group_id = os.getenv("TELEGRAM_GROUP_ID")

# Now import Telegram modules AFTER loading environment variables
try:
    from telegram import Bot
    from telegram.error import InvalidToken, Unauthorized
except ImportError:
    logger.error(
        "Could not import Telegram modules. Install with: pip install python-telegram-bot"
    )
    exit(1)


async def send_test_message():
    """Send a test message to verify the bot is working"""
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return False

    logger.info(f"Using token: {token[:5]}...{token[-5:]}")

    try:
        # Initialize the bot with the token
        bot = Bot(token=token)

        # Get bot information
        bot_info = await bot.get_me()
        logger.info(f"Connected to bot: @{bot_info.username}")

        # Try to send a message if we have a group ID
        if group_id:
            logger.info(f"Sending test message to group ID: {group_id}")

            await bot.send_message(
                chat_id=group_id,
                text=" "
✅ Test message from MAGUS PRIME X minima + "l test bot.\nIf you can see this, your b + "ot token is working correctly!",
            )

            logger.info("Test message sent successfully!")
        else:
            logger.warning("No TELEGRAM_GROUP_ID set, skipping test message")

        return True
    except InvalidToken:
        logger.error("Invalid token error. The token was rejected by Telegram.")
        return False
    except Unauthorized:
        logger.error("Unauthorized error. The token is valid but not authorized.")
        return False
    except Exception as e:
        logger.error(f"Error: {type(e).__name__}: {e}")
        return False


async def main():
    """Main function that runs the test"""
    logger.info("Starting minimal Telegram bot test")
    success = await send_test_message()
    logger.info("Test completed: %s", "✅ SUCCESS" if success else "❌ FAILED")


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
