"""
Authentication module for MAGUS PRIME X trading bot.

This module handles authentication with trading platforms and services.
"""

import logging
from typing import Dict

import requests


class Authenticator:
    """Handles authentication with trading platforms and verification of credentials."""

    def __init__(self, api_key: str, identifier: str, password: str, api_url: str):
        """Initialize the authenticator.

        Args:
            api_key: API key for authentication
            identifier: API identifier
            password: API password
            api_url: Base URL for API
        """
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.api_url = api_url
        self.session_token = None
        self.cst = None

    def verify_credentials(self) -> bool:
        """Verify that all required credentials are present.

        Returns:
            bool: True if all credentials are present
        """
        if not self.api_key:
            logging.error(
                "Missing API key. Please set CAPITAL_API_KEY in your environment."
            )
            return False

        if not self.identifier:
            logging.error(
                "Missing API identifier. Please set CAPITAL_API_IDENTIFIER in your environment."
            )
            return False

        if not self.password:
            logging.error(
                "Missing API password. Please set CAPITAL_API_PASSWORD in your environment."
            )
            return False

        if not self.api_url:
            logging.error(
                "Missing API URL. Please set CAPITAL_API_URL in your environment."
            )
            return False

        return True

    def authenticate(self) -> bool:
        """Authenticate with the trading platform API.

        Returns:
            bool: True if authentication was successful
        """
        if not self.verify_credentials():
            return False

        try:
            # Prepare authentication payload
            auth_payload = {
                "identifier": self.identifier,
                "password": self.password,
                "encryptedPassword": False,
            }

            # Set request headers
            headers = {
                "X-CAP-API-KEY": self.api_key,
                "Content-Type": "application/json",
            }

            # Make authentication request
            auth_url = f"{self.api_url}/session"
            response = requests.post(auth_url, json=auth_payload, headers=headers)

            # Check response
            if response.status_code == 200:
                # Store session tokens
                self.cst = response.headers.get("CST")
                self.session_token = response.headers.get("X-SECURITY-TOKEN")

                if self.cst and self.session_token:
                    logging.info("Authentication successful")
                    return True
                else:
                    logging.error("Missing security tokens in response")
                    return False
            else:
                logging.error(
                    f"Authentication failed: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logging.error(f"Authentication error: {e}")
            return False

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests.

        Returns:
            dict: Authentication headers
        """
        headers = {"X-CAP-API-KEY": self.api_key, "Content-Type": "application/json"}

        if self.cst:
            headers["CST"] = self.cst

        if self.session_token:
            headers["X-SECURITY-TOKEN"] = self.session_token

        return headers

    def refresh_authentication(self) -> bool:
        """Refresh authentication tokens.

        Returns:
            bool: True if refresh was successful
        """
        logging.info("Refreshing authentication tokens...")

        # Simply re-authenticate to refresh tokens
        return self.authenticate()
