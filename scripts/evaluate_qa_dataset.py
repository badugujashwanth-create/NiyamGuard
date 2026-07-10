from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


def token_overlap(a: str, b: str) -> float:
    left = {token.casefold() for token in a.split() if len(token) > 2}
    right = {token.casefold() for token in b.split() if len(token) > 2}
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the synthetic NiyamGuard policy QA dataset.")
    parser.add_argument(
        "--qa",
        default="data/niyamguard_dataset_pack_v1/ml/policy_qa_pairs.csv",
        help="Path to policy_qa_pairs.csv",
    )
    args = parser.parse_args()

    path = Path(args.qa)
    rows = list(csv.DictReader(path.open("r", encoding="utf-8", newline="")))
    intents = Counter(row["intent"] for row in rows)
    difficulty = Counter(row["difficulty"] for row in rows)
    duplicate_questions = len(rows) - len({row["user_question"] for row in rows})
    citation_coverage = sum(
        1
        for row in rows
        if row["linked_circular_id"] and row["linked_obligation_id"] and row["linked_org_id"]
    )
    average_question_answer_overlap = sum(
        token_overlap(row["user_question"], row["expected_answer"]) for row in rows
    ) / max(1, len(rows))

    print(f"rows={len(rows)}")
    print(f"duplicate_questions={duplicate_questions}")
    print(f"citation_coverage={citation_coverage}/{len(rows)}")
    print(f"average_question_answer_token_overlap={average_question_answer_overlap:.3f}")
    print(f"intents={dict(intents)}")
    print(f"difficulty={dict(difficulty)}")


if __name__ == "__main__":
    main()
