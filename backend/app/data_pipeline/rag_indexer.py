from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer

from app.config import settings
from app.data_pipeline.dataset_cleaner import clean_input_path, clean_seed_knowledge, write_chunks

INDEX_FILE = "tfidf_index.pkl"
CHUNKS_FILE = "chunks.json"
METADATA_FILE = "index_metadata.json"


def load_processed_chunks(input_path: Path) -> list[dict[str, Any]]:
    if not input_path.exists():
        return []
    chunks: list[dict[str, Any]] = []
    for path in sorted(input_path.rglob("*.json")) if input_path.is_dir() else [input_path]:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            chunks.extend(item for item in payload if isinstance(item, dict) and item.get("text"))
    return chunks


def build_index(chunks: list[dict[str, Any]], output_path: Path) -> dict[str, Any]:
    clean_chunks = [chunk for chunk in chunks if str(chunk.get("text", "")).strip()]
    if not clean_chunks:
        raise ValueError("No chunks are available for indexing.")

    texts = [str(chunk["text"]) for chunk in clean_chunks]
    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=12000,
    )
    matrix = vectorizer.fit_transform(texts)
    output_path.mkdir(parents=True, exist_ok=True)
    with (output_path / INDEX_FILE).open("wb") as handle:
        pickle.dump({"vectorizer": vectorizer, "matrix": matrix, "chunks": clean_chunks}, handle)
    with (output_path / CHUNKS_FILE).open("w", encoding="utf-8") as handle:
        json.dump(clean_chunks, handle, ensure_ascii=False, indent=2)
    with (output_path / METADATA_FILE).open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "index_type": "tfidf",
                "chunk_count": len(clean_chunks),
                "safe_default": True,
            },
            handle,
            indent=2,
        )
    return {"chunk_count": len(clean_chunks), "output": str(output_path)}


def build_default_index(output_path: Path | None = None) -> dict[str, Any]:
    return build_index(clean_seed_knowledge(), output_path or settings.rag_index_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the NiyamGuard TF-IDF RAG index.")
    parser.add_argument("--input", default=str(settings.processed_dataset_dir), help="Directory or chunks JSON file.")
    parser.add_argument("--output", default=str(settings.rag_index_path), help="Index output directory.")
    parser.add_argument("--from-raw", action="store_true", help="Clean raw input files before indexing.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    chunks = clean_input_path(input_path) if args.from_raw else load_processed_chunks(input_path)
    if not chunks:
        chunks = clean_seed_knowledge()
        write_chunks(chunks, settings.processed_dataset_dir)
        print("No processed chunks found. Indexed committed seed knowledge.")
    result = build_index(chunks, output_path)
    print(f"Built TF-IDF RAG index with {result['chunk_count']} chunks at {result['output']}")


if __name__ == "__main__":
    main()
