import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


# =========================================================
# MONGODB CONFIGURATION
# =========================================================

MONGODB_URI = os.getenv("MONGODB_URI")

DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "travelmate"
)


# =========================================================
# FALLBACK DUMMY COLLECTION
# =========================================================

class DummyResult:
    def __init__(self):
        self.inserted_id = None


class DummyCollection:

    def find(self, *args, **kwargs):
        return []

    def find_one(self, *args, **kwargs):
        return None

    def insert_one(self, *args, **kwargs):
        return DummyResult()

    def update_one(self, *args, **kwargs):
        return DummyResult()

    def delete_one(self, *args, **kwargs):
        return DummyResult()

    def aggregate(self, *args, **kwargs):
        return []

    def count_documents(self, *args, **kwargs):
        return 0


# =========================================================
# DEFAULT COLLECTIONS
# =========================================================

messages_collection = DummyCollection()
conversations_collection = DummyCollection()

emergency_contacts_collection = DummyCollection()
incidents_collection = DummyCollection()
sos_events_collection = DummyCollection()
locations_collection = DummyCollection()

itineraries_collection = DummyCollection()
translations_collection = DummyCollection()
recommendations_collection = DummyCollection()


# =========================================================
# MONGODB CLIENT
# =========================================================

client = None
db = None


# =========================================================
# CONNECT TO MONGODB
# =========================================================

if MONGODB_URI:

    try:

        print(
            "Connecting to MongoDB...",
            flush=True
        )

        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000
        )

        # Force connection check
        client.admin.command("ping")

        db = client[DATABASE_NAME]

        print(
            "MongoDB connected successfully.",
            flush=True
        )

        print(
            f"MongoDB database: {DATABASE_NAME}",
            flush=True
        )


        # =================================================
        # CHAT
        # =================================================

        messages_collection = db[
            "messages"
        ]

        conversations_collection = db[
            "conversations"
        ]


        # =================================================
        # EMERGENCY
        # =================================================

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


        # =================================================
        # ITINERARY
        # =================================================

        itineraries_collection = db[
            "itineraries"
        ]


        # =================================================
        # TRANSLATION
        # =================================================

        translations_collection = db[
            "translations"
        ]


        # =================================================
        # RECOMMENDATIONS
        # =================================================

        recommendations_collection = db[
            "recommendations"
        ]


        print(
            "MongoDB collections initialized.",
            flush=True
        )


    except Exception as e:

        print(
            f"MongoDB connection failed: {e}",
            flush=True
        )

        print(
            "Using dummy collections.",
            flush=True
        )


else:

    print(
        "WARNING: MONGODB_URI is not configured.",
        flush=True
    )

    print(
        "Using dummy collections.",
        flush=True
    )