from fastapi import WebSocket, APIRouter
from app.services.market_providers.router import get_provider
import asyncio
from starlette.websockets import WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/market/{symbol}")
async def market_ws(websocket: WebSocket, symbol: str):
    await websocket.accept()

    provider, resolved_symbol = await get_provider(symbol)

    try:
        while True:
            quote = await provider.fetch_quote(resolved_symbol)

            if isinstance(quote, dict) and "price" in quote:
                try:
                    await websocket.send_json({
                        "symbol": symbol,
                        "price": quote["price"],
                    })
                except WebSocketDisconnect:
                    break

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        # ✅ DO NOT call send() or close() again
        pass
