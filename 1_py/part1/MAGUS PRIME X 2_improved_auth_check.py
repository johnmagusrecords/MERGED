import json
import logging
import os
import sys
import time

import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("auth_check.log")],
)


def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)


def print_step(step_num, description):
    print(f"\n[Step {step_num}] {description}")
    print("-" * 60)


def load_env_variables():
    """Load and validate environment variables"""
    print_step(1, "Loading environment variables")

    # Try to load from .env file
    load_dotenv()

    # Get the relevant variables
    api_key = os.getenv("CAPITAL_API_KEY", "").strip()
    api_password = os.getenv("CAPITAL_API_PASSWORD", "").strip()
    api_identifier = os.getenv("CAPITAL_API_IDENTIFIER", "").strip()
    api_url = os.getenv(
        "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
    ).strip()

    # Validation checks
    if not api_key:
        print("❌ ERROR: CAPITAL_API_KEY is not set in .env file")
    else:
        # Mask API key for privacy
        masked_key = api_key[:4] + "****" + api_key[-4:] if len(api_key) > 8 else "****"
        print(f"✓ CAPITAL_API_KEY is set: {masked_key}")

        # Check for common issues
        if api_key.startswith(" ") or api_key.endswith(" "):
            print("⚠️ WARNING: API key contains leading or trailing spaces!")
            api_key = api_key.strip()
            print(f"   Stripped value: '{api_key}'")

            # Update .env file automatically
            try:
                update_env_file("CAPITAL_API_KEY", api_key)
                print("✓ Updated .env file to remove whitespace")
            except Exception as e:
                print(f"❌ Failed to update .env file: {e}")

    if not api_password:
        print("❌ ERROR: CAPITAL_API_PASSWORD is not set in .env file")
    else:
        print("✓ CAPITAL_API_PASSWORD is set")

    if not api_identifier:
        print("❌ ERROR: CAPITAL_API_IDENTIFIER is not set in .env file")
    else:
        print(f"✓ CAPITAL_API_IDENTIFIER is set: {api_identifier}")

    print(f"✓ CAPITAL_API_URL is set: {api_url}")

    credentials = {
        "api_key": api_key,
        "api_password": api_password,
        "api_identifier": api_identifier,
        "api_url": api_url,
    }

    # Check if we have the minimum required credentials
    if not api_key or not api_password or not api_identifier:
        print("\n❌ Missing required credentials!")
        return None

    return credentials


def update_env_file(key, value):
    """Update a value in the .env file"""
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()

        with open(env_path, "w") as f:
            for line in lines:
                if line.startswith(f"{key}="):
                    f.write(f"{key}={value}\n")
                else:
                    f.write(line)


def test_api_connectivity(api_url):
    """Test if the API URL is reachable"""
    print_step(2, "Testing API connectivity")

    try:
        # Test basic connectivity to the domain
        base_url = api_url.split("/api/")[0]
        print(f"Testing connection to {base_url}...")

        response = requests.get(f"{base_url}/ping", timeout=10)
        if response.status_code == 200:
            print(f"✓ Successfully connected to {base_url}")
            return True
        else:
            print(f"❌ Failed to connect to {base_url}: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")

        # Check if it's a DNS error
        if "Name or service not known" in str(e) or "getaddrinfo failed" in str(e):
            print(
                "   This appears to be a DNS resolution error. Check your internet connection."
            )
        elif "Connection refused" in str(e):
            print(
                "   The server actively refused the connection. The API might be down."
            )
        elif "timeout" in str(e).lower():
            print(
                "   The connection timed out. The server may be overloaded or unreachable."
            )

        return False


def authenticate(credentials):
    """Attempt to authenticate with Capital.com API"""
    print_step(3, "Testing API authentication")

    api_key = credentials["api_key"]
    api_password = credentials["api_password"]
    api_identifier = credentials["api_identifier"]
    api_url = credentials["api_url"]

    url = f"{api_url}/session"
    headers = {"X-CAP-API-KEY": api_key}
    data = {"identifier": api_identifier, "password": api_password}

    try:
        print("Sending authentication request...")
        response = requests.post(url, headers=headers, json=data, timeout=15)

        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✓ Authentication successful!")
            response_data = response.json()

            # Validate the response
            if "CST" in response_data and "X-SECURITY-TOKEN" in response_data:
                print("✓ Received valid authentication tokens")
                cst = response_data["CST"]
                security_token = response_data["X-SECURITY-TOKEN"]
                return cst, security_token
            else:
                print(
                    "❌ Authentication succeeded but response is missing expected tokens"
                )
                print(f"Response content: {json.dumps(response_data, indent=2)}")
                return None, None
        else:
            print(f"❌ Authentication failed with status code {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")

                # Analyze specific error codes
                error_code = error_data.get("errorCode", "")
                if error_code == "error.null.client.token":
                    print("\nDiagnosis: API Key Header Issue")
                    print(
                        " "
  - The API key is missing, empty, or no + "t being properly sent in the header"
                    )
                    print(
                        "  - Check for whitespace or special characters in your API key"
                    )
                    print(
                        "  - Make sure your API key exactly matches what's shown in Capital.com"
                    )
                elif error_code == "error.invalid.api.key":
                    print("\nDiagnosis: Invalid API Key Format")
                    print("  - Your API key has an invalid format")
                    print("  - Capital.com API keys typically follow a specific format")
                    print("  - Regenerate your API key in the Capital.com dashboard")
                elif error_code == "error.invalid.credentials":
                    print("\nDiagnosis: Invalid Login Credentials")
                    print("  - Your username or password is incorrect")
                    print("  - Make sure you're using the correct credentials")
                    print(
                        "  - For demo accounts, these may be different from your main account"
                    )
                else:
                    print(f"\nUnrecognized error code: {error_code}")
                    print(
                        "  - Check Capital.com documentation for specific error handling"
                    )

            except json.JSONDecodeError:
                print(f"Response content (not JSON): {response.text}")

            return None, None
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None, None


def test_market_access(credentials, cst, security_token):
    """Test access to market data endpoints"""
    if not cst or not security_token:
        print_step(4, "Skipping market data test (authentication failed)")
        return False

    print_step(4, "Testing market data access")

    api_key = credentials["api_key"]
    api_url = credentials["api_url"]

    url = f"{api_url}/markets?searchTerm=BTCUSD"
    headers = {"X-CAP-API-KEY": api_key, "CST": cst, "X-SECURITY-TOKEN": security_token}

    try:
        print("Fetching market data for 'BTCUSD'...")
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            market_data = response.json()
            markets = market_data.get("markets", [])
            if markets:
                print(f"✓ Successfully retrieved {len(markets)} markets")

                # Example market data
                if len(markets) > 0:
                    example = markets[0]
                    print("\nExample market data:")
                    print(f"  Name: {example.get('instrumentName')}")
                    print(f"  Epic: {example.get('epic')}")
                    print(f"  Status: {example.get('marketStatus')}")
                    print(f"  Bid: {example.get('bid')}")
                    print(f"  Ask: {example.get('offer')}")

                return True
            else:
                print("❌ No markets found in the response")
                print(f"Response content: {json.dumps(market_data, indent=2)}")
                return False
        else:
            print(
                f"❌ Market data request failed with status code {response.status_code}"
            )
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response content (not JSON): {response.text}")

            return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


def generate_report(credentials, auth_success, market_success):
    """Generate a detailed report and recommendations"""
    print_step(5, "Generating diagnostic report")

    # Overall status
    if auth_success and market_success:
        overall_status = "✅ PASSED"
    else:
        overall_status = "❌ FAILED"

    print(f"\nOverall Status: {overall_status}")
    print(f"Authentication Test: {'✅ PASSED' if auth_success else '❌ FAILED'}")
    print(f"Market Data Test: {'✅ PASSED' if market_success else '❌ FAILED'}")

    # Save report to file
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "api_url": credentials["api_url"],
        "api_identifier": credentials["api_identifier"],
        "api_key_masked": (
            credentials["api_key"][:4] + "****" + credentials["api_key"][-4:]
            if len(credentials["api_key"]) > 8
            else "****"
        ),
        "tests": {"authentication": auth_success, "market_data": market_success},
        "overall_status": "success" if auth_success and market_success else "failure",
        "python_version": sys.version,
        "platform": sys.platform,
    }

    with open("auth_diagnostic_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\nDetailed report saved to auth_diagnostic_report.json")

    # Show recommendations if there were failures
    if not auth_success or not market_success:
        print_recommendations()


def print_recommendations():
    """Print recommendations for fixing common issues"""
    print_header("RECOMMENDATIONS")

    print(
        """
1. API Key Issues:
   - Double-check your API key for accuracy
   - Regenerate your API key on Capital.com if needed
   - Make sure there are no spaces or special characters

2. Authentication Credentials:
   - Verify your email and password are correct
   - For demo accounts, make sure you're using demo credentials
   - Ensure you're using the correct API URL for demo/live

3. Internet Connectivity:
   - Check your firewall settings
   - Make sure you're not using a VPN that might block the API
   - Verify DNS resolution is working correctly

4. API Limits:
   - You might be hitting rate limits - wait a few minutes and try again
   - Implement proper rate limiting in your code

5. Account Issues:
   - Verify your Capital.com account is active
   - Check if you need to complete additional verification
   - Contact Capital.com support if problems persist
"""
    )


def main():
    print_header("Capital.com API Authentication Diagnostic")
    print("This tool diagnoses issues with your Capital.com API configuration.")

    # Load and validate environment variables
    credentials = load_env_variables()
    if not credentials:
        print_recommendations()
        return

    # Test API connectivity
    connectivity_success = test_api_connectivity(credentials["api_url"])
    if not connectivity_success:
        print(
            "\n❌ API connectivity test failed. Please check your internet connection and API URL."
        )
        print_recommendations()
        return

    # Test authentication
    cst, security_token = authenticate(credentials)
    auth_success = cst is not None and security_token is not None

    # Test market data access
    market_success = test_market_access(credentials, cst, security_token)

    # Generate report
    generate_report(credentials, auth_success, market_success)

    if auth_success and market_success:
        print(
            "\n✅ All tests passed! Your Capital.com API configuration is working correctly."
        )
    else:
        print("\n❌ Some tests failed. Please review the recommendations above.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDiagnostic interrupted by user.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"\n❌ An unexpected error occurred: {e}")
    finally:
        print("\nPress Enter to exit...")
        input()
