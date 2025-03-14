"""
Main entry point for Toxicity Detector FastAPI application.
"""

import sys
import logging
import os
from pathlib import Path
import json
import traceback
import datetime
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Cấu hình logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Thêm thư mục gốc vào path
project_root = Path(__file__).parent.resolve()
sys.path.append(str(project_root))

# Import settings
try:
    from backend.config.settings import settings
    API_PREFIX = settings.API_V1_STR
    PROJECT_NAME = settings.PROJECT_NAME
except ImportError:
    logger.warning("Cannot import settings. Using default values.")
    API_PREFIX = "/api"
    PROJECT_NAME = "Toxicity Detector API"

# Khởi tạo lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application")
    try:
        from backend.db.base import init_db
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        logger.error(traceback.format_exc())
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

# Tạo ứng dụng FastAPI
app = FastAPI(
    title=PROJECT_NAME,
    description="API for detecting toxic, offensive, hate speech and spam content on social media",
    version="1.0.0",
    lifespan=lifespan,
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex="chrome-extension://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"],
)

# Middleware ghi log request và response
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url.path}")
    
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

# Import và đăng ký routes
try:
    from backend.api.routes import admin, auth, extension
    
    app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
    app.include_router(extension.router, prefix=f"{API_PREFIX}/extension", tags=["Extension"])
    app.include_router(admin.router, prefix=f"{API_PREFIX}/admin", tags=["Admin"])
    
    logger.info("API routes registered successfully")
except ImportError as e:
    error_msg = f"Failed to import API routes: {str(e)}"
    logger.error(error_msg)
    logger.error(traceback.format_exc())

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "api": "toxicity-detector",
        "timestamp": str(datetime.datetime.now())
    }

# Debug endpoint
@app.get("/debug")
async def debug_info():
    try:
        # Collect debug info
        debug_data = {
            "python_version": sys.version,
            "api_prefix": API_PREFIX,
            "routes": [
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
            
            # Clean up
            try:
                next(db_generator, None)
            except StopIteration:
                pass
        except Exception as e:
            debug_data["database"] = f"Connection error: {str(e)}"
        
        return debug_data
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

# Root endpoint
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": PROJECT_NAME,
        "api_version": "1.0.0",
        "endpoints": f"{API_PREFIX}/auth, {API_PREFIX}/extension, {API_PREFIX}/admin",
        "health_check": "/health",
        "debug": "/debug"
    }

# API base endpoint
@app.get(f"{API_PREFIX}")
async def api_root():
    return {
        "message": f"{PROJECT_NAME} is operational",
        "available_endpoints": {
            "authentication": f"{API_PREFIX}/auth",
            "content_analysis": f"{API_PREFIX}/extension",
            "administration": f"{API_PREFIX}/admin"
        },
        "documentation": "/docs"
    }

# Entry point khi chạy script trực tiếp
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    logger.info(f"Starting application on port {port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)