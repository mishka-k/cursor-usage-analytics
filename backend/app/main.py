"""Application entrypoint for the FastAPI backend."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.analytics import analytics_router


def _register_system_routes(app: FastAPI) -> None:
    """Register auxiliary system routes such as health checks."""

    @app.get("/health", tags=["system"])
    def healthcheck() -> dict[str, str]:  # pragma: no cover - wrapper adds closure
        """Return a simple JSON payload indicating the service is healthy."""

        return {"status": "ok"}


def create_app() -> FastAPI:
    """Create and configure a :class:`FastAPI` application instance."""

    app = FastAPI(title="Cursor Usage Analytics API")

    # The dashboard is served from a different origin (Streamlit), therefore we
    # need permissive CORS settings so that it can consume the API. The
    # Streamlit container is internal to the docker-compose network, so using
    # "*" here is acceptable for the current deployment model.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(analytics_router)
    _register_system_routes(app)

    return app


app = create_app()
