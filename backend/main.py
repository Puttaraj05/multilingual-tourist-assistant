import os
import json
import requests
from typing import List

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

from fastapi import FastAPI, HTTPException
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


# -----------------------------
# Itinerary API
# -----------------------------

@app.post("/api/itinerary")
async def create_itinerary(data: ItineraryRequest):

    # -----------------------------
    # Destination Validation (OpenStreetMap)
    # -----------------------------

    try:
        geo = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": data.destination,
                "format": "jsonv2",
                "limit": 1
            },
            headers={
                "User-Agent": "TravelMate-Hackathon/1.0"
            },
            timeout=8
        )

        places = geo.json()

    except requests.RequestException:
        raise HTTPException(
            status_code=503,
            detail="Unable to verify the destination right now."
        )

    if not places:
        raise HTTPException(
            status_code=400,
            detail="Destination not found. Please enter a valid city or country."
        )

    # Use official place name
    data.destination = places[0]["display_name"].split(",")[0]

    # -----------------------------
    # Gemini Prompt
    # -----------------------------

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

Return ONLY valid JSON with this structure:

{{
  "destination":"{data.destination}",
  "duration":{data.duration},
  "estimated_total_cost":0,
  "destination_overview":"120-180 words about the destination.",
  "days":[
    {{
      "day":1,
      "title":"Arrival & City Highlights",
      "introduction":"Short introduction for the day.",
      "activities":[
        {{
          "time":"8:00 AM",
          "place":"Place Name",
          "category":"Landmark",
          "cost":20,
          "duration":"2 hrs",
          "description":"Informative description.",
          "best_time":"Morning",
          "tip":"Useful travel tip.",
          "nearby_food":"Restaurant nearby",
          "popularity":"Must Visit"
        }}
      ]
    }}
  ]
}}

Rules:
- Write everything in {data.language}.
- Use real tourist attractions only.
- Keep landmark names unchanged.
- Include breakfast, lunch and dinner.
- Stay within budget.
- Show prices using {data.currencySymbol}.
- Add a 120-180 word destination overview.
- Add a short introduction for every day.
- Make descriptions practical and informative.
- Include nearby food suggestions.
- Include best visiting time.
- Include travel tips.

Personalization:
- Solo: cafés, safer routes, walking exploration.
- Couple: romantic restaurants, sunset spots, scenic viewpoints.
- Family: family-friendly restaurants and easier schedules.
- Friends: adventure and nightlife.

Trip Style:
- Relaxed: around 3 activities.
- Balanced: around 4 activities.
- Packed: around 5-6 activities.

If Child Under 12 is Yes:
- Include one child-friendly activity every day.
- Avoid excessive walking.
- Include rest breaks.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TravelItinerary
            )
        )

    except ClientError as e:

        if "RESOURCE_EXHAUSTED" in str(e):
            raise HTTPException(
                status_code=429,
                detail="TravelMate is receiving heavy AI traffic. Please try again in about a minute."
            )

        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )

    except ServerError:

        raise HTTPException(
            status_code=503,
            detail="The AI service is temporarily busy. Please try again in a few moments."
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

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        return json.loads(response.text)

    except Exception:

        raise HTTPException(
            status_code=503,
            detail="Translation service is temporarily unavailable."
        )