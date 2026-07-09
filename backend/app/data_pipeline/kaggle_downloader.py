from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from app.config import settings
from app.data_pipeline.dataset_registry import SEARCH_TERMS, metadata_for


def kaggle_credentials_path() -> Path:
    return Path.home() / ".kaggle" / "kaggle.json"


def kaggle_ready() -> tuple[bool, str]:
    if not kaggle_credentials_path().exists():
        return (
            False,
            "Kaggle credentials are missing. Place kaggle.json in ~/.kaggle or use local seed datasets.",
        )
    if shutil.which("kaggle") is None:
        return False, "Kaggle CLI is not installed. Run `pip install kaggle` and retry."
    return True, "Kaggle CLI is configured."


def search_datasets(search: str) -> dict:
    ready, message = kaggle_ready()
    if not ready:
        return {"success": False, "skipped": True, "message": message, "results": []}
    result = subprocess.run(
        ["kaggle", "datasets", "list", "-s", search],
        capture_output=True,
        check=False,
        text=True,
    )
    return {
        "success": result.returncode == 0,
        "skipped": False,
        "message": result.stderr.strip() if result.returncode else "Search complete.",
        "results_text": result.stdout,
    }


def download_dataset(slug: str, output_dir: Path | None = None) -> dict:
    ready, message = kaggle_ready()
    if not ready:
        return {"success": False, "skipped": True, "message": message}
    target = output_dir or settings.dataset_dir / slug.replace("/", "__")
    target.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["kaggle", "datasets", "download", "-d", slug, "-p", str(target), "--unzip"],
        capture_output=True,
        check=False,
        text=True,
    )
    metadata = metadata_for(
        dataset_name=slug.split("/")[-1],
        source="kaggle",
        url_or_slug=slug,
        license=None,
        used_for="rag_knowledge_source",
    )
    with (target / "dataset_metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
    return {
        "success": result.returncode == 0,
        "skipped": False,
        "message": result.stderr.strip() if result.returncode else "Download complete.",
        "output_dir": str(target),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Optional Kaggle dataset search/download for NiyamGuard RAG.")
    parser.add_argument("--search", help="Search Kaggle datasets.")
    parser.add_argument("--download", help="Download a Kaggle dataset slug, for example owner/dataset.")
    parser.add_argument("--list-terms", action="store_true", help="Print recommended public-service search terms.")
    args = parser.parse_args()

    if args.list_terms:
        print("\n".join(SEARCH_TERMS))
        return
    if args.search:
        result = search_datasets(args.search)
        print(json.dumps(result, indent=2))
        return
    if args.download:
        result = download_dataset(args.download)
        print(json.dumps(result, indent=2))
        return
    parser.print_help()


if __name__ == "__main__":
    main()
