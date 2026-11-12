"""Read-only Garmin Connect API. Uses the official Garmin Connect Personal API."""
import os
import secrets
from functools import lru_cache
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json
from fastapi import FastAPI, Header, HTTPException


app = FastAPI(title="Garmin Connect read-only bridge", docs_url=None, redoc_url=None, openapi_url=None)


def authorize(authorization: str | None):
    expected = os.environ.get("API_TOKEN", "")
    if not expected or not authorization or not secrets.compare_digest(authorization, f"Bearer {expected}"):
        raise HTTPException(status_code=401, detail="Unauthorized")


GARMIN_ORIGIN = "https://personal.connectapi.garmin.com"
TOKEN_PATH = "/personalapitoken-service/personal-api/personal-api-key/token"


def request_garmin(path: str, authorization: str, method: str = "GET") -> bytes:
    request = Request(
        GARMIN_ORIGIN + path,
        headers={"Authorization": authorization},
        method=method,
    )
    with urlopen(request, timeout=20) as response:
        return response.read()


@lru_cache(maxsize=1)
def access_token() -> str:
    key = os.environ.get("GARMIN_API_KEY")
    if not key:
        raise HTTPException(status_code=503, detail="Garmin API key is missing")
    try:
        token = request_garmin(TOKEN_PATH, f"ApiKey {key}", "POST").decode().strip()
    except (URLError, TimeoutError, UnicodeError):
        raise HTTPException(status_code=502, detail="Garmin rejected the token request or is unavailable") from None
    if not token or any(character.isspace() for character in token):
        raise HTTPException(status_code=502, detail="Invalid token response from Garmin")
    return token


def garmin_json(path: str):
    token = access_token()
    try:
        try:
            payload = request_garmin(path, f"Bearer {token}")
        except HTTPError as exc:
            if exc.code != 401:
                raise
            access_token.cache_clear()
            payload = request_garmin(path, f"Bearer {access_token()}")
        return json.loads(payload)
    except (URLError, TimeoutError, ValueError):
        raise HTTPException(status_code=502, detail="Garmin activity request failed") from None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/activities")
def activities(limit: int = 10, start: int = 0, authorization: str | None = Header(default=None)):
    authorize(authorization)
    if not 1 <= limit <= 100 or not 0 <= start <= 10000:
        raise HTTPException(status_code=400, detail="Invalid pagination")
    query = urlencode({"start": start, "limit": limit})
    data = garmin_json(f"/activitylist-service/activities/search/activities?{query}")
    return {"activities": data}


@app.get("/activity/{activity_id}")
def activity(activity_id: int, authorization: str | None = Header(default=None)):
    authorize(authorization)
    if activity_id < 1:
        raise HTTPException(status_code=400, detail="Invalid activity ID")
    return {"activity": garmin_json(f"/activity-service/activity/{activity_id}")}
