from __future__ import annotations

import pandas as pd
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers.analytics import (
    analytics_router,
    get_usage_analytics_service,
)


class DummyUsageAnalyticsService:
    def tokens_per_user(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"user": "alice", "total_tokens": 100},
                {"user": "bob", "total_tokens": 50},
            ]
        )


def test_tokens_per_user_endpoint_returns_expected_payload() -> None:
    app = FastAPI()
    app.include_router(analytics_router)

    dummy_service = DummyUsageAnalyticsService()
    app.dependency_overrides[get_usage_analytics_service] = lambda: dummy_service

    client = TestClient(app)

    response = client.get("/analytics/tokens_per_user")

    assert response.status_code == 200
    assert response.json() == [
        {"user": "alice", "total_tokens": 100},
        {"user": "bob", "total_tokens": 50},
    ]

