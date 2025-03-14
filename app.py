"""
Main entry point for Toxicity Detector FastAPI application.

This module initializes the FastAPI application, configures middleware,
registers API routes, and provides health check endpoints.
"""

import sys
import logging
from pathlib import Path
import json
import traceback
import datetime
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
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

# Define lifespan context manager (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # ===== Startup =====
    logger.info("Starting up application")
    
    # Initialize database
    try:
        from backend.db.base import init_db
        
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        logger.error(traceback.format_exc())
    
    # Yield control to the application
    yield
    
    # ===== Shutdown =====
    logger.info("Shutting down application")

# Create FastAPI application instance
app = FastAPI(
    title=PROJECT_NAME,
    description="API for detecting toxic, offensive, hate speech and spam content on social media",
    version="1.0.0",
    docs_url=None,  # Disable default docs url to use custom one
    redoc_url=None,  # Disable default redoc url to use custom one
    lifespan=lifespan,  # Use lifespan context manager instead of on_event
)

# Configure CORS - cấu hình chi tiết hơn
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_origin_regex="chrome-extension://.*",  # Support Chrome extensions with any ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"],
)

# Middleware to log requests and responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Log headers for debugging CORS issues
    headers_debug = dict(request.headers)
    if "authorization" in headers_debug:
        headers_debug["authorization"] = "REDACTED"
    logger.debug(f"Headers: {json.dumps(headers_debug)}")
    
    # Try to log request body for debugging
    try:
        body = await request.body()
        if body:
            body_text = body.decode()
            # Don't log passwords
            if "password" in body_text:
                body_text = "CONTAINS PASSWORD - REDACTED"
            logger.debug(f"Request body: {body_text}")
    except Exception as e:
        logger.debug(f"Could not log request body: {str(e)}")
    
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request processing error: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(e)}"}
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
    error_msg = f"Failed to import API routes: {str(e)}"
    logger.error(error_msg)
    logger.error(traceback.format_exc())
    
    # Tạo mock router nếu import thất bại
    from fastapi import APIRouter
    
    mock_router = APIRouter()
    
    @mock_router.get("/error")
    async def api_import_error():
        return {"error": error_msg}
    
    app.include_router(mock_router, prefix=f"{API_PREFIX}", tags=["Error"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions globally."""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"}
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

# Health check endpoints for troubleshooting
@app.get("/health", tags=["Diagnostic"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "api": "toxicity-detector",
        "timestamp": str(datetime.datetime.now())
    }

@app.get("/debug", tags=["Diagnostic"])
async def debug_info():
    """Endpoint to provide debug information."""
    try:
        # Collect debug info
        debug_data = {
            "python_version": sys.version,
            "paths": sys.path,
            "api_prefix": API_PREFIX,
            "project_name": PROJECT_NAME,
            "available_routes": [
                {"path": route.path, "name": route.name, "methods": route.methods}
                for route in app.routes
            ]
        }
        
        # Test database connection
        try:
            from backend.db.base import get_db
            db_generator = get_db()
            db = next(db_generator)
            debug_data["database"] = "Connection successful"
            try:
                db_generator.close()
            except:
                pass
        except Exception as e:
            debug_data["database"] = f"Connection error: {str(e)}"
        
        return debug_data
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

# Simple test endpoint for authentication
@app.get("/test-auth", tags=["Diagnostic"])
async def test_auth():
    """Test if auth endpoint is properly configured."""
    try:
        # Check if auth router exists
        from backend.api.routes.auth import router as auth_router
        
        # List all routes
        routes = [
            {"path": route.path, "name": route.name, "methods": route.methods}
            for route in auth_router.routes
        ]
        
        return {
            "auth_status": "configured",
            "auth_routes": routes,
            "auth_url": f"{API_PREFIX}/auth/login-json",
            "test_credentials": {
                "username": "admin@example.com",
                "password": "admin123"
            }
        }
    except Exception as e:
        return {"auth_status": "error", "message": str(e)}

# API root endpoint for health check
@app.get("/")
async def root():
    """Root endpoint providing API status information."""
    return {
        "status": "online",
        "api_version": "1.0.0",
        "service": PROJECT_NAME,
        "documentation": "/docs",
        "endpoints": f"{API_PREFIX}/auth, {API_PREFIX}/extension, {API_PREFIX}/admin",
        "health_check": "/health",
        "debug_info": "/debug"
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
        "documentation": "/docs",
        "health_check": "/health"
    }

# Test endpoint for Chrome extension CORS
@app.options(f"{API_PREFIX}/auth/login-json", include_in_schema=False)
async def auth_login_preflight():
    """Handle CORS preflight request for login-json endpoint."""
    return PlainTextResponse("")

# Test endpoint for direct form submission
@app.get(f"{API_PREFIX}/auth/login-form", include_in_schema=False)
async def login_form():
    """Provide a simple HTML form for testing login."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Login Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; }
            input[type="text"], input[type="password"] { width: 100%; padding: 8px; }
            button { padding: 8px 15px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }
            #result { margin-top: 20px; padding: 10px; border: 1px solid #ddd; display: none; }
        </style>
    </head>
    <body>
        <h1>API Login Test</h1>
        <div class="form-group">
            <label for="username">Username/Email:</label>
            <input type="text" id="username" value="admin@example.com">
        </div>
        <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" value="admin123">
        </div>
        <button id="loginBtn">Test Login</button>
        <div id="result"></div>

        <script>
            document.getElementById('loginBtn').addEventListener('click', async () => {
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                const resultDiv = document.getElementById('result');
                
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = 'Sending request...';
                
                try {
                    const response = await fetch('/api/auth/login-json', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ username, password })
                    });
                    
                    const data = await response.json();
                    resultDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
                } catch (error) {
                    resultDiv.innerHTML = 'Error: ' + error.message;
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# # Note: DO NOT include the main block that starts the server
# # This is handled by Hugging Face Space directly through Procfile# Run application when executed directly
# if __name__ == "__main__":
#     import datetime
#     port = int(settings.PORT) if hasattr(settings, "PORT") else 7860
#     logger.info(f"Starting application on port {port}")
#     uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)