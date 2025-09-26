from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, StrictInt, StrictStr

try:  # pragma: no cover - compatibility fallback for older Pydantic versions
    from pydantic import ConfigDict
except ImportError:  # pragma: no cover
    ConfigDict = None  # type: ignore[misc,assignment]


class UsageEventDTO(BaseModel):
    """Data transfer object describing a single usage event."""

    date: datetime
    user: StrictStr
    kind: StrictStr
    model: StrictStr
    max_mode: StrictStr
    input_with_cache: StrictInt
    input_without_cache: StrictInt
    cache_read: StrictInt
    output_tokens: StrictInt
    total_tokens: StrictInt
    requests: StrictInt

    if ConfigDict is not None:  # pragma: no branch
        model_config = ConfigDict(extra="forbid")
    else:  # pragma: no cover - fallback for Pydantic v1
        class Config:  # type: ignore[no-redef]
            extra = "forbid"
