from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from app.config import settings
from app.data_pipeline.dataset_cleaner import chunk_id_for, clean_seed_knowledge, redact_pii, write_chunks
from app.data_pipeline.rag_indexer import build_index
from app.repositories.dataset_repository import dataset_repository

PACK_VERSION = "niyamguard_dataset_pack_v1"

COLLECTION_FILES = {
    "regulators": "raw/regulators.csv",
    "regulatory_circulars": "raw/regulatory_circulars.csv",
    "internal_policies": "raw/internal_policies.csv",
    "obligations": "processed/obligations.csv",
    "policy_obligation_mapping": "processed/policy_obligation_mapping.csv",
    "controls": "processed/controls.csv",
    "compliance_evidence": "processed/compliance_evidence.csv",
    "gap_findings": "processed/gap_findings.csv",
    "regulatory_drift_cases": "processed/regulatory_drift_cases.csv",
    "risk_scoring_labels": "processed/risk_scoring_labels.csv",
    "organizations": "app_seed/organizations.csv",
    "dataset_users": "app_seed/users.csv",
    "dataset_audit_events": "app_seed/audit_events.csv",
    "policy_qa_pairs": "ml/policy_qa_pairs.csv",
    "intent_classification": "ml/intent_classification.csv",
    "api_test_cases": "ml/api_test_cases.csv",
    "rag_documents": "ml/rag_documents.jsonl",
    "instruction_tuning_dataset": "ml/instruction_tuning_dataset.jsonl",
    "instruction_train": "ml/instruction_train.jsonl",
    "instruction_validation": "ml/instruction_validation.jsonl",
    "instruction_test": "ml/instruction_test.jsonl",
}

ID_COLUMNS = {
    "regulators": "regulator_code",
    "regulatory_circulars": "circular_id",
    "internal_policies": "policy_id",
    "obligations": "obligation_id",
    "policy_obligation_mapping": "mapping_id",
    "controls": "control_id",
    "compliance_evidence": "evidence_id",
    "gap_findings": "finding_id",
    "regulatory_drift_cases": "drift_id",
    "risk_scoring_labels": "risk_id",
    "organizations": "org_id",
    "dataset_users": "user_id",
    "dataset_audit_events": "audit_id",
    "policy_qa_pairs": "qa_id",
    "intent_classification": "example_id",
    "api_test_cases": "test_id",
    "rag_documents": "doc_id",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pack_dir(pack_dir: Path | None = None) -> Path:
    return pack_dir or settings.dataset_pack_dir


def _read_csv(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


def _read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def _records_for_file(
    collection: str,
    relative_path: str,
    pack_dir: Path,
    imported_at: str,
) -> list[dict[str, Any]]:
    path = pack_dir / relative_path
    if not path.exists():
        return []
    rows = _read_jsonl(path) if path.suffix == ".jsonl" else _read_csv(path)
    id_column = ID_COLUMNS.get(collection)
    records = []
    for index, payload in enumerate(rows, start=1):
        item_id = str(payload.get(id_column) or payload.get("id") or f"{collection}_{index:06d}")
        records.append(
            {
                "collection": collection,
                "item_id": item_id,
                "source_file": relative_path.replace("\\", "/"),
                "payload": payload,
                "imported_at": imported_at,
            }
        )
    return records


def load_pack_records(pack_dir: Path | None = None) -> list[dict[str, Any]]:
    root = _pack_dir(pack_dir)
    imported_at = _now()
    records: list[dict[str, Any]] = []
    for collection, relative_path in COLLECTION_FILES.items():
        records.extend(_records_for_file(collection, relative_path, root, imported_at))
    return records


def import_dataset_pack(pack_dir: Path | None = None, *, pack_version: str = PACK_VERSION) -> dict[str, Any]:
    records = load_pack_records(pack_dir)
    return dataset_repository.replace_pack_records(pack_version, records)


def _chunk(
    *,
    item_id: str,
    title: str,
    text: str,
    service_id: str,
    source_type: str,
    source_label: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    clean_text = redact_pii(text).strip()
    return {
        "chunk_id": chunk_id_for(source_type, item_id, clean_text),
        "title": title,
        "service_id": service_id,
        "text": clean_text,
        "language": "en",
        "source_type": source_type,
        "source_label": source_label,
        "verified": False,
        "metadata": metadata,
    }


def dataset_pack_chunks(pack_dir: Path | None = None) -> list[dict[str, Any]]:
    root = _pack_dir(pack_dir)
    chunks: list[dict[str, Any]] = []

    for row in _read_jsonl(root / "ml" / "rag_documents.jsonl"):
        metadata = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
        chunks.append(
            _chunk(
                item_id=str(row["doc_id"]),
                title=str(row.get("title") or row["doc_id"]),
                text=str(row.get("text") or ""),
                service_id=str(row.get("doc_type") or "rag_document"),
                source_type=str(row.get("doc_type") or "rag_document"),
                source_label="NiyamGuard dataset RAG documents",
                metadata={**metadata, "doc_id": row["doc_id"], "source_file": "ml/rag_documents.jsonl"},
            )
        )

    for row in _read_csv(root / "raw" / "regulatory_circulars.csv"):
        text = "\n".join([str(row.get("summary") or ""), str(row.get("full_text") or "")])
        chunks.append(
            _chunk(
                item_id=row["circular_id"],
                title=row["title"],
                text=text,
                service_id=row["circular_id"],
                source_type="regulatory_circular",
                source_label=row["circular_id"],
                metadata={
                    "circular_id": row["circular_id"],
                    "regulator_code": row.get("regulator_code"),
                    "sector": row.get("sector"),
                    "category": row.get("category"),
                    "effective_date": row.get("effective_date"),
                    "risk_category": row.get("severity"),
                    "source_file": "raw/regulatory_circulars.csv",
                },
            )
        )

    for row in _read_csv(root / "raw" / "internal_policies.csv"):
        chunks.append(
            _chunk(
                item_id=row["policy_id"],
                title=row["policy_title"],
                text=str(row.get("policy_text") or ""),
                service_id=row["org_id"],
                source_type="internal_policy",
                source_label=row["policy_id"],
                metadata={
                    "policy_id": row["policy_id"],
                    "org_id": row.get("org_id"),
                    "department": row.get("department"),
                    "effective_date": row.get("effective_from"),
                    "source_file": "raw/internal_policies.csv",
                },
            )
        )

    for row in _read_csv(root / "processed" / "obligations.csv"):
        chunks.append(
            _chunk(
                item_id=row["obligation_id"],
                title=f"{row['obligation_id']} {row.get('category', '')}",
                text=str(row.get("obligation_text") or ""),
                service_id=row["circular_id"],
                source_type="obligation",
                source_label=row["obligation_id"],
                metadata={
                    "obligation_id": row["obligation_id"],
                    "circular_id": row.get("circular_id"),
                    "regulator_code": row.get("regulator_code"),
                    "sector": row.get("sector"),
                    "category": row.get("category"),
                    "risk_category": row.get("penalty_risk"),
                    "risk_weight": row.get("risk_weight"),
                    "source_file": "processed/obligations.csv",
                },
            )
        )

    for row in _read_csv(root / "ml" / "policy_qa_pairs.csv"):
        text = f"Question: {row.get('user_question')}\nAnswer: {row.get('expected_answer')}"
        chunks.append(
            _chunk(
                item_id=row["qa_id"],
                title=row["user_question"],
                text=text,
                service_id=str(row.get("linked_org_id") or row.get("linked_circular_id") or "policy_qa"),
                source_type="policy_qa_pair",
                source_label=row["qa_id"],
                metadata={
                    "qa_id": row["qa_id"],
                    "intent": row.get("intent"),
                    "circular_id": row.get("linked_circular_id"),
                    "obligation_id": row.get("linked_obligation_id"),
                    "org_id": row.get("linked_org_id"),
                    "source_file": "ml/policy_qa_pairs.csv",
                },
            )
        )
    return [chunk for chunk in chunks if chunk["text"]]


def build_dataset_pack_index(
    pack_dir: Path | None = None,
    output_path: Path | None = None,
) -> dict[str, Any]:
    chunks = dataset_pack_chunks(pack_dir) + clean_seed_knowledge()
    write_chunks(chunks, settings.processed_dataset_dir, "dataset_pack_chunks.json")
    return build_index(chunks, output_path or settings.rag_index_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import and index the NiyamGuard synthetic dataset pack.")
    parser.add_argument("--pack", default=str(settings.dataset_pack_dir), help="Extracted dataset pack directory.")
    parser.add_argument("--import-db", action="store_true", help="Import all pack files into the app database.")
    parser.add_argument("--build-rag", action="store_true", help="Build the TF-IDF RAG index from the pack.")
    args = parser.parse_args()

    pack_dir = Path(args.pack)
    if args.import_db:
        print(json.dumps(import_dataset_pack(pack_dir), indent=2))
    if args.build_rag:
        print(json.dumps(build_dataset_pack_index(pack_dir), indent=2))
    if not args.import_db and not args.build_rag:
        parser.print_help()


if __name__ == "__main__":
    main()
