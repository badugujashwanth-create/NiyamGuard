from app.data_pipeline.dataset_cleaner import clean_seed_knowledge, redact_pii
from app.data_pipeline.rag_indexer import build_index
from app.data_pipeline.rag_retriever import RagRetriever


def test_dataset_cleaner_creates_seed_chunks() -> None:
    chunks = clean_seed_knowledge()
    assert len(chunks) >= 12
    income = next(chunk for chunk in chunks if chunk["service_id"] == "income_certificate")
    assert income["source_type"] == "seed_demo"
    assert income["verified"] is False
    assert "Income Certificate" in income["text"]


def test_pii_redaction() -> None:
    text = "Contact ravi@example.com or 9876543210. Aadhaar 1234 5678 9012."
    redacted = redact_pii(text)
    assert "ravi@example.com" not in redacted
    assert "9876543210" not in redacted
    assert "1234 5678 9012" not in redacted
    assert "[REDACTED_EMAIL]" in redacted
    assert "[REDACTED_PHONE]" in redacted
    assert "[REDACTED_ID]" in redacted


def test_rag_index_builds_and_retrieves_income_certificate(tmp_path) -> None:
    chunks = clean_seed_knowledge()
    result = build_index(chunks, tmp_path)
    assert result["chunk_count"] == len(chunks)

    retriever = RagRetriever(index_path=tmp_path, min_score=0.1)
    results = retriever.retrieve("income certificate required documents", top_k=3)
    assert results
    assert results[0]["service_id"] == "income_certificate"
    assert results[0]["source"]["verified"] is False
