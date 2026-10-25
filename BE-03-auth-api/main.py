"""
FlyRank Backend AI Engineering — Week 4 (BE-03: Auth · Login & Protect)

FastAPI entry point featuring:
- Supabase Auth as Identity Provider (IdP)
- JWT Bearer Token validation via FastAPI Depends()
- Protected routes (/protected/profile, /protected/dashboard)
- Public routes (/public/info)
- OpenAPI/Swagger UI with Bearer Token "Authorize" lock support
"""

from contextlib import asynccontextmanager
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn

from src.supabase_client import get_supabase_client
from src.routes.auth_routes import router as auth_router
from src.routes.protected_routes import router as protected_router
from src.routes.public_routes import router as public_router

# Load environment configuration
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify Supabase client connection on startup
    get_supabase_client()
    print("Server running and connected to Supabase")
    yield


def create_app() -> FastAPI:
    """Build and configure the authenticated FastAPI application."""
    app = FastAPI(
        title="Auth · Login & Protect API",
        version="1.0.0",
        description=(
            "A secure FastAPI authentication service integrated with Supabase Auth. "
            "Handles Sign Up, Log In, Log Out, and guards endpoints with JWT Bearer tokens."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Standardize validation error responses to match { "error": "..." }
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        first_error = exc.errors()[0]
        msg = first_error.get("msg", "Invalid request body")
        field = ".".join(str(loc) for loc in first_error.get("loc", []) if loc != "body")
        detail_msg = f"{field}: {msg}" if field else msg
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": detail_msg},
        )

    # Standardize HTTP exception responses to match { "error": "..." }
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if isinstance(exc.detail, dict) and "error" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": str(exc.detail)},
        )

    # Include route groups
    app.include_router(public_router)
    app.include_router(auth_router)
    app.include_router(protected_router)

    @app.get("/", tags=["System"], summary="API Root Metadata")
    def read_root():
        return {
            "name": "Auth · Login & Protect API",
            "version": "1.0.0",
            "provider": "Supabase Auth",
            "docs": "/docs",
            "endpoints": [
                "POST /auth/signup",
                "POST /auth/login",
                "POST /auth/logout",
                "GET /protected/profile",
                "GET /protected/dashboard",
                "GET /public/info",
            ],
        }

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Server starting on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
