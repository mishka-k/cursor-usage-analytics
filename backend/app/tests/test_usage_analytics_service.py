from __future__ import annotations

from datetime import datetime, timezone

from app.dto.usage_event import UsageEventDTO
from app.repositories import CSVUsageRepository
from app.services import UsageAnalyticsService


class DummyCSVUsageRepository(CSVUsageRepository):
    """Test double that returns predefined events."""

    def __init__(self, events: list[UsageEventDTO]):
        self._events = events

    def get_events(self) -> list[UsageEventDTO]:
        return list(self._events)


def test_events_per_day_aggregates_requests() -> None:
    repository = DummyCSVUsageRepository(
        [
            UsageEventDTO(
                date=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
                user="alice",
                kind="chat",
                model="gpt-4",
                max_mode="auto",
                input_with_cache=10,
                input_without_cache=0,
                cache_read=0,
                output_tokens=15,
                total_tokens=25,
                requests=1,
            ),
            UsageEventDTO(
                date=datetime(2024, 1, 1, 13, 0, tzinfo=timezone.utc),
                user="bob",
                kind="chat",
                model="gpt-4",
                max_mode="auto",
                input_with_cache=5,
                input_without_cache=0,
                cache_read=0,
                output_tokens=10,
                total_tokens=15,
                requests=2,
            ),
            UsageEventDTO(
                date=datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc),
                user="alice",
                kind="chat",
                model="gpt-4",
                max_mode="auto",
                input_with_cache=2,
                input_without_cache=0,
                cache_read=0,
                output_tokens=3,
                total_tokens=5,
                requests=5,
            ),
        ]
    )

    service = UsageAnalyticsService(repository)

    dataframe = service.events_per_day()

    assert list(dataframe.columns) == ["date", "requests_count"]
    assert dataframe.to_dict(orient="records") == [
        {"date": datetime(2024, 1, 1, tzinfo=timezone.utc).date(), "requests_count": 3},
        {"date": datetime(2024, 1, 2, tzinfo=timezone.utc).date(), "requests_count": 5},
    ]

