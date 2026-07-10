from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.security.rbac import require_roles
from app.services.hybrid_intelligence import hybrid_answer_service


router = APIRouter(tags=["Hybrid Intelligence"])


class HybridAnswerRequest(BaseModel):
    question: str = Field(min_length=1)
    language: str = "auto"
    context: dict[str, Any] = Field(default_factory=dict)
    profile: dict[str, Any] = Field(default_factory=dict)


@router.post("/api/hybrid/answer")
@router.post("/api/answer")
def answer(payload: HybridAnswerRequest) -> dict[str, Any]:
    return hybrid_answer_service.answer_question(
        payload.question,
        language=payload.language,
        context=payload.context,
        profile=payload.profile,
    )


@router.get("/api/hybrid/status")
@router.get("/api/search/status")
def status() -> dict[str, Any]:
    return hybrid_answer_service.status()


@router.post("/api/hybrid/reindex", dependencies=[Depends(require_roles("admin", "reviewer"))])
@router.post("/api/search/reindex", dependencies=[Depends(require_roles("admin", "reviewer"))])
def reindex() -> dict[str, Any]:
    return hybrid_answer_service.reindex()


@router.get("/api/search")
def search(q: str = Query(min_length=1), top_k: int | None = None) -> dict[str, Any]:
    return hybrid_answer_service.search(q, top_k=top_k)
