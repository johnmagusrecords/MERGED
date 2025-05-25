from typing import Optional, List, Dict, Any, Tuple


class TradeParams:
    def __init__(
        self,
        symbol: str,
        direction: str,
        quantity: float = 1.0,
        take_profit: Optional[float] = None,
        stop_loss: Optional[float] = None
    ):
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Symbol must be a non-empty string")
        if direction not in ("BUY", "SELL"):
            raise ValueError("Direction must be 'BUY' or 'SELL'")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        self.symbol = symbol
        self.direction = direction
        self.quantity = quantity
        self.take_profit = take_profit
        self.stop_loss = stop_loss

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "TradeParams":
        return cls(
            symbol=d.get("symbol", ""),
            direction=d.get("direction", "BUY") if d.get("direction") in ("BUY", "SELL") else "BUY",
            quantity=float(d.get("quantity", 1.0)),
            take_profit=d.get("take_profit"),
            stop_loss=d.get("stop_loss"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "direction": self.direction,
            "quantity": self.quantity,
            "take_profit": self.take_profit,
            "stop_loss": self.stop_loss,
        }


# Trade history helpers
TRADE_HISTORY_FIELDS = [
    "Timestamp", "Symbol", "Action", "TP", "SL", "Result", "PL"
]

_trade_history: List[Dict[str, Any]] = []


def add_trade_record(trade: Dict[str, Any]) -> bool:
    import datetime
    if "Timestamp" not in trade:
        trade["Timestamp"] = datetime.datetime.now().isoformat(timespec="seconds")
    _trade_history.append(trade)
    return True


def get_trade_history() -> List[Dict[str, Any]]:
    return list(_trade_history)


def clear_trade_history():
    _trade_history.clear()


def save_trade_history(filepath: Optional[str] = None) -> None:
    import csv
    if filepath is None:
        filepath = "trade_history.csv"
    if not _trade_history:
        return
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRADE_HISTORY_FIELDS)
        writer.writeheader()
        for row in _trade_history:
            filtered_row = {k: row.get(k, "") for k in TRADE_HISTORY_FIELDS}
            writer.writerow(filtered_row)


# Profit/loss calculators


def calculate_trade_pl(trade: Dict[str, Any], result: Optional[str] = None) -> float:
    if "PL" in trade:
        return float(trade["PL"])
    if result == "WIN":
        if "TP" in trade and "SL" in trade:
            return float(trade["TP"]) - float(trade["SL"])
        else:
            return 0.0
    elif result == "LOSS":
        if "TP" in trade and "SL" in trade:
            return float(trade["SL"]) - float(trade["TP"])
        else:
            return 0.0
    return 0.0


def calculate_profit_loss(trades: List[Dict[str, Any]]) -> float:
    return sum(float(t.get("PL", 0.0)) for t in trades)


def calculate_win_rate(trades: List[Dict[str, Any]]) -> float:
    if not trades:
        return 0.0
    wins = sum(1 for t in trades if t.get("Result") == "WIN")
    return 100.0 * wins / len(trades)


def calculate_trade_statistics(trades: List[Dict[str, Any]]) -> Tuple[float, float]:
    win_rate = calculate_win_rate(trades)
    pnl = calculate_profit_loss(trades)
    return (win_rate, pnl)
