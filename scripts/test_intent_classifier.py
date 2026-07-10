from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


KEYWORDS = {
    "search_circular": ["find circular", "search circular", "which circular", "regulation"],
    "summarize_circular": ["summarize", "summary", "what does circular", "explain circular"],
    "extract_obligations": ["obligation", "must", "required", "actor", "extract"],
    "check_policy_gap": ["gap", "missing", "covered", "coverage", "policy gap"],
    "show_evidence_status": ["evidence", "proof", "accepted", "expired", "submitted"],
    "compare_policy_versions": ["drift", "changed", "new requirement", "old requirement", "compare"],
    "explain_risk_score": ["risk", "score", "high risk", "band"],
    "show_audit_trail": ["audit", "trail", "event", "who changed"],
    "create_remediation_plan": ["fix", "remediate", "plan", "action"],
    "deadline_query": ["deadline", "due", "when", "days"],
    "assign_owner": ["owner", "assign", "responsible", "team"],
    "generate_report": ["report", "export", "download", "generate"],
}


def predict(text: str) -> str:
    normalized = text.casefold()
    scores = {
        intent: sum(1 for keyword in keywords if keyword in normalized)
        for intent, keywords in KEYWORDS.items()
    }
    best, score = max(scores.items(), key=lambda item: item[1])
    return best if score > 0 else "search_circular"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a simple keyword intent baseline.")
    parser.add_argument(
        "--input",
        default="data/niyamguard_dataset_pack_v1/ml/intent_classification.csv",
        help="Path to intent_classification.csv",
    )
    args = parser.parse_args()
    rows = list(csv.DictReader(Path(args.input).open("r", encoding="utf-8", newline="")))
    total = 0
    correct = 0
    confusion: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        expected = row["intent_label"]
        actual = predict(row["utterance"])
        total += 1
        correct += int(expected == actual)
        confusion[expected][actual] += 1
    print(f"rows={total}")
    print(f"accuracy={correct / max(1, total):.3f}")
    for intent, counts in sorted(confusion.items()):
        print(f"{intent}: {dict(counts)}")


if __name__ == "__main__":
    main()
