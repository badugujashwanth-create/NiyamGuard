from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services import scheme_finder_service
from app.security.rbac import require_roles

router = APIRouter(prefix="/api/scheme-finder", tags=["Scheme Finder"])


class SchemeFinderRequest(BaseModel):
    age: int | None = None
    income: int | None = None
    category: str | None = None
    student: bool = False
    occupation: str | None = None
    district: str | None = None
    disability: bool = False
    widow: bool = False
    purpose: str | None = None


@router.post("/recommend", dependencies=[Depends(require_roles("citizen"))])
def recommend(payload: SchemeFinderRequest) -> dict[str, Any]:
    return scheme_finder_service.recommend_schemes(payload.model_dump())
