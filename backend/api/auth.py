from datetime import datetime, timedelta, timezone
import os

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
import bcrypt
from bson import ObjectId

from backend.database import mongodb


# Authentication API routes.
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)


# JWT settings used for creating and validating login tokens.
from backend.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES
)

SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_ACCESS_TOKEN_EXPIRE_MINUTES


# Hash the user's password before saving it to the database.
def hash_password(password: str) -> str:

    password_bytes = password.encode("utf-8")

    # bcrypt only supports passwords up to 72 bytes.
    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=400,
            detail="Password must be 72 bytes or fewer"
        )

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed.decode("utf-8")


# Check whether a login password matches the saved password hash.
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    password_bytes = plain_password.encode("utf-8")

    if len(password_bytes) > 72:
        return False

    return bcrypt.checkpw(
        password_bytes,
        hashed_password.encode("utf-8")
    )


# Get the users collection from the connected MongoDB database.
def get_users_collection():

    if mongodb.db is None:
        raise HTTPException(
            status_code=503,
            detail="MongoDB is not connected"
        )

    return mongodb.db["users"]


# Request data used when creating a new account.
class SignupRequest(BaseModel):

    name: str

    email: EmailStr

    password: str


# Request data used when logging in.
class LoginRequest(BaseModel):

    email: EmailStr

    password: str


# User information returned by the authentication APIs.
class UserResponse(BaseModel):

    id: str

    name: str

    email: str


# Response returned after signup or login.
class AuthResponse(BaseModel):

    success: bool

    message: str

    token: str

    user: UserResponse


# Response returned for the current logged-in user.
class MeResponse(BaseModel):

    success: bool

    user: UserResponse


# Create a JWT token containing the user's ID and expiry time.
def create_access_token(user_id: str) -> str:

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    payload = {
        "sub": user_id,
        "exp": expire
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# Read and validate the user ID stored inside a JWT token.
def get_user_from_token(token: str) -> str:

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:

            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

        return user_id

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token"
        )


# Create a new user account.
@router.post(
    "/signup",
    response_model=AuthResponse
)
async def signup(data: SignupRequest):

    name = data.name.strip()

    email = str(data.email).strip().lower()

    password = data.password

    # Check the basic signup requirements.
    if len(name) < 2:

        raise HTTPException(
            status_code=400,
            detail="Name must contain at least 2 characters"
        )

    if len(password) < 6:

        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 6 characters"
        )

    users = get_users_collection()

    # Do not create another account with the same email.
    existing_user = users.find_one(
        {
            "email": email
        }
    )

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists"
        )

    # Store the new user's basic account information.
    now = datetime.now(timezone.utc)

    user = {

        "name": name,

        "email": email,

        "password_hash":
            hash_password(password),

        "created_at": now,

        "updated_at": now
    }

    try:

        result = users.insert_one(user)

    except Exception as error:

        # Handle duplicate email errors from MongoDB.
        if "duplicate" in str(error).lower():

            raise HTTPException(
                status_code=409,
                detail="An account with this email already exists"
            )

        raise HTTPException(
            status_code=500,
            detail="Unable to create account"
        )

    user_id = str(result.inserted_id)

    # Create a token so the user is logged in after signup.
    token = create_access_token(
        user_id
    )

    return {

        "success": True,

        "message":
            "Account created successfully",

        "token": token,

        "user": {

            "id": user_id,

            "name": name,

            "email": email
        }
    }


# Log an existing user into the application.
@router.post(
    "/login",
    response_model=AuthResponse
)
async def login(data: LoginRequest):

    email = str(
        data.email
    ).strip().lower()

    password = data.password

    users = get_users_collection()

    # Find the account using the provided email.
    user = users.find_one(
        {
            "email": email
        }
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Get the saved password hash.
    password_hash = user.get(
        "password_hash"
    )

    if not password_hash:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Verify the password entered during login.
    try:

        valid_password = verify_password(
            password,
            password_hash
        )

    except Exception:

        valid_password = False

    if not valid_password:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create a new login token for the user.
    user_id = str(
        user["_id"]
    )

    token = create_access_token(
        user_id
    )

    return {

        "success": True,

        "message":
            "Login successful",

        "token": token,

        "user": {

            "id": user_id,

            "name":
                user.get(
                    "name",
                    ""
                ),

            "email":
                user.get(
                    "email",
                    ""
                )
        }
    }


# Return the details of the currently authenticated user.
@router.get(
    "/me",
    response_model=MeResponse
)
async def get_current_user(
    authorization: str | None = Header(
        default=None
    )
):

    # Check that the request contains an authorization header.
    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    if not authorization.startswith(
        "Bearer "
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header"
        )

    # Extract the JWT token from the Bearer header.
    token = authorization.replace(
        "Bearer ",
        "",
        1
    ).strip()

    if not token:

        raise HTTPException(
            status_code=401,
            detail="Authentication token missing"
        )

    # Validate the token and get the user ID.
    user_id = get_user_from_token(
        token
    )

    # Convert the ID from the token into a MongoDB ObjectId.
    try:

        object_id = ObjectId(
            user_id
        )

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid user ID"
        )

    users = get_users_collection()

    # Find the user associated with the token.
    user = users.find_one(
        {
            "_id": object_id
        }
    )

    if not user:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {

        "success": True,

        "user": {

            "id":
                str(
                    user["_id"]
                ),

            "name":
                user.get(
                    "name",
                    ""
                ),

            "email":
                user.get(
                    "email",
                    ""
                )
        }
    }


# Handle logout requests.
@router.post("/logout")
async def logout():

    # JWT logout is handled on the client by removing the token.
    return {

        "success": True,

        "message":
            "Logged out successfully"
    }