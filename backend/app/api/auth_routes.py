from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

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
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Auth"])


def _apply_auth_cookies(response: Response, result: dict) -> dict:
    if not getattr(settings, "auth_cookie_mode", False):
        return result
    response.set_cookie(
        "niyamguard_access", result["access_token"], httponly=True,
        secure=getattr(settings, "auth_cookie_secure", False),
        samesite=getattr(settings, "auth_cookie_samesite", "strict"),
        max_age=settings.access_token_expire_minutes * 60, path="/",
    )
    response.set_cookie(
        "niyamguard_refresh", result["refresh_token"], httponly=True,
        secure=getattr(settings, "auth_cookie_secure", False),
        samesite=getattr(settings, "auth_cookie_samesite", "strict"),
        max_age=settings.refresh_token_expire_days * 86400, path="/api/auth",
    )
    return {**result, "access_token": None, "refresh_token": None}


def _clear_auth_cookies(response: Response) -> None:
    cookie_options = {
        "secure": getattr(settings, "auth_cookie_secure", False),
        "samesite": getattr(settings, "auth_cookie_samesite", "strict"),
    }
    response.delete_cookie("niyamguard_access", path="/", **cookie_options)
    response.delete_cookie("niyamguard_refresh", path="/api/auth", **cookie_options)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit)])
def login(payload: LoginRequest, request: Request, response: Response) -> dict:
    result = auth_service.login(payload.email, payload.password, request=request)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    return _apply_auth_cookies(response, {"success": True, **result})


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
    user: CurrentUser = Depends(get_current_user),
) -> dict:
    refresh_token = (payload.refresh_token if payload else None) or request.cookies.get("niyamguard_refresh")
    auth_service.logout(refresh_token, user, request=request)
    _clear_auth_cookies(response)
    return {"success": True}


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, payload: RefreshRequest | None = None) -> dict:
    refresh_token = (payload.refresh_token if payload else None) or request.cookies.get("niyamguard_refresh")
    result = auth_service.refresh(refresh_token) if refresh_token else None
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token.")
    return _apply_auth_cookies(response, {"success": True, **result})


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
