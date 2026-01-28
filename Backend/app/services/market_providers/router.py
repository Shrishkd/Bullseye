# app/services/market_providers/router.py

from .finnhub import FinnhubProvider
from .upstox import UpstoxProvider
from app.services.symbol_resolver import resolver


async def get_provider(symbol: str):
    """
    Resolve symbol → instrument key and select provider.
    """

    resolved = await resolver.resolve(symbol)

    # ✅ Strict validation for Upstox
    if isinstance(resolved, str) and resolved.startswith("NSE_EQ|"):
        return UpstoxProvider(), resolved

    # ❌ Fallback to Finnhub ONLY for non-Indian symbols
    return FinnhubProvider(), symbol.upper()
