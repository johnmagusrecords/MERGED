import requests
import logging
import json

class CapitalAPI:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def _make_api_request(self, method, endpoint, params=None, data=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            resp = self.session.request(method, url, params=params, json=data)
            if not resp.ok:
                logging.error(f"API error {resp.status_code}: {resp.text}")
                resp.raise_for_status()
            try:
                return resp.json()
            except json.JSONDecodeError:
                logging.error("Failed to decode JSON response")
                return None
        except requests.RequestException as e:
            logging.error(f"HTTP request failed: {e}")
            raise

    def execute_trade(self, params):
        # Ensure correct field names
        payload = {
            "epic": params.get("epic") or params.get("symbol"),
            "direction": params["direction"],
            "size": params["size"],
            "orderType": params.get("orderType", "MARKET"),
            "currencyCode": params.get("currencyCode", "USD"),
        }
        return self._make_api_request("POST", "trades", data=payload)

# ...existing code...
