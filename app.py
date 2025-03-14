"""
Main entry point for Toxicity Detector FastAPI application.

This module initializes the FastAPI application, configures middleware,
registers API routes, and provides health check endpoints.
"""

import sys
import logging
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add project root to path to ensure imports work correctly
project_root = Path(__file__).parent.resolve()
sys.path.append(str(project_root))

# Import application settings
try:
    from backend.config.settings import settings
    API_PREFIX = settings.API_V1_STR
    PROJECT_NAME = settings.PROJECT_NAME
except ImportError:
    logger.warning("Cannot import settings from backend. Using default values.")
    API_PREFIX = "/api"
    PROJECT_NAME = "Toxicity Detector API"

# Create FastAPI application instance
app = FastAPI(
    title=PROJECT_NAME,
    description="API for detecting toxic, offensive, hate speech and spam content on social media",
    version="1.0.0",
    docs_url=None,  # Disable default docs url to use custom one
    redoc_url=None,  # Disable default redoc url to use custom one
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "chrome-extension://*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register API routes
try:
    from backend.api.routes import admin, auth, extension
    
    # Mount routes using API_PREFIX from settings
    app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
    app.include_router(extension.router, prefix=f"{API_PREFIX}/extension", tags=["Extension"])
    app.include_router(admin.router, prefix=f"{API_PREFIX}/admin", tags=["Admin"])
    
    logger.info("API routes registered successfully")
except ImportError as e:
    logger.error(f"Failed to import API routes: {str(e)}")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions globally."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error. Please try again later."}
    )

# Define API documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Serve custom Swagger UI documentation."""
    return get_swagger_ui_html(
        openapi_url=f"{API_PREFIX}/openapi.json",
        title=f"{PROJECT_NAME} - Swagger UI",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Serve ReDoc documentation."""
    return get_swagger_ui_html(
        openapi_url=f"{API_PREFIX}/openapi.json",
        title=f"{PROJECT_NAME} - ReDoc",
        swagger_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.css",
    )

# API root endpoint for health check
@app.get("/")
async def root():
    """Root endpoint providing API status information."""
    return {
        "status": "online",
        "api_version": "1.0.0",
        "service": PROJECT_NAME,
        "documentation": "/docs",
        "endpoints": f"{API_PREFIX}/auth, {API_PREFIX}/extension, {API_PREFIX}/admin"
    }

# API base endpoint
@app.get(f"{API_PREFIX}")
async def api_root():
    """API root endpoint providing available routes information."""
    return {
        "message": f"{PROJECT_NAME} is operational",
        "available_endpoints": {
            "authentication": f"{API_PREFIX}/auth",
            "content_analysis": f"{API_PREFIX}/extension",
            "administration": f"{API_PREFIX}/admin"
        },
        "documentation": "/docs"
    }

# Run application when executed directly
if __name__ == "__main__":
    port = int(settings.PORT) if hasattr(settings, "PORT") else 7860
    logger.info(f"Starting application on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)