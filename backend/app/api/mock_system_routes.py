from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.security.rbac import CurrentUser, require_roles
from app.services import mock_system_service

router = APIRouter(prefix="/api/mock-systems", tags=["Mock Connected Systems"])


@router.get("")
def list_mock_systems(actor: CurrentUser = Depends(require_roles("officer", "reviewer"))) -> dict:
    return {"success": True, "systems": mock_system_service.list_mock_systems()}


@router.get("/meeseva")
def mock_meeseva(actor: CurrentUser = Depends(require_roles("officer", "reviewer"))) -> dict:
    system = mock_system_service.get_mock_system("meeseva")
    if system is None:
        raise HTTPException(status_code=404, detail="Mock MeeSeva system not found.")
    return {"success": True, "system": system}


@router.get("/public-faq")
def mock_public_faq(actor: CurrentUser = Depends(require_roles("officer", "reviewer"))) -> dict:
    system = mock_system_service.get_mock_system("public_faq")
    if system is None:
        raise HTTPException(status_code=404, detail="Mock public FAQ system not found.")
    return {"success": True, "system": system}


@router.post("/reset-demo")
def reset_demo_systems(actor: CurrentUser = Depends(require_roles("officer", "reviewer"))) -> dict:
    return {"success": True, "systems": mock_system_service.reset_demo_systems()}


@router.post("/apply-demo-patch")
def apply_demo_patch(actor: CurrentUser = Depends(require_roles("officer", "reviewer"))) -> dict:
    return {"success": True, "systems": mock_system_service.apply_demo_patch()}
