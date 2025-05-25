"""
TA-Lib Diagnostic Tool

This script checks if TA-Lib is properly installed and
provides instructions for troubleshooting and alternatives.
"""

import platform
import subprocess
import sys


def check_talib():
    print("Checking TA-Lib installation...")

    try:
        import talib

        print("✅ TA-Lib is properly installed!")

        # Test basic functionality
        import numpy as np

        print("Testing basic TA-Lib functionality...")
        close = np.random.random(100)
        talib.SMA(close)
        print("✅ TA-Lib functions work correctly!")

        print(f"\nTA-Lib version: {talib.__version__}")
        print(f"TA-Lib path: {talib.__file__}")
        return True

    except ImportError as e:
        print(f"❌ TA-Lib import error: {e}")
        return False
    except Exception as e:
        print(f"❌ TA-Lib error: {e}")
        return False


def recommend_installation():
    system = platform.system()
    print("\n=== TA-Lib Installation Instructions ===")

    if system == "Windows":
        print("For Windows:")
        print("1. Try the pre-compiled wheel:")
        print("   pip install ta-lib-binary")
        print("\n2. If that fails, download the appropriate wheel from:")
        print("   https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib")
        print("   Then install it with:")
        print("   pip install TA_Lib‑0.4.24‑cp39‑cp39‑win_amd64.whl")
        print("   (Choose the version matching your Python installation)")

    elif system == "Darwin":  # macOS
        print("For macOS:")
        print("1. Install Homebrew if you don't have it:")
        print(
            ' '
   /bin/bash -c "$(curl -fsSL https://ra + 'w.githubusercontent.com/Homebrew/install + '/HEAD/install.sh)"'
        )
        print("2. Install TA-Lib:")
        print("   brew install ta-lib")
        print("3. Install Python package:")
        print("   pip install TA-Lib")

    else:  # Linux
        print("For Linux (Ubuntu/Debian):")
        print("1. Install dependencies:")
        print("   sudo apt-get update")
        print("   sudo apt-get install -y build-essential")
        print("   sudo apt-get install -y ta-lib")
        print("2. Install Python package:")
        print("   pip install TA-Lib")

    print("\n=== Alternatives to TA-Lib ===")
    print("If you continue to have issues, consider these alternatives:")
    print("1. pandas-ta: pip install pandas-ta")
    print("2. ta: pip install ta")
    print("3. backtrader: pip install backtrader")
    print(
        "\nThese libraries provide similar functionality but are pure Python\n"
        "and don't require the C library that makes TA-Lib challenging to install."
    )


if __name__ == "__main__":
    print("===== TA-Lib Installation Checker =====")
    success = check_talib()

    if not success:
        recommend_installation()

        # Offer to try installing alternatives
        answer = input(
            "\nWould you like to install an alternative to TA-Lib now? (y/n): "
        ).lower()
        if answer == "y":
            try:
                print("Installing 'pandas-ta' (a pure Python alternative)...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "pandas-ta"]
                )
                print("✅ pandas-ta installed successfully!")

                print("To use pandas-ta instead of talib, replace imports like this:")
                print("FROM: import talib")
                print("TO:   import pandas_ta as talib")
                print("\nOr update your code to use the pandas-ta API directly.")
            except Exception as e:
                print(f"Error installing alternative: {e}")

    print("\nPress Enter to exit...")
    input()
