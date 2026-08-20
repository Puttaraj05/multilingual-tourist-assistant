from fastapi import APIRouter, HTTPException

from backend.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse
)

from backend.services.recommendation_service import (
    get_recommendations
)


# Define the API route for place recommendations.
router = APIRouter(
    prefix="/api",
    tags=["Recommendations"]
)


# Return nearby places based on the user's search criteria.
@router.post(
    "/recommendations",
    response_model=RecommendationResponse
)
async def recommend_places(
    request: RecommendationRequest
):

    try:

        # Fetch recommendations using the requested location and filters.
        result = await get_recommendations(
            latitude=request.latitude,
            longitude=request.longitude,
            location=request.location,
            category=request.category,
            radius=request.radius,
            max_results=request.max_results
        )

        return result

    except ValueError as error:

        # Return a not-found response for invalid or unavailable locations.
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except HTTPException:
        raise

    except Exception as error:

        # Return a server error if recommendation lookup fails unexpectedly.
        raise HTTPException(
            status_code=500,
            detail=(
                f"Recommendation service error: "
                f"{str(error)}"
            )
        )