from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import PriceIn, PriceOut, AssetOut
from app.crud import assets as assets_crud, prices as prices_crud
from app.api.deps import get_db, get_current_user

from fastapi import APIRouter, Depends
from app.services.market_candles import fetch_candles
from app.services.indicators import sma, ema
from app.api.deps import get_current_user

from app.services.indicators import sma, ema, rsi

router = APIRouter(prefix="/market", tags=["market"])


@router.post("/prices/ingest")
async def ingest_price(
    payload: PriceIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    asset = await assets_crud.create_asset_if_not_exists(db, payload.asset_symbol)
    price = await prices_crud.create_price(
        db,
        asset_id=asset.id,
        timestamp=payload.timestamp,
        open=payload.open,
        high=payload.high,
        low=payload.low,
        close=payload.close,
        volume=payload.volume,
    )
    return {"status": "ok", "price_id": price.id}


@router.get("/assets/{symbol}", response_model=AssetOut)
async def get_asset(
    symbol: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    asset = await assets_crud.get_asset_by_symbol(db, symbol)
    if not asset:
        raise HTTPException(404, "Asset not found")
    return asset


@router.get("/prices/{symbol}", response_model=list[PriceOut])
async def get_recent_prices(
    symbol: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    asset = await assets_crud.get_asset_by_symbol(db, symbol)
    if not asset:
        raise HTTPException(404, "Asset not found")
    prices = await prices_crud.get_recent_prices(db, asset.id, limit)
    return prices[::-1]  # return oldest → newest

@router.get("/candles/{symbol}")
async def get_candles(
    symbol: str,
    resolution: str = "5",
    period: int = 14,
    user=Depends(get_current_user),
):
    from app.services.market_providers.router import get_provider

    provider, resolved_symbol = await get_provider(symbol)
    candles = await provider.fetch_candles(resolved_symbol, resolution)


    if not candles:
        return []

    closes = [c["close"] for c in candles]

    sma_vals = sma(closes, period)
    ema_vals = ema(closes, period)
    rsi_vals = rsi(closes, period)

    for i, c in enumerate(candles):
        c["sma"] = sma_vals[i]
        c["ema"] = ema_vals[i]
        c["rsi"] = rsi_vals[i]

    return candles

