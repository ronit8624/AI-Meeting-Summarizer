"""
routes/__init__.py
------------------
Exposes the API routers for FastAPI to register on startup.

By importing submodules here, main.py can load them simply using:
    from app.routes import health, meeting
"""

from . import health
from . import meeting

__all__ = ["health", "meeting"]
