from app.evaluation.grounding_evaluation import run_evaluation


def test_frozen_grounding_evaluation_is_fully_deterministic_and_safe() -> None:
    result = run_evaluation()
    assert result["status"] == "pass"
    assert result["grounded_correctness"] == 1.0
    assert result["source_coverage"] == 1.0
    assert result["unsupported_safe_rate"] == 1.0
    assert result["hallucination_count"] == 0
    assert result["deterministic_path_rate"] == 1.0
    assert result["ai_call_rate"] == 0.0
