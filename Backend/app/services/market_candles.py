import os
import httpx
from datetime import datetime
from fastapi import HTTPException

FINNHUB_URL = "https://finnhub.io/api/v1/stock/candle"

async def fetch_candles(symbol: str, resolution="5", limit=100):
    token = os.getenv("FINNHUB_API_KEY")
    if not token:
        raise HTTPException(status_code=500, detail="Finnhub API key not configured")

    # ✅ FREE-TIER SAFE NORMALIZATION
    # If equity symbol and intraday requested → force Daily
    if symbol.isalpha() and resolution in {"1", "5", "15"}:
        resolution = "D"

    now = int(datetime.utcnow().timestamp())

    if resolution.isdigit():
        start = now - (limit * 60 * int(resolution))
    else:
        # Daily candles → 1 day = 86400 sec
        start = now - (limit * 86400)

    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": start,
        "to": now,
        "token": token,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(FINNHUB_URL, params=params)

    # ❗ DO NOT raise_for_status blindly
    if r.status_code != 200:
        print(f"Finnhub candle error {r.status_code}: {r.text}")
    return []


    data = r.json()

    if data.get("s") != "ok":
        return []

    candles = []
    for i in range(len(data["t"])):
        candles.append({
            "time": data["t"][i] * 1000,
            "open": data["o"][i],
            "high": data["h"][i],
            "low": data["l"][i],
            "close": data["c"][i],
            "volume": data["v"][i],
        })

    return candles
