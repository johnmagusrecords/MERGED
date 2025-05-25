import importlib
import logging
import os
import platform
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_directory_structure():
    """Ensure proper directory structure exists"""
    # Use the os module to check for required directories
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Working in directory: {current_dir}")

    # Check for needed directories
    required_dirs = ["logs", "data", "cache"]
    for dir_name in required_dirs:
        dir_path = os.path.join(current_dir, dir_name)
        if not os.path.exists(dir_path):
            logger.info(f"Creating missing directory: {dir_path}")
            os.makedirs(dir_path)
        else:
            logger.info(f"Directory exists: {dir_path}")

    return current_dir


def check_and_install_dependency(package_name, import_name=None, pip_name=None):
    """
    Check if a package is installed, and install it if it's not.

    Args:
        package_name: Name used for importing the package
        import_name: Actual module name to import (if different from package_name)
        pip_name: Name to use with pip install (if different from package_name)
    """
    name_to_import = import_name or package_name
    name_to_install = pip_name or package_name

    try:
        # Try to import the module to check if it's installed
        importlib.import_module(name_to_import)
        logger.info(f"{package_name} is already installed")
        return True
    except ImportError:
        logger.warning(f"{package_name} is not installed. Installing...")

        # Install the package
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", name_to_install]
            )
            logger.info(f"{package_name} installed successfully")
            return True
        except subprocess.CalledProcessError:
            logger.error(f"Failed to install {package_name}")
            return False


def install_talib():
    """Special handling for TA-Lib which is notoriously difficult to install"""
    try:
        importlib.import_module("talib")
        logger.info("TA-Lib is already installed")
        return True
    except ImportError:
        logger.warning("TA-Lib is not installed. Installing...")

        system = platform.system()
        try:
            if system == "Windows":
                # On Windows, use a pre-compiled wheel
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--no-cache-dir", "ta-lib"]
                )
            elif system == "Darwin":  # macOS
                logger.info("On macOS, TA-Lib requires Homebrew installation first:")
                logger.info(
                    ' '
  1. Install Homebrew: /bin/bash -c "$(c + 'url -fsSL https://raw.githubusercontent. + 'com/Homebrew/install/HEAD/install.sh)"'
                )
                logger.info("  2. Install TA-Lib: brew install ta-lib")
                logger.info("  3. Then: pip install TA-Lib")
                return False
            else:  # Linux
                # Try to install dependencies first
                subprocess.check_call(["apt-get", "update"])
                subprocess.check_call(
                    ["apt-get", "install", "-y", "build-essential", "ta-lib"]
                )
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "TA-Lib"]
                )

            logger.info("TA-Lib installed successfully")
            return True
        except subprocess.CalledProcessError:
            logger.error("Failed to install TA-Lib")
            logger.info(
                "\nTA-Lib installation can be challenging. Try these alternative methods:"
            )
            logger.info("1. For Windows: pip install ta-lib-binary")
            logger.info("2. For macOS: brew install ta-lib and then pip install TA-Lib")
            logger.info(
                "3. For Linux: apt-get install build-essential ta-lib and then pip install TA-Lib"
            )
            logger.info("\nOr try using a TA-Lib alternative like 'ta' or 'pandas-ta':")
            logger.info("pip install ta")
            logger.info("pip install pandas-ta")
            return False


def main():
    """Main function to fix dependencies"""
    logger.info("Starting dependency fix process")

    # Check OS
    system = platform.system()
    logger.info(f"Detected OS: {system}")

    # Check Python version
    python_version = sys.version.split(" ")[0]
    logger.info(f"Python version: {python_version}")

    # Check and create directory structure
    check_directory_structure()

    # Get environment path
    path_var = os.environ.get("PATH", "")
    logger.info(f"PATH variable length: {len(path_var)} characters")

    # Check if virtual environment is active
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        logger.info(f"Virtual environment detected: {sys.prefix}")
    else:
        logger.info("No virtual environment detected")

    logger.info("==================================================")
    logger.info("MAGUS PRIME X Dependency Installation")
    logger.info("==================================================")

    # List of required packages in format (package_name, import_name, pip_name)
    # Where import_name and pip_name are optional if different from package_name
    dependencies = [
        # Core dependencies
        ("flask", None, None),
        ("requests", None, None),
        ("pandas", None, None),
        ("numpy", None, None),
        ("python-dotenv", "dotenv", None),
        ("python-telegram-bot", "telegram", None),
        ("aiohttp", None, None),
        ("asyncio", None, None),
        ("websockets", None, None),
        # Data analysis and visualization
        ("matplotlib", None, None),
        ("plotly", None, None),
        # Technical analysis packages (alternatives to TA-Lib)
        ("pandas-ta", "pandas_ta", None),
        ("ta", None, None),
        # Machine learning and AI
        ("scikit-learn", "sklearn", None),
        # News and data feeds
        ("newsapi-python", "newsapi", None),
        # API for Telegram sending
        ("telegram", None, None),
        # Web server and cors
        ("flask_cors", None, "flask-cors"),
        ("flask_socketio", None, "flask-socketio"),
    ]

    installed_count = 0
    failed_count = 0

    for dep in dependencies:
        package, import_name, pip_name = dep
        if check_and_install_dependency(package, import_name, pip_name):
            installed_count += 1
        else:
            failed_count += 1

    # Special handling for TA-Lib
    if install_talib():
        installed_count += 1
    else:
        failed_count += 1

    logger.info("\n==================================================")
    logger.info(
        f"Installation Summary: {installed_count} packages installed successfully"
    )
    if failed_count > 0:
        logger.warning(f"{failed_count} packages failed to install")
    logger.info("==================================================")

    # Create virtual environment recommendation
    logger.info("\nRECOMMENDATION:")
    logger.info("For best results, use a virtual environment:")
    logger.info("1. Create: python -m venv venv")
    logger.info("2. Activate:")
    if platform.system() == "Windows":
        logger.info("   venv\\Scripts\\activate")
    else:
        logger.info("   source venv/bin/activate")
    logger.info("3. Run this script again within the activated environment")

    if failed_count > 0:
        logger.warning("\nSome dependencies failed to install.")
        logger.warning(
            "You may need to install them manually or troubleshoot installation issues."
        )
        return False
    else:
        logger.info(
            "\nAll dependencies installed successfully! You're ready to run MAGUS PRIME X."
        )
        return True


if __name__ == "__main__":
    success = main()

    if not success:
        logger.info("\nPress Enter to exit...")
        input()
    else:
        logger.info("\nUpdating pip...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"]
        )
        logger.info("Done!")
