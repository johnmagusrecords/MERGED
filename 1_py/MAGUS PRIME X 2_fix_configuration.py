import logging
import os
import re

import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_openai_api_key(api_key):
    """Test if the OpenAI API key is valid"""
    if not api_key or not api_key.startswith("sk-"):
        return (
            False,
            "API key is missing or has invalid format (should start with 'sk-')",
        )

    url = "https://api.openai.com/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True, "API key is valid!"
        else:
            error_message = (
                response.json().get("error", {}).get("message", "Unknown error")
            )
            return False, f"API key verification failed: {error_message}"
    except Exception as e:
        return False, f"Error testing API key: {str(e)}"


def test_telegram_token(bot_token):
    """Test if the Telegram bot token is valid"""
    if not bot_token:
        return False, "Bot token is missing"

    url = f"https://api.telegram.org/bot{bot_token}/getMe"

    try:
        response = requests.get(url)
        if response.status_code == 200 and response.json().get("ok"):
            bot_name = response.json().get("result", {}).get("username")
            return True, f"Bot token is valid! Bot name: @{bot_name}"
        else:
            error_message = response.json().get("description", "Unknown error")
            return False, f"Bot token verification failed: {error_message}"
    except Exception as e:
        return False, f"Error testing bot token: {str(e)}"


def test_telegram_chat_id(bot_token, chat_id):
    """Test if the Telegram chat ID is valid and accessible by the bot"""
    if not bot_token or not chat_id:
        return False, "Bot token or chat ID is missing"

    # Handle @ notation for channels/groups
    if chat_id.startswith("@"):
        chat_id_clean = chat_id
    else:
        # Try to convert to integer for numerical IDs
        try:
            chat_id_clean = int(chat_id)
        except ValueError:
            chat_id_clean = chat_id

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id_clean,
        "text": " "
📊 MAGUS PRIME X Configuration Test: This + " is a test message to verify chat ID. Yo + "u can delete this message.",
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200 and response.json().get("ok"):
            message_id = response.json().get("result", {}).get("message_id")
            return True, f"Chat ID is valid! Test message sent (ID: {message_id})"
        else:
            error_message = response.json().get("description", "Unknown error")
            return False, f"Chat ID verification failed: {error_message}"
    except Exception as e:
        return False, f"Error testing chat ID: {str(e)}"


def update_env_file(env_path, updates):
    """Update values in the .env file"""
    # Load current content
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            content = f.read()
    else:
        content = ""

    # Process each update
    for key, value in updates.items():
        # Check if key exists in the file
        pattern = re.compile(f"^{key}=.*$", re.MULTILINE)
        if pattern.search(content):
            # Replace existing key
            content = pattern.sub(f"{key}={value}", content)
        else:
            # Add new key at the end
            if content and not content.endswith("\n"):
                content += "\n"
            content += f"{key}={value}\n"

    # Write back to file
    with open(env_path, "w") as f:
        f.write(content)

    return True


def main():
    """Main function to diagnose and fix configuration issues"""
    print("\n====== MAGUS PRIME X Configuration Diagnostic ======\n")

    # Load environment variables
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(env_path)

    # Check OpenAI API key
    print("Testing OpenAI API Key...")
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_valid, openai_message = test_openai_api_key(openai_api_key)
    print(f"  {'✅' if openai_valid else '❌'} {openai_message}")

    # Check Telegram bot token
    print("\nTesting Telegram Bot Token...")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_valid, telegram_message = test_telegram_token(telegram_token)
    print(f"  {'✅' if telegram_valid else '❌'} {telegram_message}")

    # Check Telegram chat ID
    print("\nTesting Telegram Chat ID...")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    chat_valid, chat_message = False, "Skipped (invalid bot token)"

    if telegram_valid:
        chat_valid, chat_message = test_telegram_chat_id(
            telegram_token, telegram_chat_id
        )
    print(f"  {'✅' if chat_valid else '❌'} {chat_message}")

    # Check Telegram group chat ID
    print("\nTesting Telegram Group Chat ID...")
    telegram_group_id = os.getenv("TELEGRAM_GROUP_CHAT_ID", "")
    group_valid, group_message = False, "Skipped (invalid bot token)"

    if telegram_valid and telegram_group_id:
        group_valid, group_message = test_telegram_chat_id(
            telegram_token, telegram_group_id
        )
        print(f"  {'✅' if group_valid else '❌'} {group_message}")
    else:
        print("  ⚠️ No group chat ID configured")

    # Summary and fixes
    print("\n====== Results and Fixes ======\n")

    needs_fixing = False
    updates = {}

    if not openai_valid:
        needs_fixing = True
        print("❌ OpenAI API Key needs to be fixed")
        new_key = input(
            "Enter a valid OpenAI API key (starts with 'sk-', press Enter to skip): "
        ).strip()
        if new_key:
            updates["OPENAI_API_KEY"] = new_key

    if not telegram_valid:
        needs_fixing = True
        print("❌ Telegram Bot Token needs to be fixed")
        new_token = input(
            "Enter a valid Telegram bot token (press Enter to skip): "
        ).strip()
        if new_token:
            updates["TELEGRAM_BOT_TOKEN"] = new_token

    if telegram_valid and not chat_valid:
        needs_fixing = True
        print("❌ Telegram Chat ID needs to be fixed")
        print("  To find your chat ID:")
        print("  1. Add @userinfobot to Telegram and send it a message")
        print(
            "  2. For a channel/group, forward a message from the channel to @userinfobot"
        )
        new_chat_id = input(
            "Enter a valid Telegram chat ID (press Enter to skip): "
        ).strip()
        if new_chat_id:
            updates["TELEGRAM_CHAT_ID"] = new_chat_id

    if telegram_valid and not group_valid and telegram_group_id:
        needs_fixing = True
        print("❌ Telegram Group Chat ID needs to be fixed")
        new_group_id = input(
            "Enter a valid Telegram group chat ID (press Enter to skip): "
        ).strip()
        if new_group_id:
            updates["TELEGRAM_GROUP_CHAT_ID"] = new_group_id
    elif telegram_valid and not telegram_group_id:
        print("⚠️ No Telegram Group Chat ID is configured (optional)")
        configure_group = (
            input("Would you like to configure a group chat ID? (y/n): ")
            .strip()
            .lower()
        )
        if configure_group == "y":
            new_group_id = input("Enter the Telegram group chat ID: ").strip()
            if new_group_id:
                updates["TELEGRAM_GROUP_CHAT_ID"] = new_group_id
                needs_fixing = True

    # Update the .env file if needed
    if needs_fixing and updates:
        print("\nUpdating configuration...")
        if update_env_file(env_path, updates):
            print("✅ Configuration updated successfully!")

            # Test the updated values
            if (
                "OPENAI_API_KEY" in updates
                or "TELEGRAM_BOT_TOKEN" in updates
                or "TELEGRAM_CHAT_ID" in updates
            ):
                print("\nRunning tests with new configuration...")
                # Reload environment variables
                for key, value in updates.items():
                    os.environ[key] = value

                # Retest OpenAI
                if "OPENAI_API_KEY" in updates:
                    openai_valid, openai_message = test_openai_api_key(
                        updates["OPENAI_API_KEY"]
                    )
                    print(
                        f"  OpenAI API Key: {'✅' if openai_valid else '❌'} {openai_message}"
                    )

                # Retest Telegram
                if "TELEGRAM_BOT_TOKEN" in updates:
                    telegram_token = updates["TELEGRAM_BOT_TOKEN"]
                    telegram_valid, telegram_message = test_telegram_token(
                        telegram_token
                    )
                    print(
                        f"  Telegram Bot Token: {'✅' if telegram_valid else '❌'} {telegram_message}"
                    )

                    # Only test chat ID if bot token is valid
                    if telegram_valid:
                        chat_id = updates.get(
                            "TELEGRAM_CHAT_ID", os.getenv("TELEGRAM_CHAT_ID", "")
                        )
                        chat_valid, chat_message = test_telegram_chat_id(
                            telegram_token, chat_id
                        )
                        print(
                            f"  Telegram Chat ID: {'✅' if chat_valid else '❌'} {chat_message}"
                        )

                        group_id = updates.get(
                            "TELEGRAM_GROUP_CHAT_ID",
                            os.getenv("TELEGRAM_GROUP_CHAT_ID", ""),
                        )
                        if group_id:
                            group_valid, group_message = test_telegram_chat_id(
                                telegram_token, group_id
                            )
                            print(
                                f" "
  Telegram Group ID: {'✅' if group_valid + " else '❌'} {group_message}"
                            )
        else:
            print("❌ Failed to update configuration")
    elif not needs_fixing:
        print("\n✅ All configurations look good! No changes needed.")

    print("\n====== Additional Information ======\n")
    print("If you're still experiencing issues with the Telegram bot:")
    print("1. Make sure your bot is added to the chat/channel")
    print("2. For groups, ensure the bot has admin privileges")
    print("3. For event loop errors, try restarting the bot with:")
    print("   run_bot.bat")
    print("\nIf you continue to have issues, check the logs for more details.")


if __name__ == "__main__":
    main()
