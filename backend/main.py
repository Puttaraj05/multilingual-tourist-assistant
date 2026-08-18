import os
import json
import requests

from pathlib import Path
from typing import List

from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from pydantic import BaseModel


# =========================================================
# Environment
# =========================================================

load_dotenv()


# =========================================================
# Application
# =========================================================

app = FastAPI(
    title="TravelMate",
    version="1.0.0",
)


# =========================================================
# Base Directory
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# =========================================================
# Gemini Client
# =========================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not configured.")

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# API ROUTERS
# =========================================================
#
# These are the existing features from the original
# TravelMate application.
#
# Chat
# Chat History
# Emergency
# Translator / OCR
#
# IMPORTANT:
# The prefixes are already defined inside the router files,
# so we simply include the routers here.
# =========================================================

from backend.api.chat import router as chat_router
from backend.api.chat_history import router as chat_history_router
from backend.api.emergency import router as emergency_router
from backend.api.translator import router as translator_router


app.include_router(chat_router)

app.include_router(chat_history_router)

app.include_router(emergency_router)

app.include_router(translator_router)


# =========================================================
# Static Frontend Files
# =========================================================

# ---------------------------------------------------------
# New TravelMate itinerary frontend
#
# /css/style.css
#     ↓
# css/style.css
# ---------------------------------------------------------

app.mount(
    "/css",
    StaticFiles(
        directory=str(BASE_DIR / "css")
    ),
    name="css",
)


# ---------------------------------------------------------
# New itinerary JavaScript
#
# /js/planner.js
# /js/planner-language.js
# /js/itinerary.js
#
#     ↓
# js/
# ---------------------------------------------------------

app.mount(
    "/js",
    StaticFiles(
        directory=str(BASE_DIR / "js")
    ),
    name="js",
)


# ---------------------------------------------------------
# Existing translator frontend
#
# /static/app.js
# /static/style.css
#
#     ↓
# frontend/
# ---------------------------------------------------------

app.mount(
    "/static",
    StaticFiles(
        directory=str(BASE_DIR / "frontend")
    ),
    name="static",
)


# =========================================================
# Models
# =========================================================

class Activity(BaseModel):
    time: str
    place: str
    category: str
    cost: int
    duration: str
    description: str
    best_time: str = ""
    tip: str = ""
    nearby_food: str = ""
    popularity: str = ""


class Day(BaseModel):
    day: int
    title: str
    introduction: str = ""
    activities: List[Activity]


class TravelItinerary(BaseModel):
    destination: str
    duration: int
    estimated_total_cost: int
    destination_overview: str = ""
    days: List[Day]


class ItineraryRequest(BaseModel):
    destination: str
    duration: int
    travelDate: str
    budget: int
    currencySymbol: str = "$"
    interests: List[str]
    language: str = "English"
    travelType: str = "Solo"
    tripStyle: str = "Balanced"
    kidsUnder12: bool = False


class UITranslationRequest(BaseModel):
    language: str
    labels: dict


# =========================================================
# Health Check
# =========================================================

@app.get("/api/health")
async def health():

    return {
        "success": True,
        "message": "TravelMate API is running.",
    }


# =========================================================
# Itinerary API
# =========================================================

@app.post("/api/itinerary")
async def create_itinerary(
    data: ItineraryRequest
):

    # -----------------------------------------------------
    # Validate Gemini API key
    # -----------------------------------------------------

    if not GEMINI_API_KEY:

        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured.",
        )


    # -----------------------------------------------------
    # Validate destination using OpenStreetMap
    # -----------------------------------------------------

    try:

        geo = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": data.destination,
                "format": "jsonv2",
                "limit": 1,
            },
            headers={
                "User-Agent": "TravelMate-Hackathon/1.0",
            },
            timeout=8,
        )

        geo.raise_for_status()

        places = geo.json()

    except requests.RequestException:

        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to verify the destination right now."
            ),
        )


    # -----------------------------------------------------
    # Destination not found
    # -----------------------------------------------------

    if not places:

        raise HTTPException(
            status_code=400,
            detail=(
                "Destination not found. "
                "Please enter a valid city or country."
            ),
        )


    # -----------------------------------------------------
    # Use official place name
    # -----------------------------------------------------

    data.destination = (
        places[0]
        .get(
            "display_name",
            data.destination
        )
        .split(",")[0]
        .strip()
    )


    # -----------------------------------------------------
    # Gemini Prompt
    # -----------------------------------------------------

    prompt = f"""
You are TravelMate, an expert multilingual travel planner.

Create a realistic {data.duration}-day itinerary.

TRAVELER PROFILE

Destination: {data.destination}
Travel Date: {data.travelDate}
Budget: {data.currencySymbol}{data.budget}
Language: {data.language}
Who's Travelling: {data.travelType}
Trip Style: {data.tripStyle}
Child Under 12: {"Yes" if data.kidsUnder12 else "No"}

Interests:
{", ".join(data.interests)}

Return ONLY valid JSON with this structure:

{{
  "destination": "{data.destination}",
  "duration": {data.duration},
  "estimated_total_cost": 0,
  "destination_overview": "120-180 words about the destination.",
  "days": [
    {{
      "day": 1,
      "title": "Arrival & City Highlights",
      "introduction": "Short introduction for the day.",
      "activities": [
        {{
          "time": "8:00 AM",
          "place": "Place Name",
          "category": "Landmark",
          "cost": 20,
          "duration": "2 hrs",
          "description": "Informative description.",
          "best_time": "Morning",
          "tip": "Useful travel tip.",
          "nearby_food": "Restaurant nearby",
          "popularity": "Must Visit"
        }}
      ]
    }}
  ]
}}

RULES

- Write everything in {data.language}.
- Use real tourist attractions only.
- Keep landmark names unchanged.
- Include breakfast, lunch and dinner.
- Stay within the provided budget.
- Use numeric costs.
- Use the currency represented by {data.currencySymbol}.
- Add a 120-180 word destination overview.
- Add a short introduction for every day.
- Make descriptions practical and informative.
- Include nearby food suggestions.
- Include the best visiting time.
- Include useful travel tips.

PERSONALIZATION

- Solo:
  cafés, safer routes, walking exploration.

- Couple:
  romantic restaurants, sunset spots, scenic viewpoints.

- Family:
  family-friendly restaurants and easier schedules.

- Friends:
  adventure, nightlife and social activities.

TRIP STYLE

- Relaxed:
  around 3 activities per day.

- Balanced:
  around 4 activities per day.

- Packed:
  around 5-6 activities per day.

CHILDREN

If Child Under 12 is Yes:

- Include one child-friendly activity every day.
- Avoid excessive walking.
- Include rest breaks.
- Prefer family-friendly locations.
"""


    # -----------------------------------------------------
    # Gemini Request
    # -----------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TravelItinerary,
            ),
        )

    except ClientError as e:

        error_message = str(e)

        if "RESOURCE_EXHAUSTED" in error_message:

            raise HTTPException(
                status_code=429,
                detail=(
                    "TravelMate is receiving heavy AI traffic. "
                    "Please try again in about a minute."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {error_message}",
        )

    except ServerError:

        raise HTTPException(
            status_code=503,
            detail=(
                "The AI service is temporarily busy. "
                "Please try again in a few moments."
            ),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected AI error: {str(e)}",
        )


    # -----------------------------------------------------
    # Validate Gemini response
    # -----------------------------------------------------

    if not response.text:

        raise HTTPException(
            status_code=500,
            detail="The AI service returned an empty response.",
        )


    # -----------------------------------------------------
    # Parse Gemini JSON
    # -----------------------------------------------------

    try:

        itinerary = json.loads(
            response.text
        )

    except json.JSONDecodeError:

        raise HTTPException(
            status_code=500,
            detail="The AI service returned invalid itinerary data.",
        )


    # -----------------------------------------------------
    # Add request metadata
    # -----------------------------------------------------

    itinerary["travel_date"] = data.travelDate
    itinerary["budget"] = data.budget
    itinerary["interests"] = data.interests
    itinerary["language"] = data.language
    itinerary["currencySymbol"] = data.currencySymbol
    itinerary["travelType"] = data.travelType
    itinerary["tripStyle"] = data.tripStyle
    itinerary["kidsUnder12"] = data.kidsUnder12


    return itinerary


# =========================================================
# Dynamic UI Translation
# =========================================================

@app.post("/api/ui-translate")
async def translate_ui(
    data: UITranslationRequest
):

    # -----------------------------------------------------
    # English requires no translation
    # -----------------------------------------------------

    if data.language.lower() == "english":

        return data.labels


    # -----------------------------------------------------
    # Gemini translation prompt
    # -----------------------------------------------------

    prompt = f"""
Translate every VALUE in this JSON into {data.language}.

Keep all KEYS unchanged.

Do not add or remove keys.

Return ONLY valid JSON.

JSON:

{json.dumps(
    data.labels,
    ensure_ascii=False
)}
"""


    # -----------------------------------------------------
    # Gemini translation
    # -----------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )

        if not response.text:

            raise ValueError(
                "Empty translation response."
            )

        return json.loads(
            response.text
        )

    except Exception as e:

        print(
            f"UI translation error: {e}"
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Translation service is temporarily "
                "unavailable."
            ),
        )


# =========================================================
# Frontend Pages
# =========================================================

# ---------------------------------------------------------
# TravelMate Home
# ---------------------------------------------------------

@app.get("/")
async def home():

    return FileResponse(
        BASE_DIR / "index.html"
    )


# ---------------------------------------------------------
# Itinerary Planner
# ---------------------------------------------------------

@app.get("/planner.html")
async def planner():

    return FileResponse(
        BASE_DIR / "planner.html"
    )


# ---------------------------------------------------------
# Generated Itinerary
# ---------------------------------------------------------

@app.get("/itinerary.html")
async def itinerary():

    return FileResponse(
        BASE_DIR / "itinerary.html"
    )


# ---------------------------------------------------------
# Existing Translator Application
# ---------------------------------------------------------

@app.get("/translator")
async def translator():

    return FileResponse(
        BASE_DIR / "frontend" / "index.html"
    )