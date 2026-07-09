from __future__ import annotations

from typing import Any

from app.config import settings
from app.services.ai.fallback_provider import FallbackProvider
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.groq_provider import GroqProvider
from app.services.ai.huggingface_provider import HuggingFaceProvider
from app.services.ai.ollama_provider import OllamaProvider


class AIProviderFactory:
    @staticmethod
    def configured_providers() -> dict[str, bool]:
        return {
            "ollama": settings.ai_enabled and settings.ai_provider == "ollama",
            "huggingface": bool(settings.hf_api_token),
            "groq": bool(settings.groq_api_key),
            "gemini": bool(settings.gemini_api_key),
            "fallback": True,
        }

    @staticmethod
    def get_client():
        provider = settings.ai_provider
        if provider == "ollama" and settings.ai_enabled:
            client = OllamaProvider()
            if client.health_check().get("status") == "online":
                return client
            return FallbackProvider()
        if provider == "huggingface":
            return HuggingFaceProvider() if settings.hf_api_token else FallbackProvider()
        if provider == "groq":
            return GroqProvider() if settings.groq_api_key else FallbackProvider()
        if provider == "gemini":
            return GeminiProvider() if settings.gemini_api_key else FallbackProvider()
        return FallbackProvider()

    @staticmethod
    def status() -> dict[str, Any]:
        client = AIProviderFactory.get_client()
        status = client.health_check()
        return {
            **status,
            "active_provider": getattr(client, "provider", "fallback"),
            "requested_provider": settings.ai_provider,
            "configured_providers": AIProviderFactory.configured_providers(),
            "fallback_available": True,
            "llm_optional": settings.llm_optional,
            "llm_required": settings.llm_required,
        }
