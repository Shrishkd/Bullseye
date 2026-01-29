# app/services/market_providers/upstox.py

import os
import httpx
from datetime import datetime, timedelta
from .base import MarketProvider

UPSTOX_BASE_URL = "https://api.upstox.com/v2"


class UpstoxProvider(MarketProvider):
    def __init__(self):
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    async def fetch_quote(self, instrument_key: str) -> dict:
        if not self.access_token:
            return {}

        url = f"{UPSTOX_BASE_URL}/market-quote/ltp"
        params = {"instrument_key": instrument_key}

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers=self._headers(), params=params)

        if r.status_code != 200:
            return {}

        data = r.json().get("data", {})
        q = data.get(instrument_key)
        if not q:
            return {}

        return {
            "price": float(q["last_price"]),
            "timestamp": int(datetime.utcnow().timestamp()),
        }

    async def fetch_candles(self, instrument_key: str, resolution: str, limit=100):
        if not self.access_token:
            return []

        interval_map = {
            "1": "1minute",
            "5": "5minute",
            "15": "15minute",
            "60": "60minute",
            "D": "day",
        }

        interval = interval_map.get(resolution, "day")

        async with httpx.AsyncClient(timeout=15) as client:
            if interval == "day":
                to_date = datetime.utcnow().date()
                from_date = to_date - timedelta(days=limit)

                url = f"{UPSTOX_BASE_URL}/historical-candle/{instrument_key}/{interval}/{from_date}/{to_date}"
            else:
                url = f"{UPSTOX_BASE_URL}/historical-candle/intraday/{instrument_key}/{interval}"

            r = await client.get(url, headers=self._headers())

        if r.status_code != 200:
            return []

        raw = r.json().get("data", {}).get("candles", [])
        candles = []

        for c in raw[-limit:]:
            candles.append({
                "time": int(datetime.fromisoformat(c[0]).timestamp() * 1000),
                "open": c[1],
                "high": c[2],
                "low": c[3],
                "close": c[4],
                "volume": c[5],
            })

        return candles
