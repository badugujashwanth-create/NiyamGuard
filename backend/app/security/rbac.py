from dataclasses import dataclass
from typing import Callable

from fastapi import Depends, HTTPException, Request, status

from app.repositories.auth_repository import auth_repository
from app.security.jwt import decode_access_token


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str
    role: str


def _token_from_request(request: Request) -> str | None:
    authorization = request.headers.get("authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def get_current_user(request: Request) -> CurrentUser:
    token = _token_from_request(request)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    user_id = str(payload.get("sub", ""))
    user = auth_repository.get_user(user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is inactive or missing.")
    return CurrentUser(id=user.id, email=user.email, role=user.role)


def optional_current_user(request: Request) -> CurrentUser | None:
    try:
        return get_current_user(request)
    except HTTPException:
        return None


def require_roles(*roles: str) -> Callable:
    allowed = set(roles)

    def dependency(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role.")
        return user

    return dependency
