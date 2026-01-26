from abc import ABC, abstractmethod

class MarketProvider(ABC):
    @abstractmethod
    async def fetch_candles(
        self,
        symbol: str,
        resolution: str,
        limit: int = 100
    ):
        pass
