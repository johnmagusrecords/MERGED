async def update_stop_loss(deal_id, new_sl, cst, x_security):
    """
    Updates the stop loss for a given deal.
    """
    # Add the logic to update the stop loss here
    print(f"Updating stop loss for deal {deal_id} to {new_sl}")
    # Example: await some_api_call_to_update_sl(deal_id, new_sl, cst, x_security)


async def update_position(position, cst, x_security):
    current_price = float(position["market"]["bid"])
    entry_price = float(position["level"])
    direction = position["direction"]
    current_sl = float(
        position.get("stopLevel", 0)
    )  # Fetch current stop loss, default to 0 if not set

    if direction == "BUY":
        if current_price > entry_price:
            new_sl = max(
                current_price * 0.98, entry_price * 0.95
            )  # Ensure it's not worse than initial SL
            if new_sl > current_sl:  # Only update if the new SL is better
                await update_stop_loss(
                    position["dealId"], round(new_sl, 2), cst, x_security
                )
    elif direction == "SELL":
        if current_price < entry_price:
            new_sl = min(
                current_price * 1.02, entry_price * 1.05
            )  # Ensure it's not worse than initial SL
            if (
                new_sl < current_sl or current_sl == 0
            ):  # Only update if the new SL is better
                await update_stop_loss(
                    position["dealId"], round(new_sl, 2), cst, x_security
                )
