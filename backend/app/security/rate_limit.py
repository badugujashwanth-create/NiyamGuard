from collections import defaultdict, deque
from time import monotonic

from fastapi import HTTPException, Request, status

from app.config import settings

_attempts: dict[str, deque[float]] = defaultdict(deque)


def rate_limit(request: Request) -> None:
    if not settings.rate_limit_enabled:
        return
    key = request.client.host if request.client else "unknown"
    now = monotonic()
    window = _attempts[key]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again soon.",
        )
    window.append(now)
