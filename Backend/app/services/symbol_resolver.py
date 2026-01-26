# app/services/symbol_resolver.py

import httpx
from functools import lru_cache

UPSTOX_INSTRUMENTS_URL = "https://api.upstox.com/v2/instruments"


class SymbolResolver:
    """
    Resolves human-readable symbols (RELIANCE, TCS)
    to Upstox instrument keys (NSE_EQ|INE...)
    """

    def __init__(self):
        self._symbol_map = {}

    async def _load_instruments(self):
        """
        Load instrument master once and cache it.
        """
        if self._symbol_map:
            return

        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(UPSTOX_INSTRUMENTS_URL)

        if r.status_code != 200:
            return

        lines = r.text.splitlines()

        # CSV format (no auth needed)
        # instrument_key,exchange,segment,name,isin,...
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) < 6:
                continue

            instrument_key = parts[0]
            exchange = parts[1]
            name = parts[3]
            isin = parts[4]

            if exchange == "NSE" and instrument_key.startswith("NSE_EQ"):
                self._symbol_map[name.upper()] = instrument_key
                if isin:
                    self._symbol_map[isin.upper()] = instrument_key

    async def resolve(self, symbol: str) -> str:
        """
        Returns instrument_key if found, else original symbol.
        """
        symbol = symbol.upper().strip()

        await self._load_instruments()

        return self._symbol_map.get(symbol, symbol)


# Singleton instance
resolver = SymbolResolver()
