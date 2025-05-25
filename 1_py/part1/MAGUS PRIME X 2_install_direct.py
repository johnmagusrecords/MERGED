"""
Simple direct installer for Ruff inside a virtual environment
"""

import subprocess
import sys

print(f"Installing Ruff directly in: {sys.prefix}")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ruff"])
    print("✅ Ruff installed successfully!")

    # Check installation
    subprocess.check_call([sys.executable, "-m", "ruff", "--version"])
    print("\nYou can now use Ruff with the following command:")
    print(f"    {sys.executable} -m ruff check bot.py")
except Exception as e:
    print(f"❌ Error installing Ruff: {e}")
