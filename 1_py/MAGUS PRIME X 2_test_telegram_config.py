import argparse
import os

import requests
from dotenv import load_dotenv


def check_environment_variables():
    """Check if required environment variables for Telegram are set"""
    print("\n1. Checking Environment Variables")
    print("===================================")

    # Try to load from .env file if it exists
    load_dotenv()

    # Define expected variables
    telegram_vars = [
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHANNEL_ID",
        "TELEGRAM_CHAT_ID",
        "TELEGRAM_GROUP_ID",
    ]

    # Check for any of these variables (only one channel type is required)
    found_any = False
    missing = []

    for var in telegram_vars:
        value = os.environ.get(var)
        if value:
            found_any = True
            # Mask token value for security
            if var == "TELEGRAM_BOT_TOKEN":
                masked = value[:4] + "..." + value[-4:]
                print(f"✅ {var} is set: {masked}")
            else:
                print(f"✅ {var} is set: {value}")
        else:
            missing.append(var)
            print(f"❌ {var} is not set")

    if not found_any:
        print("\n⚠️ ERROR: No Telegram environment variables found!")
        print(
            "The Signal Sender API needs these variables to forward messages to Telegram."
        )
        print("\nPlease set at least these environment variables:")
        print("  - TELEGRAM_BOT_TOKEN (required)")
        print(
            "  - TELEGRAM_CHANNEL_ID, TELEGRAM_CHAT_ID, or TELEGRAM_GROUP_ID (at least one)"
        )

        print("\nYou can set them in a .env file with these lines:")
        print('TELEGRAM_BOT_TOKEN="your_bot_token_here"')
        print('TELEGRAM_CHANNEL_ID="your_channel_id_here"')
        return False

    if "TELEGRAM_BOT_TOKEN" in missing:
        print("\n⚠️ ERROR: Bot token is required but not set!")
        return False

    if all(
        id_var in missing
        for id_var in ["TELEGRAM_CHANNEL_ID", "TELEGRAM_CHAT_ID", "TELEGRAM_GROUP_ID"]
    ):
        print("\n⚠️ ERROR: At least one chat ID is required but none are set!")
        return False

    return True


def test_telegram_bot(token=None):
    """Test if the Telegram bot token is valid by calling getMe API"""
    print("\n2. Testing Telegram Bot Token")
    print("===================================")

    # Use provided token or get from environment
    bot_token = token or os.environ.get("TELEGRAM_BOT_TOKEN")

    if not bot_token:
        print("❌ No bot token provided or found in environment variables.")
        return False

    # Call getMe API to test token
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        print("Testing Telegram bot token...")
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("ok"):
            bot_info = data.get("result", {})
            print(
                f" "
✅ Bot token is valid! Connected to: {bot + "_info.get('username')} (ID: {bot_info.ge + "t('id')})"
            )
            return True
        else:
            print(f"❌ Bot token is invalid! Error: {data.get('description')}")
            return False

    except Exception as e:
        print(f"❌ Error testing bot token: {e}")
        return False


def test_chat_id(token=None, chat_id=None):
    """Test if the bot can send a message to the specified chat ID"""
    print("\n3. Testing Telegram Chat ID")
    print("===================================")

    # Use provided values or get from environment
    bot_token = token or os.environ.get("TELEGRAM_BOT_TOKEN")

    if not chat_id:
        # Try to get any chat ID from environment
        for var in ["TELEGRAM_CHANNEL_ID", "TELEGRAM_CHAT_ID", "TELEGRAM_GROUP_ID"]:
            chat_id = os.environ.get(var)
            if chat_id:
                print(f"Using {var}: {chat_id}")
                break

    if not bot_token or not chat_id:
        print("❌ Missing bot token or chat ID.")
        return False

    # Send test message
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🧪 Test message from Signal Sender API diagnostics",
    }

    try:
        print(f"Sending test message to chat ID: {chat_id}...")
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()

        if data.get("ok"):
            print(
                f" "
✅ Message sent successfully! Message ID: + " {
                                                                      data.get(
                                                                               'result',
                                                                      {}).get('message_id + "')}"            )
            return True
        else:
            print(f"❌ Failed to send message! Error: {data.get('description')}")

            # Special handling for common errors
            if "chat not found" in data.get("description", "").lower():
                print(
                    "\n💡 TIP: The chat ID is invalid or the bot is not a member of the chat."
                )
                print(
                    "If using a channel or group, make sure the bot is added as an admin."
                )

            return False

    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False


def fix_suggestions():
    """Print suggestions for fixing common issues"""
    print("\n4. Troubleshooting Suggestions")
    print("===================================")
    print("1. Double-check your bot token - get it from @BotFather on Telegram")
    print(
        "2. Make sure your bot is added to the channel/group and has admin privileges"
    )
    print("3. For channels, use the format '@channelname' or the channel ID")
    print("4. For private chats, you need to first send a message to the bot")
    print("5. Set environment variables directly on your system or create a .env file")
    print("6. If all else fails, create a new bot with @BotFather and try again")


def create_env_template():
    """Create a template .env file with Telegram credentials"""
    env_path = os.path.join(os.path.dirname(__file__), ".env")

    # Check if file already exists
    if os.path.exists(env_path):
        overwrite = input("A .env file already exists. Overwrite? (y/n): ").lower()
        if overwrite != "y":
            print("Aborted. Existing .env file was not modified.")
            return False

    # Create the template with ALL necessary variables
    with open(env_path, "w") as f:
        f.write("# Telegram Bot Configuration\n")
        f.write("# Get your bot token from @BotFather on Telegram\n")
        f.write("TELEGRAM_BOT_TOKEN=\n\n")
        f.write("# Use ONE of the following (channel ID, chat ID, or group ID)\n")
        f.write("# For channels: use format @channelname or channel ID number\n")
        f.write("TELEGRAM_CHANNEL_ID=\n")
        f.write("TELEGRAM_CHAT_ID=6292642600\n")
        f.write("TELEGRAM_GROUP_ID=\n\n")

        # Additional important configuration
        f.write("# Trading Bot Configuration\n")
        f.write("# Set your API keys and secrets for exchanges\n")
        f.write("BINANCE_API_KEY=\n")
        f.write("BINANCE_API_SECRET=\n\n")

        f.write("# Trading parameters\n")
        f.write("DEFAULT_RISK_PERCENTAGE=1\n")
        f.write("MAX_OPEN_TRADES=3\n")
        f.write("ENABLE_AUTOMATIC_TRADING=false\n\n")

        f.write("# Database connection (if applicable)\n")
        f.write("DB_HOST=localhost\n")
        f.write("DB_PORT=5432\n")
        f.write("DB_NAME=trading_bot\n")
        f.write("DB_USER=\n")
        f.write("DB_PASSWORD=\n\n")

        f.write("# Logging settings\n")
        f.write("LOG_LEVEL=INFO\n")
        f.write("SAVE_TRADE_HISTORY=true\n\n")

        f.write("# Webhook settings (for exchange notifications)\n")
        f.write("WEBHOOK_SECRET=\n\n")

        f.write("# Additional API endpoints\n")
        f.write("PRICE_API_URL=\n")
        f.write("MARKET_DATA_PROVIDER=\n")

    print(f"✅ Created comprehensive .env template at: {env_path}")
    print(
        "Please edit this file to add your Telegram bot token and other configuration."
    )
    print("\nIMPORTANT: Make sure to fill in at least the Telegram bot token!")

    return True


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test Telegram bot configuration")
    parser.add_argument(
        "--create-env", action="store_true", help="Create a template .env file"
    )
    args = parser.parse_args()

    if args.create_env:
        create_env_template()
        return

    print("🤖 Telegram Bot Configuration Tester")
    print("=====================================")
    print("This tool checks if your Telegram bot configuration is correct.")

    env_ok = check_environment_variables()

    if env_ok:
        token_ok = test_telegram_bot()
        if token_ok:
            chat_ok = test_chat_id()

            if chat_ok:
                print(
                    "\n✅ SUCCESS! Your Telegram bot configuration is working correctly."
                )
                print(
                    "You should be able to use the Signal Sender API to send messages to Telegram."
                )
            else:
                print("\n❌ There's an issue with your chat ID configuration.")
                fix_suggestions()
        else:
            print("\n❌ There's an issue with your bot token.")
            fix_suggestions()
    else:
        print("\n❌ Environment variables are not set up correctly.")
        fix_suggestions()
        print("\nTo create a template .env file, run:")
        print("python test_telegram_config.py --create-env")


if __name__ == "__main__":
    main()
