"""
main.py — DreamScape AI — FastAPI Entry Point
"""

import logging
import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

# ── Ensure backend/ is in Python path ─────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import torch
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.ai_core.music_gen import generate_music

from fastapi import FastAPI, Request
import os

from config import get_settings
from routes import router

# ── Logging ────────────────────────────────────────────────────────────────────
settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🌙 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"GPU available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    # Create output directories
    settings.create_output_dirs()
    logger.info("Output directories ready.")

    yield  # ── app is running ──

    logger.info("Shutting down DreamScape AI...")
    # Release GPU memory
    try:
        from src.ai_core.image_gen import unload_pipeline
        unload_pipeline()
    except Exception:
        pass


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "🌙 DreamScape AI — Turn your emotions and imagination into "
        "cinematic AI dream experiences."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 🔥 ADD THIS EXACTLY HERE
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 🔥 IMPORTANT
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ─────────────────────────────────────────
app.include_router(router, prefix="/api/v1")

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file serving for outputs ───────────────────────────────────────────
os.makedirs(settings.output_dir, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")

# ── Routes ─────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")


# ── Root ───────────────────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/v1/health",
    }


# ── Dev server ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )






