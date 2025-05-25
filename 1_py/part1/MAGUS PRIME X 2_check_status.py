import os
import socket

import requests
from dotenv import load_dotenv


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60))
    print("=" * 60)


def check_bot_status():
    """Check if the bot server is running and responding."""
    print_header("BOT SERVER STATUS")

    try:
        # Try connecting to the bot server
        response = requests.get("http://127.0.0.1:5000/ping", timeout=5)

        if response.status_code == 200:
            print("✅ Bot server is running and responding")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"⚠️ Bot server responded with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to bot server - make sure it's running")
        print("   Run 'python bot.py' to start the server")
        return False
    except Exception as e:
        print(f"❌ Error checking bot status: {e}")
        return False


def check_capital_api():
    """Check if we can connect to the Capital.com API."""
    print_header("CAPITAL.COM API STATUS")

    # Load environment variables
    load_dotenv()
    api_url = os.getenv(
        "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
    )

    try:
        # Try connecting to the API ping endpoint
        base_url = api_url.split("/api/")[0]
        response = requests.get(f"{base_url}/ping", timeout=10)

        if response.status_code == 200:
            print("✅ Capital.com API is reachable")
            print(f"API URL: {api_url}")
            print(f"Status code: {response.status_code}")
            return True
        else:
            print(
                f"⚠️ Capital.com API responded with status code: {response.status_code}"
            )
            return False
    except Exception as e:
        print(f"❌ Error connecting to Capital.com API: {e}")
        return False


def check_signal_sender():
    """Check if the signal sender is configured correctly."""
    print_header("SIGNAL SENDER STATUS")

    try:
        # Import the send_signal function
        from send_signal_helper import ASSET_CONFIG, send_signal

        print("✅ Signal sender module loaded successfully")
        print(f"✅ Asset configuration loaded for {len(ASSET_CONFIG)} assets")

        # Check if assets are properly configured
        if "BTCUSD" in ASSET_CONFIG:
            print(f"✅ BTCUSD configuration found: {ASSET_CONFIG['BTCUSD']}")
        else:
            print("⚠️ BTCUSD configuration not found")

        if "GOLD" in ASSET_CONFIG:
            print(f"✅ GOLD configuration found: {ASSET_CONFIG['GOLD']}")
        else:
            print("⚠️ GOLD configuration not found")

        return True
    except ImportError:
        print("❌ Failed to import signal sender module")
        print("   Make sure send_signal_helper.py is in the current directory")
        return False
    except Exception as e:
        print(f"❌ Error checking signal sender: {e}")
        return False


def check_network():
    """Check network connectivity."""
    print_header("NETWORK STATUS")

    # Get local IP address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"✅ Local IP address: {local_ip}")
    except:
        print("⚠️ Could not determine local IP address")

    # Check internet connectivity
    try:
        response = requests.get("https://www.google.com", timeout=5)
        print(f"✅ Internet connection is active (Google: {response.status_code})")
    except:
        print("❌ Internet connection appears to be down")
        return False

    # Check DNS resolution for Capital.com
    try:
        capital_ip = socket.gethostbyname("api-capital.backend-capital.com")
        print(f"✅ DNS resolution for Capital.com: {capital_ip}")
    except:
        print("⚠️ Could not resolve Capital.com domain")

    return True


def print_summary(results):
    """Print a summary of all checks."""
    print_header("STATUS SUMMARY")

    all_passed = all(results.values())

    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check}: {status}")

    if all_passed:
        print("\n✅ All systems operational!")
    else:
        print("\n⚠️ Some checks failed. Review the details above.")


if __name__ == "__main__":
    print_header("MAGUS PRIME X STATUS CHECK")

    results = {
        "Network": check_network(),
        "Capital.com API": check_capital_api(),
        "Bot Server": check_bot_status(),
        "Signal Sender": check_signal_sender(),
    }

    print_summary(results)

    if not results["Bot Server"]:
        print("\nTIP: If the bot server is not running, start it with:")
        print("python bot.py")
