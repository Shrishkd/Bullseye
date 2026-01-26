from fastapi import APIRouter, HTTPException, Request
from app.core.config import settings
from urllib.parse import urlencode
import httpx

router = APIRouter(prefix="/upstox", tags=["upstox"])


@router.get("/login")
def upstox_login():
    if not settings.UPSTOX_API_KEY or not settings.UPSTOX_REDIRECT_URI:
        raise HTTPException(
            status_code=500,
            detail="Upstox API key or redirect URI not configured"
        )

    params = {
        "response_type": "code",
        "client_id": settings.UPSTOX_API_KEY,
        "redirect_uri": settings.UPSTOX_REDIRECT_URI,
    }

    auth_url = (
        "https://api.upstox.com/v2/login/authorization/dialog?"
        + urlencode(params)
    )

    return {"auth_url": auth_url}


@router.get("/callback")
async def upstox_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(400, "Authorization code missing")

    if not settings.UPSTOX_API_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Upstox API secret not configured"
        )

    token_url = "https://api.upstox.com/v2/login/authorization/token"

    payload = {
        "code": code,
        "client_id": settings.UPSTOX_API_KEY,
        "client_secret": settings.UPSTOX_API_SECRET,
        "redirect_uri": settings.UPSTOX_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(token_url, data=payload, headers=headers)

    if r.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Token exchange failed: {r.text}"
        )

    token_data = r.json()

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=400,
            detail="Access token missing in Upstox response"
        )

    return {
        "access_token": access_token,
        "expires_in": token_data.get("expires_in"),
    }
