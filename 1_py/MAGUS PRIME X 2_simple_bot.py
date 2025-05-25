"""
Simple version of the MAGUS PRIME X trading bot for testing.
This minimal implementation focuses on API connectivity and core functionality.
"""

import logging
import os
import time

import requests
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables
load_dotenv()

# API settings
CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
CAPITAL_API_PASSWORD = os.getenv("CAPITAL_API_PASSWORD")
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_API_IDENTIFIER")
CAPITAL_API_URL = os.getenv(
    "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
)


class SimpleBot:
    def __init__(self):
        self.authenticated = False
        self.cst = None
        self.security_token = None

        # Try authentication on startup
        self.authenticate()

    def authenticate(self):
        """Authenticate with Capital.com API"""
        url = f"{CAPITAL_API_URL}/session"
        headers = {"X-CAP-API-KEY": CAPITAL_API_KEY}
        data = {"identifier": CAPITAL_IDENTIFIER, "password": CAPITAL_API_PASSWORD}

        try:
            logging.info("Authenticating with Capital.com API...")
            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self.cst = data.get("CST")
                self.security_token = data.get("X-SECURITY-TOKEN")
                self.authenticated = True
                logging.info("Authentication successful!")
                return True
            else:
                logging.error(
                    f"Authentication failed: {response.status_code} - {response.text}"
                )
                self.authenticated = False
                return False
        except Exception as e:
            logging.error(f"Authentication error: {str(e)}")
            self.authenticated = False
            return False

    def get_account_info(self):
        """Get account information"""
        if not self.authenticated:
            if not self.authenticate():
                return None

        url = f"{CAPITAL_API_URL}/accounts"
        headers = {
            "X-CAP-API-KEY": CAPITAL_API_KEY,
            "CST": self.cst,
            "X-SECURITY-TOKEN": self.security_token,
        }

        try:
            logging.info("Fetching account information...")
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                accounts = data.get("accounts", [])
                if accounts:
                    account = accounts[0]
                    return {
                        "balance": float(account.get("balance", 0)),
                        "pnl": float(account.get("profitLoss", 0)),
                        "currency": account.get("currency", "USD"),
                    }
                return None
            else:
                logging.error(
                    f"Failed to get account info: {response.status_code} - {response.text}"
                )
                return None
        except Exception as e:
            logging.error(f"Error getting account info: {str(e)}")
            return None

    def get_markets(self, search_term=""):
        """Get available markets"""
        if not self.authenticated:
            if not self.authenticate():
                return []

        url = f"{CAPITAL_API_URL}/markets"
        if search_term:
            url += f"?searchTerm={search_term}"

        headers = {
            "X-CAP-API-KEY": CAPITAL_API_KEY,
            "CST": self.cst,
            "X-SECURITY-TOKEN": self.security_token,
        }

        try:
            logging.info(
                f"Fetching markets{' for ' + search_term if search_term else ''}..."
            )
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return data.get("markets", [])
            else:
                logging.error(
                    f"Failed to get markets: {response.status_code} - {response.text}"
                )
                return []
        except Exception as e:
            logging.error(f"Error getting markets: {str(e)}")
            return []

    def run(self):
        """Run a simple test cycle"""
        logging.info("Starting simple test cycle...")

        # Step 1: Check authentication
        if not self.authenticated and not self.authenticate():
            logging.error("Authentication failed. Exiting test cycle.")
            return False

        # Step 2: Get account info
        account_info = self.get_account_info()
        if account_info:
            logging.info(
                f"Account Balance: {account_info['balance']} {account_info['currency']}"
            )
            logging.info(
                f"Current P&L: {account_info['pnl']} {account_info['currency']}"
            )
        else:
            logging.error("Failed to get account information.")
            return False

        # Step 3: Get popular markets
        popular_symbols = ["BTCUSD", "GOLD", "US30", "EURUSD"]
        for symbol in popular_symbols:
            markets = self.get_markets(symbol)
            if markets:
                market = markets[0]
                logging.info(
                    f"{symbol} - Bid: {market.get('bid')}, Ask: {market.get('offer')}"
                )
            else:
                logging.warning(f"Could not find market data for {symbol}")

        logging.info("Test cycle completed successfully!")
        return True


if __name__ == "__main__":
    bot = SimpleBot()

    try:
        # Run the test cycle
        if bot.run():
            print("\n✅ Simple bot test completed successfully!")
        else:
            print("\n❌ Simple bot test failed!")

        # Keep the script running
        print("\nPress Ctrl+C to exit...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nBot stopped by user.")
    except Exception as e:
        logging.error(f"Error running simple bot: {str(e)}")
