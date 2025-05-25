import os
import asyncio
from dotenv import load_dotenv
import telegram

# Load environment variables
print("Loading .env file...")
load_dotenv()

# Print the telegram token
print("TELEGRAM_BOT_TOKEN:", os.getenv("TELEGRAM_BOT_TOKEN"))


async def test_telegram_bot():
    # Try to initialize the bot
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        print("Initializing Telegram bot...")
        try:
            bot = telegram.Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
            print("Bot initialized successfully!")
            me = await bot.get_me()
            print("Bot username:", me.username)
        except Exception as e:
            print("Error initializing bot:", e)
    else:
        print("TELEGRAM_BOT_TOKEN not found in environment variables")

# Run the async function
if __name__ == "__main__":
    asyncio.run(test_telegram_bot())
