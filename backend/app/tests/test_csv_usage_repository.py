from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from app.dto.usage_event import UsageEventDTO
from app.repositories import CSVUsageRepository


def test_csv_usage_repository_parses_rows(tmp_path: Path) -> None:
    csv_path = tmp_path / "usage.csv"
    dataframe = pd.DataFrame(
        {
            "Date": ["2025-09-25T19:08:55.643Z"],
            "User": ["user@example.com"],
            "Kind": ["chat"],
            "Model": ["gpt-test"],
            "Max Mode": ["auto"],
            "Input (w/ Cache Write)": [10],
            "Input (w/o Cache Write)": [5],
            "Cache Read": [2],
            "Output Tokens": [15],
            "Total Tokens": [25],
            "Requests": [1.0],
        }
    )
    dataframe.to_csv(csv_path, index=False)

    repository = CSVUsageRepository(csv_path)
    events = repository.get_events()

    assert len(events) == 1
    event = events[0]

    assert isinstance(event, UsageEventDTO)

    assert event.date == datetime(2025, 9, 25, 19, 8, 55, 643000, tzinfo=timezone.utc)
    assert event.user == "user@example.com"
    assert event.kind == "chat"
    assert event.model == "gpt-test"
    assert event.max_mode == "auto"
    assert event.input_with_cache == 10
    assert event.input_without_cache == 5
    assert event.cache_read == 2
    assert event.output_tokens == 15
    assert event.total_tokens == 25
    assert event.requests == 1
