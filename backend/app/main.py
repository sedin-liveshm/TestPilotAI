from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
import httpx

from app.config import get_settings
from app.db.supabase import get_supabase_client

app = FastAPI(
    title="TestPilot AI Backend",
    description="Backend API for TestPilot AI",
    version="0.1.0",
)


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Basic health check endpoint to verify backend process status."""
    return {
        "status": "ok",
        "service": "testpilot-backend",
    }


@app.get("/health/db")
def db_health_check():
    """Database connectivity check endpoint to verify Supabase communication."""
    try:
        settings = get_settings()
        # Verify client can be created
        _ = get_supabase_client()

        # Perform a lightweight ping to Supabase REST gateway
        url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/"
        headers = {"apikey": settings.SUPABASE_KEY}
        
        with httpx.Client(timeout=5.0) as http_client:
            response = http_client.get(url, headers=headers)

        if response.status_code < 500:
            return {
                "status": "ok",
                "database": "connected",
            }
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "database": "disconnected",
                "message": "Database service returned an error status",
            },
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "database": "disconnected",
                "message": "Database connectivity check failed",
            },
        )
