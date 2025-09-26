"""API router that exposes usage analytics endpoints."""

from __future__ import annotations

from os import getenv
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder

from app.repositories import CSVUsageRepository
from app.services import UsageAnalyticsService


_DEFAULT_CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "usage.csv"


def _resolve_csv_path() -> Path:
    """Return the CSV path configured for usage analytics."""

    csv_path = getenv("USAGE_CSV_PATH")
    if csv_path:
        return Path(csv_path)
    return _DEFAULT_CSV_PATH


def get_usage_analytics_service() -> UsageAnalyticsService:
    """Provide an instance of :class:`UsageAnalyticsService`."""

    repository = CSVUsageRepository(_resolve_csv_path())
    return UsageAnalyticsService(repository)


analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])


@analytics_router.get("/events_per_day")
def get_events_per_day(
    service: UsageAnalyticsService = Depends(get_usage_analytics_service),
) -> list[dict[str, Any]]:
    """Return total number of requests per day as JSON."""

    dataframe = service.events_per_day()
    records = dataframe.to_dict(orient="records")
    return jsonable_encoder(records)


@analytics_router.get("/tokens_per_user")
def get_tokens_per_user(
    service: UsageAnalyticsService = Depends(get_usage_analytics_service),
) -> list[dict[str, Any]]:
    """Return total tokens consumed per user as JSON."""

    dataframe = service.tokens_per_user()
    records = dataframe.to_dict(orient="records")
    return jsonable_encoder(records)


@analytics_router.get("/tokens_by_model")
def get_tokens_by_model(
    service: UsageAnalyticsService = Depends(get_usage_analytics_service),
) -> list[dict[str, Any]]:
    """Return total tokens consumed per model as JSON."""

    dataframe = service.tokens_by_model()
    records = dataframe.to_dict(orient="records")
    return jsonable_encoder(records)


@analytics_router.get("/raw_data")
def get_raw_data(
    start_date: str | None = Query(None, description="Start date in ISO format (e.g., 2025-09-25)"),
    end_date: str | None = Query(None, description="End date in ISO format (e.g., 2025-09-26)"),
    user: str | None = Query(None, description="Filter by specific user email"),
    model: str | None = Query(None, description="Filter by specific model name"),
    _t: str | None = Query(None, description="Timestamp to prevent caching (ignored)"),
    service: UsageAnalyticsService = Depends(get_usage_analytics_service),
) -> list[dict[str, Any]]:
    """Return raw usage data with optional filtering by date range, user, and model."""

    dataframe = service.get_raw_data(start_date=start_date, end_date=end_date, user=user, model=model)
    records = dataframe.to_dict(orient="records")
    return jsonable_encoder(records)
