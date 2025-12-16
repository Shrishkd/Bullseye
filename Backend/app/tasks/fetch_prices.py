# app/tasks/fetch_prices.py
from .celery_app import celery_app
from app.services.market_data import fetch_quote_finnhub
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import datetime
import json

# Minimal sync-to-async approach: create async engine with same DATABASE_URL
from app.core.config import settings
from app.models import Asset, Price

engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task
def fetch_and_store(symbol: str):
    """
    Celery task (sync entrypoint). Fetches snapshot and stores price into DB (async).
    We'll run an async helper inside event loop.
    """
    data = fetch_quote_finnhub(symbol)
    # data has keys: c (current), h, l, o, pc, t
    # Build a payload
    timestamp = datetime.datetime.utcfromtimestamp(int(data.get("t", datetime.datetime.utcnow().timestamp())))
    payload = {
        "timestamp": timestamp.isoformat(),
        "open": data.get("o", 0.0),
        "high": data.get("h", 0.0),
        "low": data.get("l", 0.0),
        "close": data.get("c", 0.0),
        "volume": 0.0,  # Finnhub quote endpoint doesn't give volume; you can use /stock/candle for OHLCV
    }

    # run async insert
    import asyncio

    async def _store():
        async with AsyncSessionLocal() as db:
            # upsert asset
            res = await db.execute(
                # simple select import
                Asset.__table__.select().where(Asset.symbol == symbol)
            )
            existing = res.first()
            if existing:
                asset_id = existing[0]
            else:
                ins = Asset(symbol=symbol, name=symbol)
                db.add(ins)
                await db.commit()
                await db.refresh(ins)
                asset_id = ins.id

            price = Price(
                asset_id=asset_id,
                timestamp=timestamp,
                open=payload["open"],
                high=payload["high"],
                low=payload["low"],
                close=payload["close"],
                volume=payload["volume"],
            )
            db.add(price)
            await db.commit()

    asyncio.run(_store())
    return {"status": "ok", "symbol": symbol, "fetched": payload}
