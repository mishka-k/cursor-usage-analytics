"""API router that exposes usage analytics endpoints."""

from __future__ import annotations

from os import getenv
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
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
