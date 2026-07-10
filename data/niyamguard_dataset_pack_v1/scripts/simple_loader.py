"""Simple CSV loader helper for NiyamGuard dataset pack.
Usage example:
  python scripts/simple_loader.py --root ./niyamguard_dataset_pack_v1
This script prints row counts and paths. Extend it to load into your FastAPI/Postgres seed command.
"""
from pathlib import Path
import argparse, csv

parser = argparse.ArgumentParser()
parser.add_argument('--root', default='.')
args = parser.parse_args()
root = Path(args.root)
for csv_path in sorted(root.rglob('*.csv')):
    with csv_path.open(encoding='utf-8') as f:
        count = max(0, sum(1 for _ in f) - 1)
    print(f"{csv_path.relative_to(root)}: {count} rows")
