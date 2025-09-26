from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from app.dto.usage_event import UsageEventDTO


_COLUMN_MAPPING = {
    "Date": "date",
    "User": "user",
    "Kind": "kind",
    "Model": "model",
    "Max Mode": "max_mode",
    "Input (w/ Cache Write)": "input_with_cache",
    "Input (w/o Cache Write)": "input_without_cache",
    "Cache Read": "cache_read",
    "Output Tokens": "output_tokens",
    "Total Tokens": "total_tokens",
    "Requests": "requests",
}


class CSVUsageRepository:
    """Repository that loads usage events from a CSV file."""

    def __init__(self, csv_path: str | Path) -> None:
        self._csv_path = Path(csv_path)

    def get_events(self) -> list[UsageEventDTO]:
        """Load events from the configured CSV file."""
        dataframe = self._load_dataframe(self._csv_path)
        return [self._row_to_dto(row) for row in dataframe.to_dict(orient="records")]

    @staticmethod
    def _load_dataframe(csv_path: Path) -> pd.DataFrame:
        dataframe = pd.read_csv(csv_path)
        missing_columns = set(_COLUMN_MAPPING) - set(dataframe.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV file {csv_path} is missing required columns: {missing}")

        dataframe = dataframe.rename(columns=_COLUMN_MAPPING)
        dataframe["date"] = pd.to_datetime(dataframe["date"], utc=True)

        # Handle NaN values in requests column - fill with 0 for errored requests
        dataframe["requests"] = dataframe["requests"].fillna(0).astype(int)
        return dataframe

    @staticmethod
    def _row_to_dto(row: dict[str, Any]) -> UsageEventDTO:
        date_value = row["date"]
        if hasattr(date_value, "to_pydatetime"):
            date_value = date_value.to_pydatetime()

        # Helper function to safely convert to int, handling NaN values
        def safe_int(value: Any) -> int:
            if pd.isna(value):
                return 0
            return int(value)

        return UsageEventDTO(
            date=date_value,
            user=str(row["user"]),
            kind=str(row["kind"]),
            model=str(row["model"]),
            max_mode=str(row["max_mode"]),
            input_with_cache=safe_int(row["input_with_cache"]),
            input_without_cache=safe_int(row["input_without_cache"]),
            cache_read=safe_int(row["cache_read"]),
            output_tokens=safe_int(row["output_tokens"]),
            total_tokens=safe_int(row["total_tokens"]),
            requests=safe_int(row["requests"]),
        )
