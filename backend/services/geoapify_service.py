import httpx

from backend.config import GEOAPIFY_API_KEY


GEOCODING_URL = (
    "https://api.geoapify.com/v1/geocode/search"
)

PLACES_URL = (
    "https://api.geoapify.com/v2/places"
)


CATEGORY_MAPPING = {

    # Food
    "restaurant": "catering.restaurant",
    "restaurants": "catering.restaurant",

    "cafe": "catering.cafe",
    "cafes": "catering.cafe",

    "fast_food": "catering.fast_food",
    "fast food": "catering.fast_food",

    "bar": "catering.bar",

    # Accommodation
    "hotel": "accommodation.hotel",
    "hotels": "accommodation.hotel",

    "hostel": "accommodation.hostel",
    "hostels": "accommodation.hostel",

    "guest_house": "accommodation.guest_house",
    "guest house": "accommodation.guest_house",

    # Tourism
    "attraction": "tourism.sights",
    "attractions": "tourism.sights",
    "tourist attraction": "tourism.sights",

    "museum": "entertainment.museum",
    "museums": "entertainment.museum",

    # Recreation
    "park": "leisure.park",
    "parks": "leisure.park",

    # Shopping
    "shopping": "commercial.shopping_mall",
    "shopping mall": "commercial.shopping_mall",
    "mall": "commercial.shopping_mall",

    "supermarket": "commercial.supermarket",

    # Healthcare
    "hospital": "healthcare.hospital",
    "hospitals": "healthcare.hospital",

    "pharmacy": "healthcare.pharmacy",
    "medical": "healthcare.pharmacy",

    # Financial
    "bank": "service.financial.bank",
    "banks": "service.financial.bank",

    "atm": "service.financial.atm",

    # Transport
    "fuel": "service.vehicle.fuel",
    "petrol": "service.vehicle.fuel",
    "petrol station": "service.vehicle.fuel",

    "parking": "service.vehicle.parking"
}


def normalize_category(category: str) -> str:
    return category.lower().strip()


def get_geoapify_category(category: str) -> str | None:

    category = normalize_category(category)

    return CATEGORY_MAPPING.get(category)


async def geocode_location(location: str) -> dict:

    params = {
        "text": location,
        "format": "json",
        "limit": 1,
        "apiKey": GEOAPIFY_API_KEY
    }

    async with httpx.AsyncClient(
        timeout=20.0
    ) as client:

        response = await client.get(
            GEOCODING_URL,
            params=params
        )

        response.raise_for_status()

        data = response.json()

    results = data.get("results", [])

    if not results:
        raise ValueError(
            f"Location not found: {location}"
        )

    result = results[0]

    return {
        "latitude": float(result["lat"]),
        "longitude": float(result["lon"]),
        "display_name": (
            result.get("formatted")
            or location
        )
    }


async def get_nearby_places(
    latitude: float,
    longitude: float,
    category: str,
    radius_km: float,
    limit: int = 20
) -> list[dict]:

    geoapify_category = get_geoapify_category(
        category
    )

    # REC-08
    # Unsupported category returns no results
    if not geoapify_category:
        return []

    radius_meters = int(radius_km * 1000)

    params = {
        "categories": geoapify_category,

        "filter": (
            f"circle:{longitude},"
            f"{latitude},"
            f"{radius_meters}"
        ),

        "bias": (
            f"proximity:{longitude},"
            f"{latitude}"
        ),

        "limit": limit,

        "apiKey": GEOAPIFY_API_KEY
    }

    async with httpx.AsyncClient(
        timeout=30.0
    ) as client:

        response = await client.get(
            PLACES_URL,
            params=params
        )

        response.raise_for_status()

        data = response.json()

    places = []

    for feature in data.get("features", []):

        properties = feature.get(
            "properties",
            {}
        )

        geometry = feature.get(
            "geometry",
            {}
        )

        coordinates = geometry.get(
            "coordinates",
            []
        )

        if len(coordinates) < 2:
            continue

        place_longitude = coordinates[0]
        place_latitude = coordinates[1]

        name = (
            properties.get("name")
            or properties.get("address_line1")
        )

        if not name:
            continue

        address_parts = [
            properties.get("address_line1"),
            properties.get("address_line2")
        ]

        address = ", ".join(
            str(part)
            for part in address_parts
            if part
        ) or None

        places.append(
            {
                "name": name,
                "category": normalize_category(category),

                "latitude": float(place_latitude),
                "longitude": float(place_longitude),

                "rating": properties.get("rating"),

                "opening_time": properties.get(
                    "opening_hours"
                ),

                "closing_time": None,

                "address": address,

                "source_url": properties.get(
                    "website"
                )
            }
        )

    return places