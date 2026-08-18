import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    print("Gemini API key loaded successfully.")
else:
    print("WARNING: GEMINI_API_KEY is not configured.")


# =========================================================
# APPLICATION
# =========================================================

app = FastAPI(
    title="TravelMate",
    version="1.0.0",
)


# =========================================================
# DIRECTORIES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"
ROOT_JS_DIR = BASE_DIR / "js"


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

from backend.api.chat import router as chat_router
from backend.api.chat_history import router as chat_history_router
from backend.api.emergency import router as emergency_router
from backend.api.translator import router as translator_router
from backend.api.speech_router import router as speech_router
from backend.api.itinerary import router as itinerary_router


app.include_router(chat_router)
app.include_router(chat_history_router)
app.include_router(emergency_router)
app.include_router(translator_router)
app.include_router(speech_router)
app.include_router(itinerary_router)


# =========================================================
# FRONTEND PAGES
# =========================================================

@app.get("/")
async def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/planner.html")
async def planner():
    return FileResponse(FRONTEND_DIR / "planner.html")


@app.get("/itinerary.html")
async def itinerary():
    return FileResponse(FRONTEND_DIR / "itinerary.html")


@app.get("/translator")
async def translator():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/chat.html")
async def chat_page():
    return FileResponse(FRONTEND_DIR / "chat.html")


@app.get("/speech.html")
async def speech_page():
    return FileResponse(FRONTEND_DIR / "speech.html")


# =========================================================
# STATIC FILES
# =========================================================

# Frontend assets:
#
# /static/css/...
# /static/js/...
#

if FRONTEND_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="static",
    )


# =========================================================
# ROOT JS
# =========================================================

# Shared JavaScript:
#
# /js/planner.js
# /js/itinerary.js
# /js/planner-language.js
#

if ROOT_JS_DIR.exists():
    app.mount(
        "/js",
        StaticFiles(directory=str(ROOT_JS_DIR)),
        name="root-js",
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
async def health():
    return {
        "success": True,
        "message": "TravelMate API is running.",
    }