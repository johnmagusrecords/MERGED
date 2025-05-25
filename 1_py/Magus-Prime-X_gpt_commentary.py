# gpt_commentary.py
import os
import logging
import requests
from dotenv import load_dotenv
import openai

# Add your existing CONFIG definition here
CONFIG = {
    # Example configuration
}

# Define STRATEGY_DESCRIPTIONS
STRATEGY_DESCRIPTIONS = {
    "Breakout": "Breakout occurs when price moves strongly beyond resistance with high volume.",
    "Scalping": "Scalping strategy aims for small quick profits over short timeframes.",
    "Swing": "Swing trading aims to capture medium-term moves between support/resistance.",
    "FVG": "FVG (Fair Value Gap) is based on smart money theory and imbalance zones.",
    "Trend Following": "Following established market direction after confirmation of trend strength.",
    "Mean Reversion": "Trading the return to average price after extreme price movements.",
    "Support/Resistance": "Trading bounces off key structural levels where price has historically reversed.",
    "Range Trading": "Trading between established support and resistance levels in sideways markets.",
}

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

# Check if assistant is enabled
ASSISTANT_ENABLED = os.getenv(
    "MAGUS_ASSISTANT_ENABLED", "false").lower() == "true"

# OpenAI availability
try:
    OPENAI_ENABLED = True
except ImportError:
    logging.warning(
        "OpenAI package not found. Commentary will use fallback templates.")
    OPENAI_ENABLED = False

openai_api_key = os.getenv("OPENAI_API_KEY", getattr(
    CONFIG, "news", {}).get("openai_key", ""))

# Fallback explanations
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
fallback_map.update(STRATEGY_DESCRIPTIONS)


def get_gpt_commentary(pair, direction, strategy):
    """
    Generate professional trading commentary using OpenAI's GPT
    """
    api_key = openai_api_key
    if not OPENAI_ENABLED or not api_key:
        logging.warning("OpenAI API key not configured or module missing")
        if strategy in fallback_map:
            return f"{fallback_map[strategy]} {direction} signal on {pair} with favorable momentum."
        return f"{strategy} strategy applied to {pair}. Volatility suggests potential opportunity for {direction}."

    prompt = (
        f"Write a short, professional market commentary for the following signal:\n"
        f"Pair: {pair}\nDirection: {direction}\nStrategy: {strategy}\n"
        f"Include market insight, confidence tone, and recent volume or RSI factors if relevant. "
        f"Keep the response under 100 words and focused on technical factors."
    )
    try:
        try:
            openai.api_key = api_key
            # Use openai.Completion.create for legacy API, or openai.ChatCompletion.create if available
            # Fix: Use openai.ChatCompletion only if it exists, otherwise fallback to HTTP API
            if hasattr(openai, "ChatCompletion"):
                chat_completion = getattr(openai, "ChatCompletion")
                response = chat_completion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=120
                )
                content = response.choices[0].message.content if response.choices and hasattr(
                    response.choices[0].message, "content") else None
                return content.strip() if content else ""
            else:
                # Fallback to HTTP API if ChatCompletion is not available
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                data = {
                    "model": "gpt-4o",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 120
                }
                response = requests.post(
                    url, headers=headers, json=data, timeout=10)
                if response.status_code == 200:
                    content = response.json(
                    )["choices"][0]["message"].get("content")
                    return content.strip() if content else ""
                else:
                    logger.error(
                        f"OpenAI API error: {response.status_code} - {response.text}")
                    raise Exception(f"API error: {response.status_code}")
        except (AttributeError, TypeError):
            # Always fallback to HTTP API if any error
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            data = {
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 120
            }
            response = requests.post(
                url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                content = response.json(
                )["choices"][0]["message"].get("content")
                return content.strip() if content else ""
            else:
                logger.error(
                    f"OpenAI API error: {response.status_code} - {response.text}")
                raise Exception(f"API error: {response.status_code}")
    except Exception as e:
        logging.error(f"Error generating GPT commentary: {e}")
        if strategy in fallback_map:
            return f"{fallback_map[strategy]} {direction} signal on {pair} confirms momentum."
        return f"{strategy} signal on {pair}. Momentum confirms {direction} setup."


def get_market_outlook(asset, timeframe="daily"):
    """
    Get a general market outlook for an asset
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
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=100
            )
            content = response.choices[0].message.content if response.choices and hasattr(
                response.choices[0].message, "content") else None
            return content.strip() if content else None
        except (AttributeError, TypeError):
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Content-Type": "application/json",
                       "Authorization": f"Bearer {api_key}"}
            data = {"model": "gpt-4o", "messages": [
                {"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 100}
            response = requests.post(
                url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                content = response.json(
                )["choices"][0]["message"].get("content")
                return content.strip() if content else None
            else:
                logger.error(
                    f"OpenAI API error: {response.status_code} - {response.text}")
                return None
    except Exception as e:
        logging.error(f"Error generating market outlook: {e}")
        return None


def send_signal_with_buttons(bot, chat_id, text, reply_markup):
    """
    Send a signal message with buttons.
    """
    bot.send_message(chat_id, text, reply_markup=reply_markup)


def format_signal(pair, direction, entry, stop_loss, take_profits, timeframe, strategy):
    """
    Format a trading signal
    """
    return (
        f"Signal for {pair} ({timeframe}):\n"
        f"Direction: {direction}\n"
        f"Entry: {entry}\n"
        f"Stop Loss: {stop_loss}\n"
        f"Take Profits: {', '.join(map(str, take_profits))}\n"
        f"Strategy: {strategy}"
    )


def send_trade_notification_async(symbol, action, take_profit, stop_loss, confidence):
    """
    Send a trade notification asynchronously.
    """
    logging.info(
        f"Sending trade notification: {symbol} {action} TP: {take_profit} SL: {stop_loss} Confidence: {confidence}"
    )
