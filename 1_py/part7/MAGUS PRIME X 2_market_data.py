import logging

import aiohttp
import pandas as pd

# ...existing code...


async def get_market_data(symbol, timeframe="1H"):
    """Fetch market data for technical analysis"""
    cst, x_security = await authenticate()
    if not cst or not x_security:
        logging.error("Authentication failed while fetching market data")
        return None

    url = f"{CAPITAL_API_URL}/prices/{symbol}"
    headers = {
        "X-CAP-API-KEY": CAPITAL_API_KEY,
        "CST": cst,
        "X-SECURITY-TOKEN": x_security,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return pd.DataFrame(data["prices"])
                else:
                    logging.error(
                        f"Failed to fetch market data: {await response.text()}"
                    )
                    return None
    except Exception as e:
        logging.error(f"Error fetching market data: {str(e)}")
        return None


# ...existing code...
