import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

load_dotenv()


# Load MongoDB configuration.

MONGODB_URI = os.getenv("MONGODB_URI")

DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "travelmate"
)


# Provide a safe fallback result when MongoDB is unavailable.

class DummyResult:

    def __init__(self):
        self.inserted_id = None


# Provide a cursor-like fallback for safe database operations.

class DummyCursor:

    def __init__(self, documents=None):
        self.documents = documents or []

    def sort(self, *args, **kwargs):
        return self

    def limit(self, *args, **kwargs):
        return self

    def __iter__(self):
        return iter(self.documents)

    def __next__(self):
        return next(iter(self.documents))


# Provide a fallback collection when MongoDB is unavailable.

class DummyCollection:

    def find(self, *args, **kwargs):
        return DummyCursor([])

    def find_one(self, *args, **kwargs):
        return None

    def insert_one(self, *args, **kwargs):
        return DummyResult()

    def update_one(self, *args, **kwargs):
        return DummyResult()

    def delete_one(self, *args, **kwargs):
        return DummyResult()

    def aggregate(self, *args, **kwargs):
        return DummyCursor([])

    def count_documents(self, *args, **kwargs):
        return 0

    def create_index(self, *args, **kwargs):
        return None


# Initialize fallback collections before connecting to MongoDB.

messages_collection = DummyCollection()
conversations_collection = DummyCollection()

emergency_contacts_collection = DummyCollection()
incidents_collection = DummyCollection()
sos_events_collection = DummyCollection()
locations_collection = DummyCollection()

itineraries_collection = DummyCollection()
translations_collection = DummyCollection()
recommendations_collection = DummyCollection()


# Initialize MongoDB client and database references.

client = None
db = None


# Connect to MongoDB when a connection string is available.

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


        # Initialize chat collections.

        messages_collection = db["messages"]

        conversations_collection = db["conversations"]


        # Initialize emergency-related collections.

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


        # Initialize itinerary collection.

        itineraries_collection = db[
            "itineraries"
        ]


        # Initialize translation collection.

        translations_collection = db[
            "translations"
        ]


        # Initialize recommendation collection.

        recommendations_collection = db[
            "recommendations"
        ]


        # Create indexes for faster chat history queries.

        try:

            messages_collection.create_index(
                [
                    ("session_id", ASCENDING),
                    ("created_at", ASCENDING)
                ],
                name="session_created_at_idx"
            )

            conversations_collection.create_index(
                [
                    ("session_id", ASCENDING)
                ],
                unique=True,
                name="session_id_unique_idx"
            )

            print(
                "MongoDB chat indexes ready.",
                flush=True
            )

        except Exception as index_error:

            print(
                f"MongoDB index warning: {index_error}",
                flush=True
            )


        # Confirm that all MongoDB collections are ready.

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


# Get chat messages in chronological order.

def get_chat_messages(
    session_id: str,
    limit: int | None = None
):
    """
    Get all messages for a chat session in chronological order.

    IMPORTANT:
    All chat history retrieval should use this function.
    """

    query = {
        "session_id": session_id
    }

    projection = {
        "_id": 0
    }

    cursor = messages_collection.find(
        query,
        projection
    )

    # Sort messages by creation time.

    cursor = cursor.sort(
        [
            ("created_at", ASCENDING)
        ]
    )

    if limit is not None:
        cursor = cursor.limit(limit)

    return list(cursor)


# Save a single chat message with a consistent timestamp.

def save_chat_message(
    session_id: str,
    role: str,
    content: str,
    language: str = "English"
):
    """
    Save exactly one chat message.

    Every message uses created_at consistently.
    """

    now = datetime.now(timezone.utc)

    document = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "language": language,
        "created_at": now,
    }

    result = messages_collection.insert_one(
        document
    )

    return result


# Create a conversation record if it does not already exist.

def ensure_conversation(
    session_id: str,
    language: str = "English"
):
    """
    Create the conversation document if it doesn't exist.
    """

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


# Update the last activity timestamp for a conversation.

def update_conversation_timestamp(
    session_id: str
):
    """
    Update the last activity time of a conversation.
    """

    conversations_collection.update_one(
        {
            "session_id": session_id
        },
        {
            "$set": {
                "updated_at":
                    datetime.now(timezone.utc)
            }
        }
    )