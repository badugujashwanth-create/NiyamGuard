from __future__ import annotations

import json
from typing import Any

import httpx

from app.services.ai.fallback_provider import FallbackProvider


class RemoteChatProvider:
    def __init__(
        self,
        *,
        provider: str,
        model: str,
        api_key: str,
        endpoint: str,
        timeout_seconds: int,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self.headers = headers or {}
        self._fallback = FallbackProvider()

    def health_check(self) -> dict[str, Any]:
        return {
            "enabled": bool(self.api_key),
            "provider": self.provider,
            "configured": bool(self.api_key),
            "model": self.model,
            "status": "configured" if self.api_key else "fallback",
            "message": "Remote provider is configured." if self.api_key else "API key is not configured.",
        }

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Content-Type": "application/json", **self.headers}
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(self.endpoint, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def generate_text(self, prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.api_key:
            return self._fallback.generate_text(prompt, context)
        try:
            if self.provider == "huggingface":
                data = self._post({"inputs": prompt, "parameters": {"max_new_tokens": 500, "temperature": 0.1}})
                if isinstance(data, list) and data:
                    text = str(data[0].get("generated_text") or "")
                else:
                    text = json.dumps(data)
            elif self.provider == "groq":
                data = self._post(
                    {
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                    }
                )
                text = str(data["choices"][0]["message"]["content"])
            elif self.provider == "gemini":
                data = self._post({"contents": [{"parts": [{"text": prompt}]}]})
                text = str(data["candidates"][0]["content"]["parts"][0]["text"])
            else:
                return self._fallback.generate_text(prompt, context)
            return {"success": True, "provider": self.provider, "model": self.model, "text": text.strip(), "fallback": False}
        except Exception:
            return self._fallback.generate_text(prompt, context)

    def generate_json(self, prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        result = self.generate_text(prompt, context)
        if result.get("fallback"):
            return self._fallback.generate_json(prompt, context)
        try:
            return {
                "success": True,
                "provider": self.provider,
                "model": self.model,
                "data": json.loads(str(result["text"])),
                "fallback": False,
            }
        except json.JSONDecodeError:
            return self._fallback.generate_json(prompt, context)

    def generate_impact_summary(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._fallback.generate_impact_summary(payload)

    def answer_with_context(
        self,
        question: str,
        context_chunks: list[dict[str, Any]],
        language: str = "english",
    ) -> dict[str, Any]:
        return self._fallback.answer_with_context(question, context_chunks, language)
