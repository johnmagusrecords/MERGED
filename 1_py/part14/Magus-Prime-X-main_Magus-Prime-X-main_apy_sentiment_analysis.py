import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_news_sentiment(response):
    """
    Extract sentiment analysis from the response.

    Args:
        response: The response object containing sentiment data.

    Returns:
        dict: Parsed sentiment data or error details.
    """
    try:
        logger.info("Extracting sentiment from response.")
        sentiment_data = response.json()
        return {
            "sentiment": sentiment_data.get("sentiment", "neutral"),
            "confidence": sentiment_data.get("confidence", 0.0),
        }
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON response: {e}")
        return {"error": "Invalid JSON response"}
    except Exception as e:
        logger.error(f"Unexpected error while extracting sentiment: {e}")
        return {"error": str(e)}
