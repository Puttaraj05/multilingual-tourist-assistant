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


def normalize_category(category: str | None) -> str | None:

    if not category:
        return None

    return category.lower().strip()


def get_geoapify_category(category: str | None) -> str | None:

    normalized = normalize_category(category)

    if not normalized or normalized == "all":
        return None

    return CATEGORY_MAPPING.get(normalized)


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
    category: str | None,
    radius_km: float,
    limit: int = 20
) -> list[dict]:

    normalized_category = normalize_category(category)

    radius_meters = int(radius_km * 1000)

    params = {
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

    # =====================================================
    # CATEGORY FILTER
    # =====================================================

    if normalized_category and normalized_category != "all":

        geoapify_category = get_geoapify_category(
            normalized_category
        )

        # Unsupported specific category
        if not geoapify_category:
            return []

        params["categories"] = geoapify_category

    else:

        # =================================================
        # ALL PLACES
        # =================================================
        # Geoapify needs actual category names rather than
        # a generic "all" value. Request several categories
        # separately and combine the results.

        all_categories = [
            "catering.restaurant",
            "catering.cafe",
            "accommodation.hotel",
            "tourism.sights",
            "entertainment.museum",
            "leisure.park",
            "commercial.shopping_mall"
        ]

        all_places = []

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            for geoapify_category in all_categories:

                category_params = {
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

                response = await client.get(
                    PLACES_URL,
                    params=category_params
                )

                response.raise_for_status()

                data = response.json()

                for feature in data.get("features", []):
                    all_places.append(feature)

        # Remove duplicate places
        unique_places = {}
        for feature in all_places:

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

            name = (
                properties.get("name")
                or properties.get("address_line1")
            )

            if not name:
                continue

            key = (
                str(name).strip().lower(),
                round(float(coordinates[0]), 5),
                round(float(coordinates[1]), 5)
            )

            unique_places[key] = feature

        features = list(unique_places.values())

    # =====================================================
    # SPECIFIC CATEGORY REQUEST
    # =====================================================

    if normalized_category and normalized_category != "all":

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            response = await client.get(
                PLACES_URL,
                params=params
            )

            response.raise_for_status()

            data = response.json()

        features = data.get(
            "features",
            []
        )

    # =====================================================
    # BUILD PLACES
    # =====================================================

    places = []

    for feature in features:

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

        raw_category = (
            properties.get("category")
            or properties.get("categories")
            or "place"
        )

        if isinstance(raw_category, list):
            place_category = (
                raw_category[-1]
                if raw_category
                else "place"
            )
        else:
            place_category = str(raw_category)

        if (
            normalized_category
            and normalized_category != "all"
        ):
            place_category = normalized_category

        places.append(
            {
                "name": name,

                "category": place_category,

                "latitude": float(
                    place_latitude
                ),

                "longitude": float(
                    place_longitude
                ),

                "rating": properties.get(
                    "rating"
                ),

                "opening_time": properties.get(
                    "opening_hours"
                ),

                "closing_time": None,

                "address": address,

                "source_url": properties.get(
                    "datasource",
                    {}
                ).get("url")
                if isinstance(
                    properties.get("datasource"),
                    dict
                )
                else None
            }
        )

    return places
