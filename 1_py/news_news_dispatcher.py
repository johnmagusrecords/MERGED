import asyncio
# ...existing code...
import logging

# Configure logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

async def send_news_to_telegram(news_item):
    # Example implementation of sending news to Telegram
    # Replace this with the actual logic
    await asyncio.sleep(1)  # Simulate async operation
    print(f"News sent to Telegram: {news_item}")

def run_async_send(news_item):
    try:
        asyncio.run(send_news_to_telegram(news_item))
    except RuntimeError as e:
        logger.error(f"Failed to run coroutine: {e}")

# ...existing code...

# Replace this:
# asyncio.create_task(send_news_to_telegram(news_item))

# Define a sample news item
news_item = "Breaking News: AI is transforming the world!"

# With this:
run_async_send(news_item)

# ...existing code...
