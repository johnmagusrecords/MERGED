import requests


class CapitalAPI:
    def __init__(self, api_key: str, identifier: str, password: str, api_url: str):
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()  # one call

    def _make_api_request(self, endpoint: str, method: str = "GET", payload: dict = None):
        if payload is None:
            payload = {}
        url = f"{self.api_url}/{endpoint}"
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        resp = self.session.request(method, url, json=payload, headers=headers)
        data = resp.json()
        return (resp.ok, data)

    def close_trade(self, trade_id: str) -> bool:
        ok, data = self._make_api_request(
            f"positions/{trade_id}/close", method="POST")
        return ok and data.get("status") == "CLOSED"

    def execute_trade(self, params: dict) -> dict | None:
        ok, data = self._make_api_request("trades", method="POST", payload={
            "epic": params["symbol"],
            "side": params["direction"],
            "size": params["quantity"],
            "limit": params.get("take_profit"),
            "stop": params.get("stop_loss"),
        })
        return data if ok else None

    def get_active_trades(self) -> list:
        ok, data = self._make_api_request("trades/active")
        return data.get("positions", [])
