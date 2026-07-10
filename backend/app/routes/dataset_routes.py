from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.data_pipeline.dataset_pack_loader import build_dataset_pack_index, import_dataset_pack
from app.services import dataset_service

router = APIRouter(prefix="/api/dataset", tags=["NiyamGuard Dataset"])


class DatasetQARequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = 5


@router.get("/status")
def dataset_status() -> dict:
    return dataset_service.dataset_status()


@router.post("/import")
def import_dataset() -> dict:
    return {"success": True, "result": import_dataset_pack()}


@router.post("/rag/build")
def build_rag() -> dict:
    return {"success": True, "result": build_dataset_pack_index()}


@router.post("/qa")
def regulatory_qa(payload: DatasetQARequest) -> dict:
    return dataset_service.regulatory_qa(payload.question, payload.top_k)


@router.get("/obligations/search")
def obligations_search(
    q: str | None = None,
    regulator_code: str | None = None,
    sector: str | None = None,
    limit: int = 25,
) -> dict:
    return dataset_service.search_obligations(q, regulator_code, sector, limit)


@router.get("/gaps")
def gaps(
    org_id: str | None = None,
    policy_id: str | None = None,
    obligation_id: str | None = None,
    limit: int = 25,
) -> dict:
    return dataset_service.detect_gaps(org_id, policy_id, obligation_id, limit)


@router.get("/evidence")
def evidence(
    org_id: str | None = None,
    obligation_id: str | None = None,
    status: str | None = None,
    limit: int = 25,
) -> dict:
    return dataset_service.review_evidence(org_id, obligation_id, status, limit)


@router.get("/drift")
def drift(org_id: str | None = None, limit: int = 25) -> dict:
    return dataset_service.detect_drift(org_id, limit)


@router.get("/risk/{org_id}")
def risk(org_id: str) -> dict:
    return dataset_service.explain_risk(org_id)


@router.get("/audit")
def audit(org_id: str | None = None, entity_id: str | None = None, limit: int = 25) -> dict:
    return dataset_service.audit_trail(org_id, entity_id, limit)


@router.get("/demo-flow")
def demo_flow(org_id: str | None = None) -> dict:
    return dataset_service.demo_flow(org_id)


@router.get("/{collection}")
def collection(collection: str, limit: int = 50, q: str | None = None) -> dict:
    return dataset_service.list_collection(collection, limit=limit, q=q)


@router.get("/{collection}/{item_id}")
def record(collection: str, item_id: str) -> dict:
    return dataset_service.get_record(collection, item_id)
