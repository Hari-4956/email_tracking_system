from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from backend.database import init_db
from backend.config import configure_logging, get_settings

from backend.routes.tracking import router as tracking_router
from backend.routes.recipients import router as recipients_router
from backend.routes.campaigns import router as campaigns_router
from backend.routes.analytics import router as analytics_router


logger = logging.getLogger(__name__)


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()

    settings = get_settings()

    logger.info(
        "Starting E STAR Email Tracking API "
        "(env=%s, db_host=%s, base_url=%s)",
        settings.ENVIRONMENT,
        settings.safe_db_host_hint(),
        settings.BASE_URL,
    )

    # -----------------------------------------------------
    # Initialize / verify database tables
    # -----------------------------------------------------
    #
    # IMPORTANT:
    # This uses the existing init_db() function.
    #
    # It should create/check:
    #   campaigns
    #   recipients
    #   email_events
    #
    # Existing data is NOT deleted.
    # -----------------------------------------------------

    try:
        init_db()
        logger.info("Database initialization completed successfully")

    except Exception:
        logger.exception("Database initialization failed")
        raise

    yield

    logger.info("Shutting down E STAR Email Tracking API")


# =========================================================
# SETTINGS
# =========================================================

settings = get_settings()


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="E STAR Email Tracking API",
    version="1.0.0",
    description=(
        "Email open tracking, recipient/campaign APIs, and analytics. "
        "Email sending is handled externally (n8n/Gmail). "
        "Open rates reflect tracked opens, not guaranteed human opens. "
        "Tracking pixel endpoint remains public: "
        "GET /track/open/{tracking_token}."
    ),
    lifespan=lifespan,
)


# =========================================================
# CORS
# =========================================================
#
# CORS is optional and disabled unless CORS_ORIGINS
# is configured.
#
# Do not use wildcard origins in production unless
# explicitly required.
# =========================================================

cors_origins = settings.cors_origin_list()

if cors_origins:

    if "*" in cors_origins:
        logger.warning(
            "CORS_ORIGINS contains '*'; "
            "prefer explicit frontend origins in production"
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "OPTIONS"],
        allow_headers=["Accept", "Content-Type"],
    )


# =========================================================
# ROUTERS
# =========================================================

app.include_router(tracking_router)
app.include_router(recipients_router)
app.include_router(campaigns_router)
app.include_router(analytics_router)


# =========================================================
# DATABASE ERROR HANDLER
# =========================================================

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
):
    """
    Return a safe error without exposing database internals.
    """

    logger.exception(
        "Unhandled database error on %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "A database error occurred"
        },
    )


# =========================================================
# ROOT
# =========================================================

@app.get(
    "/",
    summary="Service status",
)
def root():
    return {
        "status": "online",
        "service": "E STAR Email Tracking API",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get(
    "/health",
    summary="Health check",
)
def health():
    """
    Lightweight liveness check.
    Does not expose database credentials.
    """

    return {
        "status": "healthy",
    }
