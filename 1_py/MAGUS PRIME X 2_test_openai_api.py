import logging
import os

import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def test_openai_connection():
    """Test OpenAI API connectivity with the provided key"""
    logger.info("Testing OpenAI API connection...")

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        logger.error("OpenAI API key not found in .env file")
        return False

    # Print the first few characters of the API key (for debugging)
    logger.info(
        f"API key format: {api_key[:7]}...{api_key[-4:] if len(api_key) > 10 else ''}"
    )

    # Create a simple request to the OpenAI API
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Write a short trading tip for cryptocurrency markets",
            },
        ],
    }

    try:
        logger.info("Sending request to OpenAI API...")
        response = requests.post(url, headers=headers, json=data, timeout=15)

        if response.status_code == 200:
            result = response.json()
            message = (
                result.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "No content")
            )

            logger.info("[SUCCESS] OpenAI API connection successful!")
            logger.info(f"Response: {message}")
            return True

        else:
            logger.error(f"[FAILED] OpenAI API error: {response.status_code}")
            logger.error(f"Response: {response.text}")

            # Provide helpful error messages based on status code
            if response.status_code == 401:
                logger.error(
                    "Authentication error: Your API key is invalid or improperly formatted"
                )
                logger.error(
                    "OpenAI API keys should start with 'sk-' and not include 'Bearer'"
                )
            elif response.status_code == 429:
                logger.error("Rate limit exceeded: You've exceeded your API quota")

            return False

    except Exception as e:
        logger.error(f"[ERROR] Error connecting to OpenAI API: {e}")
        return False


def test_commentary_generation():
    """Test the commentary generator with the OpenAI API"""
    logger.info("Testing commentary generation...")

    try:
        # Import our commentary generator
        from commentary_generator import generate_signal_commentary

        # Generate a sample commentary
        commentary = generate_signal_commentary(
            symbol="BTCUSD",
            direction="BUY",
            strategy="Breakout",
            timeframe="4h",
            indicators={
                "RSI": "65 (bullish)",
                "MACD": "Bullish crossover",
                "Volume": "Above average",
            },
        )

        logger.info("[SUCCESS] Commentary generated successfully!")
        logger.info(f"Strategy: {commentary['strategy_explanation']}")
        logger.info(f"Technical: {commentary['technical_insights']}")
        logger.info(f"Hold Time: {commentary['hold_time']}")

        return True

    except Exception as e:
        logger.error(f"[ERROR] Error generating commentary: {e}")
        return False


if __name__ == "__main__":
    print("===== OpenAI API Test =====")

    # Test direct API connection
    api_success = test_openai_connection()

    # If API connection was successful, test commentary generation
    if api_success:
        commentary_success = test_commentary_generation()
    else:
        commentary_success = False

    # Print summary - using ASCII characters instead of Unicode emojis
    print("\n===== Test Results =====")
    print(f"API Connection: {'[PASSED]' if api_success else '[FAILED]'}")
    print(f"Commentary Generation: {'[PASSED]' if commentary_success else '[FAILED]'}")

    input("\nPress Enter to exit...")
