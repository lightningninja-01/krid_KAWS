"""
Vision service (bonus feature) — describes inbound customer images using a
multimodal LLM, so the LLM Reasoning node can respond intelligently to
things like "does this sofa color look good?" or a photo of a damaged part.
"""
from google import genai
from google.genai import types

from app.config.settings import get_settings
from app.exceptions.custom_exceptions import LLMReasoningError
from app.services.whatsapp_client import WhatsAppClient
from app.utils.logger import get_logger

log = get_logger(__name__)


class VisionService:
    def __init__(self, whatsapp_client: WhatsAppClient) -> None:
        settings = get_settings()
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_vision_model
        self._whatsapp_client = whatsapp_client

    async def describe_media(self, media_id: str) -> str:
        """
        Two-step Meta fetch (ID -> temp URL -> bytes), then a single vision
        call. Raw bytes are passed directly using types.Part.from_bytes.
        """
        try:
            media_url = await self._whatsapp_client.fetch_media_url(media_id)
            image_bytes = await self._whatsapp_client.download_media_bytes(media_url)

            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg'
            )

            import asyncio
            max_retries = 3
            backoff_seconds = 0.5

            for attempt in range(max_retries):
                try:
                    response = await self._client.aio.models.generate_content(
                        model=self._model,
                        contents=[
                            "Briefly describe this image in one or two sentences, "
                            "focusing on details relevant to a customer support/sales context "
                            "(e.g. product shown, visible damage, color, condition).",
                            image_part
                        ],
                        config=types.GenerateContentConfig(
                            max_output_tokens=150,
                        )
                    )
                    return response.text or "(no description generated)"
                except Exception as exc:  # noqa: BLE001
                    exc_str = str(exc)
                    is_transient = any(status in exc_str for status in ["503", "429", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "overloaded"])
                    
                    if is_transient and attempt < max_retries - 1:
                        log.warning(
                            f"Gemini Vision API transient error (attempt {attempt + 1}/{max_retries}): {exc!r}. "
                            f"Retrying in {backoff_seconds}s..."
                        )
                        await asyncio.sleep(backoff_seconds)
                        backoff_seconds *= 2
                    else:
                        log.error(f"Gemini Vision API failed after {attempt + 1} attempts: {exc!r}")
                        raise LLMReasoningError(f"Vision description failed: {exc}") from exc
        except Exception as exc:  # noqa: BLE001
            raise LLMReasoningError(f"Vision description failed: {exc}") from exc
