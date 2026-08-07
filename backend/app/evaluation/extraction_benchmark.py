from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.extraction.rule_extraction_service import _deterministic_candidates

BENCHMARK_PATH = Path(__file__).resolve().parents[1] / "data" / "evaluation" / "extraction_benchmark.json"


def load_cases() -> list[dict[str, Any]]:
    with BENCHMARK_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_benchmark() -> dict[str, Any]:
    cases = load_cases()
    results: list[dict[str, Any]] = []
    for case in cases:
        candidates = _deterministic_candidates(
            f"benchmark_{case['id']}",
            case["text"],
            "2026-08-01",
        )
        expected = case["expected"]
        actual = bool(candidates)
        evidence_match = (
            not expected
            or (
                actual
                and candidates[0].old_value == case["old_value"]
                and candidates[0].new_value == case["new_value"]
                and candidates[0].source_excerpt == case["evidence"]
            )
        )
        results.append(
            {
                "id": case["id"],
                "expected_candidate": expected,
                "actual_candidate": actual,
                "evidence_match": evidence_match,
                "passed": actual == expected and evidence_match,
            }
        )
    passed = sum(1 for result in results if result["passed"])
    total = len(results)
    return {
        "dataset": BENCHMARK_PATH.name,
        "cases": total,
        "passed": passed,
        "accuracy": round(passed / total, 4) if total else 0.0,
        "threshold": 1.0,
        "status": "pass" if total and passed == total else "fail",
        "results": results,
    }


if __name__ == "__main__":
    print(json.dumps(run_benchmark(), indent=2))
