from app.api.routes.auth import router as auth_router
from app.api.routes.projects import router as projects_router
from app.api.routes.tests import router as tests_router

__all__ = ["auth_router", "projects_router", "tests_router"]
