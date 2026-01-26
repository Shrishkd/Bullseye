# app/services/market_providers/finnhub.py

import os
import httpx
from datetime import datetime
from .base import MarketProvider

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"


class FinnhubProvider(MarketProvider):
    def __init__(self):
        self.api_key = os.getenv("FINNHUB_API_KEY")

    async def fetch_quote(self, symbol: str) -> dict:
        """
        Fetch latest market price snapshot from Finnhub.
        Normalized output:
        {
          price, open, high, low, prev_close, timestamp
        }
        """
        if not self.api_key:
            return {}

        url = f"{FINNHUB_BASE_URL}/quote"
        params = {
            "symbol": symbol.upper(),
            "token": self.api_key,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)

        if r.status_code != 200:
            return {}

        data = r.json()
        if not isinstance(data, dict) or "c" not in data:
            return {}

        return {
            "price": float(data["c"]),
            "open": float(data.get("o", 0.0)),
            "high": float(data.get("h", 0.0)),
            "low": float(data.get("l", 0.0)),
            "prev_close": float(data.get("pc", 0.0)),
            "timestamp": int(data.get("t", 0)),
        }

    async def fetch_candles(
        self,
        symbol: str,
        resolution: str,
        limit: int = 100,
    ) -> list[dict]:
        """
        Fetch OHLCV candles from Finnhub.
        Returns list of:
        { time, open, high, low, close, volume }
        """

        if not self.api_key:
            return []

        # 🔒 Free-tier safety: intraday stocks not allowed
        if symbol.isalpha() and resolution in {"1", "5", "15"}:
            resolution = "D"

        now = int(datetime.utcnow().timestamp())

        if resolution.isdigit():
            start = now - (limit * 60 * int(resolution))
        else:
            start = now - (limit * 86400)

        params = {
            "symbol": symbol.upper(),
            "resolution": resolution,
            "from": start,
            "to": now,
            "token": self.api_key,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                f"{FINNHUB_BASE_URL}/stock/candle",
                params=params,
            )

        if r.status_code != 200:
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
