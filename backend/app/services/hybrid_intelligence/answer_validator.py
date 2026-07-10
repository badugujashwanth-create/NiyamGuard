from __future__ import annotations


def validate(candidate: dict) -> bool:
    if not candidate:
        return False
    if candidate.get("verified") and not candidate.get("sources"):
        return False
    if candidate.get("method") in {"exact_rule_engine", "decision_table", "application_lookup", "certificate_lookup"}:
        return bool(candidate.get("sources"))
    return True

