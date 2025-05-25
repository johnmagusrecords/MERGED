import json
import os
import sys
import time

import requests
from dotenv import load_dotenv


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(text.center(60))
    print("=" * 60)


def print_section(text):
    """Print a section header"""
    print("\n" + "-" * 60)
    print(text)
    print("-" * 60)


def check_env_file():
    """Check if .env file exists and is readable"""
    print_section("Checking .env File")

    env_path = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(env_path):
        print("❌ ERROR: .env file not found at", env_path)
        print("Please create a .env file with your Capital.com API credentials.")
        return False

    try:
        with open(env_path, "r") as f:
            content = f.read()
        print("✅ .env file exists and is readable")

        # Check for common formatting issues
        if "CAPITAL_API_KEY=" not in content:
            print("⚠️ WARNING: CAPITAL_API_KEY not found in .env file")
        if "CAPITAL_API_PASSWORD=" not in content:
            print("⚠️ WARNING: CAPITAL_API_PASSWORD not found in .env file")
        if "CAPITAL_API_IDENTIFIER=" not in content:
            print("⚠️ WARNING: CAPITAL_API_IDENTIFIER not found in .env file")

        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to read .env file: {e}")
        return False


def check_env_variables():
    """Check if required environment variables are set and not empty"""
    print_section("Checking Environment Variables")

    # Load environment variables
    load_dotenv()

    # Define required variables
    required_vars = {
        "CAPITAL_API_KEY": os.getenv("CAPITAL_API_KEY"),
        "CAPITAL_API_PASSWORD": os.getenv("CAPITAL_API_PASSWORD"),
        "CAPITAL_API_IDENTIFIER": os.getenv("CAPITAL_API_IDENTIFIER"),
        "CAPITAL_API_URL": os.getenv(
            "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
        ),
    }

    all_vars_present = True

    # Check each variable
    for var_name, var_value in required_vars.items():
        if not var_value:
            print(f"❌ {var_name} is not set or is empty")
            all_vars_present = False
        else:
            # Mask sensitive data
            if var_name in ["CAPITAL_API_KEY", "CAPITAL_API_PASSWORD"]:
                masked_value = (
                    var_value[:4] + "..." + var_value[-4:]
                    if len(var_value) > 8
                    else "***"
                )
                print(f"✅ {var_name} is set: {masked_value}")
            else:
                print(f"✅ {var_name} is set: {var_value}")

    if not all_vars_present:
        print("\n❌ Some required environment variables are missing or empty.")
        return False

    print("\n✅ All required environment variables are set.")
    return True, required_vars


def diagnose_api_url(api_url):
    """Check if the API URL is valid and reachable"""
    print_section("Checking API URL")

    if not api_url.startswith(("http://", "https://")):
        print("❌ API URL is invalid. It must start with http:// or https://")
        return False

    # Check if demo or live
    if "demo" in api_url:
        print("ℹ️ Using DEMO API environment")
    else:
        print("⚠️ Using LIVE API environment - trades will affect your real account!")

    # Test connectivity
    try:
        response = requests.get(f"{api_url}/ping", timeout=10)
        if response.status_code == 200:
            print(f"✅ API URL is valid and reachable: {api_url}")
            return True
        else:
            print(f"❌ API URL returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to API URL: {e}")
        return False


def test_auth_request(credentials):
    """Test authentication with Capital.com API"""
    print_section("Testing Authentication")

    api_key = credentials["CAPITAL_API_KEY"]
    api_password = credentials["CAPITAL_API_PASSWORD"]
    api_identifier = credentials["CAPITAL_API_IDENTIFIER"]
    api_url = credentials["CAPITAL_API_URL"]

    url = f"{api_url}/session"
    headers = {"X-CAP-API-KEY": api_key}
    data = {"identifier": api_identifier, "password": api_password}

    # First, try with just essential fields to diagnose issues
    try:
        print("1. Testing with identifier and password...")
        response = requests.post(url, headers=headers, json=data, timeout=10)

        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 200:
            print("✅ Authentication successful!")
            # Test if we got the expected tokens
            try:
                resp_data = response.json()
                cst = resp_data.get("CST")
                security = resp_data.get("X-SECURITY-TOKEN")

                if cst and security:
                    print("✅ Received valid CST and X-SECURITY-TOKEN")
                    return True, cst, security
                else:
                    print("❌ Expected tokens not found in response")
            except json.JSONDecodeError:
                print("❌ Failed to parse JSON response")
                return False, None, None
        else:
            error_message = response.text
            # Specific error handling for common issues
            if "error.invalid.api.key" in error_message:
                print("❌ API key is invalid or in incorrect format")
                print("  - Check if the API key is correctly copied from Capital.com")
                print("  - Make sure there are no extra spaces or characters")
            elif "error.invalid.credentials" in error_message:
                print("❌ Username or password is incorrect")
                print("  - Check if your email and password are correctly entered")
                print("  - Verify your account is active and not locked")
            elif "error.null.client.token" in error_message:
                print("❌ null client token error")
                print("  - This usually means your API key is missing or empty")
                print("  - Make sure X-CAP-API-KEY header is included and not empty")

            return False, None, None
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False, None, None


def test_data_endpoints(cst, security, credentials):
    """Test accessing data endpoints with authenticated session"""
    if not cst or not security:
        print_section("Data Endpoint Tests: SKIPPED (Authentication failed)")
        return

    print_section("Testing Data Endpoints")

    api_key = credentials["CAPITAL_API_KEY"]
    api_url = credentials["CAPITAL_API_URL"]

    # Test accounts endpoint
    try:
        print("1. Testing accounts endpoint...")
        url = f"{api_url}/accounts"
        headers = {"X-CAP-API-KEY": api_key, "CST": cst, "X-SECURITY-TOKEN": security}

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            accounts = response.json().get("accounts", [])
            print(f"✅ Success! Found {len(accounts)} accounts.")
            for i, account in enumerate(accounts):
                print(
                    f" "
  Account {i+1}: {account.get('accountTy + "pe')} - Balance: {account.get('balance') + "} {account.get('currency')}"
                )
        else:
            print(
                f"❌ Failed to get accounts: {response.status_code} - {response.text}"
            )
    except Exception as e:
        print(f"❌ Error accessing accounts: {e}")

    # Test markets endpoint
    try:
        print("\n2. Testing markets endpoint...")
        url = f"{api_url}/markets?searchTerm=BTCUSD"
        headers = {"X-CAP-API-KEY": api_key, "CST": cst, "X-SECURITY-TOKEN": security}

        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            markets = response.json().get("markets", [])
            print(f"✅ Success! Found {len(markets)} markets matching 'BTCUSD'.")
            if markets:
                market = markets[0]
                print(
                    f" "
  Example: {
                                        market.get(
                                                   'instrumentName') + "} - Bid: {market.get('bid')},
                                        Ask: {mark + "et.get('offer')}"                )
        else:
            print(f"❌ Failed to get markets: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error accessing markets: {e}")


def check_python_version():
    """Check Python version compatibility"""
    print_section("Checking Python Version")
    import platform

    python_version = platform.python_version()
    python_bits = "64-bit" if sys.maxsize > 2**32 else "32-bit"

    print(f"Python version: {python_version} ({python_bits})")

    # Check if Python version is compatible
    major, minor, _ = python_version.split(".")
    if int(major) >= 3 and int(minor) >= 6:
        print("✅ Python version is compatible")
    else:
        print(
            f"❌ Python version {python_version} may be too old. Recommended: Python 3.6+"
        )


def check_internet_connection():
    """Check internet connectivity"""
    print_section("Checking Internet Connection")

    urls = [
        "https://www.google.com",
        "https://api-capital.backend-capital.com",
        "https://demo-api-capital.backend-capital.com",
    ]

    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ Connected to {url}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to {url}: {e}")


def save_diagnostic_report(success, results):
    """Save diagnostic results to a file"""
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "success": success,
        "python_version": sys.version,
        "platform": sys.platform,
        "results": results,
    }

    try:
        with open("auth_diagnostic_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print("\nDiagnostic report saved to auth_diagnostic_report.json")
    except Exception as e:
        print(f"Failed to save diagnostic report: {e}")


def generate_fix_instructions(results):
    """Generate specific instructions to fix authentication issues"""
    print_section("How to Fix Authentication Issues")

    if not results.get("env_file_exists", True):
        print(
            "1. Create a .env file in the project directory with the following content:"
        )
        print("```")
        print("CAPITAL_API_KEY=your_api_key_here")
        print("CAPITAL_API_PASSWORD=your_api_password_here")
        print("CAPITAL_API_IDENTIFIER=your_email@example.com")
        print("CAPITAL_API_URL=https://demo-api-capital.backend-capital.com/api/v1")
        print("```")

    if not results.get("env_vars_complete", True):
        print("1. Make sure all required variables are set in your .env file:")
        if not os.getenv("CAPITAL_API_KEY"):
            print("   - Add CAPITAL_API_KEY=your_api_key_here")
        if not os.getenv("CAPITAL_API_PASSWORD"):
            print("   - Add CAPITAL_API_PASSWORD=your_api_password_here")
        if not os.getenv("CAPITAL_API_IDENTIFIER"):
            print("   - Add CAPITAL_API_IDENTIFIER=your_email@example.com")

    if not results.get("api_url_valid", True):
        print("2. Check that your API URL is correct:")
        print(
            "   - For demo accounts: https://demo-api-capital.backend-capital.com/api/v1"
        )
        print("   - For live accounts: https://api-capital.backend-capital.com/api/v1")

    if not results.get("auth_successful", True):
        print("3. Verify your API credentials:")
        print("   - Log in to your Capital.com account")
        print("   - Go to API Management section")
        print("   - Check that your API key is active and correctly copied")
        print("   - Ensure your email and password are correctly entered")
        print("   - If using a demo account, check that your demo credentials are used")


def main():
    print_header("Capital.com API Authentication Diagnostic")
    print("This tool will diagnose issues with your Capital.com API authentication.")

    # Store results
    results = {}

    # Step 1: Check Python version
    check_python_version()

    # Step 2: Check internet connection
    check_internet_connection()

    # Step 3: Check .env file
    results["env_file_exists"] = check_env_file()

    # Step 4: Check environment variables
    env_vars_result = check_env_variables()
    if isinstance(env_vars_result, tuple):
        results["env_vars_complete"] = True
        _, credentials = env_vars_result
    else:
        results["env_vars_complete"] = env_vars_result
        credentials = {
            "CAPITAL_API_KEY": os.getenv("CAPITAL_API_KEY", ""),
            "CAPITAL_API_PASSWORD": os.getenv("CAPITAL_API_PASSWORD", ""),
            "CAPITAL_API_IDENTIFIER": os.getenv("CAPITAL_API_IDENTIFIER", ""),
            "CAPITAL_API_URL": os.getenv(
                "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
            ),
        }

    # Step 5: Check API URL
    results["api_url_valid"] = diagnose_api_url(credentials["CAPITAL_API_URL"])

    # Step 6: Test authentication
    auth_result = test_auth_request(credentials)
    if isinstance(auth_result, tuple):
        results["auth_successful"] = auth_result[0]
        cst, security = auth_result[1], auth_result[2]
    else:
        results["auth_successful"] = auth_result
        cst, security = None, None

    # Step 7: Test data endpoints if authentication successful
    if cst and security:
        test_data_endpoints(cst, security, credentials)

    # Generate overall result
    success = results.get("auth_successful", False)

    # Print summary
    print_section("Diagnostic Summary")
    print(
        f" "
Environment file: {
                                   '✅ OK' if results.get + "(
                                                             'env_file_exists',
                                   False) else '❌ Missi + "ng/Invalid'}"    )
    print(
        f" "
Environment vars: {
                                   '✅ Complete' if resul + "ts.get(
                                                                   'env_vars_complete',
                                   False) else  + "'❌ Incomplete'}"    )
    print(
        f"API URL: {'✅ Valid' if results.get('api_url_valid', False) else '❌ Invalid'}"
    )
    print(
        f"Authentication: {'✅ Successful' if results.get('auth_successful', False) else '❌ Failed'}"
    )
    print(f"\nOverall result: {'✅ PASSED' if success else '❌ FAILED'}")

    # Generate fix instructions
    if not success:
        generate_fix_instructions(results)

    # Save diagnostic report
    save_diagnostic_report(success, results)

    print("\nDiagnostic complete. Follow the instructions above to fix any issues.")
    print("Run the bot again after making the necessary changes.")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
