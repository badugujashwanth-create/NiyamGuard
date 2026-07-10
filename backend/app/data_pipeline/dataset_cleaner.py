from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from app.config import SEED_KNOWLEDGE_PATH, settings

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
AADHAAR_RE = re.compile(r"(?<!\d)(?:\d[ -]?){12}(?!\d)")
PHONE_RE = re.compile(r"(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)")


def redact_pii(text: str) -> str:
    cleaned = EMAIL_RE.sub("[REDACTED_EMAIL]", text)
    cleaned = PHONE_RE.sub("[REDACTED_PHONE]", cleaned)
    cleaned = AADHAAR_RE.sub("[REDACTED_ID]", cleaned)
    return cleaned


def detect_language(text: str) -> str:
    if re.search(r"[\u0c00-\u0c7f]", text):
        return "te"
    if re.search(r"[\u0900-\u097f]", text):
        return "hi"
    if re.search(r"[\u0c00-\u0c7f\u0900-\u097f]", text):
        return "mixed"
    return "en" if re.search(r"[A-Za-z]", text) else "unknown"


def chunk_id_for(*parts: str) -> str:
    digest = hashlib.sha256("::".join(parts).encode("utf-8")).hexdigest()[:16]
    return f"chunk_{digest}"


def _source_from_record(record: dict[str, Any]) -> dict[str, Any]:
    source = record.get("source") if isinstance(record.get("source"), dict) else {}
    return {
        "type": str(source.get("type") or "seed"),
        "label": str(source.get("label") or "NiyamGuard knowledge source"),
        "verified": bool(source.get("verified", False)),
    }


def seed_record_to_chunk(record: dict[str, Any]) -> dict[str, Any]:
    source = _source_from_record(record)
    validity = record.get("validity") if isinstance(record.get("validity"), dict) else {}
    sections = [
        f"Service: {record.get('title', '')}",
        f"Description: {record.get('description', '')}",
        "Eligibility: " + "; ".join(record.get("eligibility") or []),
        "Required documents: " + "; ".join(record.get("required_documents") or []),
        "Process steps: " + " ".join(
            f"{index + 1}. {step}" for index, step in enumerate(record.get("process_steps") or [])
        ),
        f"Validity: {validity.get('value', 'Verified data not available')}",
    ]
    text = redact_pii("\n".join(section for section in sections if section.strip()))
    service_id = str(record.get("service_id") or "unknown")
    return {
        "chunk_id": chunk_id_for(service_id, str(record.get("title") or ""), text),
        "title": str(record.get("title") or service_id.replace("_", " ").title()),
        "service_id": service_id,
        "text": text,
        "language": "en",
        "source_type": source["type"],
        "source_label": source["label"],
        "verified": source["verified"],
        "metadata": {
            "language_support": record.get("language_support", []),
            "validity": validity,
        },
    }


def clean_seed_knowledge(seed_path: Path = SEED_KNOWLEDGE_PATH) -> list[dict[str, Any]]:
    with seed_path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)
    return [seed_record_to_chunk(record) for record in records]


def _json_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("records", "items", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [payload]
    return []


def _csv_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _text_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [{"title": path.stem, "text": text}]


def _record_text(record: dict[str, Any]) -> str:
    if isinstance(record.get("text"), str):
        return record["text"]
    parts = []
    for key, value in record.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            value = "; ".join(str(item) for item in value)
        elif isinstance(value, dict):
            value = json.dumps(value, ensure_ascii=False)
        parts.append(f"{key}: {value}")
    return "\n".join(parts)


def clean_dataset_file(
    path: Path,
    *,
    source_type: str = "kaggle",
    source_label: str | None = None,
    verified: bool = False,
) -> list[dict[str, Any]]:
    suffix = path.suffix.casefold()
    if suffix == ".json":
        records = _json_records(path)
    elif suffix == ".csv":
        records = _csv_records(path)
    elif suffix in {".txt", ".md", ".markdown"}:
        records = _text_records(path)
    else:
        return []

    chunks: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        text = redact_pii(_record_text(record)).strip()
        if not text:
            continue
        title = str(record.get("title") or record.get("name") or path.stem)
        service_id = str(record.get("service_id") or record.get("service") or "unknown")
        chunks.append(
            {
                "chunk_id": chunk_id_for(str(path), str(index), text),
                "title": title,
                "service_id": service_id,
                "text": text,
                "language": detect_language(text),
                "source_type": source_type,
                "source_label": source_label or path.name,
                "verified": verified,
                "metadata": {"file_name": path.name, "row_index": index},
            }
        )
    return chunks


def clean_input_path(input_path: Path) -> list[dict[str, Any]]:
    if not input_path.exists():
        return []
    if input_path.is_file():
        return clean_dataset_file(input_path)
    chunks: list[dict[str, Any]] = []
    for path in sorted(input_path.rglob("*")):
        if path.is_file() and path.suffix.casefold() in {".csv", ".json", ".txt", ".md", ".markdown"}:
            chunks.extend(clean_dataset_file(path))
    return chunks


def write_chunks(chunks: list[dict[str, Any]], output_dir: Path, filename: str = "chunks.json") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(chunks, handle, ensure_ascii=False, indent=2)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean public datasets into NiyamGuard RAG chunks.")
    parser.add_argument("--input", default=str(settings.dataset_dir), help="CSV, JSON, TXT, MD file or directory.")
    parser.add_argument("--output", default=str(settings.processed_dataset_dir), help="Output directory.")
    parser.add_argument("--include-seed", action="store_true", help="Include committed seed knowledge.")
    args = parser.parse_args()

    chunks = clean_input_path(Path(args.input))
    if args.include_seed or not chunks:
        chunks.extend(clean_seed_knowledge())
    output_path = write_chunks(chunks, Path(args.output))
    print(f"Wrote {len(chunks)} chunks to {output_path}")


if __name__ == "__main__":
    main()
