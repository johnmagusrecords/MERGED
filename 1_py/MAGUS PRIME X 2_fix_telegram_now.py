import sys

import requests
from dotenv import set_key


def fix_token():
    print("=" * 60)
    print("QUICK TELEGRAM TOKEN FIX")
    print("=" * 60)

    # Get new token
    print("\nPaste your Telegram bot token below (from @BotFather):")
    token = input("> ").strip()

    if not token:
        print("❌ No token provided. Exiting.")
        return False

    # Save to .env file
    set_key(".env", "TELEGRAM_BOT_TOKEN", token)
    print("✅ Token saved to .env file")

    # Test the token
    try:
        print("\nTesting token...")
        response = requests.get(
            f"https://api.telegram.org/bot{token}/getMe", timeout=10
        )

        if response.status_code == 200 and response.json().get("ok"):
            bot_info = response.json().get("result", {})
            print(f"✅ Connection successful! Bot name: @{bot_info.get('username')}")
            print("\n🟢 TOKEN FIXED - Your bot should now work correctly!")
            return True
        else:
            print(f"❌ Token verification failed: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False


if __name__ == "__main__":
    success = fix_token()
    if not success:
        print(
            "\n❌ Token fix failed. Please try again or run fix_telegram.bat for more options."
        )
    sys.exit(0 if success else 1)
