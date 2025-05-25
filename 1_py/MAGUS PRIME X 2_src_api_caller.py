import requests

from utils.rate_limiter import RateLimiter

# Instantiate a RateLimiter with a desired minimum interval between API calls.
rate_limiter = RateLimiter(0.5)


def make_api_call(url: str, params: dict = None) -> requests.Response:
    """
    Makes an HTTP GET request to the specified URL while enforcing rate-limiting.

    :param url: The API endpoint URL.
    :param params: Optional query parameters for the API call.
    :return: The response from the API call.
    """
    # Block if necessary to ensure we do not exceed the rate limit.
    rate_limiter.wait()
    response = requests.get(url, params=params)
    return response


if __name__ == "__main__":
    # Example usage of the API caller.
    test_url = "http://example.com/api/data"
    try:
        response = make_api_call(test_url)
        if response.status_code == 200:
            print("API call successful!")
        else:
            print(f"API call failed with status: {response.status_code}")
    except Exception as e:
        print(f"Error during API call: {e}")
