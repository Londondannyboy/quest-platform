"""
Quest Platform v2.2 - FastAPI Main Application
API Gateway for article generation and job status endpoints
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from prometheus_client import make_asgi_app

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis_client import init_redis, close_redis
from app.api import articles, jobs, health

# Setup structured logging
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events
    """
    # Startup
    logger.info("quest.startup", env=settings.APP_ENV, port=settings.API_PORT)

    # Initialize database connection pool
    await init_db()
    logger.info("quest.database.connected", pool_size=settings.DB_POOL_SIZE)

    # Initialize Redis connection (optional for now)
    try:
        await init_redis()
        logger.info("quest.redis.connected", url=settings.REDIS_URL.split("@")[1] if "@" in settings.REDIS_URL else "localhost")
    except Exception as e:
        logger.warning("quest.redis.connection_failed", error=str(e), msg="Continuing without Redis - queue features disabled")
        # Continue without Redis - queue features will be disabled

    yield

    # Shutdown
    logger.info("quest.shutdown")
    await close_redis()
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Quest Content Intelligence Platform",
    description="AI-powered multi-site content generation API",
    version="2.2.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(
        "quest.request",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else "unknown",
    )

    response = await call_next(request)

    logger.info(
        "quest.response",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    )

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "quest.error",
        error=str(exc),
        path=request.url.path,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred",
        },
    )


# ============================================================================
# ROUTERS
# ============================================================================

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(articles.router, prefix="/api/articles", tags=["Articles"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])

# Prometheus metrics endpoint
if settings.PROMETHEUS_ENABLED:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


# ============================================================================
# ROOT ENDPOINTS
# ============================================================================


@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "Quest Content Intelligence Platform",
        "version": "2.2.0",
        "status": "operational",
        "docs": "/docs" if settings.DEBUG else "disabled",
        "health": "/api/health",
    }


@app.get("/api/info")
async def api_info():
    """
    API information and configuration
    """
    return {
        "version": "2.2.0",
        "environment": settings.APP_ENV,
        "features": {
            "image_generation": settings.ENABLE_IMAGE_GENERATION,
            "hitl_review": settings.ENABLE_HITL_REVIEW,
            "auto_publish": settings.ENABLE_AUTO_PUBLISH,
            "batch_api": settings.ENABLE_BATCH_API,
        },
        "limits": {
            "daily_cost_cap": float(settings.DAILY_COST_CAP),
            "per_job_cost_cap": float(settings.PER_JOB_COST_CAP),
            "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
