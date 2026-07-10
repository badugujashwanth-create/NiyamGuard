from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings
from app.data_pipeline.dataset_cleaner import clean_seed_knowledge
from app.data_pipeline.rag_indexer import INDEX_FILE


def _source_for(chunk: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": chunk.get("source_type") or "unknown",
        "label": chunk.get("source_label") or "NiyamGuard knowledge source",
        "verified": bool(chunk.get("verified", False)),
    }


class RagRetriever:
    def __init__(
        self,
        index_path: Path | None = None,
        *,
        min_score: float | None = None,
    ) -> None:
        self.index_path = index_path or settings.rag_index_path
        self.min_score = settings.rag_min_score if min_score is None else min_score
        self._index: dict[str, Any] | None = None

    def _load_or_seed(self) -> dict[str, Any]:
        if self._index is not None:
            return self._index
        index_file = self.index_path / INDEX_FILE
        if index_file.exists():
            with index_file.open("rb") as handle:
                self._index = pickle.load(handle)
            return self._index

        chunks = clean_seed_knowledge()
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=12000,
        )
        matrix = vectorizer.fit_transform([str(chunk["text"]) for chunk in chunks])
        self._index = {"vectorizer": vectorizer, "matrix": matrix, "chunks": chunks}
        return self._index

    def retrieve(self, question: str, top_k: int | None = None) -> list[dict[str, Any]]:
        if not settings.rag_enabled:
            return []
        query = question.strip()
        if not query:
            return []
        index = self._load_or_seed()
        vectorizer: TfidfVectorizer = index["vectorizer"]
        matrix = index["matrix"]
        chunks: list[dict[str, Any]] = index["chunks"]
        query_vector = vectorizer.transform([query])
        scores = cosine_similarity(query_vector, matrix)[0]
        limit = top_k or settings.rag_top_k
        ranked = sorted(enumerate(scores), key=lambda item: float(item[1]), reverse=True)
        results: list[dict[str, Any]] = []
        for chunk_index, score in ranked[:limit]:
            score_value = float(score)
            if score_value < self.min_score:
                continue
            chunk = chunks[chunk_index]
            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "score": score_value,
                    "title": chunk.get("title"),
                    "service_id": chunk.get("service_id"),
                    "text": chunk["text"],
                    "source": _source_for(chunk),
                    "metadata": chunk.get("metadata", {}),
                }
            )
        return results


def retrieve(question: str, top_k: int = 5) -> list[dict[str, Any]]:
    return RagRetriever().retrieve(question, top_k=top_k)
