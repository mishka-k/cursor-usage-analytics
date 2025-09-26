from __future__ import annotations

from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app.main import create_app


def test_create_app_registers_analytics_routes() -> None:
    app = create_app()

    routes = {route.path for route in app.router.routes}

    assert "/analytics/events_per_day" in routes
    assert "/analytics/tokens_per_user" in routes
    assert "/analytics/tokens_by_model" in routes


def test_app_has_cors_enabled_for_dashboard() -> None:
    app = create_app()

    middleware_classes = {middleware.cls for middleware in app.user_middleware}

    assert CORSMiddleware in middleware_classes


def test_healthcheck_endpoint_returns_ok() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
