from fastapi import HTTPException, status

from app.config import settings
from app.security.rbac import CurrentUser, get_current_user, optional_current_user, require_roles


def require_demo_mode() -> None:
    if not settings.demo_mode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sandbox endpoint is disabled outside demo mode.",
        )

__all__ = [
    "CurrentUser",
    "get_current_user",
    "optional_current_user",
    "require_demo_mode",
    "require_roles",
]
