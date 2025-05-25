import logging
import os
import sys

import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def test_telegram_token():
    """Test if Telegram token is valid and configured properly"""
    load_dotenv()

    # Get token from environment variables
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    group_id = os.getenv("TELEGRAM_GROUP_ID")

    print("\n======== TELEGRAM TOKEN TEST ========")
    print(f"Bot Token: {'✅ Found' if token else '❌ Not found or empty'}")

    if not token:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN is not set in your .env file")
        print("Please update your .env file with a valid token")
        print("You can get a token from @BotFather on Telegram")
        return False

    if token == "your_telegram_bot_token_here":
        print("❌ ERROR: TELEGRAM_BOT_TOKEN is still set to the default placeholder")
        print("Please update your .env file with your actual token from @BotFather")
        return False

    # Check the token with Telegram API
    try:
        print("\nChecking token with Telegram API...")
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"❌ ERROR: Token invalid - Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

        data = response.json()
        if not data.get("ok"):
            print("❌ ERROR: Token rejected by Telegram API")
            print(f"Response: {data}")
            return False

        bot_info = data.get("result", {})
        print(f"✅ Token valid! Connected to bot: @{bot_info.get('username')}")
        print(f"   Bot name: {bot_info.get('first_name')}")

        # Check chat/group ID
        print(f"\nChat ID: {chat_id or 'Not set'}")
        print(f"Group ID: {group_id or 'Not set'}")

        if not (chat_id or group_id):
            print("⚠️ WARNING: No chat or group ID set. Messages may not be delivered.")
            print("Update TELEGRAM_CHAT_ID and/or TELEGRAM_GROUP_ID in your .env file")
            return True  # Token is valid, but IDs are missing

        # Try to send a test message
        target_id = group_id or chat_id
        print(f"\nSending test message to ID: {target_id}")

        message_url = f"https://api.telegram.org/bot{token}/sendMessage"
        message_data = {
            "chat_id": target_id,
            "text": "✅ MAGUS PRIME X Telegram test successful! Your bot is properly configured.",
            "parse_mode": "Markdown",
        }

        msg_response = requests.post(message_url, json=message_data, timeout=10)
        if msg_response.status_code != 200:
            print(
                f"❌ ERROR: Failed to send message - Status code: {msg_response.status_code}"
            )
            print(f"Response: {msg_response.text}")

            # Common group chat errors
            if "chat not found" in msg_response.text.lower():
                print("\n⚠️ HINT: For group chats, make sure:")
                print("1. The bot has been added to the group")
                print("2. The group ID starts with -100 (e.g., -1001234567890)")
                print("3. The bot has permission to send messages in the group")

            return False

        msg_data = msg_response.json()
        if msg_data.get("ok"):
            print("✅ Test message sent successfully!")
            print("\nYour Telegram configuration is working correctly!")
            return True
        else:
            print(f"❌ ERROR: Failed to send message: {msg_data}")
            return False

    except Exception as e:
        print(f"❌ ERROR: Failed to connect to Telegram API: {e}")
        return False


if __name__ == "__main__":
    result = test_telegram_token()

    if not result:
        print("\n======== FIX INSTRUCTIONS ========")
        print("1. Create a Telegram bot with @BotFather if you haven't already")
        print("2. Copy the bot token provided by @BotFather")
        print("3. Update your .env file with the correct token:")
        print("   TELEGRAM_BOT_TOKEN=your_actual_token_here")
        print("\nFor group chats:")
        print("1. Add your bot to the target group")
        print("2. Get the group ID (usually starts with -100)")
        print("3. Update TELEGRAM_GROUP_ID in your .env file\n")
        print("You can also run setup_telegram.py for an interactive setup.")
        sys.exit(1)
