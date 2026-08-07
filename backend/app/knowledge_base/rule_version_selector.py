"""Deterministic, UTC-date rule-version selection.

This module is deliberately independent of the answer engine.  Policy version
selection is a legal-data operation: it must not use retrieval or an LLM.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Iterable

from app.models.self_update_models import VerifiedPolicyRuleVersion


def as_utc_date(value: date | datetime | str | None = None) -> date:
    """Normalise a policy "as of" value to a calendar date in UTC.

    Date-only policy metadata is interpreted as a UTC calendar date.  Naive
    datetimes are also treated as UTC, so the selection is reproducible across
    application hosts.
    """
    if value is None:
        return datetime.now(timezone.utc).date()
    if isinstance(value, datetime):
        return (value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)).date()
    if isinstance(value, date):
        return value
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)).date()


def _date(value: str) -> date:
    return as_utc_date(value)


def select_active_version(
    versions: Iterable[VerifiedPolicyRuleVersion], *, as_of: date | datetime | str | None = None
) -> VerifiedPolicyRuleVersion | None:
    """Return the one version effective on ``as_of`` using stable tie-breaks.

    A version is eligible only on/after its effective date and through its
    optional expiry date (inclusive).  A valid ``is_current`` marker wins to
    make an explicit rollback authoritative; otherwise the most recently
    effective version wins.  Publication time, version number and id make an
    overlapping set deterministic rather than relying on database order.
    """
    selection_date = as_utc_date(as_of)
    active = [
        version
        for version in versions
        if _date(version.effective_date) <= selection_date
        and (version.expiry_date is None or selection_date <= _date(version.expiry_date))
    ]
    if not active:
        return None
    current = [version for version in active if version.is_current]
    candidates = current or active
    return max(
        candidates,
        key=lambda version: (
            _date(version.effective_date),
            as_utc_date(version.published_at),
            version.version_number,
            version.id,
        ),
    )
