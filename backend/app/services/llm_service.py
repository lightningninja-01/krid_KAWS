"""
LLM service — the agentic decision-making core.

Uses OpenAI's structured outputs (response_format=json_schema) rather than
free-text + regex parsing, so the LLM Reasoning node always receives a
validated ReplyDecision or a clear failure — never a half-parseable string.
"""
from google import genai
from google.genai import types

from app.config.settings import get_settings
from app.exceptions.custom_exceptions import LLMReasoningError
from app.graph.state import IncomingMessage, ReplyDecision
from app.utils.logger import get_logger

log = get_logger(__name__)


class LLMService:
    def __init__(self) -> None:
        settings = get_settings()
        self._client = genai.Client(api_key=settings.gemini_api_key)
        self._model = settings.gemini_model
        self._handover_threshold = settings.handover_sentiment_threshold

    async def decide_reply(
        self,
        *,
        system_prompt: str,
        media_library: dict[str, str],
        history: list[dict],
        incoming_message: IncomingMessage,
        media_description: str | None,
    ) -> ReplyDecision:
        prompt = self._build_prompt(
            system_prompt=system_prompt,
            media_library=media_library,
            history=history,
            incoming_message=incoming_message,
            media_description=media_description,
        )

        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ReplyDecision,
                    temperature=0.3,
                ),
            )
            decision = response.parsed
            if not decision:
                raise LLMReasoningError("Gemini returned empty or invalid response.")
        except Exception as exc:  # noqa: BLE001
            raise LLMReasoningError(str(exc)) from exc

        # Belt-and-suspenders: sentiment threshold enforced in code too, not
        # solely trusted from the model's own needs_human flag.
        if decision.sentiment_score >= self._handover_threshold:
            decision.needs_human = True

        return decision

    def _build_prompt(
        self,
        *,
        system_prompt: str,
        media_library: dict[str, str],
        history: list[dict],
        incoming_message: IncomingMessage,
        media_description: str | None,
    ) -> str:
        media_keys_description = ", ".join(media_library.keys()) if media_library else "(none available)"
        history_lines = []
        for turn in history:
            content = turn["text"] or f"[{turn['message_type']}]"
            history_lines.append(f"{turn['sender']}: {content}")
        history_text = "\n".join(history_lines) or "(no prior messages)"

        media_note = f"\nThe customer's inbound image was described as: {media_description}" if media_description else ""

        return f"""{system_prompt}

You are a WhatsApp sales/support agent. Decide how to respond to the customer's latest message.

Available media assets (choose by key, only if genuinely relevant to the request): {media_keys_description}

Conversation history (most recent last):
{history_text}

Customer's latest message: "{incoming_message.text_body or f'[{incoming_message.message_type} message]'}"{media_note}

Decide:
- reply_type: "text" for a plain reply, "image" or "document" if the customer is asking for a visual/catalog/asset that matches one of the available media keys.
- text_content: your reply text (always required, even for media replies — used as the caption).
- media_asset_key: the exact key from the available media assets if reply_type is image/document, otherwise null.
- sentiment_score: 0.0 (calm) to 1.0 (highly frustrated/angry), based on the customer's tone across this conversation.
- needs_human: true only if the customer explicitly wants a human, or frustration is severe and unresolved.
- reasoning: one short sentence explaining your choice (internal only, not sent to the customer).
"""
