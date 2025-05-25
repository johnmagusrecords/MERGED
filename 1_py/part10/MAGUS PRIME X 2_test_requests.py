"""
Test script to verify requests library is working correctly.
This provides examples of how to use the requests module properly.
"""

import os
import sys

import requests


def test_requests():
    print(f"Requests version: {requests.__version__}")
    print(f"Python version: {sys.version}")
    print("-" * 60)

    print("\nTesting basic GET request...")
    try:
        # Make a simple GET request to a reliable endpoint
        response = requests.get("https://httpbin.org/get", timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type')}")
        print(f"Response size: {len(response.text)} bytes")
        print("Request successful!")
    except Exception as e:
        print(f"GET request failed: {e}")

    print("\nTesting POST request...")
    try:
        # Make a POST request with some data
        data = {"name": "test", "value": 123}
        response = requests.post("https://httpbin.org/post", json=data, timeout=5)
        print(f"Status code: {response.status_code}")
        print(f"Sent data echoed back: {response.json()['json']}")
        print("POST request successful!")
    except Exception as e:
        print(f"POST request failed: {e}")

    # Check for optional dependencies
    print("\nChecking optional dependencies:")
    try:
        import chardet

        print(f"✓ chardet {chardet.__version__} is installed")
    except ImportError:
        print(
            "✗ chardet is not installed (used for auto-detecting character encodings)"
        )
        print("  Install with: pip install chardet")

    try:
        import cryptography

        print(f"✓ cryptography {cryptography.__version__} is installed")
    except ImportError:
        print("✗ cryptography is not installed (used for secure connections)")
        print("  Install with: pip install cryptography")


def print_environment_info():
    """Print environment information relevant to requests library operation"""
    print("\nEnvironment Information:")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Platform: {os.name}")

    # Show relevant environment variables
    print("\nRelevant Environment Variables:")
    for var in [
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "NO_PROXY",
        "REQUESTS_CA_BUNDLE",
        "SSL_CERT_FILE",
    ]:
        value = os.environ.get(var)
        print(f"  {var}: {value if value else 'Not set'}")

    # Show Python executable path
    print(f"\nPython executable: {os.path.abspath(sys.executable)}")
    print(
        f"Site packages directory: {os.path.join(os.path.dirname(os.__file__), 'site-packages')}"
    )


if __name__ == "__main__":
    print("REQUESTS MODULE TEST\n")
    test_requests()
    print_environment_info()
    print("\nTest complete.")
