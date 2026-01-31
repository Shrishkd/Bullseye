from .upstox import UpstoxProvider
from app.services.symbol_resolver import resolver

async def get_provider(symbol: str):
    resolved = await resolver.resolve(symbol)

    if not isinstance(resolved, str) or "|" not in resolved:
        raise ValueError(f"Invalid symbol or instrument key: {symbol}")

    return UpstoxProvider(), resolved
