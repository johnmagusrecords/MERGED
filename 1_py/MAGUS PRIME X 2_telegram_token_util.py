import logging
import os

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Always load environment variables first
load_dotenv(override=True)


def get_telegram_token():
    """
    Get Telegram bot token from environment variables.
    Uses the standard os.getenv("TELEGRAM_BOT_TOKEN") pattern.
    """
    # Get token using the standard pattern
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    # Validate token
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return None

    if token == "your_telegram_bot_token_here":
        logger.error("TELEGRAM_BOT_TOKEN is still set to the default placeholder")
        return None

    # Log partial token for debugging (safely)
    if len(token) > 10:
        logger.info(f"Using Telegram token: {token[:5]}...{token[-5:]}")

    return token


def get_telegram_chat_id():
    """Get the primary chat ID to use for messaging"""
    # Try group ID first, then chat ID as fallback
    group_id = os.getenv("TELEGRAM_GROUP_ID")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    return group_id or chat_id


# Pre-loaded token for convenience
TELEGRAM_TOKEN = get_telegram_token()
TELEGRAM_CHAT_ID = get_telegram_chat_id()

if __name__ == "__main__":
    # When run directly, verify the token
    token = get_telegram_token()
    if token:
        print(f"✅ Telegram token loaded successfully: {token[:5]}...{token[-5:]}")
    else:
        print("❌ Failed to load Telegram token")

    chat_id = get_telegram_chat_id()
    if chat_id:
        print(f"✅ Telegram chat ID loaded: {chat_id}")
    else:
        print("❌ No Telegram chat ID found")
