from typing import Optional

from pydantic import BaseModel, Field, model_validator


class RecommendationRequest(BaseModel):
    # Option 1: Near Me
    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180
    )

    # Option 2: Search Near a typed location
    location: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=200
    )

    category: str = Field(
        default="all"
    )

    radius: float = Field(
        default=5.0,
        gt=0,
        le=50
    )

    max_results: int = Field(
        default=5,
        gt=0,
        le=20
    )

    @model_validator(mode="after")
    def validate_location(self):

        has_latitude = self.latitude is not None
        has_longitude = self.longitude is not None

        has_location = (
            self.location is not None
            and self.location.strip() != ""
        )

        # Latitude and longitude must both exist
        if has_latitude != has_longitude:
            raise ValueError(
                "Both latitude and longitude must be provided together."
            )

        # User must select Near Me OR type a location
        if not (
            has_latitude and has_longitude
        ) and not has_location:

            raise ValueError(
                "Provide either coordinates for Near Me "
                "or type a location."
            )

        return self


class Recommendation(BaseModel):
    name: str
    category: str

    latitude: float
    longitude: float

    rating: Optional[float] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None

    address: Optional[str] = None

    distance_km: float

    navigation_url: str
    source_url: Optional[str] = None


class RecommendationResponse(BaseModel):
    search_latitude: float
    search_longitude: float
    search_location: Optional[str] = None

    recommendations: list[Recommendation]
    count: int