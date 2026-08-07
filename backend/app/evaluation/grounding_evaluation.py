"""Frozen source-grounding evaluation for the public answer boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.hybrid_intelligence.hybrid_answer_service import answer_question

EVALUATION_PATH = Path(__file__).resolve().parents[1] / "data" / "evaluation" / "grounding_evaluation.json"


def load_cases() -> list[dict[str, Any]]:
    with EVALUATION_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_evaluation() -> dict[str, Any]:
    """Run deterministic, fixture-backed grounding checks without an AI call."""
    results: list[dict[str, Any]] = []
    for case in load_cases():
        answer = answer_question(case["question"])
        sources = answer.get("sources", [])
        expected_source = case.get("expected_source")
        expected_source_type = case.get("expected_source_type")
        source_match = (
            (not expected_source or any(item.get("label") == expected_source for item in sources))
            and (not expected_source_type or any(item.get("type") == expected_source_type for item in sources))
        )
        text_match = not case.get("expected_text") or case["expected_text"] in answer.get("answer", "")
        unsupported = bool(case.get("unsupported"))
        safe_unsupported = not unsupported or (
            answer.get("fallback") is True
            and answer.get("method") == "safe_fallback"
            and not sources
            and "Verified data is not available" in answer.get("answer", "")
        )
        passed = (
            answer.get("method") == case["expected_method"]
            and source_match
            and text_match
            and safe_unsupported
            and answer.get("ai_called") is False
        )
        results.append(
            {
                "id": case["id"],
                "passed": passed,
                "method": answer.get("method"),
                "source_count": len(sources),
                "ai_called": bool(answer.get("ai_called")),
                "unsupported": unsupported,
            }
        )
    total = len(results)
    grounded = [item for item in results if not item["unsupported"]]
    unsupported = [item for item in results if item["unsupported"]]
    grounded_passed = sum(item["passed"] for item in grounded)
    unsupported_passed = sum(item["passed"] for item in unsupported)
    ai_calls = sum(item["ai_called"] for item in results)
    return {
        "dataset": EVALUATION_PATH.name,
        "cases": total,
        "grounded_correctness": round(grounded_passed / len(grounded), 4) if grounded else 0.0,
        "source_coverage": round(sum(item["source_count"] > 0 for item in grounded) / len(grounded), 4) if grounded else 0.0,
        "unsupported_safe_rate": round(unsupported_passed / len(unsupported), 4) if unsupported else 0.0,
        "hallucination_count": sum(not item["passed"] for item in results),
        "deterministic_path_rate": round(sum(not item["ai_called"] for item in results) / total, 4) if total else 0.0,
        "ai_call_rate": round(ai_calls / total, 4) if total else 0.0,
        "status": "pass" if total and all(item["passed"] for item in results) else "fail",
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run_evaluation(), indent=2))
