import logging
import random

from fastapi import FastAPI, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pydantic_settings import BaseSettings
import httpx

logging.getLogger().setLevel(logging.INFO)

app = FastAPI(title="Proxy")

class Config(BaseSettings):
    MONOLITH_URL: str
    MOVIES_SERVICE_URL: str
    EVENTS_SERVICE_URL: str
    GRADUAL_MIGRATION: bool
    MOVIES_MIGRATION_PERCENT: int

config = Config()

ENDPOINT_MAPPING = {
    "/api/movies": config.MOVIES_SERVICE_URL,
    "/api/users": config.MONOLITH_URL,
    "/api/events": config.EVENTS_SERVICE_URL,
}

class ReverseProxyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        for path, target_host in ENDPOINT_MAPPING.items():
            if (
                    request.url.path.startswith(path)
                    and (random.random() < config.MOVIES_MIGRATION_PERCENT / 100 or not config.GRADUAL_MIGRATION)
            ):
                target_url = f"{target_host}{request.url.path}"
                break

        else:
            target_url = f"{config.MONOLITH_URL}{request.url.path}"
        async with httpx.AsyncClient() as client:
            print(target_url)
            response = await client.request(request.method, target_url, headers=dict(request.headers), data=await request.body())
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

app.add_middleware(ReverseProxyMiddleware)