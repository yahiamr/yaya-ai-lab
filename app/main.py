"""
Application entrypoint.

- Defines a create_app() factory that builds and configures the FastAPI app.
- Exposes 'app' for ASGI servers (e.g. uvicorn app.main:app).
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import get_settings, Settings
from app.core.logging import configure_logging, get_logger


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    Steps:
    - Load settings using get_settings()
    - Configure logging with configure_logging(settings)
    - Create the FastAPI() instance with basic metadata
    - Register routes
    - Register startup event handler
    - Return the app
    """
    # Load configuration (reads env variables / .env)
    settings = get_settings()

    # Configure logging according to settings.DEBUG, etc.
    configure_logging(settings)

    # Create the FastAPI application instance
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        version="0.1.0",
    )

    # Register all routes/endpoints for the app
    register_routes(app)

    # Example of a startup event handler
    @app.on_event("startup")
    async def on_startup() -> None:
        """
        Startup hook for the application.

        Later, you can:
        - Test DB connectivity.
        - Warm up vector store connections.
        - Log startup information.
        """
        logger = get_logger("app.startup")
        logger.info("Application startup complete.", extra={"env": settings.APP_ENV})

    return app


def register_routes(app: FastAPI) -> None:
    """
    Attach all routes to the application.

    For Phase 1:
    - Implement a simple /health endpoint that returns {"status": "ok"}.
    - Later, include versioned routers (e.g. /api/v1).
    """

    logger = get_logger("app.routes")

    @app.get("/health", tags=["system"], response_class=JSONResponse)
    async def health() -> JSONResponse:
        """
        Health check endpoint.

        For now, just returns a static JSON payload.
        Later, you can check DB/vector-store connectivity here.
        """
        logger.debug("Health check called.")
        return JSONResponse({"status": "ok"})

    # Future:
    # from app.api.v1.router import api_router
    # app.include_router(api_router, prefix="/api/v1")


# Global app instance for ASGI servers
app = create_app()