from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "niyamguard.db"
DEFAULT_BACKUP_DIR = ROOT / "backups"


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def backup(db_path: Path, backup_dir: Path) -> Path:
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    output = backup_dir / f"{db_path.stem}_{timestamp()}{db_path.suffix}"
    shutil.copy2(db_path, output)
    return output


def restore(db_path: Path, backup_file: Path) -> Path:
    if not backup_file.exists():
        raise FileNotFoundError(f"Backup not found: {backup_file}")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup_file, db_path)
    return db_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Backup or restore the NiyamGuard SQLite demo database.")
    parser.add_argument("action", choices=["backup", "restore"])
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path.")
    parser.add_argument("--backup-dir", default=str(DEFAULT_BACKUP_DIR), help="Backup output directory.")
    parser.add_argument("--backup-file", help="Backup file to restore from.")
    args = parser.parse_args()

    db_path = Path(args.db).resolve()
    if args.action == "backup":
        print(backup(db_path, Path(args.backup_dir).resolve()))
        return

    if not args.backup_file:
        raise SystemExit("--backup-file is required for restore")
    print(restore(db_path, Path(args.backup_file).resolve()))


if __name__ == "__main__":
    main()
