from app.evaluation.extraction_benchmark import run_benchmark


def test_frozen_extraction_benchmark_meets_exact_evidence_threshold() -> None:
    result = run_benchmark()

    assert result["dataset"] == "extraction_benchmark.json"
    assert result["cases"] == 20
    assert result["passed"] == 20
    assert result["accuracy"] == 1.0
    assert result["status"] == "pass"
