from app.config import settings
from app.services.ai.remote_provider import RemoteChatProvider


class GroqProvider(RemoteChatProvider):
    def __init__(self) -> None:
        super().__init__(
            provider="groq",
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            endpoint="https://api.groq.com/openai/v1/chat/completions",
            timeout_seconds=settings.ai_timeout_seconds,
            headers={"Authorization": f"Bearer {settings.groq_api_key}"} if settings.groq_api_key else {},
        )
