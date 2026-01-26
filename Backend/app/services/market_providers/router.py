from .finnhub import FinnhubProvider
from .upstox import UpstoxProvider
from app.services.symbol_resolver import resolver


async def get_provider(symbol: str):
    """
    Resolve symbol → instrument key and select provider.
    """

    resolved = await resolver.resolve(symbol)

    if resolved.startswith("NSE_EQ"):
        return UpstoxProvider(), resolved

    return FinnhubProvider(), symbol
