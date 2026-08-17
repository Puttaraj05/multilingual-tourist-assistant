from datetime import datetime, timezone

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

router = APIRouter(prefix="/api", tags=["Emergency AI"])


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


def initialize_emergency_database():
    try:
        client.admin.command("ping")

        if emergency_contacts_collection.count_documents({}) == 0:
            emergency_contacts_collection.insert_many(CONTACTS)
            print("Emergency contacts inserted.")
        else:
            print("Emergency contacts already exist.")

    except PyMongoError as error:
        print("Emergency MongoDB initialization failed:")
        print(error)


def get_contacts(country_code: str):
    code = (country_code or "IN").upper()

    return list(
        emergency_contacts_collection.find(
            {"country_code": code},
            {"_id": 0},
        )
    )


# =========================================================
# PYDANTIC MODELS
# =========================================================

class LocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: float | None = Field(default=None, ge=0)
    countryCode: str | None = None


class SOSRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: float | None = Field(default=None, ge=0)
    countryCode: str | None = None


class IncidentRequest(BaseModel):
    type: str
    description: str = ""
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    accuracy: float | None = Field(default=None, ge=0)
    countryCode: str | None = None




# =========================================================
# COUNTRIES
# =========================================================

@router.get("/countries")
def countries():

    countries_data = list(
        emergency_contacts_collection.aggregate(
            [
                {
                    "$group": {
                        "_id": "$country_code",
                        "name": {"$first": "$country_name"},
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

    return [
        {
            "code": item["_id"],
            "name": item["name"],
        }
        for item in countries_data
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
        "country": code,
        "contacts": get_contacts(code),
    }


# =========================================================
# SAVE LOCATION
# =========================================================

@router.post("/location")
def save_location(location: LocationRequest):

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

    result = locations_collection.insert_one(document)

    return {
        "success": True,
        "locationId": str(result.inserted_id),
        "latitude": location.latitude,
        "longitude": location.longitude,
        "accuracy": location.accuracy,
    }


# =========================================================
# SOS
# =========================================================

@router.post("/sos")
def create_sos(sos: SOSRequest):

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

    result = sos_events_collection.insert_one(document)

    return {
        "success": True,
        "eventId": str(result.inserted_id),
        "message": (
            "SOS event logged. "
            "Call the local emergency service immediately."
        ),
        "contacts": get_contacts(country),
    }


# =========================================================
# CREATE INCIDENT
# =========================================================

@router.post("/incidents")
def create_incident(incident: IncidentRequest):

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
        "description": (incident.description or "")[:2000],
        "latitude": incident.latitude,
        "longitude": incident.longitude,
        "accuracy": incident.accuracy,
        "country_code": country,
        "created_at": now_iso(),
    }

    result = incidents_collection.insert_one(document)

    return {
        "success": True,
        "incidentId": str(result.inserted_id),
        "message": "Incident saved to your TravelAI support log.",
    }


# =========================================================
# GET INCIDENTS
# =========================================================

@router.get("/incidents")
def incidents():

    documents = list(
        incidents_collection
        .find({})
        .sort("created_at", -1)
        .limit(100)
    )

    return [
        {
            "id": str(document["_id"]),
            "type": document.get("type"),
            "description": document.get("description", ""),
            "latitude": document.get("latitude"),
            "longitude": document.get("longitude"),
            "accuracy": document.get("accuracy"),
            "country_code": document.get("country_code"),
            "created_at": document.get("created_at"),
        }
        for document in documents
    ]


# =========================================================
# GET SOS EVENTS
# =========================================================

@router.get("/sos")
def sos_events():

    documents = list(
        sos_events_collection
        .find({})
        .sort("created_at", -1)
        .limit(100)
    )

    return [
        {
            "id": str(document["_id"]),
            "latitude": document.get("latitude"),
            "longitude": document.get("longitude"),
            "accuracy": document.get("accuracy"),
            "country_code": document.get("country_code"),
            "status": document.get("status"),
            "created_at": document.get("created_at"),
        }
        for document in documents
    ]


# =========================================================
# GET SHARED LOCATIONS
# =========================================================

@router.get("/locations")
def locations():

    documents = list(
        locations_collection
        .find({})
        .sort("created_at", -1)
        .limit(100)
    )

    return [
        {
            "id": str(document["_id"]),
            "latitude": document.get("latitude"),
            "longitude": document.get("longitude"),
            "accuracy": document.get("accuracy"),
            "country_code": document.get("country_code"),
            "created_at": document.get("created_at"),
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
            "database": emergency_contacts_collection.database.name,
            "collections": {
                "emergency_contacts":
                    emergency_contacts_collection.count_documents({}),
                "incidents":
                    incidents_collection.count_documents({}),
                "sos_events":
                    sos_events_collection.count_documents({}),
                "shared_locations":
                    locations_collection.count_documents({}),
            },
        }

    except PyMongoError as error:

        return {
            "connected": False,
            "error": str(error),
        }
