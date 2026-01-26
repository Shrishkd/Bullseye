from .finnhub import FinnhubProvider
from .upstox import UpstoxProvider


async def get_provider(symbol: str):
    """
    Provider selection rule:
    - NSE_/BSE_ instrument keys → Upstox
    - Everything else → Finnhub
    """

    if symbol.startswith("NSE_") or symbol.startswith("BSE_") or "|" in symbol:
        return UpstoxProvider()

    return FinnhubProvider()
