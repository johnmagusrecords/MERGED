import logging
import os
import time
from typing import List, Optional

import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
OPENAI_API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

# Cache mechanism to avoid excessive API calls
commentary_cache = {}
CACHE_EXPIRY = 3600  # Cache entries expire after 1 hour


def get_trade_commentary(
    symbol: str,
    direction: str,
    entry: float,
    stop_loss: float,
    targets: List[float],
    strategy: str = "Technical",
) -> Optional[str]:
    """
    Generate detailed trading commentary for a signal using OpenAI's API.

    Args:
        symbol: Trading pair/symbol (e.g., "BTCUSD")
        direction: Trade direction ("BUY" or "SELL")
        entry: Entry price
        stop_loss: Stop loss price
        targets: List of target prices [tp1, tp2, tp3]
        strategy: Strategy type (e.g., "Breakout", "Support/Resistance")

    Returns:
        str: AI-generated commentary or None if generation failed
    """
    if not OPENAI_API_KEY:
        logger.warning(
            "OpenAI API key not set. Cannot generate trade commentary.")
        return None

    # Normalize inputs
    direction = direction.upper()
    strategy = strategy or "Technical"
    symbol = symbol.upper()

    # Check cache first (using a composite key)
    cache_key = f"{symbol}:{direction}:{entry}:{stop_loss}:{strategy}"
    if cache_key in commentary_cache:
        cache_entry = commentary_cache[cache_key]
        # If cache entry is still valid
        if time.time() - cache_entry["timestamp"] < CACHE_EXPIRY:
            logger.info(f"Using cached commentary for {symbol} {direction}")
            return cache_entry["commentary"]

    # Calculate risk-reward ratios
    risk = abs(entry - stop_loss)
    rewards = [abs(target - entry) /
                   risk for target in targets if target is not None]
    risk_reward_text = ", ".join(
        [f"{rr:.2f}R" for rr in rewards]) if rewards else "N/A"

    # Generate a prompt for the AI model
    prompt = f"""
You are MAGUS PRIME X, an expert trading assistant specializing in financial market analysis.
Write a concise, professional trading analysis for a {direction} signal on {symbol}.

Trade details:
- Symbol: {symbol}
- Direction: {direction}
- Entry Price: {entry}
- Stop Loss: {stop_loss}
- Targets: {', '.join([str(t) for t in targets if t is not None])}
- Risk-Reward Ratio: {risk_reward_text}
- Strategy: {strategy}

Your analysis should include:
1. The key technical or fundamental reasons for this {direction} signal
2. Key levels to watch and potential resistance/support zones
3. Market context that supports this trade
4. Any specific patterns that form the basis of this {strategy} strategy
5. Risk management advice specific to this trade

Keep your response under 400 characters. Be direct, professional, and use trading terminology.
Do not include disclaimers or prefaces like "Here's an analysis".
"""

    try:
        # Set up the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        }

        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": " "
You are MAGUS PRIME X, an expert trading + " assistant specializing in financial mar + "ket analysis.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": OPENAI_TEMPERATURE,
            "max_tokens": OPENAI_MAX_TOKENS,
        }

        # Make the API call
        logger.info(f"Requesting AI commentary for {symbol} {direction} signal")
        response = requests.post(
            OPENAI_API_ENDPOINT, headers=headers, json=payload, timeout=30
        )

        # Check for successful response
        if response.status_code == 200:
            result = response.json()
            commentary = result["choices"][0]["message"]["content"].strip()

            # Cache the result
            commentary_cache[cache_key] = {
                "commentary": commentary,
                "timestamp": time.time(),
            }

            logger.info(
                f"Generated AI commentary for {symbol} ({len(commentary)} chars)"
            )
            return commentary
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error generating trade commentary: {e}")
        return None


def get_market_analysis(symbol: str) -> Optional[str]:
    """
    Generate a broader market analysis for a symbol.

    Args:
        symbol: Trading pair/symbol to analyze

    Returns:
        str: AI-generated market analysis or None if generation failed
    """
    if not OPENAI_API_KEY:
        return None

    # Similar implementation as get_trade_commentary but with a different prompt
    prompt = f"""
Provide a brief market analysis for {symbol}. Include:
1. Current market sentiment and trend direction
2. Key technical levels to watch
3. Recent fundamental drivers affecting this asset
4. Short-term price outlook

Keep your response under 500 characters and focused on actionable insights.
"""

    try:
        # Set up the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        }

        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are MAGUS PRIME X, an expert market analyst.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": OPENAI_TEMPERATURE,
            "max_tokens": OPENAI_MAX_TOKENS,
        }

        # Make the API call
        response = requests.post(
            OPENAI_API_ENDPOINT, headers=headers, json=payload, timeout=30
        )

        # Check for successful response
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error generating market analysis: {e}")
        return None


def generate_trade_recap(
    symbol: str,
    direction: str,
    entry: float,
    exit: float,
    targets_hit: List[bool],
    strategy: str,
    trade_duration: str,
) -> Optional[str]:
    """
    Generate a recap commentary for a completed trade.

    Args:
        symbol: Trading pair/symbol
        direction: Original trade direction
        entry: Entry price
        exit: Exit price
        targets_hit: List of booleans indicating which targets were hit
        strategy: Original strategy
        trade_duration: How long the trade was active

    Returns:
        str: AI-generated trade recap or None if generation failed
    """
    if not OPENAI_API_KEY:
        return None

    # Format targets hit information
    targets_summary = "No targets hit"
    if any(targets_hit):
        hit_count = sum(targets_hit)
        targets_summary = f"{hit_count} target{'s' if hit_count > 1 else ''} hit"

    # Calculate profit/loss percentage
    if direction.upper() == "BUY":
        pnl_percent = ((exit - entry) / entry) * 100
    else:  # SELL
        pnl_percent = ((entry - exit) / entry) * 100

    pnl_direction = "profit" if pnl_percent > 0 else "loss"

    # Generate the prompt
    prompt = f"""
Generate a brief trade recap for a {direction} trade on {symbol} that just completed.

Trade details:
- Symbol: {symbol}
- Direction: {direction}
- Entry: {entry}
- Exit: {exit}
- P&L: {abs(pnl_percent):.2f}% {pnl_direction}
- Strategy: {strategy}
- Duration: {trade_duration}
- Results: {targets_summary}

Keep your response under 300 characters. Focus on what worked or didn't work in this trade
and any lessons that could be applied to future trades.
"""

    try:
        # Set up the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        }

        payload = {
            "model": OPENAI_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are MAGUS PRIME X, an expert trading assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": OPENAI_TEMPERATURE,
            "max_tokens": OPENAI_MAX_TOKENS,
        }

        # Make the API call
        response = requests.post(
            OPENAI_API_ENDPOINT, headers=headers, json=payload, timeout=30
        )

        # Check for successful response
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error generating trade recap: {e}")
        return None


def clear_cache():
    """Clear the commentary cache."""
    global commentary_cache
    commentary_cache = {}
    logger.info("Commentary cache cleared")


# Initialization and self-test
def initialize():
    """Initialize the OpenAI assistant."""
    if not OPENAI_API_KEY:
        logger.warning(
            "OpenAI API key not set. AI-powered trade commentary will not be available."
        )
        return False

    logger.info(f"MAGUS PRIMEX ASSISTANT initialized with model: {OPENAI_MODEL}")
    return True


# Run initialization when module is imported
is_initialized = initialize()

# Self-test when run directly
if __name__ == "__main__":
    # Test the assistant
    symbol = "BTCUSD"
    entry = 72000
    stop_loss = 71000
    targets = [73000, 74000, 75000]

    print(f"Testing MAGUS PRIMEX ASSISTANT with {symbol}...")

    if not OPENAI_API_KEY:
        print("❌ OpenAI API key not set. Please set OPENAI_API_KEY in your .env file.")
        exit(1)

    # Test BUY commentary
    buy_commentary = get_trade_commentary(
        symbol=symbol,
        direction="BUY",
        entry=entry,
        stop_loss=stop_loss,
        targets=targets,
        strategy="Breakout",
    )

    if buy_commentary:
        print("\n=== BUY Signal Commentary ===")
        print(buy_commentary)
        print("\n✅ BUY commentary generated successfully")
    else:
        print("❌ Failed to generate BUY commentary")

    # Test SELL commentary
    sell_commentary = get_trade_commentary(
        symbol=symbol,
        direction="SELL",
        entry=entry,
        stop_loss=entry + 1000,
        targets=[entry - 1000, entry - 2000, entry - 3000],
        strategy="Support/Resistance",
    )

    if sell_commentary:
        print("\n=== SELL Signal Commentary ===")
        print(sell_commentary)
        print("\n✅ SELL commentary generated successfully")
    else:
        print("❌ Failed to generate SELL commentary")

    # Test market analysis
    analysis = get_market_analysis(symbol)
    if analysis:
        print("\n=== Market Analysis ===")
        print(analysis)
        print("\n✅ Market analysis generated successfully")
    else:
        print("❌ Failed to generate market analysis")

    print("\nMAGUS PRIMEX ASSISTANT is ready to use!")
