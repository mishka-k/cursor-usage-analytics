"""Service layer for building usage analytics aggregates."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd

from app.dto.usage_event import UsageEventDTO
from app.repositories.csv_usage_repository import CSVUsageRepository


class UsageAnalyticsService:
    """Service that provides aggregated analytics over usage events."""

    def __init__(self, repository: CSVUsageRepository) -> None:
        self._repository = repository

    def events_per_day(self) -> pd.DataFrame:
        """Return the total number of requests per day."""

        dataframe = self._load_dataframe()
        if dataframe.empty:
            return pd.DataFrame(columns=["date", "requests_count"])

        grouped = (
            dataframe.assign(date=dataframe["date"].dt.date)
            .groupby("date", as_index=False)["requests"]
            .sum()
            .rename(columns={"requests": "requests_count"})
            .sort_values("date", ignore_index=True)
        )
        return grouped

    def tokens_per_user(self) -> pd.DataFrame:
        """Return the total number of tokens consumed per user."""

        dataframe = self._load_dataframe()
        if dataframe.empty:
            return pd.DataFrame(columns=["user", "total_tokens"])

        grouped = (
            dataframe.groupby("user", as_index=False)["total_tokens"]
            .sum()
            .sort_values("user", ignore_index=True)
        )
        return grouped

    def tokens_by_model(self) -> pd.DataFrame:
        """Return the total number of tokens consumed per model."""

        dataframe = self._load_dataframe()
        if dataframe.empty:
            return pd.DataFrame(columns=["model", "total_tokens"])

        grouped = (
            dataframe.groupby("model", as_index=False)["total_tokens"]
            .sum()
            .sort_values("model", ignore_index=True)
        )
        return grouped

    def _load_dataframe(self) -> pd.DataFrame:
        events = self._repository.get_events()
        if not events:
            return pd.DataFrame(columns=self._dataframe_columns())

        return pd.DataFrame.from_records(
            (self._event_to_dict(event) for event in events),
            columns=self._dataframe_columns(),
        )

    @staticmethod
    def _event_to_dict(event: UsageEventDTO) -> dict[str, Any]:
        if hasattr(event, "model_dump"):
            return event.model_dump(mode="python")  # type: ignore[call-arg]
        return event.dict()

    @staticmethod
    def _dataframe_columns() -> Sequence[str]:
        return [
            "date",
            "user",
            "kind",
            "model",
            "max_mode",
            "input_with_cache",
            "input_without_cache",
            "cache_read",
            "output_tokens",
            "total_tokens",
            "requests",
        ]

