from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx

from app.api.routes.auth import router as auth_router
from app.api.routes.projects import router as projects_router
from app.api.routes.tests import router as tests_router
from app.config import get_settings
from app.db.supabase import get_supabase_client

app = FastAPI(
    title="TestPilot AI Backend",
    description="Backend API for TestPilot AI",
    version="0.1.0",
)


# ============================================================================
# CORS MIDDLEWARE
# Enables frontend communication from Next.js dev server (http://localhost:3000)
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# EXCEPTION HANDLERS
# Formats error responses compatible with frontend apiClient and FastAPI standards
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "code": f"HTTP_{exc.status_code}",
                "details": None,
            },
            "detail": exc.detail,
        },
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": {
                "message": "Request validation error",
                "code": "VALIDATION_ERROR",
                "details": exc.errors(),
            },
            "detail": exc.errors(),
        },
    )


# ============================================================================
# HEALTH CHECK ROUTES
# Preserved from D03-09 setup
# ============================================================================

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    """Basic health check endpoint to verify backend process status."""
    return {
        "status": "ok",
        "service": "testpilot-backend",
    }


@app.get("/health/db", tags=["Health"])
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


# ============================================================================
# API ROUTERS
# Mounted under both /api/v1 (frontend convention) and / (contract convention)
# ============================================================================

app.include_router(auth_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(tests_router, prefix="/api/v1")

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(tests_router)
