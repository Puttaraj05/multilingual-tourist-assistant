import os
import json
from typing import List

from dotenv import load_dotenv
from google import genai
from google.genai import types

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

app = FastAPI(title="TravelMate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -----------------------------
# Currency Map
# -----------------------------

CURRENCY_MAP = {
    "india": ("INR", "₹"),
    "usa": ("USD", "$"),
    "united states": ("USD", "$"),
    "new york": ("USD", "$"),
    "japan": ("JPY", "¥"),
    "tokyo": ("JPY", "¥"),
    "france": ("EUR", "€"),
    "paris": ("EUR", "€"),
    "italy": ("EUR", "€"),
    "rome": ("EUR", "€"),
    "spain": ("EUR", "€"),
    "germany": ("EUR", "€"),
    "uae": ("AED", "د.إ"),
    "dubai": ("AED", "د.إ"),
    "china": ("CNY", "¥"),
    "south korea": ("KRW", "₩"),
    "korea": ("KRW", "₩"),
    "thailand": ("THB", "฿"),
    "bangkok": ("THB", "฿"),
    "turkey": ("TRY", "₺"),
    "vietnam": ("VND", "₫"),
    "indonesia": ("IDR", "Rp"),
    "switzerland": ("CHF", "CHF"),
    "uk": ("GBP", "£"),
    "united kingdom": ("GBP", "£"),
    "london": ("GBP", "£"),
    "canada": ("CAD", "C$"),
    "australia": ("AUD", "A$")
}

# -----------------------------
# Models
# -----------------------------

class Activity(BaseModel):
    time: str
    place: str
    category: str
    cost: int
    duration: str
    description: str


class Day(BaseModel):
    day: int
    title: str
    activities: List[Activity]


class TravelItinerary(BaseModel):
    destination: str
    duration: int
    estimated_total_cost: int
    days: List[Day]


class ItineraryRequest(BaseModel):
    destination: str
    duration: int
    travelDate: str
    budget: int
    interests: List[str]
    language: str = "English"


class UITranslationRequest(BaseModel):
    language: str
    labels: dict


# -----------------------------
# Itinerary API
# -----------------------------

@app.post("/api/itinerary")
async def create_itinerary(data: ItineraryRequest):

    currency_code, currency_symbol = CURRENCY_MAP.get(
        data.destination.lower(),
        ("USD", "$")
    )

    prompt = f"""
You are an expert multilingual travel planner.

Create a realistic {data.duration}-day itinerary.

Destination: {data.destination}
Travel Date: {data.travelDate}
Budget: {currency_symbol}{data.budget} ({currency_code})
Interests: {", ".join(data.interests)}
Preferred Language: {data.language}

Rules:
- Write EVERYTHING in {data.language}.
- Use REAL tourist attractions.
- Keep famous landmark names unchanged.
- Include breakfast, lunch and dinner.
- Show every activity cost using {currency_symbol}.
- Stay within budget.
- Return ONLY valid JSON.
"""

    response = client.models.generate_content(
        model="models/gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TravelItinerary
        )
    )

    itinerary = json.loads(response.text)

    itinerary["travel_date"] = data.travelDate
    itinerary["budget"] = data.budget
    itinerary["interests"] = data.interests
    itinerary["language"] = data.language
    itinerary["currencyCode"] = currency_code
    itinerary["currencySymbol"] = currency_symbol

    return itinerary


# -----------------------------
# Dynamic UI Translation
# -----------------------------

@app.post("/api/ui-translate")
async def translate_ui(data: UITranslationRequest):

    if data.language.lower() == "english":
        return data.labels

    prompt = f"""
Translate every VALUE in this JSON into {data.language}.

Keep the KEYS unchanged.

Return ONLY valid JSON.

JSON:
{json.dumps(data.labels, ensure_ascii=False)}
"""

    response = client.models.generate_content(
        model="models/gemini-3.1-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)