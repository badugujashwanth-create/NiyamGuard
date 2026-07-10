from app.config import settings
from app.services.ai.remote_provider import RemoteChatProvider


class GeminiProvider(RemoteChatProvider):
    def __init__(self) -> None:
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
            f"?key={settings.gemini_api_key}"
        )
        super().__init__(
            provider="gemini",
            model=settings.gemini_model,
            api_key=settings.gemini_api_key,
            endpoint=endpoint,
            timeout_seconds=settings.ai_timeout_seconds,
        )
