from fastapi import FastAPI

app = FastAPI(
    title="Multilingual Tourist Assistant",
    description="AI-powered multilingual tourism assistant",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Multilingual Tourist Assistant API is running"
    }


@app.get("/api/health")
async def health():
    return {
        "success": True,
        "status": "healthy"
    }