from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any


SEARCH_TERMS = [
    "government schemes india",
    "indian government schemes",
    "public welfare schemes india",
    "government circulars india",
    "policy documents india",
    "meeseva services",
    "income certificate",
    "caste certificate",
    "ration card scheme",
    "scholarship scheme india",
]


@dataclass(frozen=True)
class DatasetMetadata:
    dataset_name: str
    source: str
    url_or_slug: str
    license: str | None
    downloaded_at: str
    used_for: str


def metadata_for(
    *,
    dataset_name: str,
    source: str,
    url_or_slug: str,
    license: str | None = None,
    used_for: str = "rag_knowledge_source",
) -> dict[str, Any]:
    return asdict(
        DatasetMetadata(
            dataset_name=dataset_name,
            source=source,
            url_or_slug=url_or_slug,
            license=license,
            downloaded_at=datetime.now(timezone.utc).isoformat(),
            used_for=used_for,
        )
    )
