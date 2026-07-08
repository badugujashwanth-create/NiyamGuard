from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.schemas.auth_schemas import (
    CreateUserRequest,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UpdateUserRequest,
)
from app.security.rate_limit import rate_limit
from app.security.rbac import CurrentUser, get_current_user, require_roles
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit)])
def login(payload: LoginRequest, request: Request) -> dict:
    result = auth_service.login(payload.email, payload.password, request=request)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    return {"success": True, **result}


@router.post("/logout")
def logout(payload: RefreshRequest | None = None, request: Request = None, user: CurrentUser = Depends(get_current_user)) -> dict:
    auth_service.logout(payload.refresh_token if payload else None, user, request=request)
    return {"success": True}


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest) -> dict:
    result = auth_service.refresh(payload.refresh_token)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
    return {"success": True, **result}


@router.get("/me")
def me(user: CurrentUser = Depends(get_current_user)) -> dict:
    return {"success": True, "user": {"id": user.id, "email": user.email, "role": user.role}}


@router.post("/users", dependencies=[Depends(require_roles("admin"))])
def create_user(payload: CreateUserRequest, request: Request, actor: CurrentUser = Depends(get_current_user)) -> dict:
    return {"success": True, "user": auth_service.create_user(payload, actor=actor, request=request)}


@router.get("/users", dependencies=[Depends(require_roles("admin"))])
def list_users() -> dict:
    return {"success": True, "users": auth_service.list_users()}


@router.patch("/users/{user_id}", dependencies=[Depends(require_roles("admin"))])
def update_user(
    user_id: str,
    payload: UpdateUserRequest,
    request: Request,
    actor: CurrentUser = Depends(get_current_user),
) -> dict:
    user = auth_service.update_user(user_id, payload, actor=actor, request=request)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"success": True, "user": user}
