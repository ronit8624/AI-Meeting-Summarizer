"""
main.py
-------
FastAPI application entry point.

Responsibilities:
- Bootstrap the FastAPI app with metadata
- Register CORS middleware
- Mount all API routers
- Ensure upload/output directories exist on startup
- Configure structured logging
"""

import sys
import os
import logging

# ─────────────────────────────────────────────────────────────────
# CRITICAL: Add the project root to sys.path
#
# The root-level core/ and utils/ packages need to be importable
# from inside backend/. This line makes:
#   from core.summarizer import summarize
#   from utils.audio_processor import process_input
# work correctly regardless of where uvicorn is launched from.
# ─────────────────────────────────────────────────────────────────
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env before importing settings so all env vars are available
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.core.config import settings
from app.routes import health, meeting

# ─────────────────────────────────────────────────────────────────
# LOGGING CONFIGURATION
#
# Using Python's built-in logging. In production you'd swap this
# for structlog or similar, but this keeps zero extra dependencies.
# ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────
# LIFESPAN HANDLER
#
# FastAPI's modern way to run code on startup and shutdown.
# We use it to ensure the uploads/ and outputs/ directories
# always exist before any request hits the server.
# ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────
    logger.info("Starting up AI Meeting Summarizer API...")

    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    logger.info(f"Uploads directory ready: {settings.UPLOADS_DIR}")

    os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)
    logger.info(f"Outputs directory ready: {settings.OUTPUTS_DIR}")

    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    yield  # ← Application runs here

    # ── Shutdown ──────────────────────────────────────────────────
    logger.info("Shutting down AI Meeting Summarizer API...")


# ─────────────────────────────────────────────────────────────────
# FASTAPI APP INSTANCE
# ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-grade FastAPI backend for the AI Meeting Summarizer. "
        "Handles audio upload, transcription, summarization, "
        "insight extraction, and RAG-powered Q&A."
    ),
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc UI
    lifespan=lifespan,
)


# ─────────────────────────────────────────────────────────────────
# CORS MIDDLEWARE
#
# Allows the Flutter app (running on a different origin/port)
# to make requests to this API without being blocked by the browser.
# ALLOWED_ORIGINS is read from .env — set to "*" in development,
# and lock it down to your Flutter app's domain in production.
# ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────
# ROUTER REGISTRATION
#
# health router  → GET /  and  GET /health
# meeting router → all /api/v1/meeting/* endpoints
# ─────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(meeting.router, prefix="/api/v1")

logger.info("All routers registered successfully.")
