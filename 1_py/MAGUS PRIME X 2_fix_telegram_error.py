import logging
import os

import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")


def diagnose_token_error():
    """Diagnose and fix the InvalidToken error"""
    print("\n===== TELEGRAM TOKEN ERROR DIAGNOSIS =====")

    # Load environment variables
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    # Check if token exists
    if not token:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in environment variables")
        print("   Solution: Add the token to your .env file")
        return False

    # Check if token is the default placeholder
    if token == "your_telegram_bot_token_here":
        print("❌ ERROR: Token is still set to the default placeholder")
        print("   Solution: Replace with a real token from @BotFather")
        return False

    # Check for common token format errors
    if ":" not in token:
        print(
            "❌ ERROR: Token format is invalid. Telegram tokens contain a colon (':')."
        )
        print("   Solution: Make sure you're using the full token from @BotFather")
        return False

    print(f"🔑 Found token: {token[:5]}...{token[-5:]}")

    # Test the token with Telegram directly
    print("\nTesting token with Telegram API...")
    try:
        # Direct API call with requests to bypass any issues with python-telegram-bot
        response = requests.get(
            f"https://api.telegram.org/bot{token}/getMe", timeout=10
        )
        status_code = response.status_code
        response_text = response.text

        if status_code != 200:
            print(f"❌ ERROR: Token invalid (Status code: {status_code})")
            print(f"   Telegram response: {response_text}")

            if "unauthorized" in response_text.lower():
                print("   Diagnosis: Token is rejected by Telegram (unauthorized)")
            elif "not found" in response_text.lower():
                print("   Diagnosis: Token doesn't exist or is malformed")

            return False

        # Parse the response
        data = response.json()

        if not data.get("ok"):
            print(f"❌ ERROR: Token rejected by Telegram with message: {data}")
            return False

        # Valid token
        bot_info = data.get("result", {})
        print(
            f"✅ Token valid! Connected to bot: @{bot_info.get('username', 'unknown')}"
        )
        print(f"   Bot name: {bot_info.get('first_name', 'Unknown')}")

        # Check environment variable usage
        print("\nChecking how your bot loads the token...")
        print("The most common issue is that the bot isn't using the token from .env")

        # Solution for fixing how token is loaded in bot.py
        print("\n===== SOLUTION =====")
        print("To ensure your bot uses the token correctly:")
        print("1. Make sure you're loading .env variables at the start of your code.")
        print("   Add this near the top of your bot.py:")
        print("   ```")
        print("   from dotenv import load_dotenv")
        print("   load_dotenv()")
        print("   ```")
        print("\n2. Check how TELEGRAM_BOT_TOKEN is loaded in your bot.py:")
        print("   ```")
        print("   TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')")
        print("   ```")

        # Create bot.py token patch if user wants
        apply_patch = input(
            "\nWould you like to create a small script to test the token directly? (y/N): "
        )
        if apply_patch.lower() == "y":
            create_token_test()

        return True

    except Exception as e:
        print(f"❌ ERROR: Failed to test token: {e}")
        print("   This could be a network issue or an invalid token")
        return False


def create_token_test():
    """Create a simple test script that uses python-telegram-bot library"""
    test_code = """
# filepath: c:\\Users\\djjoh\\OneDrive\\Desktop\\MAGUS PRIME X\\test_telegram_direct.py
import os
import sys
import asyncio
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
                       level=logging.INFO,
                       format=' '
%(asctime)s - %(name)s - %(levelname)s - + ' %(message)s')logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def test_bot():
    try:
        # Import telegram libraries
        from telegram import Bot
        from telegram.error import InvalidToken, Unauthorized, NetworkError
        
        print(f"Using token: {TOKEN[:5]}...{TOKEN[-5:]}")
        
        # Create bot instance
        bot = Bot(token=TOKEN)
        
        # Get bot information
        print("Connecting to Telegram...")
        bot_info = await bot.get_me()
        
        print(f"✅ Connection successful!")
        print(f"Bot username: @{bot_info.username}")
        print(f"Bot name: {bot_info.first_name}")
        
        # Try to get updates to further validate
        print("\\nTesting getting updates...")
        updates = await bot.get_updates(limit=5)
        print(f"Retrieved {len(updates)} recent updates")
        
        print("\\n✅ TELEGRAM TOKEN IS WORKING CORRECTLY!")
        return True
        
    except InvalidToken:
        print("❌ ERROR: Invalid token. The token was rejected by Telegram.")
        print("Please check that you have the correct token from @BotFather")
        return False
    except Unauthorized:
        print("❌ ERROR: Unauthorized. The token was rejected by Telegram.")
        print("The token may have been revoked or is incorrect.")
        return False
    except NetworkError as e:
        print(f"❌ ERROR: Network error when connecting to Telegram: {e}")
        print("Please check your internet connection.")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    if not TOKEN:
        print("❌ ERROR: No token found. Please set TELEGRAM_BOT_TOKEN in your .env file.")
        sys.exit(1)
        
    print("Testing Telegram bot token...")
    result = asyncio.run(test_bot())
    sys.exit(0 if result else 1)
"""

    # Write the test file
    with open("test_telegram_direct.py", "w") as f:
        f.write(test_code)

    # Create batch file
    with open("run_direct_telegram_test.bat", "w") as f:
        f.write("@echo off\n")
        f.write("echo Testing Telegram token directly...\n")
        f.write("python test_telegram_direct.py\n")
        f.write("pause\n")

    print("✅ Created test_telegram_direct.py and run_direct_telegram_test.bat")
    print("Run run_direct_telegram_test.bat to test your Telegram token directly")


if __name__ == "__main__":
    if diagnose_token_error():
        print("\n✅ Token diagnosis complete.")
    else:
        print("\n❌ Token diagnosis found issues that need to be fixed.")

    print("\nIf you need to update your token, run:")
    print("python fix_telegram_now.py")
