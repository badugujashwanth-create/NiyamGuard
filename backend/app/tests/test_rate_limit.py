from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.config import settings
from app.security.rate_limit import rate_limit


def test_database_rate_limit_is_shared_by_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "rate_limit_backend", "database")
    monkeypatch.setattr(settings, "rate_limit_per_minute", 1)
    request = SimpleNamespace(client=SimpleNamespace(host=f"test-{uuid4().hex}"))

    rate_limit(request)
    with pytest.raises(HTTPException) as error:
        rate_limit(request)
    assert error.value.status_code == 429
