from app.knowledge_base.rule_version_selector import select_active_version
from app.models.self_update_models import VerifiedPolicyRuleVersion


def version(
    number: int,
    effective: str,
    *,
    expiry: str | None = None,
    current: bool = False,
    value: str | None = None,
) -> VerifiedPolicyRuleVersion:
    return VerifiedPolicyRuleVersion(
        id=f"v{number}", rule_id="rule_001", version_number=number,
        service_id="income_certificate", rule_key="validity", value=value or str(number), unit="months",
        source_circular_id=f"c{number}", source_circular_number=f"GO-{number}",
        effective_date=effective, expiry_date=expiry, published_at=f"2026-01-{number:02d}T00:00:00+00:00",
        is_current=current,
    )


def test_no_active_version_returns_none() -> None:
    assert select_active_version([version(1, "2026-08-02")], as_of="2026-08-01") is None


def test_effective_date_boundary_is_inclusive() -> None:
    assert select_active_version([version(1, "2026-08-01")], as_of="2026-08-01").id == "v1"


def test_expiry_boundary_is_inclusive_then_expires() -> None:
    versions = [version(1, "2026-01-01", expiry="2026-08-01")]
    assert select_active_version(versions, as_of="2026-08-01").id == "v1"
    assert select_active_version(versions, as_of="2026-08-02") is None


def test_no_expiry_remains_active() -> None:
    assert select_active_version([version(1, "2026-01-01")], as_of="2030-01-01").id == "v1"


def test_future_version_never_overrides_before_effective_date() -> None:
    versions = [version(1, "2026-01-01", current=False), version(2, "2026-09-01", current=True)]
    assert select_active_version(versions, as_of="2026-08-01").id == "v1"


def test_newer_effective_version_wins() -> None:
    versions = [version(1, "2026-01-01"), version(2, "2026-08-01")]
    assert select_active_version(versions, as_of="2026-08-01").id == "v2"


def test_expired_newest_version_falls_back_to_active_prior_version() -> None:
    versions = [version(1, "2026-01-01"), version(2, "2026-02-01", expiry="2026-03-01")]
    assert select_active_version(versions, as_of="2026-04-01").id == "v1"


def test_explicit_rollback_current_marker_wins_when_both_are_date_active() -> None:
    versions = [version(1, "2026-01-01", current=True), version(2, "2026-02-01", current=False)]
    assert select_active_version(versions, as_of="2026-08-01").id == "v1"


def test_overlap_uses_stable_publication_and_version_tie_breakers() -> None:
    versions = [version(1, "2026-01-01"), version(2, "2026-01-01")]
    assert select_active_version(versions, as_of="2026-08-01").id == "v2"


def test_utc_datetime_is_normalised_to_utc_calendar_date() -> None:
    versions = [version(1, "2026-08-01")]
    assert select_active_version(versions, as_of="2026-08-01T23:30:00-05:00").id == "v1"
