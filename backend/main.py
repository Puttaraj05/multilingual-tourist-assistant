from fastapi import FastAPI

from backend.database.mongodb import client


app = FastAPI(
    title="Multilingual Tourist Assistant",
    description="AI-powered multilingual tourism assistant",
    version="1.0.0",
)


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