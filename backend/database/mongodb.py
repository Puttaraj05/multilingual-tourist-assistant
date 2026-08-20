import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING


# Load environment variables from .env.
load_dotenv()


# Read MongoDB configuration.
MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "travelmate"
)


# These fallback classes allow the application to continue
# running when MongoDB is unavailable.

class DummyResult:

    def __init__(self):
        self.inserted_id = None


class DummyCursor:

    def __init__(self, documents=None):
        self.documents = documents or []

    def sort(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def __iter__(self):
        return iter(self.documents)


class DummyCollection:

    def find(self, *args, **kwargs):
        return DummyCursor()

    def find_one(self, *args, **kwargs):
        return None

    def insert_one(self, *args, **kwargs):
        return DummyResult()

    def insert_many(self, *args, **kwargs):
        return DummyResult()

    def update_one(self, *args, **kwargs):
        return DummyResult()

    def delete_one(self, *args, **kwargs):
        return DummyResult()

    def aggregate(self, *args, **kwargs):
        return DummyCursor()

    def count_documents(self, *args, **kwargs):
        return 0

    def create_index(self, *args, **kwargs):
        return None


# MongoDB client and database references.
client = None
db = None


# Fallback collections used when MongoDB is unavailable.
messages_collection = DummyCollection()
conversations_collection = DummyCollection()

emergency_contacts_collection = DummyCollection()
incidents_collection = DummyCollection()
sos_events_collection = DummyCollection()
locations_collection = DummyCollection()


# Connect application features to their MongoDB collections.
def initialize_collections():

    global messages_collection
    global conversations_collection
    global emergency_contacts_collection
    global incidents_collection
    global sos_events_collection
    global locations_collection

    messages_collection = db["messages"]

    conversations_collection = db["conversations"]

    emergency_contacts_collection = db[
        "emergency_contacts"
    ]

    incidents_collection = db[
        "incidents"
    ]

    sos_events_collection = db[
        "sos_events"
    ]

    locations_collection = db[
        "locations"
    ]


# Create indexes for fields that are frequently queried.
def initialize_indexes():

    try:

        # Find chat messages by session and creation time.
        messages_collection.create_index(
            [
                ("session_id", ASCENDING),
                ("created_at", ASCENDING)
            ],
            name="session_created_at_idx"
        )

        # Ensure every conversation session ID is unique.
        conversations_collection.create_index(
            [
                ("session_id", ASCENDING)
            ],
            unique=True,
            name="session_id_unique_idx"
        )

        # Speed up incident history queries.
        incidents_collection.create_index(
            [
                ("created_at", ASCENDING)
            ],
            name="incident_created_at_idx"
        )

        # Speed up SOS event history queries.
        sos_events_collection.create_index(
            [
                ("created_at", ASCENDING)
            ],
            name="sos_created_at_idx"
        )

        # Speed up location history queries.
        locations_collection.create_index(
            [
                ("created_at", ASCENDING)
            ],
            name="location_created_at_idx"
        )

        print(
            "MongoDB indexes ready.",
            flush=True
        )

    except Exception as error:

        print(
            f"MongoDB index warning: {error}",
            flush=True
        )


# Add default emergency contact numbers when the collection
# is empty. This prevents duplicate seed data.
def initialize_emergency_contacts():

    contacts = [

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
            "description": "Emergency medical response."
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
            "description": "Civil Defence / fire emergency."
        },

        {
            "country_code": "US",
            "country_name": "United States",
            "service": "Unified Emergency",
            "number": "911",
            "description": "Police, fire and medical emergency."
        },

        {
            "country_code": "GB",
            "country_name": "United Kingdom",
            "service": "Unified Emergency",
            "number": "999",
            "description": "Police, fire and ambulance emergency."
        },

        {
            "country_code": "GB",
            "country_name": "United Kingdom",
            "service": "Alternative Emergency",
            "number": "112",
            "description": "Alternative emergency number."
        }
    ]

    try:

        if emergency_contacts_collection.count_documents({}) == 0:

            emergency_contacts_collection.insert_many(
                contacts
            )

            print(
                "Emergency contacts initialized.",
                flush=True
            )

    except Exception as error:

        print(
            f"Emergency contacts initialization warning: {error}",
            flush=True
        )


# Connect to MongoDB when a connection URI is available.
if MONGODB_URI:

    try:

        print(
            "Connecting to MongoDB...",
            flush=True
        )

        # Create one MongoClient instance for the application.
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000
        )

        # Check whether MongoDB is reachable.
        client.admin.command("ping")

        # Select the TravelMate database.
        db = client[DATABASE_NAME]

        print(
            "MongoDB connected successfully.",
            flush=True
        )

        print(
            f"MongoDB database: {DATABASE_NAME}",
            flush=True
        )

        # Initialize the collections used by TravelMate.
        initialize_collections()

        # Create indexes for faster database queries.
        initialize_indexes()

        # Add default emergency contact data.
        initialize_emergency_contacts()

        print(
            "MongoDB collections initialized.",
            flush=True
        )

    except Exception as error:

        print(
            f"MongoDB connection failed: {error}",
            flush=True
        )

        print(
            "Using safe fallback collections.",
            flush=True
        )

else:

    print(
        "WARNING: MONGODB_URI is not configured.",
        flush=True
    )

    print(
        "Using safe fallback collections.",
        flush=True
    )


# Retrieve chat messages for a specific session.
def get_chat_messages(
    session_id: str,
    limit: int | None = None
):

    query = {
        "session_id": session_id
    }

    # Hide MongoDB's internal document ID.
    cursor = messages_collection.find(
        query,
        {"_id": 0}
    )

    # Return messages in chronological order.
    cursor = cursor.sort(
        [
            ("created_at", ASCENDING)
        ]
    )

    # Limit the number of messages when requested.
    if limit is not None:
        cursor = cursor.limit(limit)

    return list(cursor)


# Save one user or assistant message.
def save_chat_message(
    session_id: str,
    role: str,
    content: str,
    language: str = "English"
):

    document = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "language": language,
        "created_at": datetime.now(timezone.utc),
    }

    return messages_collection.insert_one(
        document
    )


# Create a conversation record if it does not already exist.
def ensure_conversation(
    session_id: str,
    language: str = "English"
):

    existing = conversations_collection.find_one(
        {
            "session_id": session_id
        }
    )

    if existing:
        return existing

    now = datetime.now(timezone.utc)

    document = {
        "session_id": session_id,
        "language": language,
        "created_at": now,
        "updated_at": now,
    }

    conversations_collection.insert_one(
        document
    )

    return document


# Update the last activity time of a conversation.
def update_conversation_timestamp(
    session_id: str
):

    conversations_collection.update_one(
        {
            "session_id": session_id
        },
        {
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )