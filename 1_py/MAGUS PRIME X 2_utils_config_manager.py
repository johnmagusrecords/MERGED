"""
Configuration manager for MAGUS PRIME X trading bot.

This module handles loading and managing configuration settings.
"""

import logging
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv


class ConfigManager:
    """Manages configuration for the trading bot."""

    def __init__(self, env_file_path: Optional[str] = None):
        """Initialize the configuration manager.

        Args:
            env_file_path: Optional path to .env file
        """
        # Load environment variables
        if env_file_path and os.path.exists(env_file_path):
            load_dotenv(env_file_path)
        else:
            load_dotenv()

        # Initialize configuration dictionary
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables.

        Returns:
            dict: Configuration dictionary
        """
        config = {
            # API credentials
            "CAPITAL_API_KEY": os.getenv("CAPITAL_API_KEY"),
            "CAPITAL_API_PASSWORD": os.getenv("CAPITAL_API_PASSWORD"),
            "CAPITAL_API_IDENTIFIER": os.getenv("CAPITAL_API_IDENTIFIER"),
            "CAPITAL_API_URL": os.getenv(
                "CAPITAL_API_URL", "https://demo-api-capital.backend-capital.com/api/v1"
            ),
            # Trading configuration
            "STRATEGY_MODE": os.getenv("STRATEGY_MODE", "conservative"),
            "TRADE_INTERVAL": int(os.getenv("TRADE_INTERVAL", "300")),  # 5 minutes
            "RISK_PERCENT": float(
                os.getenv("RISK_PERCENT", "1.0")
            ),  # 1% risk per trade
            "USE_ALL_MARKETS": os.getenv("USE_ALL_MARKETS", "0")
            == "1",  # Default false
            "MAX_ACTIVE_TRADES": int(os.getenv("MAX_ACTIVE_TRADES", "3")),
            "MAX_DAILY_RISK": float(os.getenv("MAX_DAILY_RISK", "5.0")),
            "MAX_DRAWDOWN_LIMIT": float(os.getenv("MAX_DRAWDOWN_LIMIT", "10.0")),
            # Telegram configuration
            "TELEGRAM_TOKEN": os.getenv("TELEGRAM_TOKEN"),
            "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
            # Dashboard configuration
            "DASHBOARD_PASSWORD": os.getenv("DASHBOARD_PASSWORD", "magus"),
            # News monitoring configuration
            "NEWS_API_KEY": os.getenv("NEWS_API_KEY"),
            "ARABIC_NEWS_RSS_URL": os.getenv("ARABIC_NEWS_RSS_URL"),
            "NEWS_CHECK_INTERVAL": int(
                os.getenv("NEWS_CHECK_INTERVAL", "300")
            ),  # 5 minutes
        }

        return config

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            default: Default value if key is not found

        Returns:
            Any: Configuration value
        """
        return self.config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.

        Returns:
            dict: All configuration values
        """
        return self.config.copy()

    def validate_trading_config(self) -> bool:
        """Validate trading configuration.

        Returns:
            bool: True if configuration is valid
        """
        # Validate risk percentage
        risk_percent = self.get("RISK_PERCENT")
        if risk_percent <= 0 or risk_percent > 5:
            logging.warning(
                f"Risk percentage {risk_percent}% is outside reasonable range (0-5%)"
            )
            return False

        # Validate max active trades
        max_trades = self.get("MAX_ACTIVE_TRADES")
        if max_trades <= 0:
            logging.warning(f"Max active trades {max_trades} should be positive")
            return False

        # Validate trade interval
        trade_interval = self.get("TRADE_INTERVAL")
        if trade_interval < 60:  # Less than 1 minute
            logging.warning(f"Trade interval {trade_interval}s is too short")
            return False

        return True
