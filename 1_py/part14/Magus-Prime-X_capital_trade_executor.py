# Ensure this is your Capital.com client
from capital_com_trader import CapitalComTrader
from openai_assistant import generate_gpt_commentary
import logging
import os
import json


def get_pip_value_for_asset(symbol: str) -> float:
    """
    Get the pip value for a given asset.

    Args:
        symbol (str): Trading symbol.

    Returns:
        float: Pip value for the asset.
    """
    pip_table = {
        "XAUUSD": 0.1, "GOLD": 0.1,
        "XAGUSD": 0.01,
        "WTIUSD": 0.01,
        "US100": 1.0,
        "GER40": 1.0,
        "BTCUSD": 10.0,
        "ETHUSD": 1.0,
        "EURUSD": 0.0001,
        "GBPUSD": 0.0001
    }
    return pip_table.get(symbol.upper(), 1.0)  # default 1.0


def split_lot_across_targets(total_lot_size: float, targets: int = 3) -> list:
    """
    Split total lot size evenly across N targets (default 3 TPs).

    Args:
        total_lot_size (float): Total lot size to split.
        targets (int): Number of targets.

    Returns:
        list: List of lot sizes for each target.
    """
    if total_lot_size < 0.01:
        return [0.0, 0.0, 0.0]

    base = round(total_lot_size / targets, 2)
    return [base] * targets


def calculate_r_based_targets(entry: float, stop_loss: float, risk_reward_factors: list = [1, 2, 3]) -> list:
    """
    Calculate TP levels using R-multiples (1R, 2R, 3R).

    Returns:
        List of TP prices based on risk distance.
    """
    direction = "BUY" if entry > stop_loss else "SELL"
    risk = abs(entry - stop_loss)
    tps = []

    for r in risk_reward_factors:
        if direction == "BUY":
            tps.append(round(entry + r * risk, 2))
        else:
            tps.append(round(entry - r * risk, 2))

    return tps


def calculate_atr_based_levels(entry_price: float, atr_value: float, direction: str, sl_mult: float = 1.5, tp_mult: float = 3.0):
    """
    Use ATR to calculate SL/TP based on volatility.

    Returns:
        (stop_loss, take_profits) — list of 3 TPs
    """
    if direction.upper() == "BUY":
        sl = round(entry_price - atr_value * sl_mult, 2)
        tps = [round(entry_price + atr_value * (tp_mult * r), 2)
               for r in [1/3, 2/3, 1]]
    else:
        sl = round(entry_price + atr_value * sl_mult, 2)
        tps = [round(entry_price - atr_value * (tp_mult * r), 2)
               for r in [1/3, 2/3, 1]]
    return sl, tps


def generate_trade_preview(symbol, direction, entry, stop_loss, take_profits, strategy, lot_size):
    """
    Generate a trade preview string for logging or Telegram.

    Args:
        symbol: Trading symbol.
        direction: Trade direction (BUY/SELL).
        entry: Entry price.
        stop_loss: Stop loss price.
        take_profits: List of take profit levels.
        strategy: Trading strategy.
        lot_size: Lot size for the trade.

    Returns:
        str: Formatted trade preview.
    """
    rr = abs(take_profits[0] - entry) / abs(entry -
                                            stop_loss) if stop_loss != entry else "∞"
    preview = f"""
🧾 *Trade Preview*:
🔹 Symbol: {symbol}
🔹 Direction: {direction}
🔹 Entry: {entry}
🔹 Stop Loss: {stop_loss}
🔹 Take Profits: {', '.join(map(str, take_profits))}
🔹 Lot Size: {lot_size}
🔹 Strategy: {strategy}
🔹 R:R Estimate: {round(rr, 2) if isinstance(rr, float) else rr}
"""
    return preview.strip()


def get_gpt_trade_approval(symbol, direction, entry, stop_loss, tps, strategy):
    """
    Use GPT-4 to validate and suggest improvements for a trade idea.

    Args:
        symbol: Trading symbol.
        direction: Trade direction (BUY/SELL).
        entry: Entry price.
        stop_loss: Stop loss price.
        tps: List of take profit levels.
        strategy: Trading strategy.

    Returns:
        str: GPT-4 generated commentary and decision.
    """
    prompt = f"""
You're MAGUS PRIME X. Validate the following trade idea:

- Symbol: {symbol}
- Direction: {direction}
- Entry: {entry}
- Stop Loss: {stop_loss}
- TPs: {', '.join(map(str, tps))}
- Strategy: {strategy}

Decide if this trade is valid and suggest improvements if needed.
Also return a short summary.
"""
    return generate_gpt_commentary(prompt)


def gpt_trade_approval_check(symbol, direction, entry, stop_loss, tps, strategy):
    """
    Use GPT to approve or reject a trade idea.

    Args:
        symbol: Trading symbol.
        direction: Trade direction (BUY/SELL).
        entry: Entry price.
        stop_loss: Stop loss price.
        tps: List of take profit levels.
        strategy: Trading strategy.

    Returns:
        dict: GPT approval decision and reason.
    """
    prompt = f"""
You are MAGUS PRIME X. Decide whether to approve this trade.

Symbol: {symbol}
Direction: {direction}
Entry: {entry}
Stop Loss: {stop_loss}
TPs: {', '.join(map(str, tps))}
Strategy: {strategy}

Respond in this exact JSON format:
{{
  "approval": true/false,
  "reason": "short explanation"
}}
"""
    response = generate_gpt_commentary(prompt)
    try:
        return json.loads(response)
    except Exception as e:
        logging.error(f"Error parsing GPT response: {e}")
        return {"approval": True, "reason": "Default approval (GPT parse error)"}


def execute_capital_trade(symbol, direction, entry, stop_loss, take_profits=None, lot_size=None, atr_value=None):
    """
    Execute a trade via the Capital.com API.

    Args:
        symbol (str): Trading symbol.
        direction (str): Trade direction ("BUY" or "SELL").
        entry (float): Entry price.
        stop_loss (float): Stop loss price.
        take_profits (list): List of take profit levels.
        lot_size (float): Lot size for the trade.
        atr_value (float): ATR value for SL/TP calculation.

    Returns:
        dict: API response or error details.
    """
    try:
        client = CapitalComTrader()
        client.initialize()  # Authenticate the client

        # Check balance threshold
        if not client.check_balance_threshold(min_balance=100.0):
            return {"error": "Insufficient balance. Trade blocked."}

        # Calculate lot size based on risk if not provided
        if lot_size is None:
            pip_value = get_pip_value_for_asset(symbol)
            stop_loss_pips = abs(entry - stop_loss) / pip_value

            lot_size = client.calculate_lot_size_by_risk(
                risk_percent=1.0,
                stop_loss_pips=stop_loss_pips,
                pip_value=pip_value
            )

            if lot_size < 0.01:
                logging.warning(
                    "❌ Trade blocked: lot size too small based on risk model.")
                return {"error": "Lot size below minimum threshold. Trade not placed."}

        # Generate SL/TP using ATR if enabled
        if atr_value:
            stop_loss, take_profits = calculate_atr_based_levels(
                entry, atr_value, direction)

        # Generate TP levels if not provided
        if not take_profits:
            take_profits = calculate_r_based_targets(entry, stop_loss)

        # Generate trade preview
        trade_preview = generate_trade_preview(
            symbol, direction, entry, stop_loss, take_profits, "Custom Strategy", lot_size)
        logging.info(trade_preview)

        # Optionally send preview to Telegram admin
        # send_telegram_message(TELEGRAM_ADMIN_CHAT_ID, trade_preview)

        # Check GPT approval if enabled
        require_gpt = os.getenv("REQUIRE_GPT_APPROVAL",
                                "false").lower() == "true"
        if require_gpt:
            decision = gpt_trade_approval_check(
                symbol, direction, entry, stop_loss, take_profits, "Custom Strategy")
            if not decision.get("approval", True):
                logging.warning(f"🛑 GPT blocked trade: {decision['reason']}")
                return {"error": "GPT disapproved trade: " + decision['reason']}

        # Get GPT approval for the trade
        gpt_decision = get_gpt_trade_approval(
            symbol, direction, entry, stop_loss, take_profits, "Custom Strategy")
        logging.info(f"GPT Decision: {gpt_decision}")

        # Split lot size across take profit levels
        tp_lots = split_lot_across_targets(lot_size, targets=len(take_profits))
        for tp_level, tp_lot in zip(take_profits, tp_lots):
            if tp_lot >= 0.01:
                result = client.execute_trade(
                    symbol=symbol,
                    direction=direction,
                    size=tp_lot,
                    take_profit=tp_level,
                    stop_loss=stop_loss
                )
                logging.info(f"✅ Trade result for TP {tp_level}: {result}")

        return {"status": "success", "message": "Trades executed for all TPs."}
    except Exception as e:
        logging.error(f"❌ Capital trade failed: {e}")
        return {"error": str(e)}
