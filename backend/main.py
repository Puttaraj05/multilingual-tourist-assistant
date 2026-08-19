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
    title="Multilingual Tourist Assistant",
    version="1.0.0",
)


# =========================================================
# DIRECTORIES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"

CSS_DIR = FRONTEND_DIR / "css"
JS_DIR = FRONTEND_DIR / "js"


print("========================================")
print("TravelMate Directories")
print("========================================")
print("Project:", BASE_DIR)
print("Frontend:", FRONTEND_DIR)
print("CSS:", CSS_DIR)
print("JS:", JS_DIR)
print("========================================")


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
from backend.api.recommendation import router as recommendation_router


app.include_router(chat_router)
app.include_router(chat_history_router)
app.include_router(emergency_router)
app.include_router(translator_router)
app.include_router(speech_router)
app.include_router(itinerary_router)
app.include_router(recommendation_router)


# =========================================================
# STATIC FILES
# =========================================================

if FRONTEND_DIR.exists():

    app.mount(
        "/static",
        StaticFiles(
            directory=str(FRONTEND_DIR)
        ),
        name="static",
    )

else:

    print(
        f"WARNING: Frontend directory not found: {FRONTEND_DIR}"
    )


# =========================================================
# FAVICON
# =========================================================

@app.get(
    "/favicon.ico",
    include_in_schema=False
)
async def favicon():

    favicon_path = (
        FRONTEND_DIR
        / "images"
        / "logo.webp"
    )

    if favicon_path.exists():

        return FileResponse(
            favicon_path,
            media_type="image/webp"
        )

    return {
        "success": False,
        "error": "Favicon not found"
    }


# =========================================================
# FRONTEND PAGE HELPER
# =========================================================

def frontend_file(filename: str):

    file_path = FRONTEND_DIR / filename

    if not file_path.exists():

        return {
            "success": False,
            "error": f"Page not found: {filename}",
        }

    return FileResponse(file_path)


# =========================================================
# FRONTEND PAGES
# =========================================================

@app.get("/")
async def home():

    return frontend_file("index.html")


@app.get("/index.html")
async def index_page():

    return frontend_file("index.html")


@app.get("/about.html")
async def about_page():

    return frontend_file("about.html")


@app.get("/auth.html")
async def auth_page():

    return frontend_file("auth.html")


@app.get("/chat.html")
async def chat_page():

    return frontend_file("chat.html")


@app.get("/emergency.html")
async def emergency_page():

    return frontend_file("emergency.html")


@app.get("/features.html")
async def features_page():

    return frontend_file("features.html")


@app.get("/planner.html")
async def planner_page():

    return frontend_file("planner.html")


@app.get("/itinerary.html")
async def itinerary_page():

    return frontend_file("itinerary.html")


@app.get("/recommendations.html")
async def recommendations_page():

    return frontend_file(
        "recommendations.html"
    )


@app.get("/translation.html")
async def translation_page():

    return frontend_file(
        "translation.html"
    )


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
async def health():

    return {
        "success": True,
        "message": "TravelMate API is running",
    }