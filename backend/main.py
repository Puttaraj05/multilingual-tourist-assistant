from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.chat import router as chat_router
from backend.api.chat_history import router as chat_history_router
from backend.api.translator import router as translator_router
from backend.database.mongodb import client


# =========================================================
# APP
# =========================================================

app = FastAPI(
    title="Multilingual Tourist Assistant API"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# API ROUTERS
# =========================================================

app.include_router(chat_router)
app.include_router(chat_history_router)
app.include_router(translator_router)


# =========================================================
# FRONTEND
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend"
)


# =========================================================
# HOME
# =========================================================

@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Multilingual Tourist Assistant API is running",
        "docs": "/docs",
        "features": {
            "chat": "/api/chat",
            "translation": "/api/translate",
            "image_translation": "/api/image-translate"
        }
    }

# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
async def health():

    return {
        "success": True,
        "status": "healthy",
    }


# =========================================================
# DATABASE HEALTH
# =========================================================

@app.get("/api/health/database")
async def database_health():

    try:

        client.admin.command("ping")

        return {
            "success": True,
            "database": "connected",
        }

    except Exception as e:

        return {
            "success": False,
            "database": "disconnected",
            "error": str(e),
        }