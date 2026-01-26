# app/api/v1/ws_market.py

from fastapi import WebSocket, APIRouter
from app.services.market_providers.router import get_provider
import asyncio

router = APIRouter()

@router.websocket("/ws/market/{symbol}")
async def market_ws(websocket: WebSocket, symbol: str):
    await websocket.accept()

    provider = await get_provider(symbol)

    try:
        while True:
            quote = await provider.fetch_quote(symbol)

            price = quote.get("price") if isinstance(quote, dict) else None
            if price is not None:
                await websocket.send_json({
                    "symbol": symbol,
                    "price": price,
                })

            await asyncio.sleep(1)

    except Exception:
        await websocket.close()
