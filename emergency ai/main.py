from datetime import datetime, timezone
from pathlib import Path
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

PUBLIC_DIR = BASE_DIR / "public"


# =========================================================
# MONGODB CONFIGURATION
# =========================================================

MONGODB_URL = os.getenv(
    "MONGODB_URL",
    "mongodb://localhost:27017"
)

MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "travelai"
)


# =========================================================
# MONGODB CONNECTION
# =========================================================

client = MongoClient(
    MONGODB_URL,
    serverSelectionTimeoutMS=5000
)

database = client[MONGODB_DATABASE]


contacts_collection = database[
    "emergency_contacts"
]

incidents_collection = database[
    "incidents"
]

sos_collection = database[
    "sos_events"
]

locations_collection = database[
    "shared_locations"
]


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title="TravelAI Emergency Support API",
    version="2.0.0",
    description=(
        "FastAPI + MongoDB backend for "
        "TravelAI Feature 5 — Emergency Travel Support."
    )
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
        "description": "Pan-India emergency number."
    },

    {
        "country_code": "IN",
        "country_name": "India",
        "service": "Police",
        "number": "100",
        "description": "Police emergency."
    },

    {
        "country_code": "IN",
        "country_name": "India",
        "service": "Ambulance",
        "number": "108",
        "description": (
            "Emergency medical response."
        )
    },

    {
        "country_code": "IN",
        "country_name": "India",
        "service": "Fire",
        "number": "101",
        "description": "Fire emergency."
    },

    {
        "country_code": "AE",
        "country_name": "United Arab Emirates",
        "service": "Police",
        "number": "999",
        "description": "Police emergency."
    },

    {
        "country_code": "AE",
        "country_name": "United Arab Emirates",
        "service": "Ambulance",
        "number": "998",
        "description": "Ambulance emergency."
    },

    {
        "country_code": "AE",
        "country_name": "United Arab Emirates",
        "service": "Fire",
        "number": "997",
        "description": (
            "Civil Defence / fire emergency."
        )
    },

    {
        "country_code": "US",
        "country_name": "United States",
        "service": "Unified Emergency",
        "number": "911",
        "description": (
            "Police, fire and medical emergency."
        )
    },

    {
        "country_code": "GB",
        "country_name": "United Kingdom",
        "service": "Unified Emergency",
        "number": "999",
        "description": (
            "Police, fire and ambulance emergency."
        )
    },

    {
        "country_code": "GB",
        "country_name": "United Kingdom",
        "service": "Alternative Emergency",
        "number": "112",
        "description": (
            "Alternative emergency number."
        )
    }

]


# =========================================================
# UTILITY FUNCTIONS
# =========================================================

def now_iso():
    return datetime.now(
        timezone.utc
    ).isoformat()


def serialize_document(document):
    """
    Convert MongoDB ObjectId to string.
    """

    if not document:
        return None

    document["_id"] = str(
        document["_id"]
    )

    return document


def get_contacts(country_code):

    code = (
        country_code or "IN"
    ).upper()

    contacts = list(
        contacts_collection.find(
            {
                "country_code": code
            },
            {
                "_id": 0
            }
        )
    )

    return contacts


# =========================================================
# INITIALIZE MONGODB
# =========================================================

def initialize_database():

    try:

        client.admin.command(
            "ping"
        )

        print(
            "MongoDB connection successful."
        )

    except PyMongoError as error:

        print(
            "MongoDB connection failed:"
        )

        print(error)

        return

    if (
        contacts_collection.count_documents({})
        == 0
    ):

        contacts_collection.insert_many(
            CONTACTS
        )

        print(
            "Emergency contacts inserted."
        )

    else:

        print(
            "Emergency contacts already exist."
        )


# =========================================================
# PYDANTIC MODELS
# =========================================================

class LocationRequest(BaseModel):

    latitude: float = Field(
        ...,
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180
    )

    accuracy: float | None = Field(
        default=None,
        ge=0
    )

    countryCode: str | None = None


class SOSRequest(BaseModel):

    latitude: float = Field(
        ...,
        ge=-90,
        le=90
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180
    )

    accuracy: float | None = Field(
        default=None,
        ge=0
    )

    countryCode: str | None = None


class IncidentRequest(BaseModel):

    type: str

    description: str = ""

    latitude: float | None = Field(
        default=None,
        ge=-90,
        le=90
    )

    longitude: float | None = Field(
        default=None,
        ge=-180,
        le=180
    )

    accuracy: float | None = Field(
        default=None,
        ge=0
    )

    countryCode: str | None = None


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
def startup():

    initialize_database()


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/api/health")
def health():

    try:

        client.admin.command(
            "ping"
        )

        return {

            "ok": True,

            "service":
                "TravelAI Emergency Support",

            "database":
                "MongoDB",

            "database_name":
                MONGODB_DATABASE

        }

    except PyMongoError:

        return {

            "ok": False,

            "service":
                "TravelAI Emergency Support",

            "database":
                "MongoDB",

            "database_name":
                MONGODB_DATABASE

        }


# =========================================================
# COUNTRIES
# =========================================================

@app.get("/api/countries")
def countries():

    countries_data = list(
        contacts_collection.aggregate(
            [
                {
                    "$group": {
                        "_id":
                            "$country_code",

                        "name": {
                            "$first":
                                "$country_name"
                        }
                    }
                },

                {
                    "$sort": {
                        "name": 1
                    }
                }
            ]
        )
    )


    return [

        {
            "code":
                item["_id"],

            "name":
                item["name"]

        }

        for item in countries_data

    ]


# =========================================================
# EMERGENCY CONTACTS
# =========================================================

@app.get("/api/emergency-contacts")
def emergency_contacts(

    country: str = Query(
        default="IN",
        min_length=2,
        max_length=2
    )

):

    code = country.upper()

    contacts = get_contacts(
        code
    )


    return {

        "country":
            code,

        "contacts":
            contacts

    }


# =========================================================
# SAVE LOCATION
# =========================================================

@app.post("/api/location")
def save_location(
    location: LocationRequest
):

    country = (
        location.countryCode
        or "IN"
    ).upper()


    document = {

        "latitude":
            location.latitude,

        "longitude":
            location.longitude,

        "accuracy":
            location.accuracy,

        "country_code":
            country,

        "created_at":
            now_iso()

    }


    result = locations_collection.insert_one(
        document
    )


    return {

        "success":
            True,

        "locationId":
            str(result.inserted_id),

        "latitude":
            location.latitude,

        "longitude":
            location.longitude,

        "accuracy":
            location.accuracy

    }


# =========================================================
# SOS
# =========================================================

@app.post("/api/sos")
def create_sos(
    sos: SOSRequest
):

    country = (
        sos.countryCode
        or "IN"
    ).upper()


    document = {

        "latitude":
            sos.latitude,

        "longitude":
            sos.longitude,

        "accuracy":
            sos.accuracy,

        "country_code":
            country,

        "status":
            "logged",

        "created_at":
            now_iso()

    }


    result = sos_collection.insert_one(
        document
    )


    return {

        "success":
            True,

        "eventId":
            str(result.inserted_id),

        "message":
            (
                "SOS event logged. "
                "Call the local emergency "
                "service immediately."
            ),

        "contacts":
            get_contacts(country)

    }


# =========================================================
# CREATE INCIDENT
# =========================================================

@app.post("/api/incidents")
def create_incident(
    incident: IncidentRequest
):

    allowed = {

        "medical",

        "lost",

        "theft",

        "unsafe",

        "document",

        "other"

    }


    if incident.type not in allowed:

        raise HTTPException(

            status_code=400,

            detail=
                "Invalid incident type."

        )


    country = (
        incident.countryCode
        or "IN"
    ).upper()


    description = (
        incident.description
        or ""
    )[:2000]


    document = {

        "type":
            incident.type,

        "description":
            description,

        "latitude":
            incident.latitude,

        "longitude":
            incident.longitude,

        "accuracy":
            incident.accuracy,

        "country_code":
            country,

        "created_at":
            now_iso()

    }


    result = incidents_collection.insert_one(
        document
    )


    return {

        "success":
            True,

        "incidentId":
            str(result.inserted_id),

        "message":
            "Incident saved to your TravelAI support log."

    }


# =========================================================
# GET INCIDENTS
# =========================================================

@app.get("/api/incidents")
def incidents():

    documents = list(

        incidents_collection
        .find({})
        .sort(
            "created_at",
            -1
        )
        .limit(100)

    )


    result = []


    for document in documents:

        result.append({

            "id":
                str(
                    document["_id"]
                ),

            "type":
                document.get(
                    "type"
                ),

            "description":
                document.get(
                    "description",
                    ""
                ),

            "latitude":
                document.get(
                    "latitude"
                ),

            "longitude":
                document.get(
                    "longitude"
                ),

            "accuracy":
                document.get(
                    "accuracy"
                ),

            "country_code":
                document.get(
                    "country_code"
                ),

            "created_at":
                document.get(
                    "created_at"
                )

        })


    return result


# =========================================================
# GET SOS EVENTS
# =========================================================

@app.get("/api/sos")
def sos_events():

    documents = list(

        sos_collection
        .find({})
        .sort(
            "created_at",
            -1
        )
        .limit(100)

    )


    result = []


    for document in documents:

        result.append({

            "id":
                str(
                    document["_id"]
                ),

            "latitude":
                document.get(
                    "latitude"
                ),

            "longitude":
                document.get(
                    "longitude"
                ),

            "accuracy":
                document.get(
                    "accuracy"
                ),

            "country_code":
                document.get(
                    "country_code"
                ),

            "status":
                document.get(
                    "status"
                ),

            "created_at":
                document.get(
                    "created_at"
                )

        })


    return result


# =========================================================
# GET SHARED LOCATIONS
# =========================================================

@app.get("/api/locations")
def locations():

    documents = list(

        locations_collection
        .find({})
        .sort(
            "created_at",
            -1
        )
        .limit(100)

    )


    result = []


    for document in documents:

        result.append({

            "id":
                str(
                    document["_id"]
                ),

            "latitude":
                document.get(
                    "latitude"
                ),

            "longitude":
                document.get(
                    "longitude"
                ),

            "accuracy":
                document.get(
                    "accuracy"
                ),

            "country_code":
                document.get(
                    "country_code"
                ),

            "created_at":
                document.get(
                    "created_at"
                )

        })


    return result


# =========================================================
# MONGODB STATS
# =========================================================

@app.get("/api/database-status")
def database_status():

    try:

        client.admin.command(
            "ping"
        )


        return {

            "connected":
                True,

            "database":
                MONGODB_DATABASE,

            "collections": {

                "emergency_contacts":
                    contacts_collection.count_documents({}),

                "incidents":
                    incidents_collection.count_documents({}),

                "sos_events":
                    sos_collection.count_documents({}),

                "shared_locations":
                    locations_collection.count_documents({})

            }

        }

    except PyMongoError as error:

        return {

            "connected":
                False,

            "database":
                MONGODB_DATABASE,

            "error":
                str(error)

        }


# =========================================================
# SERVE FRONTEND
# =========================================================

app.mount(
    "/static",
    StaticFiles(
        directory=PUBLIC_DIR
    ),
    name="static"
)


@app.get(
    "/",
    include_in_schema=False
)
def home():

    return FileResponse(
        PUBLIC_DIR / "index.html"
    )


@app.get(
    "/{path:path}",
    include_in_schema=False
)
def frontend(path: str):

    requested =        PUBLIC_DIR / path


    if (
        path
        and requested.is_file()
    ):

        return FileResponse(
            requested
        )


    return FileResponse(
        PUBLIC_DIR / "index.html"
    )