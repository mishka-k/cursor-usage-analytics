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


def test_get_raw_data_returns_all_data_when_no_filters() -> None:
    """Test that get_raw_data returns all data when no filters are applied."""
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
                date=datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc),
                user="bob",
                kind="chat",
                model="gpt-3.5",
                max_mode="auto",
                input_with_cache=5,
                input_without_cache=0,
                cache_read=0,
                output_tokens=10,
                total_tokens=15,
                requests=2,
            ),
        ]
    )

    service = UsageAnalyticsService(repository)
    dataframe = service.get_raw_data()

    assert len(dataframe) == 2
    assert dataframe.iloc[0]["user"] == "bob"  # Should be sorted by date descending
    assert dataframe.iloc[1]["user"] == "alice"


def test_get_raw_data_filters_by_start_date() -> None:
    """Test that get_raw_data correctly filters by start date."""
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
                date=datetime(2024, 1, 3, 9, 0, tzinfo=timezone.utc),
                user="bob",
                kind="chat",
                model="gpt-3.5",
                max_mode="auto",
                input_with_cache=5,
                input_without_cache=0,
                cache_read=0,
                output_tokens=10,
                total_tokens=15,
                requests=2,
            ),
        ]
    )

    service = UsageAnalyticsService(repository)
    dataframe = service.get_raw_data(start_date="2024-01-02")

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["user"] == "bob"


def test_get_raw_data_filters_by_end_date() -> None:
    """Test that get_raw_data correctly filters by end date."""
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
                date=datetime(2024, 1, 3, 9, 0, tzinfo=timezone.utc),
                user="bob",
                kind="chat",
                model="gpt-3.5",
                max_mode="auto",
                input_with_cache=5,
                input_without_cache=0,
                cache_read=0,
                output_tokens=10,
                total_tokens=15,
                requests=2,
            ),
        ]
    )

    service = UsageAnalyticsService(repository)
    dataframe = service.get_raw_data(end_date="2024-01-02")

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["user"] == "alice"


def test_get_raw_data_filters_by_user() -> None:
    """Test that get_raw_data correctly filters by user."""
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
                date=datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc),
                user="bob",
                kind="chat",
                model="gpt-3.5",
                max_mode="auto",
                input_with_cache=5,
                input_without_cache=0,
                cache_read=0,
                output_tokens=10,
                total_tokens=15,
                requests=2,
            ),
        ]
    )

    service = UsageAnalyticsService(repository)
    dataframe = service.get_raw_data(user="alice")

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["user"] == "alice"


def test_get_raw_data_filters_by_date_range_and_user() -> None:
    """Test that get_raw_data correctly applies multiple filters."""
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
                date=datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc),
                user="alice",
                kind="chat",
                model="gpt-3.5",
                max_mode="auto",
                input_with_cache=5,
                input_without_cache=0,
                cache_read=0,
                output_tokens=10,
                total_tokens=15,
                requests=2,
            ),
            UsageEventDTO(
                date=datetime(2024, 1, 3, 9, 0, tzinfo=timezone.utc),
                user="bob",
                kind="chat",
                model="gpt-3.5",
                max_mode="auto",
                input_with_cache=5,
                input_without_cache=0,
                cache_read=0,
                output_tokens=10,
                total_tokens=15,
                requests=2,
            ),
        ]
    )

    service = UsageAnalyticsService(repository)
    dataframe = service.get_raw_data(start_date="2024-01-02", end_date="2024-01-02", user="alice")

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["user"] == "alice"
    assert dataframe.iloc[0]["date"] == datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc)


def test_get_raw_data_returns_empty_dataframe_when_no_matches() -> None:
    """Test that get_raw_data returns empty dataframe when no data matches filters."""
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
        ]
    )

    service = UsageAnalyticsService(repository)
    dataframe = service.get_raw_data(user="nonexistent_user")

    assert len(dataframe) == 0
    assert list(dataframe.columns) == [
        "date", "user", "kind", "model", "max_mode", "input_with_cache",
        "input_without_cache", "cache_read", "output_tokens", "total_tokens", "requests"
    ]


def test_get_raw_data_filters_by_model() -> None:
    """Test that get_raw_data correctly filters by model."""
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
                date=datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc),
                user="bob",
                kind="chat",
                model="gpt-3.5",
                max_mode="auto",
                input_with_cache=5,
                input_without_cache=0,
                cache_read=0,
                output_tokens=10,
                total_tokens=15,
                requests=2,
            ),
        ]
    )

    service = UsageAnalyticsService(repository)
    dataframe = service.get_raw_data(model="gpt-4")

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["model"] == "gpt-4"
    assert dataframe.iloc[0]["user"] == "alice"


def test_get_raw_data_filters_by_user_and_model() -> None:
    """Test that get_raw_data correctly applies user and model filters together."""
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
                date=datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc),
                user="alice",
                kind="chat",
                model="gpt-3.5",
                max_mode="auto",
                input_with_cache=5,
                input_without_cache=0,
                cache_read=0,
                output_tokens=10,
                total_tokens=15,
                requests=2,
            ),
            UsageEventDTO(
                date=datetime(2024, 1, 3, 9, 0, tzinfo=timezone.utc),
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
        ]
    )

    service = UsageAnalyticsService(repository)
    dataframe = service.get_raw_data(user="alice", model="gpt-4")

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["user"] == "alice"
    assert dataframe.iloc[0]["model"] == "gpt-4"


def test_get_raw_data_filters_by_all_parameters() -> None:
    """Test that get_raw_data correctly applies all filters together."""
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
                date=datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc),
                user="alice",
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
                date=datetime(2024, 1, 3, 9, 0, tzinfo=timezone.utc),
                user="bob",
                kind="chat",
                model="gpt-3.5",
                max_mode="auto",
                input_with_cache=5,
                input_without_cache=0,
                cache_read=0,
                output_tokens=10,
                total_tokens=15,
                requests=2,
            ),
        ]
    )

    service = UsageAnalyticsService(repository)
    dataframe = service.get_raw_data(
        start_date="2024-01-02", 
        end_date="2024-01-02", 
        user="alice", 
        model="gpt-4"
    )

    assert len(dataframe) == 1
    assert dataframe.iloc[0]["user"] == "alice"
    assert dataframe.iloc[0]["model"] == "gpt-4"
    assert dataframe.iloc[0]["date"] == datetime(2024, 1, 2, 9, 0, tzinfo=timezone.utc)

