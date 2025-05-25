import os
import asyncio
import telegram
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Telegram credentials
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


class TelegramHelper:
    def __init__(self, token=None):
        self.token = token or TELEGRAM_BOT_TOKEN
        self.bot = telegram.Bot(token=self.token)

    async def send_message_async(self, chat_id=None, text=""):
        chat_id = chat_id or TELEGRAM_CHAT_ID
        try:
            await self.bot.send_message(chat_id=chat_id, text=text)
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

# Synchronous wrapper function that will be used in the main bot code


def send_telegram_message(message, chat_id=None):
    """
    This function provides a synchronous interface to send a Telegram message
    by running the async code in a new event loop
    """
    helper = TelegramHelper()

    # Create a new event loop for the async call
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        # Run the async function in the loop
        result = loop.run_until_complete(
            helper.send_message_async(chat_id, message))
        return result
    finally:
        loop.close()


# Test the function if this file is run directly
if __name__ == "__main__":
    message = "Test message from Telegram Helper"
    print(f"Sending test message: {message}")
    result = send_telegram_message(message)
    print(f"Message sent: {result}")
