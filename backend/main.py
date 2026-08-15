from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from backend.api.chat import router as chat_router
from backend.database.mongodb import client
from backend.api.chat_history import router as chat_history_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(chat_history_router)
@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Multilingual Tourist Assistant API is running",
    }


@app.get("/api/health")
async def health():
    return {
        "success": True,
        "status": "healthy",
    }


@app.get("/api/health/database")
async def database_health():
    try:
        client.admin.command("ping")

        return {
            "success": True,
            "database": "connected",
        }

    except Exception as e:
        return {
            "success": False,
            "database": "disconnected",
            "error": str(e),
        }