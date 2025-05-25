import logging
import os

import requests
from dotenv import load_dotenv, set_key

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def check_token(token):
    """Check if a Telegram token is valid"""
    if not token or token == "your_telegram_bot_token_here":
        return False, "Token not provided or using default placeholder"

    # Try to get bot info to verify token
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_name = data.get("result", {}).get("username", "Unknown")
                return True, f"Valid token for bot: @{bot_name}"
        return False, f"Invalid token: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Error checking token: {e}"


def setup_telegram_token():
    """Interactive setup for Telegram bot token"""
    load_dotenv()
    env_file = ".env"

    # Get current token
    current_token = os.getenv("TELEGRAM_BOT_TOKEN", "")

    print("\n=== Telegram Bot Token Setup ===")
    print("The Telegram bot token is required to send signals and alerts.")
    print(
        "You can get a token by messaging @BotFather on Telegram and creating a new bot."
    )

    # Check if current token is valid
    if current_token and current_token != "your_telegram_bot_token_here":
        is_valid, message = check_token(current_token)
        if is_valid:
            print(f"\n✅ Current token is valid! {message}")
            change = input("\nDo you want to change the token? (y/N): ").lower()
            if change != "y":
                print("Keeping current token.")
                return True
    else:
        print("\n❌ Current token is missing or invalid.")

    # Get new token
    new_token = input("\nEnter your Telegram bot token: ").strip()

    if not new_token:
        print("❌ No token provided. Setup canceled.")
        return False

    # Verify new token
    is_valid, message = check_token(new_token)
    if is_valid:
        print(f"\n✅ Token is valid! {message}")

        # Save to .env file
        set_key(env_file, "TELEGRAM_BOT_TOKEN", new_token)
        print(f"✅ Token saved to {env_file}")

        # Ask for chat ID
        print("\n=== Telegram Chat/Group ID Setup ===")
        print("The Chat ID is where the bot will send messages.")
        print("For groups, it usually starts with -100...")

        current_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        current_group_id = os.getenv("TELEGRAM_GROUP_ID", "")

        if current_chat_id and current_chat_id != "your_chat_id_here":
            print(f"\nCurrent Chat ID: {current_chat_id}")
        if current_group_id and current_group_id != "your_group_id_here":
            print(f"Current Group ID: {current_group_id}")

        change_chat_id = input(
            "\nDo you want to update the Chat/Group IDs? (y/N): "
        ).lower()
        if change_chat_id == "y":
            new_chat_id = input("Enter Chat ID (leave empty to keep current): ").strip()
            if new_chat_id:
                set_key(env_file, "TELEGRAM_CHAT_ID", new_chat_id)
                print(f"✅ Chat ID saved to {env_file}")

            new_group_id = input(
                "Enter Group ID (leave empty to keep current): "
            ).strip()
            if new_group_id:
                set_key(env_file, "TELEGRAM_GROUP_ID", new_group_id)
                print(f"✅ Group ID saved to {env_file}")

        return True
    else:
        print(f"\n❌ Token validation failed: {message}")
        print("Please make sure you're using a valid token from @BotFather.")
        return False


if __name__ == "__main__":
    if setup_telegram_token():
        print("\n✅ Telegram configuration completed successfully.")
    else:
        print("\n❌ Telegram configuration failed or was canceled.")
        print("You can run this script again later to complete the setup.")
