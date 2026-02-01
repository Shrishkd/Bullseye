from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import auth, market, chat, health, ws_market, news
from app.services.instrument_registry import load_instruments
from app.db.session import engine
from app.models import Base

# -----------------------------
# Create FastAPI app
# -----------------------------
app = FastAPI(title=settings.PROJECT_NAME)

# -----------------------------
# CORS configuration
# -----------------------------
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# SAFE STARTUP TASKS (light only)
# -----------------------------
@app.on_event("startup")
async def on_startup():
    # Only lightweight DB init here
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ DB ready. Server started successfully.")

# -----------------------------
# Routers
# -----------------------------
app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(market.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(ws_market.router)
app.include_router(news.router, prefix="/api")

# -----------------------------
# Admin endpoint to load NSE instruments (run once)
# -----------------------------
@app.get("/admin/load-instruments")
def load_all_instruments():
    load_instruments()
    return {"status": "NSE instruments loaded successfully"}

# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
async def root():
    return {"message": "Bullseye backend is running"}
