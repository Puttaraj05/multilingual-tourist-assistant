from fastapi import APIRouter, HTTPException

from backend.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse
)

from backend.services.recommendation_service import (
    get_recommendations
)


router = APIRouter(
    prefix="/api",
    tags=["Recommendations"]
)


@router.post(
    "/recommendations",
    response_model=RecommendationResponse
)
async def recommend_places(
    request: RecommendationRequest
):

    try:

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

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Recommendation service error: "
                f"{str(error)}"
            )
        )