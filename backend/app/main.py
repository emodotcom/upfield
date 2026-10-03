import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .routers import checks, monitors, settings
from .scheduler import monitor_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables + launch background loop
    Base.metadata.create_all(bind=engine)
    task = asyncio.create_task(monitor_loop())
    yield
    # Shutdown: cancel the loop gracefully
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Upfield — Uptime & Health Checker",
    description="Monitor URLs and get notified when they go down.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this in production (set your domain)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitors.router)
app.include_router(checks.router)
app.include_router(settings.router)


@app.get("/health", tags=["System"], summary="Liveness probe")
def health():
    return {"status": "ok"}
