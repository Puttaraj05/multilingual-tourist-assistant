from backend.services.geoapify_service import (
    geocode_location,
    get_nearby_places,
    normalize_category
)

from backend.utils.distance import calculate_distance
from backend.utils.navigation import create_navigation_url


async def get_recommendations(
    latitude: float | None,
    longitude: float | None,
    location: str | None,
    category: str,
    radius: float,
    max_results: int
) -> dict:

    search_location = None

    # Use the user's coordinates when searching for places nearby.

    if latitude is not None and longitude is not None:

        search_latitude = latitude
        search_longitude = longitude

        search_location = "Near Me"

    # Otherwise, convert the provided location name into coordinates.

    else:

        location_data = await geocode_location(
            location
        )

        search_latitude = location_data["latitude"]
        search_longitude = location_data["longitude"]

        search_location = location_data["display_name"]

    # Normalize the requested category before searching for places.

    normalized_category = None

    if category and category.lower() != "all":
        normalized_category = normalize_category(category)

    # Fetch more places than needed so results outside the requested radius
    # can be filtered before returning the final recommendations.

    fetch_limit = max(
        max_results * 4,
        20
    )

    places = await get_nearby_places(
        latitude=search_latitude,
        longitude=search_longitude,
        category=normalized_category,
        radius_km=radius,
        limit=fetch_limit
    )

    recommendations = []

    # Calculate the distance and build the response for each nearby place.

    for place in places:

        distance_km = calculate_distance(
            search_latitude,
            search_longitude,
            place["latitude"],
            place["longitude"]
        )

        if distance_km > radius:
            continue

        recommendations.append(
            {
                "name": place["name"],
                "category": place["category"],

                "latitude": place["latitude"],
                "longitude": place["longitude"],

                "rating": place.get("rating"),

                "opening_time": place.get(
                    "opening_time"
                ),

                "closing_time": place.get(
                    "closing_time"
                ),

                "address": place.get(
                    "address"
                ),

                "distance_km": round(
                    distance_km,
                    2
                ),

                "navigation_url": create_navigation_url(
                    search_latitude,
                    search_longitude,
                    place["latitude"],
                    place["longitude"]
                ),

                "source_url": place.get(
                    "source_url"
                )
            }
        )

    # Sort recommendations from the closest place to the farthest.

    recommendations.sort(
        key=lambda item: item["distance_km"]
    )

    recommendations = recommendations[
        :max_results
    ]

    return {
        "search_latitude": search_latitude,
        "search_longitude": search_longitude,
        "search_location": search_location,
        "recommendations": recommendations,
        "count": len(recommendations)
    }