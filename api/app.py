"""
Whiteboard Animator REST API

A structured REST API for generating whiteboard-style animations from images.
This API provides endpoints for image analysis and animation creation with
configurable parameters for customization.

Features:
- Image analysis for optimal animation settings
- Whiteboard animation generation with hand cursor
- Multiple platform support (Linux, Windows, Android, Mac)
- Video format conversion with FFmpeg
- Comprehensive API documentation with OpenAPI/Swagger

Author: Whiteboard Animator Team
Version: 1.0.0
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .routes.animation_routes import router as animation_router
from .models.animation_models import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Whiteboard Animator API...")
    yield
    # Shutdown
    logger.info("Shutting down Whiteboard Animator API...")


# Create FastAPI application
app = FastAPI(
    title="Whiteboard Animator API",
    description="""
    A REST API for generating whiteboard-style animation videos from images.
    
    ## Features
    
    * **Image Analysis**: Analyze images to determine optimal animation settings
    * **Animation Creation**: Generate whiteboard-style animation videos
    * **Multiple Platforms**: Support for Linux, Windows, Android, and Mac
    * **Customizable**: Configurable parameters for frame rate, drawing speed, and more
    * **Video Conversion**: Automatic FFmpeg-based video optimization
    
    ## Workflow
    
    1. **Analyze Image** (Optional): Use `/api/v1/animation/analyze` to get recommended settings
    2. **Create Animation**: Use `/api/v1/animation/create` to generate the animation video
    
    ## Common Use Cases
    
    - Educational content creation
    - Marketing and presentation videos
    - Tutorial and explainer videos
    - Social media content
    
    ## Technical Details
    
    The API uses OpenCV for image processing, NumPy for numerical operations,
    and FFmpeg (via PyAV) for video encoding. The animation simulates a hand
    drawing the image on a whiteboard by progressively revealing the image
    in small grid sections.
    """,
    version="1.0.0",
    terms_of_service="https://github.com/armelgeek/whiteboard-animator",
    contact={
        "name": "Whiteboard Animator Team",
        "url": "https://github.com/armelgeek/whiteboard-animator",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/armelgeek/whiteboard-animator/blob/main/LICENSE",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(animation_router)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": False,
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "details": str(exc)
        }
    )


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Get API information and available endpoints"
)
async def root():
    """
    Root endpoint providing API information and links to documentation.
    """
    return {
        "name": "Whiteboard Animator API",
        "version": "1.0.0",
        "description": "REST API for generating whiteboard-style animations",
        "documentation": {
            "interactive": "/docs",
            "redoc": "/redoc",
            "openapi_spec": "/openapi.json"
        },
        "endpoints": {
            "health": "/api/v1/animation/health",
            "analyze_image": "/api/v1/animation/analyze",
            "create_animation": "/api/v1/animation/create"
        },
        "repository": "https://github.com/armelgeek/whiteboard-animator"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
