from typing import List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    language: str = "English"
    session_id: Optional[str] = None


class Attraction(BaseModel):
    name: str
    description: str
    category: Optional[str] = None


class FoodRecommendation(BaseModel):
    name: str
    description: str
    type: Optional[str] = None


class TransportOption(BaseModel):
    mode: str
    description: str


class TravelTip(BaseModel):
    title: str
    description: str


class ItineraryDay(BaseModel):
    day: int
    title: str
    activities: List[str]


class ChatResponse(BaseModel):
    success: bool
    session_id: str
    language: str

    message: str

    destination: Optional[str] = None

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