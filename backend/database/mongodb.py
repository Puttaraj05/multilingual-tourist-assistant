from pymongo import MongoClient

from backend.config import DATABASE_NAME, MONGODB_URI


client = None
db = None

conversations_collection = None
messages_collection = None
itineraries_collection = None
translations_collection = None
recommendations_collection = None


if MONGODB_URI:

    try:
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=3000
        )

        db = client[DATABASE_NAME]

        conversations_collection = db["conversations"]
        messages_collection = db["messages"]
        itineraries_collection = db["itineraries"]
        translations_collection = db["translations"]
        recommendations_collection = db["recommendations"]

    except Exception as error:
        print(f"MongoDB connection unavailable: {error}")