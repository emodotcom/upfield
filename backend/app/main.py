import asyncio
import logging
import string
import random
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, SessionLocal
from .models import User
from .auth import get_password_hash
from .routers import checks, monitors, settings, auth
from .scheduler import monitor_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
)

def generate_random_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def init_db():
    db = SessionLocal()
    try:
        if not db.query(User).first():
            temp_password = generate_random_password()
            print("\n" + "="*50)
            print("🚀 FIRST RUN - ADMIN ACCOUNT CREATED 🚀")
            print(f"Username: admin")
            print(f"Password: {temp_password}")
            print("="*50 + "\n")
            
            admin_user = User(
                username="admin",
                hashed_password=get_password_hash(temp_password)
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables + launch background loop
    Base.metadata.create_all(bind=engine)
    init_db()
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

app.include_router(auth.router)
app.include_router(monitors.router)
app.include_router(checks.router)
app.include_router(settings.router)

@app.get("/health", tags=["System"], summary="Liveness probe")
def health():
    return {"status": "ok"}
