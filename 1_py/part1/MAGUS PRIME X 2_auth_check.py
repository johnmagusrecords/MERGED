import logging
import os

import requests
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables
load_dotenv()


def check_capital_auth():
    """Test Capital.com API authentication credentials"""
    print("\n=== Testing Capital.com API Authentication ===")

    # Get credentials from environment
    api_key = os.getenv("CAPITAL_API_KEY")
    api_password = os.getenv("CAPITAL_API_PASSWORD")
    api_identifier = os.getenv("CAPITAL_API_IDENTIFIER")
    api_url = os.getenv(
        "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
    )

    # Check if credentials are set
    if not api_key or not api_password or not api_identifier:
        print("❌ ERROR: API credentials are missing from environment variables")
        print("Please check your .env file contains:")
        print("  CAPITAL_API_KEY=your_api_key")
        print("  CAPITAL_API_PASSWORD=your_api_password")
        print("  CAPITAL_API_IDENTIFIER=your_email@example.com")
        return False

    # Print masked credentials for verification
    print(
        f"API Key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}"
    )
    print(f"API Identifier: {api_identifier}")
    print(f"API URL: {api_url}")

    # Try to authenticate
    url = f"{api_url}/session"
    headers = {"X-CAP-API-KEY": api_key}
    data = {"identifier": api_identifier, "password": api_password}

    try:
        print("\nAttempting authentication...")
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            data = response.json()
            cst = data.get("CST")
            security = data.get("X-SECURITY-TOKEN")

            if cst and security:
                print("✅ Authentication successful!")
                print(f"CST: {cst[:4]}...{cst[-4:] if len(cst) > 8 else ''}")
                print(
                    f"X-SECURITY-TOKEN: {security[:4]}...{security[-4:] if len(security) > 8 else ''}"
                )
                return True
            else:
                print("❌ Unexpected response: Tokens missing")
                print(f"Response: {data}")
                return False
        else:
            print("❌ Authentication failed")
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
        print("Auth check failed:", e)
        return False


if __name__ == "__main__":
    print("===== Capital.com API Authentication Check =====")
    print(
        "This utility checks if your Capital.com API credentials are working correctly.\n"
    )

    check_capital_auth()

    print("\nTo fix authentication issues:")
    print("1. Verify your credentials are correct in the .env file")
    print("2. Make sure you're using the correct API URL for demo/live")
    print("3. Check if your Capital.com account is active")
    print("4. Ensure your IP address is not blocked by Capital.com")

    print("\nPress Enter to exit...")
    # do_this() is not defined, so it has been removed or replaced with a placeholder
    pass

    # then_that() is not defined, so it has been removed or replaced with a placeholder
    pass

    input()
