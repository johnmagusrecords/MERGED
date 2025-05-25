import logging

import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


# Test direct Assistant access
def test_assistant_direct():
    """Test direct access to the OpenAI Assistant"""
    logger.info("Testing direct Assistant access...")

    try:
        # Import assistant functionality
        from openai_assistant import get_trade_analysis, get_trade_commentary

        # Test market analysis
        logger.info("Getting market analysis for BTCUSD...")
        analysis = get_trade_analysis(symbol="BTCUSD", price=72000, timeframe="4h")

        if analysis and "error" not in analysis:
            logger.info("✅ Got analysis successfully:")
            logger.info(analysis["analysis"][:100] + "...")
        else:
            logger.error("❌ Failed to get analysis")
            if analysis:
                logger.error(f"Error: {analysis.get('error')}")

        # Test trade commentary
        logger.info("\nGetting trade commentary for BTCUSD...")
        commentary = get_trade_commentary(
            symbol="BTCUSD",
            direction="BUY",
            entry=72000,
            stop_loss=71000,
            targets=[73000, 74000, 75000],
            strategy="Breakout",
        )

        if commentary:
            logger.info("✅ Got commentary successfully:")
            logger.info(commentary[:100] + "...")
            return True
        else:
            logger.error("❌ Failed to get commentary")
            return False

    except ImportError:
        logger.error("❌ Could not import OpenAI Assistant module")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing Assistant: {str(e)}")
        return False


# Test Signal Dispatcher API integration
def test_signal_dispatcher_api():
    """Test accessing the OpenAI Assistant through the Signal Dispatcher API"""
    logger.info("\nTesting Signal Dispatcher API integration...")

    try:
        # Assume Signal Dispatcher is running on default port
        base_url = "http://localhost:5001"

        # Test the AI commentary endpoint
        endpoint = f"{base_url}/api/get_ai_commentary"
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": "magus_prime_secret_key",  # Default API key
        }

        payload = {
            "symbol": "BTCUSD",
            "direction": "BUY",
            "entry": 72000,
            "stop_loss": 71000,
            "tp1": 73000,
            "tp2": 74000,
            "tp3": 75000,
            "strategy": "Breakout",
        }

        logger.info(f"Sending request to {endpoint}...")
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            commentary = result.get("commentary")

            if commentary:
                logger.info("✅ Got commentary from API successfully:")
                logger.info(commentary[:100] + "...")
                return True
            else:
                logger.error("❌ Response OK but no commentary returned")
                return False
        else:
            logger.error(f"❌ API error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False

    except requests.RequestException as e:
        logger.error(f"❌ Error connecting to Signal Dispatcher API: {str(e)}")
        logger.info(
            "Make sure the Signal Dispatcher is running (run_signal_dispatcher.bat)"
        )
        return False
    except Exception as e:
        logger.error(f"❌ Error testing Signal Dispatcher API: {str(e)}")
        return False


if __name__ == "__main__":
    print("===== TESTING MAGUS PRIMEX ASSISTANT INTEGRATION =====")

    # Test direct assistant access
    direct_result = test_assistant_direct()

    # Test Signal Dispatcher API integration
    api_result = test_signal_dispatcher_api()

    # Print summary
    print("\n===== TEST RESULTS =====")
    print(f"Direct Assistant Access: {'PASSED' if direct_result else 'FAILED'}")
    print(f"Signal Dispatcher API Integration: {'PASSED' if api_result else 'FAILED'}")

    if not direct_result and not api_result:
        print(
            " "
\n❌ Both tests failed. Please run fix_as + "sistant_imports.bat to install required  + "dependencies."
        )
    elif not api_result:
        print(
            " "
\n⚠️ Direct access works but API integra + "tion failed. Make sure Signal Dispatcher + " is running."
        )
    else:
        print("\n✅ All tests passed! MAGUS PRIMEX ASSISTANT is properly integrated.")

    input("\nPress Enter to exit...")
