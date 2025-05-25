import json
import os

import requests
from dotenv import load_dotenv


def print_header(title):
    print("\n" + "=" * 70)
    print(f" {title} ".center(70))
    print("=" * 70)


def print_section(title):
    print("\n" + "-" * 70)
    print(f" {title} ".center(70))
    print("-" * 70)


def dump_json(data):
    """Format and print JSON data"""
    try:
        if isinstance(data, str):
            # Try to parse string as JSON
            parsed = json.loads(data)
            print(json.dumps(parsed, indent=2))
        else:
            # Already a dictionary
            print(json.dumps(data, indent=2))
    except:
        # Not valid JSON, print as is
        print(data)


def debug_auth_response():
    """Debug the authentication response in detail"""
    print_header("CAPITAL.COM API TOKEN DEBUGGER")

    # Load environment variables
    load_dotenv()

    # Get credentials
    api_key = os.getenv("CAPITAL_API_KEY", "").strip()
    api_password = os.getenv("CAPITAL_API_PASSWORD", "").strip()
    api_identifier = os.getenv("CAPITAL_API_IDENTIFIER", "").strip()
    api_url = os.getenv(
        "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
    ).strip()

    # Check credentials
    missing = []
    if not api_key:
        missing.append("CAPITAL_API_KEY")
    if not api_password:
        missing.append("CAPITAL_API_PASSWORD")
    if not api_identifier:
        missing.append("CAPITAL_API_IDENTIFIER")

    if missing:
        print(f"❌ Missing required credentials: {', '.join(missing)}")
        return

    # Display credentials for verification (masked)
    masked_key = api_key[:4] + "****" + api_key[-4:] if len(api_key) > 8 else "****"
    print(f"API Key: {masked_key}")
    print(f"API Identifier: {api_identifier}")
    print(f"API URL: {api_url}")

    # Make authentication request
    print_section("SENDING AUTHENTICATION REQUEST")

    url = f"{api_url}/session"
    headers = {"X-CAP-API-KEY": api_key}
    data = {"identifier": api_identifier, "password": api_password}

    # Print full request details
    print(f"Request URL: {url}")
    print(f"Request Headers: {headers}")
    print("Request Data:")
    dump_json(data)

    try:
        print("\nSending request...")
        response = requests.post(url, headers=headers, json=data, timeout=15)

        # Print full response details
        print_section("RAW API RESPONSE")
        print(f"Status Code: {response.status_code}")
        print("Response Headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")

        print("\nResponse Content:")
        try:
            dump_json(response.text)
        except:
            print(response.text)

        # Analyze the response
        print_section("RESPONSE ANALYSIS")

        if response.status_code == 200:
            print("✅ Received HTTP 200 OK status")

            try:
                json_data = response.json()
                print("✅ Response is valid JSON")

                # Check for expected tokens
                if "CST" in json_data:
                    print(f"✅ CST token found: {json_data['CST'][:5]}...")
                else:
                    print("❌ CST token missing from response body")

                    # Check if token is in headers instead
                    if "CST" in response.headers:
                        print(
                            f"💡 CST found in response HEADERS: {response.headers['CST'][:5]}..."
                        )

                if "X-SECURITY-TOKEN" in json_data:
                    print(
                        f"✅ X-SECURITY-TOKEN found: {json_data['X-SECURITY-TOKEN'][:5]}..."
                    )
                else:
                    print("❌ X-SECURITY-TOKEN missing from response body")

                    # Check if token is in headers instead
                    if "X-SECURITY-TOKEN" in response.headers:
                        print(
                            f" "
💡 X-SECURITY-TOKEN found in response HEA + "DERS: {response.headers['X-SECURITY-TOKE + "N'][:5]}..."
                        )

            except json.JSONDecodeError:
                print("❌ Response is not valid JSON")
        else:
            print(f"❌ Received HTTP {response.status_code} error status")

            if response.status_code == 429:
                print("💡 You are being rate limited. Wait before trying again.")
            elif response.status_code == 401:
                print("💡 Authentication failed - check your credentials.")

    except Exception as e:
        print(f"❌ Request error: {str(e)}")

    print_section("POSSIBLE SOLUTIONS")

    print(
        """
1. If tokens are in response HEADERS instead of body:
   - Update the authentication code to check both locations

2. If rate limited (HTTP 429):
   - Implement a longer backoff period between requests
   - Reduce the frequency of API calls

3. If no tokens found anywhere:
   - Double-check all credentials for accuracy
   - Try regenerating your API key on Capital.com
   - Ensure account is active and not locked

4. Check the Capital.com API documentation:
   - API format may have changed
   - Different authentication endpoint might be needed

5. Network issues:
   - Check if firewall is blocking certain types of responses
   - Try from a different network if possible
    """
    )


if __name__ == "__main__":
    debug_auth_response()
    input("\nPress Enter to exit...")
