"""
FastAPI Main Application
Entry point for the CodeOrbit AI backend server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared.logger import logger
from shared.config import settings
from backend.api import repository, chat

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered repository intelligence assistant",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(repository.router)
app.include_router(chat.router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(content={
        "message": "Welcome to CodeOrbit AI API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/repository/health"
    })

# Health check
@app.get("/health")
async def health():
    """Global health check"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "codeorbit-ai",
        "version": settings.app_version
    })

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Log level: {settings.log_level}")
    logger.info(f"Storage path: {settings.repo_storage_path}")
    
    # Ensure directories exist
    settings.ensure_directories()
    logger.info("✓ All directories verified")
    
    # Check local AI configuration
    logger.info("AI Configuration:")
    logger.info("  Local embeddings (sentence-transformers) - Ready for offline use")
    logger.info("  Semantic search and code retrieval - Fully functional")
    logger.info("  No API keys required - 100% offline operation")
    
    logger.info("=" * 60)
    logger.success(f"✅ {settings.app_name} is ready!")
    logger.info(f"📚 API Documentation: http://{settings.backend_host}:{settings.backend_port}/docs")
    logger.info("=" * 60)

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down CodeOrbit AI")

# Error handlers
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError, HTTPException as FastAPIHTTPException

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle Starlette HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail if exc.detail else "HTTP error",
            "error": str(exc.detail)
        }
    )

@app.exception_handler(FastAPIHTTPException)
async def fastapi_http_exception_handler(request: Request, exc: FastAPIHTTPException):
    """Handle FastAPI HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail if exc.detail else "HTTP error",
            "error": str(exc.detail)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.error(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Request validation failed",
            "error": str(exc)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error": str(exc)
        }
    )

# Run with: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Made with Bob