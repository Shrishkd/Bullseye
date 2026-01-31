# app/services/symbol_resolver.py

# Temporary hard-mapped resolver for Indian equities
# (We will later replace this with DB / Upstox instrument master)

SYMBOL_MAP = {
    "RELIANCE": "NSE_EQ|INE002A01018",
    "TCS": "NSE_EQ|INE467B01029",
    "INFY": "NSE_EQ|INE009A01021",
    "HDFCBANK": "NSE_EQ|INE040A01034",
    "ICICIBANK": "NSE_EQ|INE090A01021",
}


class SymbolResolver:
    async def resolve(self, symbol: str) -> str | None:
        if not symbol:
            return None

        symbol = symbol.upper().strip()
        return SYMBOL_MAP.get(symbol)


resolver = SymbolResolver()
