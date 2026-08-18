import os
from dotenv import load_dotenv

load_dotenv()

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

if not GEOAPIFY_API_KEY:
    raise ValueError(
        "GEOAPIFY_API_KEY is missing. "
        "Add it to your .env file."
    )