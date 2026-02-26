import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from core.config import settings
from core.events import create_es_indices
from modules.auth.router import router as auth_router
from modules.logs.router import router as logs_router
from modules.logs.upload_router import router as logs_upload_router
from modules.ids.router import router as ids_router
from modules.network.router import router as network_router
from modules.network.config_router import router as network_config_router
from modules.alerts.router import router as alerts_router
from modules.assets.router import router as assets_router
from modules.dashboard.router import router as dashboard_router
from websocket.handlers import router as ws_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.es = AsyncElasticsearch([settings.elasticsearch_url])
    app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)
    await create_es_indices(app.state.es)
    logger.info("SOC Platform started")
    yield
    await app.state.es.close()
    await app.state.redis.aclose()
    logger.info("SOC Platform stopped")


app = FastAPI(
    title="SOC Platform API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router,           prefix="/api/v1/auth",      tags=["auth"])
app.include_router(logs_router,           prefix="/api/v1/logs",      tags=["logs"])
app.include_router(logs_upload_router,    prefix="/api/v1/logs",      tags=["logs"])
app.include_router(ids_router, prefix="/api/v1/ids", tags=["ids"])
app.include_router(network_router, prefix="/api/v1/network", tags=["network"])
app.include_router(network_config_router, prefix="/api/v1/network", tags=["network-config"])
app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(assets_router, prefix="/api/v1/assets", tags=["assets"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(ws_router, tags=["websocket"])


@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "service": "SOC Platform"}
