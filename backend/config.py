import os
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# GEOAPIFY
# =========================================================

GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

if not GEOAPIFY_API_KEY:
    raise ValueError(
        "GEOAPIFY_API_KEY is missing. "
        "Add it to your .env file."
    )


# =========================================================
# JWT AUTHENTICATION
# =========================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

if not JWT_SECRET_KEY:
    raise ValueError(
        "JWT_SECRET_KEY is missing. "
        "Add it to your .env file."
    )

JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7