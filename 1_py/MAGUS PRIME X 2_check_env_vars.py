import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv, set_key

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Required environment variables and their descriptions
REQUIRED_VARS = {
    "TELEGRAM_BOT_TOKEN": "Your Telegram bot token (obtained from @BotFather)",
    "TELEGRAM_GROUP_ID": "Your Telegram group ID (e.g., -100XXXXXXXXXX)",
    "OPENAI_API_KEY": "Your OpenAI API key (starts with sk-)",
    "MAGUS_ASSISTANT_ENABLED": "Whether to enable AI assistant (true/false)",
    "ALPHAVANTAGE_API_KEY": "Your Alpha Vantage API key for market data",
    "NEWSAPI_KEY": "Your News API key for news monitoring",
    "PORT": "Port for the signal dispatcher server (default: 8080)",
}

# Default values for non-sensitive variables
DEFAULT_VALUES = {"MAGUS_ASSISTANT_ENABLED": "true", "PORT": "8080"}


def check_environment_variables():
    """Check if all required environment variables are set"""
    # Load environment variables from .env file if it exists
    load_dotenv()

    env_path = Path(".env")
    env_exists = env_path.exists()

    missing_vars = []
    set_vars = []

    for var, description in REQUIRED_VARS.items():
        value = os.getenv(var)
        if value is None or value.strip() == "":
            missing_vars.append((var, description))
        else:
            # Mask sensitive values
            if "TOKEN" in var or "KEY" in var:
                masked_value = (
                    value[:4] + "..." + value[-4:] if len(value) > 8 else "****"
                )
                set_vars.append((var, masked_value))
            else:
                set_vars.append((var, value))

    # Print results
    logger.info("=" * 60)
    logger.info("MAGUS PRIME X Environment Variables Check")
    logger.info("=" * 60)

    if set_vars:
        logger.info("\n✅ Variables correctly set:")
        for var, value in set_vars:
            logger.info(f"  • {var} = {value}")

    if missing_vars:
        logger.info("\n⚠️ Missing variables:")
        for var, description in missing_vars:
            logger.info(f"  • {var}: {description}")

    # Provide guidance
    if missing_vars:
        logger.info("\n" + "=" * 60)
        logger.info("Instructions to set missing variables:")
        logger.info("-" * 60)

        if env_exists:
            logger.info("Edit your .env file and add the following lines:")
        else:
            logger.info(
                "Create a .env file in the root directory with the following lines:"
            )

        for var, description in missing_vars:
            default = DEFAULT_VALUES.get(var, "your_value_here")
            logger.info(f"{var}={default}  # {description}")

        logger.info(
            " "
\nAlternatively, run this script with th + "e --setup flag to interactively set the  + "variables:"
        )
        logger.info("python check_env_vars.py --setup")
    else:
        logger.info("\n🎉 All required environment variables are set!")

    logger.info("=" * 60)
    return len(missing_vars) == 0


def setup_environment_variables():
    """Interactive setup for environment variables"""
    load_dotenv()
    env_path = Path(".env")

    logger.info("=" * 60)
    logger.info("MAGUS PRIME X Environment Variables Setup")
    logger.info("=" * 60)
    logger.info("Press Enter to keep current value or set default (shown in brackets)")
    logger.info("For security, input for API keys and tokens will be hidden")

    for var, description in REQUIRED_VARS.items():
        current = os.getenv(var, "")
        is_sensitive = "TOKEN" in var or "KEY" in var

        if is_sensitive and current:
            # Mask sensitive values that are already set
            display_current = (
                current[:4] + "..." + current[-4:] if len(current) > 8 else "****"
            )
        else:
            display_current = current or DEFAULT_VALUES.get(var, "")

        # Prompt user for input
        logger.info(f"\n{var}: {description}")

        if is_sensitive and not current:
            # No masking for new sensitive values
            value = input("Enter value: ")
        else:
            value = input(f"Enter value [{display_current}]: ")

        # Use default or current value if empty input
        if value.strip() == "":
            value = current or DEFAULT_VALUES.get(var, "")

        # Save to .env file
        if value:
            set_key(str(env_path), var, value)

    logger.info("\n✅ Environment variables saved to .env file")
    logger.info("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_environment_variables()
    else:
        all_set = check_environment_variables()
        if not all_set:
            logger.info("\nRun with --setup to interactively configure variables:")
            logger.info("python check_env_vars.py --setup")
