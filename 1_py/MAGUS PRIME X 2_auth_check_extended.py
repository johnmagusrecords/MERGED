import json
import logging
import os
import time

import requests
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("auth_check.log", mode="w"), logging.StreamHandler()],
)

# Load environment variables
load_dotenv()


def test_connection(api_url):
    """Test basic connectivity to the API"""
    try:
        print("\n1. Testing API connectivity...")
        response = requests.get(f"{api_url}/ping", timeout=10)
        if response.status_code == 200:
            print("✓ API connectivity test passed")
            return True
        else:
            print(f"✗ API connectivity test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ API connectivity error: {str(e)}")
        return False


def check_capital_auth():
    """Test Capital.com API authentication credentials"""
    print("\n2. Testing Capital.com API Authentication")

    # Get credentials from environment
    api_key = os.getenv("CAPITAL_API_KEY")
    api_password = os.getenv("CAPITAL_API_PASSWORD")
    api_identifier = os.getenv("CAPITAL_API_IDENTIFIER")
    api_url = os.getenv(
        "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
    )

    # Check if credentials are set
    if not api_key or not api_password or not api_identifier:
        print("✗ ERROR: API credentials are missing from environment variables")
        print("Please check your .env file contains:")
        print("  CAPITAL_API_KEY=your_api_key")
        print("  CAPITAL_API_PASSWORD=your_api_password")
        print("  CAPITAL_API_IDENTIFIER=your_email@example.com")
        return False

    # Print masked credentials for verification
    print(f"API Key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")
    print(f"API Identifier: {api_identifier}")
    print(f"API URL: {api_url}")

    # Test connection first
    if not test_connection(api_url):
        print("⚠ API connectivity issue - check your network or API URL")

    # Try to authenticate
    url = f"{api_url}/session"
    headers = {"X-CAP-API-KEY": api_key}
    data = {"identifier": api_identifier, "password": api_password}

    try:
        print("Attempting authentication...")
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            data = response.json()
            cst = data.get("CST")
            security = data.get("X-SECURITY-TOKEN")

            if cst and security:
                print("✓ Authentication successful!")
                print(f"CST: {cst[:4]}...{cst[-4:] if len(cst) > 8 else ''}")
                print(
                    f"X-SECURITY-TOKEN: {security[:4]}...{security[-4:] if len(security) > 8 else ''}"
                )
                return cst, security
            else:
                print("✗ Unexpected response: Tokens missing")
                print(f"Response: {data}")
                return False
        else:
            print("✗ Authentication failed")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")

            # Check for specific error cases
            if "error.invalid.api.key" in response.text:
                print("\nPROBLEM: Your API key is invalid")
                print("SOLUTION: Get a new API key from Capital.com")
            elif "error.invalid.credentials" in response.text:
                print("\nPROBLEM: Your identifier or password is incorrect")
                print("SOLUTION: Double-check your credentials")
            elif "error.null.client.token" in response.text:
                print("\nPROBLEM: Missing or invalid X-CAP-API-KEY header")
                print(
                    "SOLUTION: Make sure your API key is correct and properly formatted"
                )

            return False
    except Exception as e:
        print(f"✗ Error connecting to API: {e}")
        return False


def test_get_markets(cst, security):
    """Test retrieving markets to verify the authentication works"""
    if not cst or not security:
        print("\n3. Market Data Test: SKIPPED (Authentication failed)")
        return False

    print("\n3. Testing API Market Data Retrieval")
    api_url = os.getenv(
        "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
    )
    api_key = os.getenv("CAPITAL_API_KEY")

    try:
        url = f"{api_url}/markets?searchTerm=BTC"
        headers = {"X-CAP-API-KEY": api_key, "CST": cst, "X-SECURITY-TOKEN": security}

        print("Retrieving market data for 'BTC'...")
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            markets = data.get("markets", [])
            print(f"✓ Successfully retrieved {len(markets)} markets related to BTC")
            return True
        else:
            print(f"✗ Failed to retrieve markets: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error retrieving markets: {e}")
        return False


def run_diagnostic():
    print("===== Capital.com API Authentication Diagnostic =====")
    print("Running comprehensive tests...")

    # Timestamp the test for the report
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    auth_result = check_capital_auth()

    if auth_result and isinstance(auth_result, tuple):
        cst, security = auth_result
        market_result = test_get_markets(cst, security)
    else:
        market_result = False

    # Generate summary report
    print("\n===== DIAGNOSTIC SUMMARY =====")
    print(f"Timestamp: {timestamp}")
    print(f"Authentication Test: {'PASSED' if auth_result else 'FAILED'}")
    print(f"Market Data Test: {'PASSED' if market_result else 'FAILED'}")
    print(
        f"Overall Status: {'✓ ALL TESTS PASSED' if auth_result and market_result else '✗ SOME TESTS FAILED'}"
    )

    # Write detailed report to file
    try:
        report = {
            "timestamp": timestamp,
            "auth_status": bool(auth_result),
            "market_status": market_result,
            "overall_status": bool(auth_result and market_result),
            "env": {
                "api_url": os.getenv("CAPITAL_API_URL"),
                "api_key_masked": f"{os.getenv('CAPITAL_API_KEY', '')[:4]}...",
                "identifier_masked": os.getenv("CAPITAL_API_IDENTIFIER"),
            },
        }

        with open("auth_diagnostic.json", "w") as f:
            json.dump(report, f, indent=2)

        print("\nDetailed report saved to 'auth_diagnostic.json'")
    except Exception as e:
        print(f"Error writing report: {e}")

    print("\nTo fix authentication issues:")
    print("1. Verify your credentials are correct in the .env file")
    print("2. Make sure you're using the correct API URL for demo/live")
    print("3. Check if your Capital.com account is active")
    print("4. Ensure your IP address is not blocked by Capital.com")


if __name__ == "__main__":
    run_diagnostic()
    print("\nPress Enter to exit...")
    input()
