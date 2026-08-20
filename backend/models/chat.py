from typing import List, Optional

from pydantic import BaseModel, Field


# Define the data received from the chat request.
class ChatRequest(BaseModel):

    message: str

    language: str = "English"

    session_id: Optional[str] = None


# Define the structure of a tourist attraction.
class Attraction(BaseModel):

    name: str

    description: str

    category: Optional[str] = None

    best_time: Optional[str] = None

    estimated_time: Optional[str] = None

    location: Optional[str] = None


# Define the structure of a food recommendation.
class FoodRecommendation(BaseModel):

    name: str

    description: str

    type: Optional[str] = None

    must_try: Optional[bool] = None

    best_for: Optional[str] = None

    approximate_cost: Optional[str] = None


# Define the available transportation options.
class TransportOption(BaseModel):

    mode: str

    description: str

    best_for: Optional[str] = None

    approximate_cost: Optional[str] = None

    travel_time: Optional[str] = None


# Define a useful travel tip.
class TravelTip(BaseModel):

    title: str

    description: str


# Define one activity in the itinerary.
class ItineraryActivity(BaseModel):

    time: Optional[str] = None

    activity: str

    location: Optional[str] = None

    duration: Optional[str] = None

    description: Optional[str] = None

    estimated_cost: Optional[str] = None


# Define the activities and details for one itinerary day.
class ItineraryDay(BaseModel):

    day: int

    title: str

    summary: Optional[str] = None

    # Store activities for each part of the day.
    morning: List[ItineraryActivity] = Field(
        default_factory=list
    )

    afternoon: List[ItineraryActivity] = Field(
        default_factory=list
    )

    evening: List[ItineraryActivity] = Field(
        default_factory=list
    )

    night: List[ItineraryActivity] = Field(
        default_factory=list
    )

    activities: List[str] = Field(
        default_factory=list
    )

    meals: List[str] = Field(
        default_factory=list
    )

    accommodation: Optional[str] = None

    travel_notes: Optional[str] = None

    estimated_cost: Optional[str] = None

    distance: Optional[str] = None


# Define the complete response returned by the chat API.
class ChatResponse(BaseModel):

    success: bool

    session_id: str

    language: str

    message: str

    destination: Optional[str] = None

    trip_overview: Optional[str] = None

    trip_duration: Optional[str] = None

    travel_style: Optional[str] = None

    best_time_to_visit: Optional[str] = None

    estimated_budget: Optional[str] = None

    attractions: List[Attraction] = Field(
        default_factory=list
    )

    food: List[FoodRecommendation] = Field(
        default_factory=list
    )

    transportation: List[TransportOption] = Field(
        default_factory=list
    )

    tips: List[TravelTip] = Field(
        default_factory=list
    )

    itinerary: List[ItineraryDay] = Field(
        default_factory=list
    )