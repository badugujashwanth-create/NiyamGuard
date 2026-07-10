from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare local fine-tuning JSONL from the synthetic dataset.")
    parser.add_argument(
        "--input",
        default="data/niyamguard_dataset_pack_v1/ml/instruction_tuning_dataset.jsonl",
        help="Source instruction JSONL.",
    )
    parser.add_argument(
        "--output",
        default="data/training/niyamguard_finetune_prepared.jsonl",
        help="Prepared output JSONL.",
    )
    args = parser.parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with input_path.open("r", encoding="utf-8") as source, output_path.open("w", encoding="utf-8") as target:
        for line in source:
            if not line.strip():
                continue
            row = json.loads(line)
            target.write(
                json.dumps(
                    {
                        "instruction": row.get("instruction", ""),
                        "input": row.get("input", ""),
                        "output": row.get("output", ""),
                        "source": "niyamguard_dataset_pack_v1",
                        "task": row.get("task"),
                        "split": row.get("split"),
                        "verified": False,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            count += 1
    print(f"wrote={count} output={output_path}")


if __name__ == "__main__":
    main()
