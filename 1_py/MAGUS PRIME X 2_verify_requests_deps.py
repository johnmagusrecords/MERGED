"""
Verify that requests optional dependencies are installed correctly.
This script imports the optional dependencies that requests uses.
"""

import os
import sys

# Add the output to a log file for reference
log_file = os.path.join(os.path.dirname(__file__), "requests_deps_check.log")
with open(log_file, "w") as f:
    f.write(f"Python version: {sys.version}\n\n")
    f.write("Checking requests optional dependencies...\n\n")

    # Try importing chardet
    f.write("Trying to import chardet...\n")
    try:
        import chardet

        f.write(f"SUCCESS: chardet {chardet.__version__} is installed\n")
    except ImportError as e:
        f.write(f"ERROR: Failed to import chardet: {e}\n")
        f.write("Run 'pip install chardet' to install it.\n")

    # Try importing cryptography
    f.write("\nTrying to import cryptography...\n")
    try:
        import cryptography

        f.write(f"SUCCESS: cryptography {cryptography.__version__} is installed\n")
    except ImportError as e:
        f.write(f"ERROR: Failed to import cryptography: {e}\n")
        f.write("Run 'pip install cryptography' to install it.\n")

    # Also check for requests itself
    f.write("\nTrying to import requests...\n")
    try:
        import requests

        f.write(f"SUCCESS: requests {requests.__version__} is installed\n")
    except ImportError as e:
        f.write(f"ERROR: Failed to import requests: {e}\n")

print(f"Check completed. Results written to {log_file}")
