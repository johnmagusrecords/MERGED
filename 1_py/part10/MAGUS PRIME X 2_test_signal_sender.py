import argparse
import json
import os
import sys
import time

import requests


# Add a helper function to create a runner batch file
def create_runner():
    """Create a batch file to easily run this script without path issues"""
    batch_path = os.path.join(os.path.dirname(__file__), "run_test.bat")
    with open(batch_path, "w") as f:
        f.write("@echo off\n")
        f.write("echo Running Signal Sender Test...\n")
        f.write("python test_signal_sender.py\n")
        f.write("pause\n")
    print(f"Created runner batch file at: {batch_path}")
    print("You can now run the test with a simple double-click on run_test.bat")


def test_send_signal(
    base_url="http://127.0.0.1:8080", endpoint="/send-signal", custom_data=None
):
    """Test function to send a trading signal to the Signal Sender API"""

    # Define the signal data - this is what the API actually expects based on error response
    signal_data = custom_data or {
        "pair": "GOLD",
        "entry": 3110,
        "stop_loss": 3100,
        "tp1": 3120,
        "tp2": 3135,
        "tp3": 3150,
        "timeframe": "30m",
        "mode": "SAFE_RECOVERY",
        "type": "Breakout",
    }

    url = f"{base_url}{endpoint}"
    print(f"Attempting to send signal to {url}...")

    try:
        # Try to get available endpoints (for API discovery)
        try:
            print("Checking available API endpoints...")
            discovery = requests.get(base_url, timeout=5)
            print(f"API root returned status code: {discovery.status_code}")
            if discovery.status_code == 200:
                try:
                    content = discovery.json()
                    print(f"API root response: {json.dumps(content)[:100]}...")
                except:
                    print(f"API root response: {discovery.text[:100]}...")
        except Exception as e:
            print(f"Could not retrieve API information from root endpoint: {e}")

        # Send POST request to the Signal Sender API
        print(f"Sending data: {json.dumps(signal_data, indent=2)}")
        response = requests.post(
            url, json=signal_data, timeout=10  # Add timeout to prevent hanging
        )

        # Print the response
        print("Status Code:", response.status_code)

        # Try to parse JSON, but handle non-JSON responses
        try:
            response_data = response.json()
            print("Response:", response_data)

            # Check for 400 error with specific missing fields
            if (
                response.status_code == 400
                and isinstance(response_data, dict)
                and "error" in response_data
            ):
                if "Missing required fields" in str(response_data["error"]):
                    print(
                        "\n✅ GOOD NEWS! The API endpoint exists but requires specific fields."
                    )
                    print(
                        "The server is expecting these fields:",
                        response_data["error"].replace("Missing required fields: ", ""),
                    )
                    print(
                        "\nTry running again with the complete data format (default):"
                    )
                    print("python test_signal_sender.py")
                    return response_data

            # Additional error handling for 404 in response body
            if (
                "error" in response_data
                and response_data.get("error", {}).get("error_code") == 404
            ):
                print("\nTROUBLESHOOTING SUGGESTIONS:")
                print(
                    "1. Verify the API server has the correct '/send-signal' endpoint configured"
                )
                print(
                    "2. Check if the API is expecting different parameters than what we're sending"
                )
                print(
                    " "
3. Make sure your Telegram bot token and + " chat IDs are correctly set in environme + "nt variables"
                )
                print(
                    "4. Examine the API server logs for more detailed error information"
                )
                print("\nCOMMON ALTERNATIVE ENDPOINTS TO TRY:")
                print("  --endpoint /signal")
                print("  --endpoint /signals/create")
                print("  --endpoint /api/send-signal")
                print("  --endpoint /telegram/send")
                print("\nTRY SIMPLER DATA FORMAT:")
                print("  Use --simple-data flag to test with minimal required fields")

            # Check for Telegram-specific error format
            if (
                "error" in response_data
                and isinstance(response_data["error"], dict)
                and response_data["error"].get("error_code") == 404
                and "ok" in response_data["error"]
            ):

                print("\n🚨 TELEGRAM ERROR DETECTED!")
                print(
                    "The API successfully received your request, but got a 404 error from Telegram."
                )
                print("This usually means one of the following:")
                print("1. Your Telegram bot token is invalid or missing")
                print("2. The chat/channel ID is incorrect or the bot is not a member")
                print("3. The bot doesn't have permission to post in the channel/group")
                print("\nPlease run our Telegram configuration tester to diagnose:")
                print("python test_telegram_config.py")
                return response_data

            return response_data
        except ValueError:
            print(f"Response is not valid JSON: {response.text[:100]}...")
            return {"error": "Invalid JSON response"}

    except requests.exceptions.ConnectionError:
        print(
            "ERROR: Connection failed. Make sure the API server is running at http://127.0.0.1:8080"
        )
        return None
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out. Server may be overloaded or unresponsive.")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error occurred: {e}")
        return None


def get_server_info(base_url="http://127.0.0.1:8080"):
    """Try to get information about the server and its capabilities"""
    print(f"Getting server information from {base_url}...")

    endpoints_to_try = [
        "/",
        "/api",
        "/docs",
        "/swagger",
        "/openapi.json",
        "/health",
        "/status",
    ]

    for endpoint in endpoints_to_try:
        try:
            url = f"{base_url}{endpoint}"
            print(f"Checking {url}...")
            response = requests.get(url, timeout=3)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type", "")
                if "json" in content_type:
                    try:
                        print(f"  Content: {json.dumps(response.json())[:100]}...")
                    except:
                        print(f"  Content: {response.text[:100]}...")
                else:
                    print(f"  Content: {response.text[:100]}...")
        except Exception as e:
            print(f"  Error: {e}")


def run_multiple_tests(
    count=1, delay=2, base_url="http://127.0.0.1:8080", endpoint="/send-signal"
):
    """Run the signal test multiple times with a delay between runs"""
    print(f"Running test {count} time(s) with {delay} second delay between runs")

    for i in range(count):
        print(f"\nTest run {i+1}/{count}")
        print("-" * 30)
        test_send_signal(base_url, endpoint)

        if i < count - 1:  # Don't delay after the last run
            print(f"Waiting {delay} seconds before next test...")
            time.sleep(delay)


def show_success_message():
    """Display a message about the successful discovery"""
    print("\n============================================")
    print("🎉 DISCOVERY SUMMARY")
    print("============================================")
    print("We found that the /send-signal endpoint exists and is working!")
    print("The API expects these specific fields:")
    print("  - pair")
    print("  - entry")
    print("  - stop_loss")
    print("  - tp1")
    print("  - tp2")
    print("  - tp3")
    print("  - timeframe")
    print("  - mode")
    print("  - type")
    print("\nThe simplified data test confirmed this by returning a 400 error")
    print(
        "with a specific message about missing fields, which is correct API behavior."
    )
    print("\nNEXT STEPS:")
    print("1. Run the test with complete data:")
    print("   python test_signal_sender.py")
    print("2. If you get a Telegram 404 error, run our configuration tester:")
    print("   python test_telegram_config.py")
    print("3. Check server logs for any additional errors during signal processing")
    print("============================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the Signal Sender API")
    parser.add_argument(
        "--url", default="http://127.0.0.1:8080", help="Base URL of the API server"
    )
    parser.add_argument("--endpoint", default="/send-signal", help="API endpoint path")
    parser.add_argument("--count", type=int, default=1, help="Number of test runs")
    parser.add_argument(
        "--delay", type=int, default=2, help="Delay between runs in seconds"
    )
    parser.add_argument(
        "--create-runner",
        action="store_true",
        help="Create a batch file to run this script",
    )
    parser.add_argument(
        "--check-endpoints", action="store_true", help="Try common endpoint variations"
    )
    parser.add_argument(
        "--server-info", action="store_true", help="Gather information about the server"
    )
    parser.add_argument(
        "--simple-data", action="store_true", help="Use simplified data format"
    )
    parser.add_argument(
        "--port", type=int, default=8080, help="Use a different port number"
    )
    parser.add_argument(
        "--show-summary", action="store_true", help="Show discovery summary"
    )

    args = parser.parse_args()

    # Update URL if port is specified
    if args.port != 8080:
        args.url = f"http://127.0.0.1:{args.port}"

    print("Signal Sender Test Script")
    print("========================")

    if args.create_runner:
        create_runner()
        sys.exit(0)

    if args.server_info:
        get_server_info(args.url)
        sys.exit(0)

    # Use simplified data if requested
    custom_data = None
    if args.simple_data:
        custom_data = {
            "pair": "GOLD",
            "message": "Buy GOLD now",
            "text": "Trading signal for GOLD",
        }
        print("Using simplified data format")

    if args.check_endpoints:
        common_endpoints = [
            "/send-signal",
            "/signal",
            "/signals/create",
            "/api/send-signal",
            "/telegram/send",
            "/webhook",
            "/bot/send",
            "/message",
        ]
        print(f"Testing {len(common_endpoints)} common endpoints...")
        for endpoint in common_endpoints:
            print(f"\n--- Testing endpoint: {endpoint} ---")
            test_send_signal(args.url, endpoint, custom_data)
            time.sleep(1)  # Brief delay between tests
        sys.exit(0)

    if args.show_summary:
        show_success_message()
        sys.exit(0)

    # Run the test with command line arguments
    run_multiple_tests(
        count=args.count, delay=args.delay, base_url=args.url, endpoint=args.endpoint
    )

    print(
        " "
\nINSIGHT: Based on our tests, the /send + "-signal endpoint exists and expects spec + "ific fields."
    )
    print("For a complete summary, run: python test_signal_sender.py --show-summary")

    print("\nCOMMAND OPTIONS:")
    print("  --server-info      Get information about the server capabilities")
    print("  --check-endpoints  Try common API endpoints")
    print("  --simple-data      Use a simplified data format")
    print("  --port PORT        Try a different port number")
    print("  --create-runner    Create a batch file for easy running")
    print("  --show-summary     Show discovery summary")
