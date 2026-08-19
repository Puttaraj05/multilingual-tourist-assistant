from datetime import datetime, timezone
from math import radians, sin, cos, sqrt, atan2
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from pymongo.errors import PyMongoError

from backend.database.mongodb import (
    client,
    emergency_contacts_collection,
    incidents_collection,
    sos_events_collection,
    locations_collection,
)


router = APIRouter(
    prefix="/api",
    tags=["Emergency AI"],
)


# =========================================================
# EMERGENCY CONTACT DATA
# =========================================================

CONTACTS = [
    {
        "country_code": "IN",
        "country_name": "India",
        "service": "Unified Emergency",
        "number": "112",
        "description": "Pan-India emergency number.",
    },
    {
        "country_code": "IN",
        "country_name": "India",
        "service": "Police",
        "number": "100",
        "description": "Police emergency.",
    },
    {
        "country_code": "IN",
        "country_name": "India",
        "service": "Ambulance",
        "number": "108",
        "description": "Emergency medical response.",
    },
    {
        "country_code": "IN",
        "country_name": "India",
        "service": "Fire",
        "number": "101",
        "description": "Fire emergency.",
    },

    {
        "country_code": "AE",
        "country_name": "United Arab Emirates",
        "service": "Police",
        "number": "999",
        "description": "Police emergency.",
    },
    {
        "country_code": "AE",
        "country_name": "United Arab Emirates",
        "service": "Ambulance",
        "number": "998",
        "description": "Ambulance emergency.",
    },
    {
        "country_code": "AE",
        "country_name": "United Arab Emirates",
        "service": "Fire",
        "number": "997",
        "description": "Civil Defence / fire emergency.",
    },

    {
        "country_code": "US",
        "country_name": "United States",
        "service": "Unified Emergency",
        "number": "911",
        "description": "Police, fire and medical emergency.",
    },

    {
        "country_code": "GB",
        "country_name": "United Kingdom",
        "service": "Unified Emergency",
        "number": "999",
        "description": "Police, fire and ambulance emergency.",
    },
    {
        "country_code": "GB",
        "country_name": "United Kingdom",
        "service": "Alternative Emergency",
        "number": "112",
        "description": "Alternative emergency number.",
    },
]


# =========================================================
# UTILITIES
# =========================================================

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def get_contacts(country_code: str):

    code = (country_code or "IN").upper()

    try:

        contacts = list(
            emergency_contacts_collection.find(
                {"country_code": code},
                {"_id": 0},
            )
        )

        if contacts:
            return contacts

    except PyMongoError as error:

        print("MongoDB unavailable for emergency contacts:")
        print(error)

    return [
        contact
        for contact in CONTACTS
        if contact["country_code"] == code
    ]


# =========================================================
# DISTANCE CALCULATION
# =========================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2,
):
    """
    Calculate distance between two GPS coordinates
    using the Haversine formula.

    Returns distance in kilometers.
    """

    earth_radius_km = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return earth_radius_km * c


# =========================================================
# OPENSTREETMAP / OVERPASS
# =========================================================

def search_nearby_osm(
    latitude: float,
    longitude: float,
    service_type: str,
    radius: int = 5000,
):
    """
    Search nearby real-world services using OpenStreetMap
    Overpass API.

    radius = meters.
    """

    service_type = service_type.lower().strip()

    filters = {

        "hospital": """
            node["amenity"="hospital"](around:{radius},{lat},{lon});
            way["amenity"="hospital"](around:{radius},{lat},{lon});
            relation["amenity"="hospital"](around:{radius},{lat},{lon});
        """,

        "police": """
            node["amenity"="police"](around:{radius},{lat},{lon});
            way["amenity"="police"](around:{radius},{lat},{lon});
            relation["amenity"="police"](around:{radius},{lat},{lon});
        """,

        "fire station": """
            node["amenity"="fire_station"](around:{radius},{lat},{lon});
            way["amenity"="fire_station"](around:{radius},{lat},{lon});
            relation["amenity"="fire_station"](around:{radius},{lat},{lon});
        """,

        "ambulance": """
            node["emergency"="ambulance_station"](around:{radius},{lat},{lon});
            way["emergency"="ambulance_station"](around:{radius},{lat},{lon});
            relation["emergency"="ambulance_station"](around:{radius},{lat},{lon});
        """,
    }

    query_template = filters.get(service_type)

    if not query_template:

        # Ambulance services are sometimes mapped as
        # healthcare facilities.
        query_template = filters["hospital"]

    query = f"""
    [out:json][timeout:20];

    (
        {query_template.format(
            radius=radius,
            lat=latitude,
            lon=longitude
        )}
    );

    out center tags;
    """

    url = "https://overpass-api.de/api/interpreter"

    try:

        request = Request(
            url,
            data=query.encode("utf-8"),
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "TravelMate-Emergency-App/1.0",
            },
            method="POST",
        )

        with urlopen(
            request,
            timeout=25,
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        return data.get("elements", [])

    except Exception as error:

        print("OpenStreetMap search failed:")
        print(error)

        return []


# =========================================================
# FORMAT OSM RESULT
# =========================================================

def format_osm_results(
    elements,
    user_lat,
    user_lon,
    service_type,
):

    results = []

    for element in elements:

        tags = element.get("tags", {})

        # Nodes
        lat = element.get("lat")
        lon = element.get("lon")

        # Ways / relations
        if lat is None or lon is None:

            center = element.get("center", {})

            lat = center.get("lat")
            lon = center.get("lon")

        # IMPORTANT:
        # Never return an incomplete location.
        if lat is None or lon is None:
            continue

        try:

            lat = float(lat)
            lon = float(lon)

        except (TypeError, ValueError):

            continue

        name = (
            tags.get("name")
            or tags.get("official_name")
            or f"Nearby {service_type.title()}"
        )

        address_parts = []

        for key in [
            "addr:housenumber",
            "addr:street",
            "addr:city",
            "addr:postcode",
        ]:

            value = tags.get(key)

            if value:
                address_parts.append(value)

        address = ", ".join(address_parts)

        distance = calculate_distance(
            user_lat,
            user_lon,
            lat,
            lon,
        )

        results.append(
            {
                "name": name,
                "service": service_type.title(),
                "latitude": lat,
                "longitude": lon,
                "distance_km": round(
                    distance,
                    2,
                ),
                "address": address,
                "phone": (
                    tags.get("phone")
                    or tags.get("contact:phone")
                ),
                "website": (
                    tags.get("website")
                    or tags.get("contact:website")
                ),
                "maps_url": (
                    "https://www.google.com/maps/dir/?"
                    + urlencode(
                        {
                            "api": "1",
                            "destination": (
                                f"{lat},{lon}"
                            ),
                        }
                    )
                ),
            }
        )

    results.sort(
        key=lambda item: item["distance_km"]
    )

    return results


# =========================================================
# PYDANTIC MODELS
# =========================================================

class LocationRequest(BaseModel):

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
    )

    accuracy: float | None = Field(
        default=None,
        ge=0,
    )

    countryCode: str | None = None


class SOSRequest(BaseModel):

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
    )

    accuracy: float | None = Field(
        default=None,
        ge=0,
    )

    countryCode: str | None = None


class IncidentRequest(BaseModel):

    type: str

    description: str = ""

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90,
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180,
    )

    accuracy: float | None = Field(
        default=None,
        ge=0,
    )

    countryCode: str | None = None


# =========================================================
# REAL GPS NEARBY SEARCH
# =========================================================

@router.get("/nearby-emergency")
def nearby_emergency(
    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
    ),

    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
    ),

    type: str = Query(
        default="Hospital",
    ),

    radius: int = Query(
        default=5000,
        ge=500,
        le=20000,
    ),
):

    service_type = type.lower().strip()

    allowed = {
        "hospital",
        "police",
        "ambulance",
        "fire station",
    }

    if service_type not in allowed:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid emergency type. "
                "Use Hospital, Police, Ambulance "
                "or Fire Station."
            ),
        )

    print(
        f"Searching nearby {service_type}: "
        f"{latitude}, {longitude}"
    )

    elements = search_nearby_osm(
        latitude=latitude,
        longitude=longitude,
        service_type=service_type,
        radius=radius,
    )

    results = format_osm_results(
        elements,
        latitude,
        longitude,
        service_type,
    )

    return {
        "success": True,

        "location": {
            "latitude": latitude,
            "longitude": longitude,
        },

        "type": service_type.title(),

        "radius_km": radius / 1000,

        "count": len(results),

        "results": results[:20],
    }


# =========================================================
# COUNTRIES
# =========================================================

@router.get("/countries")
def countries():

    try:

        countries_data = list(
            emergency_contacts_collection.aggregate(
                [
                    {
                        "$group": {
                            "_id": "$country_code",
                            "name": {
                                "$first": "$country_name"
                            },
                        }
                    },
                    {
                        "$sort": {
                            "name": 1,
                        }
                    },
                ]
            )
        )

        if countries_data:

            return [
                {
                    "code": item["_id"],
                    "name": item["name"],
                }
                for item in countries_data
            ]

    except PyMongoError:
        pass

    seen = {}

    for contact in CONTACTS:

        seen[
            contact["country_code"]
        ] = contact["country_name"]

    return [
        {
            "code": code,
            "name": name,
        }
        for code, name in sorted(
            seen.items(),
            key=lambda item: item[1],
        )
    ]


# =========================================================
# EMERGENCY CONTACTS
# =========================================================

@router.get("/emergency-contacts")
def emergency_contacts(
    country: str = Query(
        default="IN",
        min_length=2,
        max_length=2,
    )
):

    code = country.upper()

    return {
        "success": True,
        "country": code,
        "contacts": get_contacts(code),
    }


# =========================================================
# SAVE LOCATION
# =========================================================

@router.post("/location")
def save_location(
    location: LocationRequest,
):

    country = (
        location.countryCode or "IN"
    ).upper()

    document = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "accuracy": location.accuracy,
        "country_code": country,
        "created_at": now_iso(),
    }

    try:

        result = locations_collection.insert_one(
            document
        )

        return {
            "success": True,
            "locationId": str(
                result.inserted_id
            ),
            "latitude": location.latitude,
            "longitude": location.longitude,
            "accuracy": location.accuracy,
        }

    except PyMongoError as error:

        print("Location save failed:")
        print(error)

        return {
            "success": False,
            "message": (
                "Location received but "
                "could not be saved."
            ),
            "latitude": location.latitude,
            "longitude": location.longitude,
        }


# =========================================================
# SOS
# =========================================================

@router.post("/sos")
def create_sos(
    sos: SOSRequest,
):

    country = (
        sos.countryCode or "IN"
    ).upper()

    document = {
        "latitude": sos.latitude,
        "longitude": sos.longitude,
        "accuracy": sos.accuracy,
        "country_code": country,
        "status": "logged",
        "created_at": now_iso(),
    }

    try:

        result = sos_events_collection.insert_one(
            document
        )

        event_id = str(
            result.inserted_id
        )

    except PyMongoError as error:

        print("SOS MongoDB save failed:")
        print(error)

        event_id = None

    return {
        "success": True,
        "eventId": event_id,
        "message": (
            "SOS event received. "
            "Call the local emergency service immediately."
        ),
        "contacts": get_contacts(country),
    }


# =========================================================
# CREATE INCIDENT
# =========================================================

@router.post("/incidents")
def create_incident(
    incident: IncidentRequest,
):

    allowed = {
        "medical",
        "lost",
        "theft",
        "unsafe",
        "document",
        "other",
    }

    if incident.type not in allowed:

        raise HTTPException(
            status_code=400,
            detail="Invalid incident type.",
        )

    country = (
        incident.countryCode or "IN"
    ).upper()

    document = {
        "type": incident.type,
        "description": (
            incident.description or ""
        )[:2000],
        "latitude": incident.latitude,
        "longitude": incident.longitude,
        "accuracy": incident.accuracy,
        "country_code": country,
        "created_at": now_iso(),
    }

    try:

        result = incidents_collection.insert_one(
            document
        )

        return {
            "success": True,
            "incidentId": str(
                result.inserted_id
            ),
            "message": (
                "Incident saved to your "
                "TravelMate support log."
            ),
        }

    except PyMongoError as error:

        print("Incident MongoDB save failed:")
        print(error)

        return {
            "success": True,
            "incidentId": None,
            "message": (
                "Incident received, but "
                "database storage is unavailable."
            ),
        }


# =========================================================
# GET INCIDENTS
# =========================================================

@router.get("/incidents")
def incidents():

    try:

        documents = list(
            incidents_collection
            .find({})
            .sort(
                "created_at",
                -1,
            )
            .limit(100)
        )

    except PyMongoError as error:

        return {
            "success": False,
            "incidents": [],
            "error": str(error),
        }

    return [
        {
            "id": str(
                document["_id"]
            ),
            "type": document.get("type"),
            "description": document.get(
                "description",
                "",
            ),
            "latitude": document.get(
                "latitude"
            ),
            "longitude": document.get(
                "longitude"
            ),
            "accuracy": document.get(
                "accuracy"
            ),
            "country_code": document.get(
                "country_code"
            ),
            "created_at": document.get(
                "created_at"
            ),
        }
        for document in documents
    ]


# =========================================================
# GET SOS EVENTS
# =========================================================

@router.get("/sos")
def sos_events():

    try:

        documents = list(
            sos_events_collection
            .find({})
            .sort(
                "created_at",
                -1,
            )
            .limit(100)
        )

    except PyMongoError as error:

        return {
            "success": False,
            "events": [],
            "error": str(error),
        }

    return [
        {
            "id": str(
                document["_id"]
            ),
            "latitude": document.get(
                "latitude"
            ),
            "longitude": document.get(
                "longitude"
            ),
            "accuracy": document.get(
                "accuracy"
            ),
            "country_code": document.get(
                "country_code"
            ),
            "status": document.get(
                "status"
            ),
            "created_at": document.get(
                "created_at"
            ),
        }
        for document in documents
    ]


# =========================================================
# GET SHARED LOCATIONS
# =========================================================

@router.get("/locations")
def locations():

    try:

        documents = list(
            locations_collection
            .find({})
            .sort(
                "created_at",
                -1,
            )
            .limit(100)
        )

    except PyMongoError as error:

        return {
            "success": False,
            "locations": [],
            "error": str(error),
        }

    return [
        {
            "id": str(
                document["_id"]
            ),
            "latitude": document.get(
                "latitude"
            ),
            "longitude": document.get(
                "longitude"
            ),
            "accuracy": document.get(
                "accuracy"
            ),
            "country_code": document.get(
                "country_code"
            ),
            "created_at": document.get(
                "created_at"
            ),
        }
        for document in documents
    ]


# =========================================================
# DATABASE STATUS
# =========================================================

@router.get("/database-status")
def database_status():

    try:

        client.admin.command("ping")

        return {
            "connected": True,
            "database": (
                emergency_contacts_collection
                .database
                .name
            ),
            "collections": {
                "emergency_contacts":
                    emergency_contacts_collection
                    .count_documents({}),

                "incidents":
                    incidents_collection
                    .count_documents({}),

                "sos_events":
                    sos_events_collection
                    .count_documents({}),

                "shared_locations":
                    locations_collection
                    .count_documents({}),
            },
        }

    except PyMongoError as error:

        return {
            "connected": False,
            "error": str(error),
        }