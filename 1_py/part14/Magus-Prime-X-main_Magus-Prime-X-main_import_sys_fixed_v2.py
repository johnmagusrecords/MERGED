import sys
from apy.telegram_helper import send_telegram_message
import asyncio

async def main():
    # Print Python version using sys
    print(f"Python version: {sys.version}")
    await send_telegram_message("Script executed successfully\\.")

asyncio.run(main())
