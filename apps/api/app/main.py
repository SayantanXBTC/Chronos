from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.routers import entities, events, world


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="History Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(world.router, prefix="/api/v1/world", tags=["world"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.api_env}
