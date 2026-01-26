# app/services/market_providers/upstox.py

import os
import httpx
from datetime import datetime
from .base import MarketProvider

UPSTOX_BASE_URL = "https://api.upstox.com/v2"


class UpstoxProvider(MarketProvider):
    """
    Upstox market data provider (India-focused).
    Supports:
    - Quotes (LTP)
    - Historical & intraday candles
    """

    def __init__(self):
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")

    def _headers(self) -> dict:
        if not self.access_token:
            return {}
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    # -----------------------------
    # QUOTE (LTP)
    # -----------------------------
    async def fetch_quote(self, instrument_key: str) -> dict:
        """
        instrument_key example:
        NSE_EQ|INE002A01018  (RELIANCE)
        """

        if not self.access_token:
            return {}

        url = f"{UPSTOX_BASE_URL}/market-quote/ltp"

        params = {
            "instrument_key": instrument_key,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers=self._headers(), params=params)

        if r.status_code != 200:
            return {}

        data = r.json().get("data", {})
        quote = data.get(instrument_key)

        if not quote or "last_price" not in quote:
            return {}

        return {
            "price": float(quote["last_price"]),
            "open": float(quote.get("ohlc", {}).get("open", quote["last_price"])),
            "high": float(quote.get("ohlc", {}).get("high", quote["last_price"])),
            "low": float(quote.get("ohlc", {}).get("low", quote["last_price"])),
            "timestamp": int(datetime.utcnow().timestamp()),
            "volume": 0.0,
        }

    # -----------------------------
    # CANDLES (OHLCV)
    # -----------------------------
    async def fetch_candles(
        self,
        instrument_key: str,
        resolution: str,
        limit: int = 100,
    ) -> list[dict]:
        """
        resolution mapping:
        "1"  -> 1minute
        "5"  -> 5minute
        "15" -> 15minute
        "D"  -> day
        """

        if not self.access_token:
            return []

        interval_map = {
            "1": "1minute",
            "5": "5minute",
            "15": "15minute",
            "D": "day",
        }

        interval = interval_map.get(resolution, "day")

        to_dt = datetime.utcnow()
        from_dt = to_dt

        if interval == "day":
            from_dt = to_dt.replace(hour=0, minute=0, second=0)
        else:
            from_dt = to_dt

        url = f"{UPSTOX_BASE_URL}/historical-candle/intraday/{instrument_key}/{interval}"

        params = {
            "from_date": from_dt.strftime("%Y-%m-%d"),
            "to_date": to_dt.strftime("%Y-%m-%d"),
        }

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers=self._headers(), params=params)

        if r.status_code != 200:
            return []

        raw = r.json().get("data", {}).get("candles", [])
        if not raw:
            return []

        candles = []
        for c in raw[-limit:]:
            # Upstox candle format:
            # [timestamp, open, high, low, close, volume]
            candles.append({
                "time": int(datetime.fromisoformat(c[0]).timestamp() * 1000),
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5]),
            })

        return candles
