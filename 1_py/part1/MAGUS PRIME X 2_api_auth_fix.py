import json
import os

import requests
from dotenv import load_dotenv


def print_separator(message):
    print("\n" + "=" * 50)
    print(message)
    print("=" * 50)


def check_env_loading():
    """Check if environment variables are loading properly"""
    print_separator("CHECKING ENVIRONMENT VARIABLES")

    # Try to load from .env file
    load_dotenv()

    # Get API credentials
    api_key = os.getenv("CAPITAL_API_KEY")
    api_identifier = os.getenv("CAPITAL_API_IDENTIFIER")
    api_password = os.getenv("CAPITAL_API_PASSWORD")
    api_url = os.getenv(
        "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
    )

    # Display credentials (with masking for sensitive info)
    print(
        f"API Key: {api_key[:4] + '****' if api_key and len(api_key) > 4 else 'Not set'}"
    )
    print(f"API Identifier: {api_identifier or 'Not set'}")
    print(f"API Password: {'*' * 8 if api_password else 'Not set'}")
    print(f"API URL: {api_url}")

    # Check for leading/trailing whitespace
    if api_key and (api_key.strip() != api_key):
        print("⚠️ WARNING: API key contains leading or trailing whitespace!")
        print(f"Raw API key: '{api_key}'")

        # Fix API key if needed
        fixed_key = api_key.strip()
        print(f"Fixed API key: '{fixed_key}'")

        # Update .env file
        try:
            with open(".env", "r") as file:
                env_content = file.read()

            # Replace the API key with the fixed version
            env_content = env_content.replace(
                f"CAPITAL_API_KEY={api_key}", f"CAPITAL_API_KEY={fixed_key}"
            )

            with open(".env", "w") as file:
                file.write(env_content)

            print("✅ Fixed API key whitespace in .env file")

            # Reload environment variables
            os.environ["CAPITAL_API_KEY"] = fixed_key
            api_key = fixed_key
        except Exception as e:
            print(f"❌ Failed to update .env file: {e}")

    return api_key, api_identifier, api_password, api_url


def test_authentication(api_key, api_identifier, api_password, api_url):
    """Test authentication with Capital.com API"""
    print_separator("TESTING API AUTHENTICATION")

    url = f"{api_url}/session"
    headers = {"X-CAP-API-KEY": api_key}
    data = {"identifier": api_identifier, "password": api_password}

    try:
        print("Sending authentication request...")
        response = requests.post(url, headers=headers, json=data, timeout=10)

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        if response.status_code == 200:
            print("✅ Authentication successful!")

            try:
                resp_data = response.json()
                cst = resp_data.get("CST")
                security = resp_data.get("X-SECURITY-TOKEN")

                if cst and security:
                    print("✅ Received valid security tokens")
                    return True
                else:
                    print("❌ Missing security tokens in response")
            except json.JSONDecodeError:
                print("❌ Response not valid JSON")

            return False
        else:
            print("❌ Authentication failed")

            # Check for common error types
            error_text = response.text.lower()
            if "error.invalid.api.key" in error_text:
                print("\nIssue: Invalid API key format")
                print(
                    "- Double-check that your API key is copied correctly from Capital.com"
                )
                print("- Make sure there are no leading/trailing spaces")
            elif "error.invalid.credentials" in error_text:
                print("\nIssue: Invalid credentials (email/password)")
                print("- Verify your email and password are correct")
                print("- Check if you need to use demo account credentials")
            elif "error.null.client.token" in error_text:
                print("\nIssue: Null client token (empty API key)")
                print("- Make sure your API key isn't empty")
                print("- Check if API key has any unexpected characters")
            else:
                print("\nUnspecified error. Check the response for details.")

            return False
    except Exception as e:
        print(f"❌ Error during request: {e}")
        return False


def suggest_fixes():
    """Display suggestions for fixing authentication issues"""
    print_separator("SUGGESTIONS")

    print("1. Visit Capital.com and verify your API credentials")
    print("2. Make sure you're using demo API credentials with the demo URL")
    print("3. Check for any special characters or whitespace in your credentials")
    print("4. Try regenerating your API key in your Capital.com account")
    print("5. Update your .env file with the new credentials")

    print("\nSample .env format:")
    print(
        """
CAPITAL_API_KEY=your_api_key_here
CAPITAL_API_PASSWORD=your_password_here
CAPITAL_API_IDENTIFIER=your_email@example.com
CAPITAL_API_URL=https://demo-api-capital.backend-capital.com/api/v1
"""
    )


def main():
    print("🔍 CAPITAL.COM API AUTHENTICATION DIAGNOSTIC")
    print("This tool will help diagnose and fix API authentication issues")

    # Check environment variables
    api_key, api_identifier, api_password, api_url = check_env_loading()

    # Check if any credentials are missing
    if not api_key or not api_identifier or not api_password:
        print("❌ Missing required credentials!")
        suggest_fixes()
        return

    # Test authentication
    auth_success = test_authentication(api_key, api_identifier, api_password, api_url)

    if not auth_success:
        suggest_fixes()
    else:
        print("\n✅ Authentication is working correctly now!")
        print("You can run your bot with these credentials.")


if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
