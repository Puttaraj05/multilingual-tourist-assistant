import httpx


OVERPASS_URL = (
    "https://overpass-api.de/api/interpreter"
)


CATEGORY_QUERIES = {
    "restaurant": [
        'node["amenity"="restaurant"]',
        'way["amenity"="restaurant"]',
        'relation["amenity"="restaurant"]'
    ],

    "hotel": [
        'node["tourism"="hotel"]',
        'way["tourism"="hotel"]',
        'relation["tourism"="hotel"]'
    ],

    "attraction": [
        'node["tourism"="attraction"]',
        'way["tourism"="attraction"]',
        'relation["tourism"="attraction"]',
        'node["tourism"="museum"]',
        'way["tourism"="museum"]',
        'node["historic"]',
        'way["historic"]'
    ]
}


def normalize_category(category: str) -> str:

    category = category.lower().strip()

    mapping = {
        "restaurants": "restaurant",
        "food": "restaurant",

        "hotels": "hotel",
        "stay": "hotel",

        "tourist attraction": "attraction",
        "tourist_attraction": "attraction",
        "attractions": "attraction",
        "places to visit": "attraction",
        "sightseeing": "attraction"
    }

    return mapping.get(category, category)


async def find_nearby_places(
    latitude: float,
    longitude: float,
    category: str,
    radius_km: float
) -> list[dict]:

    category = normalize_category(category)

    if category not in CATEGORY_QUERIES:
        return []

    radius_meters = int(radius_km * 1000)

    queries = CATEGORY_QUERIES[category]

    query_parts = []

    for query in queries:

        query_parts.append(
            f'{query}(around:{radius_meters},'
            f'{latitude},{longitude});'
        )

    overpass_query = f"""
    [out:json][timeout:25];

    (
        {" ".join(query_parts)}
    );

    out center tags;
    """

    async with httpx.AsyncClient(
        timeout=40.0
    ) as client:

        response = await client.post(
            OVERPASS_URL,
            data={"data": overpass_query}
        )

        response.raise_for_status()

        data = response.json()

    places = []

    for element in data.get("elements", []):

        tags = element.get("tags", {})

        name = tags.get("name")

        if not name:
            continue

        # Nodes contain lat/lon directly
        if (
            "lat" in element
            and "lon" in element
        ):
            place_latitude = element["lat"]
            place_longitude = element["lon"]

        # Ways/relations may contain center
        elif "center" in element:
            place_latitude = element[
                "center"
            ].get("lat")

            place_longitude = element[
                "center"
            ].get("lon")

        else:
            continue

        if (
            place_latitude is None
            or place_longitude is None
        ):
            continue

        address_parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:suburb"),
            tags.get("addr:city")
        ]

        address = ", ".join(
            str(part)
            for part in address_parts
            if part
        )

        places.append(
            {
                "name": name,
                "category": category,
                "latitude": float(place_latitude),
                "longitude": float(place_longitude),
                "address": (
                    address
                    if address
                    else None
                ),
                "osm_id": element.get("id")
            }
        )

    return places