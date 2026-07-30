"""
routes/health.py
----------------
Lightweight check endpoints for monitoring and diagnostics.

Endpoints:
  - GET /        -> Simple HTML welcome page or JSON status
  - GET /health  -> Detailed health check API for load balancers
"""

import time
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

router = APIRouter(tags=["System Health"])

# Record server start time to calculate uptime
START_TIME = time.time()


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall health state. Should be 'ok'")
    uptime_seconds: float = Field(..., description="Seconds since server startup")
    app_version: str = Field(..., description="Current running backend version")


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Root Welcome Endpoint",
    description="Simple welcome endpoint to verify the API is reachable.",
)
async def root():
    return {
        "message": "Welcome to the AI Meeting Summarizer API",
        "docs_url": "/docs",
        "status": "online"
    }


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Diagnostic Check",
    description="Returns server status, uptime, and metadata for monitoring.",
)
async def health_check():
    uptime = time.time() - START_TIME
    return HealthResponse(
        status="ok",
        uptime_seconds=round(uptime, 2),
        app_version="1.0.0"
    )
