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

    def get_raw_data(self, start_date: str | None = None, end_date: str | None = None, user: str | None = None, model: str | None = None) -> pd.DataFrame:
        # Return test data that can be filtered
        all_data = [
            {
                "date": "2024-01-01T12:00:00Z",
                "user": "alice",
                "kind": "chat",
                "model": "gpt-4",
                "max_mode": "auto",
                "input_with_cache": 10,
                "input_without_cache": 0,
                "cache_read": 0,
                "output_tokens": 15,
                "total_tokens": 25,
                "requests": 1,
            },
            {
                "date": "2024-01-02T09:00:00Z",
                "user": "bob",
                "kind": "chat",
                "model": "gpt-3.5",
                "max_mode": "auto",
                "input_with_cache": 5,
                "input_without_cache": 0,
                "cache_read": 0,
                "output_tokens": 10,
                "total_tokens": 15,
                "requests": 2,
            },
        ]
        
        # Simple filtering logic for testing
        filtered_data = all_data
        if user:
            filtered_data = [item for item in filtered_data if item["user"] == user]
        if model:
            filtered_data = [item for item in filtered_data if item["model"] == model]
        if start_date:
            filtered_data = [item for item in filtered_data if item["date"] >= start_date]
        if end_date:
            filtered_data = [item for item in filtered_data if item["date"] <= end_date]
            
        return pd.DataFrame(filtered_data)


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


def test_raw_data_endpoint_returns_all_data_without_filters() -> None:
    """Test that /analytics/raw_data returns all data when no query parameters are provided."""
    app = FastAPI()
    app.include_router(analytics_router)

    dummy_service = DummyUsageAnalyticsService()
    app.dependency_overrides[get_usage_analytics_service] = lambda: dummy_service

    client = TestClient(app)

    response = client.get("/analytics/raw_data")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["user"] == "alice"
    assert data[1]["user"] == "bob"


def test_raw_data_endpoint_filters_by_user() -> None:
    """Test that /analytics/raw_data correctly filters by user parameter."""
    app = FastAPI()
    app.include_router(analytics_router)

    dummy_service = DummyUsageAnalyticsService()
    app.dependency_overrides[get_usage_analytics_service] = lambda: dummy_service

    client = TestClient(app)

    response = client.get("/analytics/raw_data?user=alice")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user"] == "alice"


def test_raw_data_endpoint_filters_by_start_date() -> None:
    """Test that /analytics/raw_data correctly filters by start_date parameter."""
    app = FastAPI()
    app.include_router(analytics_router)

    dummy_service = DummyUsageAnalyticsService()
    app.dependency_overrides[get_usage_analytics_service] = lambda: dummy_service

    client = TestClient(app)

    response = client.get("/analytics/raw_data?start_date=2024-01-02")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user"] == "bob"


def test_raw_data_endpoint_filters_by_end_date() -> None:
    """Test that /analytics/raw_data correctly filters by end_date parameter."""
    app = FastAPI()
    app.include_router(analytics_router)

    dummy_service = DummyUsageAnalyticsService()
    app.dependency_overrides[get_usage_analytics_service] = lambda: dummy_service

    client = TestClient(app)

    response = client.get("/analytics/raw_data?end_date=2024-01-01T23:59:59Z")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user"] == "alice"


def test_raw_data_endpoint_filters_by_multiple_parameters() -> None:
    """Test that /analytics/raw_data correctly applies multiple filters."""
    app = FastAPI()
    app.include_router(analytics_router)

    dummy_service = DummyUsageAnalyticsService()
    app.dependency_overrides[get_usage_analytics_service] = lambda: dummy_service

    client = TestClient(app)

    response = client.get("/analytics/raw_data?start_date=2024-01-01&end_date=2024-01-01T23:59:59Z&user=alice")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user"] == "alice"


def test_raw_data_endpoint_returns_empty_list_when_no_matches() -> None:
    """Test that /analytics/raw_data returns empty list when no data matches filters."""
    app = FastAPI()
    app.include_router(analytics_router)

    dummy_service = DummyUsageAnalyticsService()
    app.dependency_overrides[get_usage_analytics_service] = lambda: dummy_service

    client = TestClient(app)

    response = client.get("/analytics/raw_data?user=nonexistent")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_raw_data_endpoint_filters_by_model() -> None:
    """Test that /analytics/raw_data correctly filters by model parameter."""
    app = FastAPI()
    app.include_router(analytics_router)

    dummy_service = DummyUsageAnalyticsService()
    app.dependency_overrides[get_usage_analytics_service] = lambda: dummy_service

    client = TestClient(app)

    response = client.get("/analytics/raw_data?model=gpt-4")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["model"] == "gpt-4"
    assert data[0]["user"] == "alice"


def test_raw_data_endpoint_filters_by_user_and_model() -> None:
    """Test that /analytics/raw_data correctly applies user and model filters together."""
    app = FastAPI()
    app.include_router(analytics_router)

    dummy_service = DummyUsageAnalyticsService()
    app.dependency_overrides[get_usage_analytics_service] = lambda: dummy_service

    client = TestClient(app)

    response = client.get("/analytics/raw_data?user=alice&model=gpt-4")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user"] == "alice"
    assert data[0]["model"] == "gpt-4"


def test_raw_data_endpoint_filters_by_all_parameters_including_model() -> None:
    """Test that /analytics/raw_data correctly applies all filters including model."""
    app = FastAPI()
    app.include_router(analytics_router)

    dummy_service = DummyUsageAnalyticsService()
    app.dependency_overrides[get_usage_analytics_service] = lambda: dummy_service

    client = TestClient(app)

    response = client.get("/analytics/raw_data?start_date=2024-01-01&end_date=2024-01-01T23:59:59Z&user=alice&model=gpt-4")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user"] == "alice"
    assert data[0]["model"] == "gpt-4"

