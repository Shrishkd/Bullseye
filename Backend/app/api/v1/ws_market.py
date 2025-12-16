from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from app.services.market_data import fetch_quote_finnhub

router = APIRouter()

active_connections: dict[str, set[WebSocket]] = {}

@router.websocket("/ws/market/{symbol}")
async def market_ws(websocket: WebSocket, symbol: str):
    await websocket.accept()
    symbol = symbol.upper()

    if symbol not in active_connections:
        active_connections[symbol] = set()

    active_connections[symbol].add(websocket)

    try:
        while True:
            price = fetch_quote_finnhub(symbol)
            await websocket.send_json({
                "symbol": symbol,
                "price": price["c"],
                "timestamp": price["t"]
            })
            await asyncio.sleep(2)  # stream every 2 seconds
    except WebSocketDisconnect:
        active_connections[symbol].remove(websocket)
