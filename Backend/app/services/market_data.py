# app/services/market_data.py

import os
import httpx

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"


async def fetch_quote_finnhub(symbol: str) -> dict:
    """
    Fetch latest market price snapshot from Finnhub.

    Returns:
    {
        "price": float,
        "open": float,
        "high": float,
        "low": float,
        "prev_close": float,
        "timestamp": int
    }
    """

    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        raise RuntimeError("FINNHUB_API_KEY not set in environment")

    url = f"{FINNHUB_BASE_URL}/quote"
    params = {
        "symbol": symbol.upper(),
        "token": api_key,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    # Finnhub response keys:
    # c = current price
    # o = open
    # h = high
    # l = low
    # pc = previous close
    # t = timestamp

    if "c" not in data:
        raise ValueError("Invalid response from Finnhub")

    return {
        "price": float(data["c"]),
        "open": float(data.get("o", 0)),
        "high": float(data.get("h", 0)),
        "low": float(data.get("l", 0)),
        "prev_close": float(data.get("pc", 0)),
        "timestamp": int(data.get("t", 0)),
    }
