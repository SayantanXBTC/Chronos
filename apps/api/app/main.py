from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import entities, events, place_names, rivers, sources, world


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="History Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(world.router, prefix="/api/v1/world", tags=["world"])
app.include_router(entities.router, prefix="/api/v1/entities", tags=["entities"])
app.include_router(events.router, prefix="/api/v1/events", tags=["events"])
app.include_router(place_names.router, prefix="/api/v1/place-names", tags=["place-names"])
app.include_router(rivers.router, prefix="/api/v1/rivers", tags=["rivers"])
app.include_router(sources.router, prefix="/api/v1/sources", tags=["sources"])


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.api_env}
