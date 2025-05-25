import os
import sys

import requests
from dotenv import load_dotenv

# Explicitly load environment variables from .env file
load_dotenv(override=True)

# Get token from environment variables
token = os.getenv("TELEGRAM_BOT_TOKEN")
print(
    f" "
TELEGRAM_BOT_TOKEN from .env: {token[:5] + "}...{token[-5:] if token and len(token)  + "> 10 else 'Not found'}"
)

# Verify token directly with Telegram API (no library dependencies)
try:
    print("Testing direct API connection to Telegram...")
    response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)

    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            bot_info = data.get("result", {})
            print(f"✅ Token is valid! Connected to bot: @{bot_info.get('username')}")
            print(f"✅ Bot name: {bot_info.get('first_name')}")
            sys.exit(0)  # Success
        else:
            print(f"❌ Telegram API returned error: {data}")
    else:
        print(f"❌ Error connecting to Telegram API: Status {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

sys.exit(1)  # Error
