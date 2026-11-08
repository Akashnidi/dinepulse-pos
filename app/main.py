"""
FastAPI application entry-point.
Serves static files and mounts all API routers.
Path resolution is PyInstaller-safe (sys._MEIPASS fallback).
"""
import sys
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import init_db
from app.routers import menu, orders, settings, dashboard

# ── Resolve static files directory ───────────────────────────────────────────
if getattr(sys, "frozen", False):
    # Running as PyInstaller bundle
    _BASE = Path(sys._MEIPASS)  # type: ignore[attr-defined]
else:
    _BASE = Path(__file__).resolve().parent.parent

STATIC_DIR = _BASE / "static"

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="DinePOS", version="1.0.0", docs_url="/docs")

# Boot DB on startup
@app.on_event("startup")
def startup():
    init_db()

# Mount API routers
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(settings.router)
app.include_router(dashboard.router)

# Serve static assets (CSS/JS/icons embedded in HTML so this is minimal)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(str(STATIC_DIR / "index.html"))

