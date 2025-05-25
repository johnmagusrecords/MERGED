import os
import subprocess

import requests
from dotenv import load_dotenv, set_key


def check_current_token():
    """Check if the current token exists and is valid"""
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    print("==== TELEGRAM TOKEN CHECK ====")

    if not token:
        print("❌ No token found in .env file")
        return False

    if token == "your_telegram_bot_token_here":
        print("❌ Token is still set to the default placeholder")
        return False

    print(f"Found token: {token[:5]}...{token[-5:]} (masked for security)")

    # Test the token with Telegram API
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"❌ Token invalid: {response.status_code} - {response.text}")
            return False

        data = response.json()
        if not data.get("ok"):
            print("❌ Token rejected by Telegram API")
            return False

        bot_info = data.get("result", {})
        print(f"✅ Token valid! Connected to bot: @{bot_info.get('username')}")
        return True
    except Exception as e:
        print(f"❌ Error checking token: {e}")
        return False


def set_new_token():
    """Interactive function to set a new token"""
    print("\n==== SET NEW TELEGRAM TOKEN ====")
    print(
        "You can get a token by messaging @BotFather on Telegram and following these steps:"
    )
    print("1. Start a chat with @BotFather")
    print("2. Send /newbot command")
    print("3. Follow the instructions to create a bot")
    print("4. Copy the API token (looks like: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ)")
    print("\nNote: Make sure to add your bot to your Telegram group after this\n")

    token = input("Enter your Telegram bot token: ")

    if not token:
        print("❌ No token entered. Aborting.")
        return False

    # Set the token in .env file
    set_key(".env", "TELEGRAM_BOT_TOKEN", token)
    print("✅ Token saved to .env file")

    # Also update the environment variable for the current session
    os.environ["TELEGRAM_BOT_TOKEN"] = token

    # Verify the token
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(
                f"❌ Token verification failed: {response.status_code} - {response.text}"
            )
            return False

        data = response.json()
        if not data.get("ok"):
            print("❌ Token verification failed")
            return False

        bot_info = data.get("result", {})
        print(f"✅ Token verified! Connected to bot: @{bot_info.get('username')}")

        # Get group ID if needed
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        group_id = os.getenv("TELEGRAM_GROUP_ID")

        if not (chat_id or group_id):
            print("\nYou also need to set a chat ID or group ID.")
            print("For group chats, the ID usually starts with -100...")
            set_id = input("Do you want to set a group/chat ID now? (y/n): ").lower()

            if set_id == "y":
                new_id = input("Enter the group/chat ID: ")
                if new_id:
                    set_key(".env", "TELEGRAM_GROUP_ID", new_id)
                    print("✅ Group ID saved to .env file")
                    # Also set it for the current session
                    os.environ["TELEGRAM_GROUP_ID"] = new_id

                    # Try sending a test message
                    test_msg = input(
                        "Do you want to send a test message to verify? (y/n): "
                    ).lower()
                    if test_msg == "y":
                        url = f"https://api.telegram.org/bot{token}/sendMessage"
                        payload = {
                            "chat_id": new_id,
                            "text": " "
✅ MAGUS PRIME X test message successful! + " Your bot is properly configured.",
                        }
                        try:
                            msg_response = requests.post(url, json=payload, timeout=10)
                            if msg_response.status_code == 200:
                                print("✅ Test message sent successfully!")
                            else:
                                print(
                                    f" "
❌ Failed to send test message: {msg_resp + "onse.status_code} - {msg_response.text}"
                                )
                        except Exception as e:
                            print(f"❌ Error sending test message: {e}")

        return True
    except Exception as e:
        print(f"❌ Error verifying token: {e}")
        return False


def restart_services():
    """Ask if user wants to restart the bot"""
    restart = input(
        "\nDo you want to restart your bot now to apply the changes? (y/n): "
    ).lower()
    if restart == "y":
        print("Restarting the bot...")
        try:
            # This is a simple restart approach - in a real environment, you might want to use a more robust method
            subprocess.run(["python", "bot.py"], check=True)
        except Exception as e:
            print(f"❌ Error restarting bot: {e}")
            print("Please restart your bot manually")


def main():
    print("==============================================")
    print("MAGUS PRIME X Telegram Token Fix Utility")
    print("==============================================")

    # Check if the token is already valid
    if check_current_token():
        fix_anyway = input(
            "\nYour token appears valid. Do you still want to set a new token? (y/n): "
        ).lower()
        if fix_anyway != "y":
            print("✅ Your Telegram token is already set correctly!")
            return

    # Set a new token
    if set_new_token():
        print("\n✅ Telegram token successfully updated!")
        print(
            "\nNote: If you have issues with the bot not sending messages to your group:"
        )
        print("1. Make sure you've added the bot to your Telegram group")
        print("2. Ensure the bot has permission to send messages in the group")
        print("3. If using a group, make sure the group ID starts with -100")

        # Ask to restart services
        restart_services()
    else:
        print("\n❌ Failed to set a valid Telegram token.")
        print("Please try again or contact support.")


if __name__ == "__main__":
    main()
