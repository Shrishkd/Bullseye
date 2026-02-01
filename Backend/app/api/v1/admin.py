from fastapi import APIRouter
from app.services.instrument_registry import load_instruments

router = APIRouter()

@router.get("/load-instruments")
def load_all():
    load_instruments()
    return {"status": "instruments loaded"}
