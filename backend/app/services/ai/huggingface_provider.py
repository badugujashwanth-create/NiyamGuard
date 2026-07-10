from app.config import settings
from app.services.ai.remote_provider import RemoteChatProvider


class HuggingFaceProvider(RemoteChatProvider):
    def __init__(self) -> None:
        super().__init__(
            provider="huggingface",
            model=settings.hf_model,
            api_key=settings.hf_api_token,
            endpoint=f"https://api-inference.huggingface.co/models/{settings.hf_model}",
            timeout_seconds=settings.ai_timeout_seconds,
            headers={"Authorization": f"Bearer {settings.hf_api_token}"} if settings.hf_api_token else {},
        )
