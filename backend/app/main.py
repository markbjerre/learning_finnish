"""Main FastAPI application for Learning Finnish"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os

from app.config import settings
from app.routers import health, lessons, vocabulary, progress, words, exercise, settings as settings_router, concepts
from app.database import init_db, close_db

logger = logging.getLogger(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)


class AuthMiddleware:
    """Optional Bearer token auth for /api/* when FINNISH_API_KEY is set."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        from starlette.requests import Request
        from starlette.responses import JSONResponse

        request = Request(scope)
        if settings.finnish_api_key and request.url.path.startswith("/api/"):
            if "/health" not in request.url.path:
                auth = request.headers.get("Authorization", "")
                key = auth.replace("Bearer ", "").strip()
                if key != settings.finnish_api_key:
                    response = JSONResponse(status_code=401, content={"error": "unauthorized"})
                    await response(scope, receive, send)
                    return

        await self.app(scope, receive, send)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Initializing Learning Finnish API...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database initialization: {e}")
    logger.info(f"Application {settings.app_name} started successfully")

    yield

    # Shutdown
    logger.info(f"Application {settings.app_name} shutting down...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# Optional auth (add before CORS so auth runs first)
if settings.finnish_api_key:
    app.add_middleware(AuthMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(lessons.router, prefix=settings.api_prefix)
app.include_router(vocabulary.router, prefix=settings.api_prefix)
app.include_router(progress.router, prefix=settings.api_prefix)
app.include_router(words.router, prefix=settings.api_prefix)
app.include_router(exercise.router, prefix=settings.api_prefix)
app.include_router(settings_router.router, prefix=settings.api_prefix)
app.include_router(concepts.router, prefix=settings.api_prefix)

# Mount static files (for serving built React app)
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# SPA fallback - serve index.html for all unmatched routes
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve the React SPA for all routes not handled by API"""
    # Don't serve as SPA for API routes
    if full_path.startswith("api/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve index.html for SPA routing
    index_path = os.path.join(STATIC_DIR, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"message": "Learning Finnish API - Frontend not built yet"}


@app.get("/")
async def root():
    """Root endpoint"""
    index_path = os.path.join(STATIC_DIR, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {
        "message": "Learning Finnish API",
        "version": "1.0.0",
        "docs": "/docs",
        "api": settings.api_prefix,
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
