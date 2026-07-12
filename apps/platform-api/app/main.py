from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.api.v1.router import api_router
from app.core.config.settings import settings
from app.observability import PrometheusMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    PrometheusMiddleware,
)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/", tags=["Platform"])
async def root() -> dict[str, str]:
    return {
        "name": settings.APP_NAME,
        "description": settings.APP_DESCRIPTION,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }