from pymongo import MongoClient

from backend.config import DATABASE_NAME, MONGODB_URI


if not MONGODB_URI:
    raise RuntimeError("MONGODB_URI is not configured")


client = MongoClient(
    MONGODB_URI,
    tls=True,
    tlsAllowInvalidCertificates=False,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
    socketTimeoutMS=20000,
)

db = client[DATABASE_NAME]


conversations_collection = db["conversations"]
messages_collection = db["messages"]
itineraries_collection = db["itineraries"]
translations_collection = db["translations"]
recommendations_collection = db["recommendations"]
emergency_contacts_collection = db["emergency_contacts"]
incidents_collection = db["incidents"]
sos_events_collection = db["sos_events"]
locations_collection = db["shared_locations"]