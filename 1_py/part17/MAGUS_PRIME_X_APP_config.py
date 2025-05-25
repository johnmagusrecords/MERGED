from dotenv import load_dotenv
load_dotenv(override=True)

import os
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ...existing code...

def get_retry_adapter():
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],
        backoff_factor=1
    )
    return HTTPAdapter(max_retries=retry_strategy)

# Securely load secrets from environment
CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# ...other env vars...

# Import CapitalComTrader from the correct module
# from capital_com_trader import CapitalComTrader

# ...existing code...
