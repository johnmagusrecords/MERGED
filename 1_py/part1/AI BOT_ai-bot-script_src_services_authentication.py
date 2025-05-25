import os
import requests
import logging

CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
CAPITAL_IDENTIFIER = os.getenv("CAPITAL_IDENTIFIER")
CAPITAL_API_PASSWORD = os.getenv("CAPITAL_API_PASSWORD")
CAPITAL_API_URL = os.getenv("CAPITAL_API_URL")

def authenticate():
    url = f"{CAPITAL_API_URL}/session"
    headers = {"X-CAP-API-KEY": CAPITAL_API_KEY, "Content-Type": "application/json"}
    payload = {"identifier": CAPITAL_IDENTIFIER, "password": CAPITAL_API_PASSWORD}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        cst = response.headers.get("CST")
        x_security = response.headers.get("X-SECURITY-TOKEN")
        logging.info("✅ Authentication successful!")
        return cst, x_security
    else:
        logging.error(f"❌ Authentication Failed: {response.json()}")
        return None, None