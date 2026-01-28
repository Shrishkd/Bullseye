# app/services/market_providers/upstox.py

import os
import httpx
from datetime import datetime, timedelta
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
        if not self.access_token or "|" not in instrument_key:
            return {}

        url = f"{UPSTOX_BASE_URL}/market-quote/ltp"
        params = {"instrument_key": instrument_key}

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, headers=self._headers(), params=params)

        if r.status_code != 200:
            return {}

        data = r.json().get("data", {})
        quote = data.get(instrument_key)

        if not quote or "last_price" not in quote:
            return {}

        ohlc = quote.get("ohlc", {})

        return {
            "price": float(quote["last_price"]),
            "open": float(ohlc.get("open", quote["last_price"])),
            "high": float(ohlc.get("high", quote["last_price"])),
            "low": float(ohlc.get("low", quote["last_price"])),
            "timestamp": int(datetime.utcnow().timestamp()),
            "volume": float(quote.get("volume", 0.0)),
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

        if not self.access_token or "|" not in instrument_key:
            print("❌ Invalid Upstox instrument_key:", instrument_key)
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

            # -----------------------------
            # DAILY / HISTORICAL (FIXED)
            # -----------------------------
            if interval == "day":
                to_date = datetime.utcnow().date().isoformat()
                from_date = (
                    datetime.utcnow().date() - timedelta(days=365)
                ).isoformat()

                url = (
                    f"{UPSTOX_BASE_URL}/historical-candle/"
                    f"{instrument_key}/day/{from_date}/{to_date}"
                )

            # -----------------------------
            # INTRADAY
            # -----------------------------
            else:
                url = (
                    f"{UPSTOX_BASE_URL}/historical-candle/intraday/"
                    f"{instrument_key}/{interval}"
                )

            print("📡 Upstox candles URL:", url)

            r = await client.get(url, headers=self._headers())

        if r.status_code != 200:
            print("❌ Upstox error:", r.status_code, r.text)
            return []

        payload = r.json()
        candles = payload.get("data", {}).get("candles", [])

        print("🕯️ Candles received:", len(candles))

        result = []
        for c in candles[-limit:]:
            result.append({
                "time": int(datetime.fromisoformat(c[0]).timestamp() * 1000),
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5]),
            })

        return result
