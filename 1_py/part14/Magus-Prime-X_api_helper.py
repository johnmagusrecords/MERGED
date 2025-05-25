import os
import time
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Capital.com API credentials
CAPITAL_API_KEY = os.getenv('CAPITAL_API_KEY')
CAPITAL_API_IDENTIFIER = os.getenv('CAPITAL_API_IDENTIFIER')
CAPITAL_API_PASSWORD = os.getenv('CAPITAL_API_PASSWORD')
CAPITAL_API_URL = os.getenv('CAPITAL_API_URL')


class CapitalAPIHelper:
    def __init__(self):
        self.base_url = CAPITAL_API_URL
        self.session = requests.Session()
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def api_request(self, endpoint, method="GET", params=None, data=None, headers=None):
        """Make API request with automatic retry for rate limiting"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        default_headers = {
            "X-CAP-API-KEY": CAPITAL_API_KEY,
            "Content-Type": "application/json"
        }

        if headers:
            default_headers.update(headers)

        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=default_headers,
                    timeout=30
                )

                if "error.too-many.requests" in response.text:
                    wait_time = self.retry_delay * (attempt + 1)
                    logger.warning(
                        f"Rate limit hit. Waiting {wait_time} seconds before retry.")
                    time.sleep(wait_time)
                    continue

                return response.json()

            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

        return {"error": "Max retries exceeded"}


# Test function
if __name__ == "__main__":
    api = CapitalAPIHelper()
    print("Testing Capital.com API connection...")
    # Test with a simple endpoint
    result = api.api_request("/session")
    print(f"API Response: {result}")
