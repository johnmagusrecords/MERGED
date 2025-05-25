import asyncio
import logging
import os

from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables
load_dotenv()


def check_environment_variables():
    """Check if required environment variables for Telegram are set"""
    print("\n1. Checking Environment Variables")
    print("===================================")

    telegram_vars = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    all_vars_set = True

    for var in telegram_vars:
        value = os.environ.get(var)
        if value:
            # Mask token value for security
            if var == "TELEGRAM_BOT_TOKEN":
                masked = value[:4] + "..." + value[-4:]
                print(f"✅ {var} is set: {masked}")
            else:
                print(f"✅ {var} is set: {value}")
        else:
            all_vars_set = False
            print(f"❌ {var} is not set")

    return all_vars_set


def test_telegram_sync():
    """Test Telegram message sending using synchronous API"""
    print("\n2. Testing Synchronous Telegram Message")
    print("===================================")

    try:
        import telegram

        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")

        if not bot_token or not chat_id:
            print("❌ Missing required environment variables")
            return False

        # Create bot instance
        bot = telegram.Bot(token=bot_token)

        # Send test message
        print("Sending test message...")
        message = bot.send_message(
            chat_id=chat_id, text="🔄 Test message from MAGUS PRIME X (sync API)"
        )

        print(f"✅ Message sent successfully (message_id: {message.message_id})")
        return True

    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False


async def test_telegram_async():
    """Test Telegram message sending using asynchronous API"""
    print("\n3. Testing Asynchronous Telegram Message")
    print("===================================")

    try:
        from telegram.ext import ApplicationBuilder

        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")

        if not bot_token or not chat_id:
            print("❌ Missing required environment variables")
            return False

        # Create bot instance
        app = ApplicationBuilder().token(bot_token).build()

        # Send test message
        print("Sending test message...")
        message = await app.bot.send_message(
            chat_id=chat_id, text="🔄 Test message from MAGUS PRIME X (async API)"
        )

        print(f"✅ Message sent successfully (message_id: {message.message_id})")
        return True

    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False


def main():
    """Run all Telegram tests"""
    print("===== Telegram Integration Test =====")

    # Check environment variables
    env_ok = check_environment_variables()
    if not env_ok:
        print("\n❌ Environment variables are not properly set!")
        print("Please check your .env file contains:")
        print("  TELEGRAM_BOT_TOKEN=your_bot_token")
        print("  TELEGRAM_CHAT_ID=your_chat_id")
        return

    # Test synchronous API
    sync_ok = test_telegram_sync()

    # Test asynchronous API
    try:
        async_ok = asyncio.run(test_telegram_async())
    except Exception as e:
        print(f"❌ Error running async test: {e}")
        async_ok = False

    # Print summary
    print("\n===== TEST SUMMARY =====")
    print(f"Environment Variables: {'PASSED' if env_ok else 'FAILED'}")
    print(f"Synchronous API Test: {'PASSED' if sync_ok else 'FAILED'}")
    print(f"Asynchronous API Test: {'PASSED' if async_ok else 'FAILED'}")
    print(
        f" "
Overall Status: {'✅ ALL TESTS PASSED' if + " (env_ok and sync_ok and async_ok) else  + "'❌ SOME TESTS FAILED'}"
    )

    # Show troubleshooting tips if any tests failed
    if not (env_ok and sync_ok and async_ok):
        print("\nTroubleshooting Tips:")
        print("1. Check that your bot token is valid (from @BotFather)")
        print("2. Confirm your chat_id is correct")
        print("3. Make sure you've started a conversation with your bot")
        print("4. Check your internet connection")
        print("5. Try running the bot in polling mode instead of webhook")


if __name__ == "__main__":
    main()
    print("\nPress Enter to exit...")
    input()
