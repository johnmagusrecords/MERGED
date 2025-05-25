import logging
import os

import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def escape_html(text):
    """Escape HTML special characters"""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def send_test_message():
    """Send a simple test message to Telegram with proper HTML escaping"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logger.error("Missing Telegram credentials")
        return False

    # Create a simple message with HTML formatting
    message = """
<b>TEST MESSAGE</b>

This is a <b>test</b> message with special characters: 
&lt;test&gt; &amp; &quot;quotes&quot;

Special characters must be properly escaped for HTML formatting to work.
"""

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        logger.info("Sending test message to Telegram...")
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()

        logger.info("✅ Message sent successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to send message: {e}")
        if hasattr(e, "response"):
            logger.error(f"Response: {e.response.text}")
        return False


if __name__ == "__main__":
    print("Testing Telegram message delivery...")
    if send_test_message():
        print("✅ Test passed! Check your Telegram for the message.")
    else:
        print("❌ Test failed. See logs for details.")
