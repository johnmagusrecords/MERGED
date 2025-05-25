# ...existing code...

import logging

import requests

# Define constants for Capital.com API
CAPITAL_API_URL = "https://api-capital.backend-capital.com"
CAPITAL_API_KEY = "your_api_key_here"
CAPITAL_IDENTIFIER = "your_identifier_here"
CAPITAL_API_PASSWORD = "your_password_here"


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""

    pass


def authenticate():
    """Authenticate with Capital.com API"""
    url = f"{CAPITAL_API_URL}/session"
    headers = {"X-CAP-API-KEY": CAPITAL_API_KEY, "Content-Type": "application/json"}
    payload = {"identifier": CAPITAL_IDENTIFIER, "password": CAPITAL_API_PASSWORD}

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()
        return data.get("cst"), data.get("x_security")
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred during authentication: {http_err}")
        raise AuthenticationError("Authentication failed due to HTTP error")
    except Exception as e:
        logging.error(f"Authentication error: {str(e)}")
        raise AuthenticationError("Authentication failed")


# ...existing code...
