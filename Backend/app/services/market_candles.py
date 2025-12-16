import os
import httpx
from datetime import datetime

FINNHUB_URL = "https://finnhub.io/api/v1/stock/candle"

def fetch_candles(symbol: str, resolution="5", limit=100):
    token = os.getenv("FINNHUB_API_KEY")
    now = int(datetime.utcnow().timestamp())
    start = now - (limit * 60 * int(resolution))

    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": start,
        "to": now,
        "token": token,
    }

    r = httpx.get(FINNHUB_URL, params=params, timeout=10)
    r.raise_for_status()
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
