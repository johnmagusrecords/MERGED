from config import STRATEGY_DESCRIPTIONS, config
import logging
import os
import random
import requests  # Fixed missing import

# Try to import openai, handle gracefully if not available
try:
    import openai  # type: ignore
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning(
        "OpenAI package not found. Commentary will use fallback templates.")
    logging.warning("Install with: pip install openai")

# Import the assistant integration with proper lowercase comparison
try:
    from openai_assistant import get_trade_commentary

    ASSISTANT_AVAILABLE = True
except ImportError:
    ASSISTANT_AVAILABLE = False
    logging.warning("MAGUS PRIMEX ASSISTANT integration not available")

# Configure and check assistant enablement
MAGUS_ASSISTANT_ENABLED = (
    os.getenv("MAGUS_ASSISTANT_ENABLED", "false").lower() == "true"
)


logger = logging.getLogger(__name__)

# Configure OpenAI if available
openai_key = config["news"]["openai_key"]
if OPENAI_AVAILABLE and openai_key:
    openai.api_key = openai_key
    OPENAI_CONFIGURED = True
else:
    OPENAI_CONFIGURED = False
    if openai_key and not OPENAI_AVAILABLE:
        logging.warning(
            "OpenAI API key found but openai package is not installed")
    elif not openai_key and OPENAI_AVAILABLE:
        logging.warning(
            "OpenAI package installed but API key is not configured")


def generate_fallback_commentary(pair, direction, strategy):
    """
    Generate fallback commentary when AI is not available or fails

    Args:
        pair: Symbol/trading pair (e.g., BTCUSD)
        direction: Trade direction (BUY or SELL)
        strategy: Trading strategy name

    Returns:
        str: Human-readable commentary on the trading signal
    """
    dir_txt = "buying opportunity" if direction.upper() == "BUY" else "selling pressure"

    if strategy.lower() == "breakout":
        return f"Breakout setup detected on {pair}. Recent price action suggests strong {dir_txt} after a consolidation range."
    elif strategy.lower() == "swing":
        return f"Swing trade setup active for {pair}. Indicators suggest a medium-term move aligned with trend direction."
    elif strategy.lower() == "scalping":
        return f"Scalping opportunity on {pair}. Volatility spike confirms {dir_txt} potential over next few candles."
    elif strategy.lower() == "fvg":
        return f"Fair Value Gap strategy in play on {pair}. Smart money imbalance indicates likely {dir_txt} zone."
    elif strategy.lower() == "news-based":
        return f"News-based trade triggered on {pair}. Reaction to fundamental news aligns with short-term {dir_txt} signal."
    return f"{strategy} strategy activated for {pair}. {dir_txt.capitalize()} detected by current indicators."


class CommentaryGenerator:
    """
    Generates intelligent commentary for trading signals including:
    - Strategy explanations
    - Technical analysis insights
    - Market mood assessment
    """

    def __init__(self):
        self.strategies = STRATEGY_DESCRIPTIONS
        self.openai_enabled = OPENAI_CONFIGURED
        self.assistant_enabled = ASSISTANT_AVAILABLE

        # Fallback templates when OpenAI is not available
        self.bullish_templates = [
            "Strong momentum with increasing volume suggests continued upward movement.",
            "Multiple technical indicators showing bullish convergence.",
            "Clear breakout from previous resistance level with strong confirmation.",
            "Bullish engulfing pattern with strong follow-through expected.",
            "Higher lows forming with increasing buying pressure.",
        ]

        self.bearish_templates = [
            "Declining momentum with increasing volume suggests continued downward movement.",
            "Multiple technical indicators showing bearish divergence.",
            "Clear breakdown from previous support level with strong confirmation.",
            "Bearish engulfing pattern with strong follow-through expected.",
            "Lower highs forming with increasing selling pressure.",
        ]

        self.technical_insights = {
            "RSI": [
                "RSI showing oversold conditions, potential reversal point.",
                "RSI in overbought territory, watch for resistance.",
                "RSI crossing above 50, confirming bullish momentum.",
                "RSI crossing below 50, confirming bearish momentum.",
            ],
            "MACD": [
                "MACD crossing above signal line, bullish signal.",
                "MACD crossing below signal line, bearish signal.",
                "MACD histogram expanding, trend strengthening.",
                "MACD histogram contracting, potential trend weakness.",
            ],
            "Volume": [
                "Increasing volume confirms the price movement.",
                "Decreasing volume suggests potential trend weakness.",
                "Volume spike indicates strong interest at current levels.",
                "Above average volume on this breakout increases confidence.",
            ],
        }

    def get_strategy_explanation(self, strategy_name):
        """Get explanation for a trading strategy"""
        strategy = strategy_name.strip()

        # Return the description if available
        if strategy in self.strategies:
            return self.strategies[strategy]

        # Try to match partially
        for key, description in self.strategies.items():
            if key.lower() in strategy.lower() or strategy.lower() in key.lower():
                return description

        # Default generic explanation
        return "This signal is based on technical analysis and market conditions, following price action and momentum."

    def generate_ai_commentary(self, symbol, direction, strategy_name, indicators=None):
        """Generate sophisticated commentary using OpenAI if available"""

        # Try using the MAGUS PRIMEX ASSISTANT first if available
        if self.assistant_enabled and ASSISTANT_AVAILABLE and MAGUS_ASSISTANT_ENABLED:
            try:
                # Format indicators for the assistant
                indicator_text = ""
                if indicators:
                    for key, value in indicators.items():
                        indicator_text += f"{key}: {value}, "

                # Get commentary from the assistant
                entry_price = indicators.get("Price", "current price")
                targets = [
                    indicators.get("TP1"),
                    indicators.get("TP2"),
                    indicators.get("TP3"),
                ]
                stop_loss = indicators.get("SL", "appropriate stop loss")

                assistant_commentary = get_trade_commentary(
                    symbol=symbol,
                    direction=direction,
                    entry=entry_price,
                    stop_loss=stop_loss,
                    targets=targets,
                    strategy=strategy_name,
                )

                if assistant_commentary:
                    return assistant_commentary

                # Fall through to standard OpenAI if assistant fails

            except Exception as e:
                logger.error(f"Error using MAGUS PRIMEX ASSISTANT: {e}")
                # Fall through to standard OpenAI approach

        # Use standard OpenAI if assistant not available or failed
        if not self.openai_enabled:
            return self.generate_fallback_commentary(
                direction, strategy_name, indicators
            )

        try:
            # Create a prompt for OpenAI
            prompt = f"""
            Generate a brief, professional trading commentary for a {direction} signal on {symbol}.
            This is a {strategy_name} strategy.
            
            Additional technical details to mention:
            """

            # Add indicator information if available
            if indicators:
                for key, value in indicators.items():
                    prompt += f"- {key}: {value}\n"

            # Keep the response short, focused, and professional
            prompt += """
            Keep the commentary between 2-3 sentences, focused on key technical factors.
            Be specific and insightful - avoid generic statements.
            Don't use emoji or informal language. This is for professional traders.
            """

            # Update to use the chat completions API format
            try:
                # First try with client API
                messages = [
                    {
                        "role": "system",
                        "content": "You are a professional trading analyst.",
                    },
                    {"role": "user", "content": prompt},
                ]

                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=100,
                )

                commentary = response.choices[0].message.content.strip()
            except AttributeError:
                # Fall back to direct API call if client API doesn't work
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai.api_key}",
                }
                data = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional trading analyst.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 100,
                }

                response = requests.post(url, headers=headers, json=data)
                response_data = response.json()
                commentary = response_data["choices"][0]["message"]["content"].strip(
                )

            return commentary

        except Exception as e:
            logger.error(f"Error generating AI commentary: {e}")
            return self.generate_fallback_commentary(
                direction, strategy_name, indicators
            )

    def generate_fallback_commentary(self, direction, strategy_name, indicators=None):
        """Generate commentary using templates when OpenAI is unavailable"""
        commentary = []

        # Add directional commentary
        if direction.upper() == "BUY":
            commentary.append(random.choice(self.bullish_templates))
        else:
            commentary.append(random.choice(self.bearish_templates))

        # Add strategy explanation
        strategy_explanation = self.get_strategy_explanation(strategy_name)
        commentary.append(strategy_explanation)

        # Add technical insights if indicators provided
        if indicators:
            if "RSI" in indicators:
                commentary.append(random.choice(
                    self.technical_insights["RSI"]))
            if "MACD" in indicators:
                commentary.append(random.choice(
                    self.technical_insights["MACD"]))
            if "Volume" in indicators:
                commentary.append(random.choice(
                    self.technical_insights["Volume"]))

        # Return combined commentary
        return " ".join(commentary)

    def generate_hold_time_explanation(self, timeframe, asset_type):
        """Generate explanation of expected hold time based on timeframe and asset type"""
        timeframe_hours = {
            "1m": 0.5,
            "5m": 1,
            "15m": 3,
            "30m": 6,
            "1h": 12,
            "4h": 48,
            "1d": 120,
        }

        # Get base hours from timeframe
        base_hours = timeframe_hours.get(timeframe, 24)

        # Adjust based on asset type
        if asset_type == "Crypto":
            base_hours *= 0.8  # Crypto tends to move faster
        elif asset_type == "Forex":
            base_hours *= 1.0  # Standard
        elif asset_type in ["Stock", "Index"]:
            base_hours *= 1.2  # Stocks tend to take longer
        elif asset_type == "Commodity":
            base_hours *= 1.5  # Commodities typically take longer

        # Format the time description
        if base_hours < 1:
            minutes = int(base_hours * 60)
            time_desc = f"{minutes} minutes"
        elif base_hours < 24:
            time_desc = f"{base_hours:.1f} hours"
        else:
            days = base_hours / 24
            time_desc = f"{days:.1f} days"

        return f"Expected hold time: {time_desc}"


# Create a global instance for easy access
commentary_gen = CommentaryGenerator()


def generate_signal_commentary(symbol, direction, strategy, timeframe, indicators=None):
    """
    Generate comprehensive commentary for a trading signal

    Args:
        symbol (str): Trading symbol
        direction (str): BUY or SELL
        strategy (str): Trading strategy name
        timeframe (str): Chart timeframe
        indicators (dict): Optional indicator values

    Returns:
        dict: Commentary with strategy explanation and technical insights
    """
    # Get asset type from configuration
    asset_type = "Unknown"
    if symbol in config["assets"]:
        asset_type = config["assets"][symbol].get("type", "Unknown")

    # Generate hold time explanation
    hold_time = commentary_gen.generate_hold_time_explanation(
        timeframe, asset_type)

    # Generate AI commentary if indicators provided
    if indicators:
        technical_insights = commentary_gen.generate_ai_commentary(
            symbol, direction, strategy, indicators
        )
    else:
        technical_insights = commentary_gen.generate_fallback_commentary(
            direction, strategy, indicators
        )

    # Get strategy explanation
    strategy_explanation = commentary_gen.get_strategy_explanation(strategy)

    # If we don't have a technical insight yet, use the standalone fallback
    if not technical_insights:
        technical_insights = generate_fallback_commentary(
            symbol, direction, strategy)

    return {
        "strategy_explanation": strategy_explanation,
        "technical_insights": technical_insights,
        "hold_time": hold_time,
        "asset_type": asset_type,
    }


if __name__ == "__main__":
    # Simple test script
    test_symbol = "BTCUSD"
    test_direction = "BUY"
    test_strategy = "Breakout"
    test_timeframe = "4h"

    test_indicators = {
        "RSI": 65,
        "MACD": "Bullish crossover",
        "Volume": "Above average",
    }

    print("Commentary Generator Test")
    print("-" * 50)

    commentary = generate_signal_commentary(
        test_symbol, test_direction, test_strategy, test_timeframe, test_indicators
    )

    print(f"Symbol: {test_symbol} ({commentary['asset_type']})")
    print(f"Direction: {test_direction}")
    print(f"Strategy: {test_strategy}")
    print(f"Timeframe: {test_timeframe}")
    print("-" * 50)
    print(f"Strategy Explanation: {commentary['strategy_explanation']}")
    print(f"Technical Insights: {commentary['technical_insights']}")
    print(f"Hold Time: {commentary['hold_time']}")

    # Test the standalone fallback function
    print("\nTesting standalone fallback commentary:")
    print("-" * 50)
    for strat in ["breakout", "swing", "scalping", "fvg", "news-based", "unknown"]:
        commentary = generate_fallback_commentary(
            test_symbol, test_direction, strat)
        print(f"{strat.capitalize()}: {commentary}")
