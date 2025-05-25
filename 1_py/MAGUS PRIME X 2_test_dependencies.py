import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    try:
        logger.info("Testing imports...")

        # Test pandas
        logger.info("Testing pandas...")
        import pandas as pd

        pd.DataFrame({"test": [1, 2, 3]})
        logger.info("✓ Pandas working")

        # Test numpy
        logger.info("Testing numpy...")
        import numpy as np

        np.array([1, 2, 3])
        logger.info("✓ Numpy working")

        # Test TA-Lib
        logger.info("Testing TA-Lib...")
        import talib

        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        talib.SMA(data)
        logger.info("✓ TA-Lib working")

        # Test News API
        logger.info("Testing News API...")
        from newsapi import NewsApiClient

        NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
        logger.info("✓ News API client loaded")

        # Test requests
        logger.info("Testing requests...")
        import requests

        requests.get("https://api.github.com")
        logger.info("✓ Requests working")

        # Test python-dotenv
        logger.info("Testing python-dotenv...")
        from dotenv import load_dotenv

        load_dotenv()
        logger.info("✓ python-dotenv working")

        logger.info("All dependencies working correctly!")
        return True

    except Exception as e:
        logger.error(f"Error testing dependencies: {str(e)}")
        return False


if __name__ == "__main__":
    test_imports()
