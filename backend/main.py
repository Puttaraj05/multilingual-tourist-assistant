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
    currencySymbol: str = "$"

    interests: List[str]

    language: str = "English"

    travelType: str = "Solo"

    tripStyle: str = "Balanced"

    kidsUnder12: bool = False


class UITranslationRequest(BaseModel):
    language: str
    labels: dict


# -----------------------------
# Itinerary API
# -----------------------------

@app.post("/api/itinerary")
async def create_itinerary(data: ItineraryRequest):

    prompt = f"""
You are TravelMate, an expert multilingual travel planner.

Create a realistic {data.duration}-day itinerary.

Traveler Profile

Destination: {data.destination}

Travel Date: {data.travelDate}

Budget: {data.currencySymbol}{data.budget}

Language: {data.language}

Who's Travelling: {data.travelType}

Trip Style: {data.tripStyle}

Child Under 12: {"Yes" if data.kidsUnder12 else "No"}

Interests:
{", ".join(data.interests)}

Rules

1. Write EVERYTHING in {data.language}.

2. Use REAL tourist attractions.

3. Keep famous landmark names unchanged.

4. Include breakfast, lunch and dinner.

5. Keep the total cost within {data.currencySymbol}{data.budget}.

6. Show all prices using {data.currencySymbol}.

Personalization

Travel Type

Solo:
- safer routes
- cafés
- local experiences
- walking exploration

Couple:
- scenic viewpoints
- romantic restaurants
- sunset activities
- photo-worthy spots

Family:
- comfortable schedules
- family-friendly restaurants
- easy transport

Friends:
- adventure
- nightlife
- group activities

Trip Style

Relaxed:
- around 3 activities per day
- longer breaks
- relaxed sightseeing

Balanced:
- around 4 activities
- sightseeing with breaks

Packed:
- around 5–6 activities
- maximize sightseeing

If Child Under 12 is Yes:

- include ONE child-friendly activity every day
- avoid excessive walking
- include rest breaks.

Return ONLY valid JSON.
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

    itinerary["currencySymbol"] = data.currencySymbol
    itinerary["travelType"] = data.travelType
    itinerary["tripStyle"] = data.tripStyle
    itinerary["kidsUnder12"] = data.kidsUnder12

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