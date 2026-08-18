import os
import json
import time

from typing import List

from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# =========================================================
# GEMINI CLIENT
# =========================================================

client = None

if GEMINI_API_KEY:

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    print("Gemini API key loaded successfully.")

else:

    print(
        "WARNING: GEMINI_API_KEY is not configured "
        "for itinerary service."
    )


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/api",
    tags=["Itinerary"],
)


# =========================================================
# RESPONSE MODELS
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


# =========================================================
# REQUEST MODEL
# =========================================================

class ItineraryRequest(BaseModel):

    destination: str

    duration: int

    travelDate: str

    budget: int

    currencySymbol: str = "₹"

    interests: List[str] = []

    language: str = "English"

    travelType: str = "Solo"

    tripStyle: str = "Balanced"

    kidsUnder12: bool = False


# =========================================================
# CREATE ITINERARY
# =========================================================

@router.post("/itinerary")
async def create_itinerary(
    data: ItineraryRequest
):

    print("\n========================================")
    print("ITINERARY REQUEST RECEIVED")
    print("========================================")

    print("Destination:", data.destination)
    print("Duration:", data.duration)
    print("Travel Date:", data.travelDate)
    print("Budget:", data.budget)
    print("Currency:", data.currencySymbol)
    print("Language:", data.language)
    print("Travel Type:", data.travelType)
    print("Trip Style:", data.tripStyle)
    print("Kids Under 12:", data.kidsUnder12)
    print("Interests:", data.interests)

    # =====================================================
    # GEMINI VALIDATION
    # =====================================================

    if not GEMINI_API_KEY or client is None:

        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured.",
        )

    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    if not data.destination.strip():

        raise HTTPException(
            status_code=400,
            detail="Destination is required.",
        )

    if data.duration < 1 or data.duration > 30:

        raise HTTPException(
            status_code=400,
            detail=(
                "Trip duration must be between "
                "1 and 30 days."
            ),
        )

    if data.budget <= 0:

        raise HTTPException(
            status_code=400,
            detail="Budget must be greater than zero.",
        )

    # =====================================================
    # INTERESTS
    # =====================================================

    interests = (
        ", ".join(data.interests)
        if data.interests
        else "General sightseeing"
    )

    # =====================================================
    # GEMINI PROMPT
    # =====================================================

    prompt = f"""
You are TravelMate, an expert multilingual travel planner.

Create a realistic {data.duration}-day itinerary.

=====================================================
TRAVELER PROFILE
=====================================================

Destination:
{data.destination}

Travel Date:
{data.travelDate}

Budget:
{data.currencySymbol}{data.budget}

Language:
{data.language}

Who's Travelling:
{data.travelType}

Trip Style:
{data.tripStyle}

Child Under 12:
{"Yes" if data.kidsUnder12 else "No"}

Interests:
{interests}


=====================================================
OUTPUT FORMAT
=====================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "destination": "{data.destination}",
    "duration": {data.duration},
    "estimated_total_cost": 0,
    "destination_overview": "120-180 word overview.",
    "days": [
        {{
            "day": 1,
            "title": "Arrival & City Highlights",
            "introduction": "Short introduction for this day.",
            "activities": [
                {{
                    "time": "8:00 AM",
                    "place": "Real Tourist Attraction",
                    "category": "Landmark",
                    "cost": 20,
                    "duration": "2 hrs",
                    "description": "Practical description.",
                    "best_time": "Morning",
                    "tip": "Useful travel tip.",
                    "nearby_food": "Nearby food option",
                    "popularity": "Must Visit"
                }}
            ]
        }}
    ]
}}


=====================================================
GENERAL RULES
=====================================================

1. Write everything in {data.language}.

2. Use real tourist attractions.

3. Do NOT invent attractions.

4. Keep landmark names unchanged when appropriate.

5. Include breakfast, lunch and dinner suggestions.

6. Stay within the provided budget.

7. Use numeric costs only.

8. Use the currency represented by {data.currencySymbol}.

9. Add a 120-180 word destination overview.

10. Add an introduction for every day.

11. Make descriptions practical.

12. Include nearby food suggestions.

13. Include the best visiting time.

14. Include useful travel tips.

15. Do not return markdown.

16. Do not return ```json.

17. Return ONLY the JSON object.

18. Group nearby attractions together.

19. Avoid impossible travel schedules.

20. Respect the travel date and budget.


=====================================================
TRIP STYLE
=====================================================

Relaxed:

Around 3 activities per day.

Give the traveler enough rest time.


Balanced:

Around 4 activities per day.

Mix sightseeing with breaks.


Packed:

Around 5-6 activities per day.

Include more attractions while keeping
the schedule realistic.


=====================================================
TRAVEL TYPE
=====================================================

Solo:

Focus on safe routes, cafes and walking.


Couple:

Include romantic restaurants,
sunset spots and scenic viewpoints.


Family:

Use family-friendly restaurants,
easier schedules and child-friendly places.


Friends:

Include adventure, nightlife and
social activities.


=====================================================
CHILDREN
=====================================================

If Child Under 12 is Yes:

- Include at least one child-friendly activity every day.
- Avoid excessive walking.
- Include rest breaks.
- Prefer family-friendly locations.
- Avoid activities unsuitable for children.
"""


    # =====================================================
    # GEMINI REQUEST WITH RETRIES
    # =====================================================

    response = None

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        try:

            print("\n----------------------------------------")
            print(
                f"Sending request to Gemini "
                f"(attempt {attempt}/{max_attempts})"
            )
            print("Model: gemini-3.6-flash")
            print("----------------------------------------")

            response = client.models.generate_content(

                model="gemini-3.6-flash",

                contents=prompt,

                config=types.GenerateContentConfig(

                    response_mime_type="application/json",

                    response_schema=TravelItinerary,

                ),
            )

            print("Gemini response received.")

            break

        # =================================================
        # GEMINI SERVER ERROR
        # =================================================

        except ServerError as e:

            print("\n========================================")
            print("GEMINI SERVER ERROR")
            print("========================================")
            print(repr(e))

            if attempt < max_attempts:

                wait_time = attempt * 3

                print(
                    f"Gemini is temporarily busy."
                )

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            else:

                raise HTTPException(
                    status_code=503,
                    detail=(
                        "Gemini is currently experiencing "
                        "high demand. Please try again "
                        "in a few seconds."
                    ),
                )

        # =================================================
        # GEMINI CLIENT ERROR
        # =================================================

        except ClientError as e:

            print("\n========================================")
            print("GEMINI CLIENT ERROR")
            print("========================================")
            print(repr(e))

            error_message = str(e)

            # ---------------------------------------------
            # QUOTA
            # ---------------------------------------------

            if "RESOURCE_EXHAUSTED" in error_message:

                raise HTTPException(
                    status_code=429,
                    detail=(
                        "Gemini API quota has been exceeded. "
                        "Please try again later."
                    ),
                )

            # ---------------------------------------------
            # MODEL NOT FOUND
            # ---------------------------------------------

            if "NOT_FOUND" in error_message:

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "The configured Gemini model is "
                        "not available."
                    ),
                )

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Gemini client error: "
                    f"{error_message}"
                ),
            )

        # =================================================
        # UNEXPECTED ERROR
        # =================================================

        except Exception as e:

            print("\n========================================")
            print("GEMINI UNEXPECTED ERROR")
            print("========================================")
            print(repr(e))

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Unexpected Gemini error: "
                    f"{str(e)}"
                ),
            )


    # =====================================================
    # NO RESPONSE
    # =====================================================

    if response is None:

        raise HTTPException(
            status_code=503,
            detail=(
                "Unable to generate itinerary "
                "at this time."
            ),
        )


    # =====================================================
    # EMPTY RESPONSE
    # =====================================================

    if not response.text:

        print(
            "Gemini returned an empty response."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "The AI service returned an "
                "empty response."
            ),
        )


    # =====================================================
    # PARSE JSON
    # =====================================================

    try:

        itinerary = json.loads(
            response.text
        )

    except json.JSONDecodeError as e:

        print("\n========================================")
        print("JSON PARSE ERROR")
        print("========================================")

        print(repr(e))

        print("\nGEMINI RESPONSE:")
        print(response.text)

        raise HTTPException(
            status_code=500,
            detail=(
                "The AI service returned invalid "
                "itinerary data."
            ),
        )


    # =====================================================
    # ADD REQUEST METADATA
    # =====================================================

    itinerary["travel_date"] = (
        data.travelDate
    )

    itinerary["budget"] = (
        data.budget
    )

    itinerary["interests"] = (
        data.interests
    )

    itinerary["language"] = (
        data.language
    )

    itinerary["currencySymbol"] = (
        data.currencySymbol
    )

    itinerary["travelType"] = (
        data.travelType
    )

    itinerary["tripStyle"] = (
        data.tripStyle
    )

    itinerary["kidsUnder12"] = (
        data.kidsUnder12
    )


    # =====================================================
    # SUCCESS
    # =====================================================

    print("\n========================================")
    print("ITINERARY GENERATED SUCCESSFULLY")
    print("========================================")

    print(
        "Destination:",
        itinerary.get("destination")
    )

    print(
        "Days:",
        len(itinerary.get("days", []))
    )

    print(
        "Estimated Cost:",
        itinerary.get("estimated_total_cost")
    )

    print("========================================\n")


    return itinerary