"""
commentary_generator.py

Provides AI-powered and fallback commentary generators for trade signals.
"""

import os
import logging
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Read API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning(
        "OPENAI_API_KEY is not set; falling back to static commentary.")

openai.api_key = OPENAI_API_KEY


def generate_gpt_commentary(symbol: str, direction: str, strategy: str = "") -> str:
    """
    Generate a short, professional market commentary using OpenAI.
    Falls back to generate_fallback_commentary on error or if API key is missing.
    """
    if not OPENAI_API_KEY:
        return generate_fallback_commentary(symbol, direction, strategy)

    prompt = (
        f"Write a concise, technical trading commentary under 100 words:\n"
        f"Symbol: {symbol}\n"
        f"Direction: {direction}\n"
        f"Strategy: {strategy}\n"
        f"Include key momentum indicators or volume context."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=120
        )
        commentary = response.choices[0].message.content.strip()
        logger.info(f"GPT commentary generated for {symbol}: {commentary}")
        return commentary
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return generate_fallback_commentary(symbol, direction, strategy)


def analyze_sentiment(text: str) -> str:
    """
    Perform a simple sentiment analysis on the given text using OpenAI.
    Returns 'positive', 'negative', or 'neutral'.
    """
    if not OPENAI_API_KEY:
        return "neutral"
    prompt = f"Classify the sentiment of this news headline as positive, negative, or neutral:\n\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=10
        )
        sentiment = response.choices[0].message.content.strip().lower()
        logger.info(f"Sentiment for '{text}': {sentiment}")
        return sentiment
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return "neutral"


def get_trade_commentary(symbol: str, direction: str, entry: float, stop_loss: float, targets: list[float], strategy: str = "") -> str:
    """
    Wrapper to fetch AI commentary for a trade signal.
    """
    try:
        return generate_gpt_commentary(symbol, direction, strategy)
    except Exception as e:
        logger.error(f"get_trade_commentary error: {e}")
        return generate_fallback_commentary(symbol, direction, strategy)


def generate_fallback_commentary(symbol: str, direction: str, strategy: str = "") -> str:
    """
    Generate a simple fallback commentary if AI is unavailable.
    """
    return f"No detailed commentary available for {symbol} {direction} signal."


if __name__ == "__main__":
    # Quick demo
    logging.basicConfig(level=logging.INFO)
    demo = generate_gpt_commentary("BTCUSD", "BUY", "Trend Following")
    print("Demo GPT Commentary:", demo)
    sentiment = analyze_sentiment("Bitcoin rallies 5% on bullish volume")
    print("Demo Sentiment:", sentiment)
