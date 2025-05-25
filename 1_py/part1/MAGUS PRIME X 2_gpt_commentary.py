import logging
import os

import requests
from dotenv import load_dotenv

from config import STRATEGY_DESCRIPTIONS, config

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Check for assistant enablement with proper lowercase comparison
ASSISTANT_ENABLED = os.getenv(
    "MAGUS_ASSISTANT_ENABLED", "false").lower() == "true"

# Load MAGUS Assistant flag
MAGUS_ASSISTANT_ENABLED = (
    os.getenv("MAGUS_ASSISTANT_ENABLED", "False").lower() == "true"
)
if not MAGUS_ASSISTANT_ENABLED:
    MAGUS_ASSISTANT_ENABLED = True  # Force-enable Assistant
    print("🤖 MAGUS Assistant auto-activated for enhanced trading experience")

# Try to import OpenAI with graceful fallback
try:
    import openai

    OPENAI_ENABLED = True
except ImportError:
    logging.warning(
        "OpenAI package not found. Commentary will use fallback templates.")
    OPENAI_ENABLED = False

# Get OpenAI API key from environment or config
openai_api_key = os.getenv("OPENAI_API_KEY", config["news"]["openai_key"])

# === FALLBACK EXPLANATIONS ===
fallback_map = {
    "Breakout": "Breakout occurs when price moves strongly beyond resistance with high volume.",
    "Scalping": "Scalping strategy aims for small quick profits over short timeframes.",
    "Swing": "Swing trading aims to capture medium-term moves between support/resistance.",
    "FVG": "FVG (Fair Value Gap) is based on smart money theory and imbalance zones.",
    "Trend Following": "Following established market direction after confirmation of trend strength.",
    "Mean Reversion": "Trading the return to average price after extreme price movements.",
    "Support/Resistance": "Trading bounces off key structural levels where price has historically reversed.",
    "Range Trading": "Trading between established support and resistance levels in sideways markets.",
}

# Use strategy descriptions from config if available
fallback_map.update(STRATEGY_DESCRIPTIONS)


def get_gpt_commentary(pair, direction, strategy):
    """
    Generate professional trading commentary using OpenAI's GPT

    Args:
        pair: Trading pair/symbol (e.g., "BTCUSD")
        direction: Trade direction ("BUY" or "SELL")
        strategy: Trading strategy name

    Returns:
        str: AI-generated commentary or fallback explanation
    """
    # Set API key either from env or directly
    api_key = openai_api_key

    if not OPENAI_ENABLED or not api_key:
        logging.warning("OpenAI API key not configured or module missing")
        # Use strategy-specific fallback if available
        if strategy in fallback_map:
            return f"{fallback_map[strategy]} {direction} signal on {pair} with favorable momentum."
        return f"{strategy} strategy applied to {pair}. Volatility suggests potential opportunity for {direction}."

    prompt = (
        f"Write a short, professional market commentary for the following signal:\n"
        f"Pair: {pair}\n"
        f"Direction: {direction}\n"
        f"Strategy: {strategy}\n"
        f"Include market insight, confidence tone, and recent volume or RSI factors if relevant."
        f"Keep the response under 100 words and focused on technical factors."
    )

    try:
        # Try to use the client-based API approach first (for OpenAI SDK v1.0.0+)
        try:
            # Create a client instance with the API key
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=120,
            )
            return response.choices[0].message.content.strip()
        except (AttributeError, TypeError):
            # Fall back to direct API call if client methods fail
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 120,
            }

            response = requests.post(
                url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                logger.error(
                    f"OpenAI API error: {response.status_code} - {response.text}"
                )
                raise Exception(f"API error: {response.status_code}")

    except Exception as e:
        logging.error(f"Error generating GPT commentary: {e}")

        # Use strategy-specific fallback if available
        if strategy in fallback_map:
            return f"{fallback_map[strategy]} {direction} signal on {pair} confirms momentum."

        return f"{strategy} signal on {pair}. Momentum confirms {direction} setup."


def get_market_outlook(asset, timeframe="daily"):
    """
    Get a general market outlook for an asset

    Args:
        asset: Asset symbol (e.g., "BTCUSD")
        timeframe: Timeframe for the outlook

    Returns:
        str: Market outlook commentary or None if not available
    """
    api_key = openai_api_key

    if not OPENAI_ENABLED or not api_key:
        return None

    prompt = (
        f"Provide a concise {timeframe} market outlook for {asset}.\n"
        f"Include key support/resistance levels, momentum, and one technical indicator insight.\n"
        f"Keep it under 50 words and professional in tone."
    )

    try:
        # Try client-based approach for OpenAI SDK v1.0.0+
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100,
            )
            return response.choices[0].message.content.strip()
        except (AttributeError, TypeError):
            # Fall back to direct API call
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 100,
            }

            response = requests.post(
                url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                logger.error(
                    f"OpenAI API error: {response.status_code} - {response.text}"
                )
                return None

    except Exception as e:
        logging.error(f"Error generating market outlook: {e}")
        return None


async def start_assistant_listener(bot):
    import asyncio

    from telegram.ext import Application, CommandHandler

    async def handle_message(update, context):
        text = update.message.text
        chat_id = update.effective_chat.id

        if "/status" in text.lower():
            await bot.send_message(
                chat_id=chat_id, text="🤖 MAGUS Assistant is online and listening."
            )
        else:
            await bot.send_message(
                chat_id=chat_id, text="💬 Assistant received your message."
            )

    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("status", handle_message))
    app.add_handler(CommandHandler("pause", handle_message))
    app.add_handler(CommandHandler("resume", handle_message))

    await app.initialize()
    await app.start()
    await asyncio.sleep(1)
    logging.info("Assistant command listener is now running.")


if __name__ == "__main__":
    # Test the commentary generation
    logging.basicConfig(level=logging.INFO)

    print("Testing GPT Commentary")
    print("-" * 50)

    test_pairs = ["BTCUSD", "EURUSD", "GOLD"]
    test_directions = ["BUY", "SELL"]
    test_strategies = ["Breakout", "Trend Following", "Support/Resistance"]

    for pair in test_pairs:
        for direction in test_directions:
            strategy = test_strategies[test_pairs.index(
                pair) % len(test_strategies)]
            print(f"\nTesting {direction} {strategy} on {pair}:")
            commentary = get_gpt_commentary(pair, direction, strategy)
            print(f"Commentary: {commentary}")

    # Test market outlook
    print("\nTesting market outlook for BTCUSD:")
    outlook = get_market_outlook("BTCUSD")
    if outlook:
        print(f"Outlook: {outlook}")
    else:
        print("Market outlook not available (API key may be missing)")
