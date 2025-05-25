import logging
import os
import time

import requests
from dotenv import load_dotenv, set_key

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def main():
    load_dotenv()

    # Check if token is set
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "your_telegram_bot_token_here":
        print("❌ ERROR: You need to set a valid TELEGRAM_BOT_TOKEN first")
        print("Please run quick_token_fix.bat to set up your token")
        return False

    print("=" * 60)
    print("TELEGRAM GROUP ID FINDER")
    print("=" * 60)
    print("\nThis utility will help you get your Telegram group ID.")
    print("\nINSTRUCTIONS:")
    print("1. Make sure you've already created your bot with @BotFather")
    print("2. Add your bot to your Telegram group")
    print("3. Post a message in your group by typing: /my_id")
    print("4. This bot will detect your message and extract the group ID")
    print("\nWaiting for messages... (Press Ctrl+C to exit)")

    # Create getUpdates URL
    updates_url = f"https://api.telegram.org/bot{token}/getUpdates"

    # Remember the last update_id we processed
    last_update_id = 0

    try:
        while True:
            # Get updates from Telegram
            response = requests.get(
                f"{updates_url}?offset={last_update_id+1}", timeout=10
            )

            if response.status_code != 200:
                print(f"❌ Error accessing Telegram API: {response.status_code}")
                print(response.text)
                return False

            data = response.json()

            if not data.get("ok"):
                print(f"❌ Telegram API error: {data}")
                return False

            updates = data.get("result", [])

            for update in updates:
                # Track the latest update_id
                update_id = update.get("update_id", 0)
                if update_id > last_update_id:
                    last_update_id = update_id

                # Check for messages
                message = update.get("message", {})
                if not message:
                    continue

                # Look for the /my_id command
                text = message.get("text", "")
                if text.startswith("/my_id"):
                    chat = message.get("chat", {})
                    chat_id = chat.get("id")
                    chat_type = chat.get("type")
                    chat_title = chat.get("title", "Unknown")

                    if chat_type in ["group", "supergroup"]:
                        print("\n" + "=" * 60)
                        print(f"✅ Found group: {chat_title}")
                        print(f"📝 Group ID: {chat_id}")
                        print("=" * 60)

                        # Update .env file
                        update_env = input(
                            "\nDo you want to update your .env file with this group ID? (y/N): "
                        ).lower()
                        if update_env == "y":
                            set_key(".env", "TELEGRAM_GROUP_ID", str(chat_id))
                            print("✅ Group ID saved to .env file")

                            # Try sending a test message
                            test_msg = input(
                                "Do you want to send a test message to verify? (y/N): "
                            ).lower()
                            if test_msg == "y":
                                msg_url = (
                                    f"https://api.telegram.org/bot{token}/sendMessage"
                                )
                                payload = {
                                    "chat_id": chat_id,
                                    "text": " "
✅ MAGUS PRIME X test message successful! + " Your bot is properly configured.",
                                    "parse_mode": "Markdown",
                                }
                                try:
                                    msg_response = requests.post(
                                        msg_url, json=payload, timeout=10
                                    )
                                    if msg_response.status_code == 200:
                                        print("✅ Test message sent successfully!")
                                        print(
                                            "\nYour Telegram configuration is now complete!"
                                        )
                                        return True
                                    else:
                                        print(
                                            f" "
❌ Failed to send test message: {msg_resp + "onse.status_code}"
                                        )
                                        print(msg_response.text)
                                except Exception as e:
                                    print(f"❌ Error sending test message: {e}")

            # Sleep before checking again
            time.sleep(3)

    except KeyboardInterrupt:
        print("\nExiting...")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    main()
