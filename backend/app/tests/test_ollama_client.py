import httpx

from app.services.ollama_client import FallbackAIClient, OllamaClient


def test_fallback_impact_summary_uses_verified_payload() -> None:
    payload = {
        "finding": {
            "status": "drifted",
            "expected_value": "6 months",
            "actual_value": "12 months",
            "citizen_impact_reason": "Citizens may follow an outdated rule.",
            "recommended_fix": "Update the portal.",
        },
        "rule": {"rule_name": "Income Certificate Validity"},
        "circular": {"circular_number": "GO-138"},
        "connected_system": {"name": "MeeSeva Portal"},
    }
    result = FallbackAIClient().generate_impact_summary(payload)
    assert result["fallback"] is True
    assert result["source"] == {
        "rule": "Income Certificate Validity",
        "circular": "GO-138",
        "verified": True,
    }
    assert "12 months" in result["summary"]
    assert "6 months" in result["summary"]


def test_ollama_timeout_uses_deterministic_fallback(monkeypatch) -> None:
    client = OllamaClient()

    def raise_timeout(messages):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr(client, "_post_chat", raise_timeout)
    result = client.generate_text("Explain this", {"fallback_text": "safe fallback"})
    assert result["provider"] == "fallback"
    assert result["fallback"] is True
    assert result["text"] == "safe fallback"


def test_ollama_invalid_json_uses_fallback(monkeypatch) -> None:
    client = OllamaClient()
    monkeypatch.setattr(
        client,
        "generate_text",
        lambda prompt, context=None: {
            "success": True,
            "provider": "ollama",
            "model": client.model,
            "text": "not-json",
            "fallback": False,
        },
    )
    result = client.generate_json("Return JSON", {"fallback_text": "safe fallback"})
    assert result["fallback"] is True
    assert result["data"]["answer"] == "safe fallback"
