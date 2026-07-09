from __future__ import annotations

import json
import re
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import settings

SAFE_MISSING_ANSWER = "Verified data is not available for this question."


class TemporaryAIError(RuntimeError):
    """Raised for retryable local AI failures."""


def _language_code(language: str) -> str:
    return {"telugu": "te-IN", "hindi": "hi-IN", "english": "en-IN"}.get(language, "en-IN")


def _safe_error_message() -> str:
    return "Ollama is unavailable. Deterministic fallback is active."


def _first_value(text: str, label: str) -> str | None:
    match = re.search(rf"{re.escape(label)}:\s*(.+)", text, flags=re.IGNORECASE)
    if not match:
        return None
    return match.group(1).strip()


def _references_from_chunks(context_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    references = []
    for chunk in context_chunks:
        source = chunk.get("source") or {}
        references.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "service_id": chunk.get("service_id"),
                "title": chunk.get("title"),
                "source_type": source.get("type"),
                "source_label": source.get("label"),
                "verified": bool(source.get("verified", False)),
                "score": chunk.get("score"),
            }
        )
    return references


class FallbackAIClient:
    provider = "fallback"
    model = "deterministic-template"

    def health_check(self) -> dict[str, Any]:
        return {
            "enabled": False,
            "provider": settings.ai_provider,
            "configured": False,
            "model": settings.ollama_model,
            "rag_enabled": settings.rag_enabled,
            "status": "fallback",
            "message": _safe_error_message(),
        }

    def generate_text(self, prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        return {
            "success": True,
            "provider": self.provider,
            "model": self.model,
            "text": str(context.get("fallback_text") or SAFE_MISSING_ANSWER),
            "fallback": True,
        }

    def generate_json(self, prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        if context.get("kind") == "impact_summary":
            return self.generate_impact_summary(context.get("payload") or {})
        return {
            "success": True,
            "provider": self.provider,
            "model": self.model,
            "data": {"answer": str(context.get("fallback_text") or SAFE_MISSING_ANSWER)},
            "fallback": True,
        }

    def generate_impact_summary(self, payload: dict[str, Any]) -> dict[str, Any]:
        finding = payload.get("finding") or {}
        rule = payload.get("rule") or {}
        circular = payload.get("circular") or {}
        system = payload.get("connected_system") or {}
        priority = payload.get("priority_score") or {}
        system_name = system.get("name") or finding.get("connected_system_id") or "Connected system"
        expected = finding.get("expected_value") or rule.get("current_value") or "missing verified value"
        actual = finding.get("actual_value") or "missing"
        status = finding.get("status") or "unknown"
        summary = (
            f"{system_name} is {status}. It shows {actual}, while the verified rule expects {expected}. "
            f"{finding.get('citizen_impact_reason') or 'Citizen impact data is missing.'}"
        )
        return {
            "success": True,
            "provider": self.provider,
            "model": self.model,
            "summary": summary,
            "citizen_friendly_explanation": (
                "A citizen may receive outdated guidance if this connected system is not updated."
                if status != "compliant"
                else "No current citizen impact is detected from this finding."
            ),
            "officer_friendly_explanation": (
                f"Update {system_name} to match the verified rule value {expected}."
                if status != "compliant"
                else "No officer action is required for this compliant finding."
            ),
            "risk_explanation": priority.get("reason") or finding.get("citizen_impact_reason") or "Risk data is missing.",
            "recommended_action": finding.get("recommended_fix") or "Review verified policy data before action.",
            "source": {
                "rule": rule.get("rule_name") or finding.get("rule_key"),
                "circular": circular.get("circular_number") or rule.get("circular_id"),
                "verified": bool(rule),
            },
            "fallback": True,
            "limitations": "AI summary is explanatory only. Verified rules remain the source of truth.",
        }

    def answer_with_context(
        self,
        question: str,
        context_chunks: list[dict[str, Any]],
        language: str = "english",
    ) -> dict[str, Any]:
        if not context_chunks:
            return {
                "success": True,
                "answer": SAFE_MISSING_ANSWER,
                "provider": self.provider,
                "model": self.model,
                "fallback": True,
                "references": [],
            }
        top = context_chunks[0]
        text = str(top.get("text") or "")
        title = str(top.get("title") or top.get("service_id") or "This service")
        normalized = question.casefold()
        if any(marker in normalized for marker in ["document", "docs", "proof", "enti", "patralu"]):
            detail = _first_value(text, "Required documents") or text[:700]
            if language == "telugu":
                answer = f"{title} kosam retrieved source prakaram documents: {detail}."
            elif language == "hindi":
                answer = f"{title} ke liye retrieved source ke anusaar documents: {detail}."
            else:
                answer = f"For {title}, the retrieved source lists these documents: {detail}."
        elif any(marker in normalized for marker in ["eligib", "eligible", "arhata", "yogyata"]):
            detail = _first_value(text, "Eligibility") or text[:700]
            answer = f"{title} eligibility from retrieved source: {detail}."
        elif any(marker in normalized for marker in ["process", "apply", "steps", "ela", "kaise"]):
            detail = _first_value(text, "Process steps") or text[:700]
            answer = f"{title} process from retrieved source: {detail}."
        else:
            answer = f"From the retrieved NiyamGuard source for {title}: {text[:900]}"
        return {
            "success": True,
            "answer": answer,
            "provider": self.provider,
            "model": self.model,
            "fallback": True,
            "references": _references_from_chunks(context_chunks),
        }


class OllamaClient:
    provider = "ollama"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int | None = None,
        max_retries: int | None = None,
    ) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout_seconds = timeout_seconds or settings.ai_timeout_seconds
        self.max_retries = max_retries or settings.ai_max_retries
        self._fallback = FallbackAIClient()

    def health_check(self) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=min(self.timeout_seconds, 5)) as client:
                response = client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
        except Exception:
            return self._fallback.health_check()
        return {
            "enabled": True,
            "provider": "ollama",
            "configured": True,
            "base_url": self.base_url,
            "model": self.model,
            "rag_enabled": settings.rag_enabled,
            "status": "online",
        }

    def _retry_attempts(self) -> int:
        return max(1, int(self.max_retries) + 1)

    @retry(
        retry=retry_if_exception_type((TemporaryAIError, httpx.TimeoutException, httpx.TransportError)),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=3),
        stop=stop_after_attempt(max(1, settings.ai_max_retries + 1)),
        reraise=True,
    )
    def _post_chat(self, messages: list[dict[str, str]]) -> str:
        payload = {"model": self.model, "messages": messages, "stream": False}
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(f"{self.base_url}/api/chat", json=payload)
        if response.status_code >= 500:
            raise TemporaryAIError("temporary local model failure")
        response.raise_for_status()
        data = response.json()
        content = (data.get("message") or {}).get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("empty Ollama response")
        return content.strip()

    def generate_text(self, prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        context = context or {}
        system = context.get("system") or (
            "You are NiyamGuard AI. Use only provided verified or retrieved context. "
            "Do not invent government rules, circulars, dates, departments, eligibility, or findings. "
            f"If context is missing, answer exactly: {SAFE_MISSING_ANSWER}"
        )
        try:
            text = self._post_chat(
                [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ]
            )
            return {
                "success": True,
                "provider": self.provider,
                "model": self.model,
                "text": text,
                "fallback": False,
            }
        except Exception:
            return self._fallback.generate_text(prompt, context)

    def generate_json(self, prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        text_result = self.generate_text(prompt, context)
        if text_result.get("fallback"):
            return self._fallback.generate_json(prompt, context)
        try:
            return {
                "success": True,
                "provider": self.provider,
                "model": self.model,
                "data": json.loads(str(text_result["text"])),
                "fallback": False,
            }
        except (TypeError, json.JSONDecodeError):
            return self._fallback.generate_json(prompt, context)

    def generate_impact_summary(self, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            "Use only this verified NiyamGuard JSON data. Return strict JSON with keys: "
            "summary, citizen_friendly_explanation, officer_friendly_explanation, "
            "risk_explanation, recommended_action. Do not invent circulars, departments, dates, "
            "eligibility rules, or government decisions.\n\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
        )
        result = self.generate_json(prompt, {"kind": "impact_summary", "payload": payload})
        if result.get("fallback"):
            return self._fallback.generate_impact_summary(payload)
        data = result.get("data") or {}
        fallback = self._fallback.generate_impact_summary(payload)
        return {
            **fallback,
            "provider": self.provider,
            "model": self.model,
            "summary": str(data.get("summary") or fallback["summary"]),
            "citizen_friendly_explanation": str(
                data.get("citizen_friendly_explanation") or fallback["citizen_friendly_explanation"]
            ),
            "officer_friendly_explanation": str(
                data.get("officer_friendly_explanation") or fallback["officer_friendly_explanation"]
            ),
            "risk_explanation": str(data.get("risk_explanation") or fallback["risk_explanation"]),
            "recommended_action": str(data.get("recommended_action") or fallback["recommended_action"]),
            "fallback": False,
        }

    def answer_with_context(
        self,
        question: str,
        context_chunks: list[dict[str, Any]],
        language: str = "english",
    ) -> dict[str, Any]:
        if not context_chunks:
            return self._fallback.answer_with_context(question, [], language)
        prompt = (
            f"Question language: {language} ({_language_code(language)}).\n"
            "Answer in the same language. Use only the retrieved context chunks below. "
            "If the answer is not present, say verified data is not available. "
            "Cite no facts outside the chunks.\n\n"
            f"Question: {question}\n\n"
            f"Retrieved chunks:\n{json.dumps(context_chunks, ensure_ascii=False, indent=2)}"
        )
        result = self.generate_text(prompt)
        if result.get("fallback"):
            return self._fallback.answer_with_context(question, context_chunks, language)
        return {
            "success": True,
            "answer": str(result.get("text") or SAFE_MISSING_ANSWER),
            "provider": self.provider,
            "model": self.model,
            "fallback": False,
            "references": _references_from_chunks(context_chunks),
        }


class AIClientFactory:
    @staticmethod
    def fallback() -> FallbackAIClient:
        return FallbackAIClient()

    @staticmethod
    def ollama() -> OllamaClient:
        return OllamaClient()

    @staticmethod
    def status() -> dict[str, Any]:
        if settings.ai_provider != "ollama" or not settings.ai_enabled:
            return FallbackAIClient().health_check()
        return OllamaClient().health_check()

    @staticmethod
    def get_client() -> OllamaClient | FallbackAIClient:
        if settings.ai_provider != "ollama" or not settings.ai_enabled:
            return FallbackAIClient()
        client = OllamaClient()
        if client.health_check().get("status") != "online":
            return FallbackAIClient()
        return client
