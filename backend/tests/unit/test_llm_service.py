from app.services.llm_service import GeminiReplyDecision, LLMService


class TestLLMService:
    def test_normalizes_empty_media_key_to_none(self):
        service = LLMService.__new__(LLMService)
        decision = service._normalize_decision(
            GeminiReplyDecision(
                reply_type="text",
                text_content="Happy to help.",
                media_asset_key="",
                sentiment_score=0.1,
                needs_human=False,
                reasoning="Plain text answer is enough.",
            )
        )

        assert decision.media_asset_key is None

    def test_preserves_real_media_key(self):
        service = LLMService.__new__(LLMService)
        decision = service._normalize_decision(
            GeminiReplyDecision(
                reply_type="document",
                text_content="Here is the catalog.",
                media_asset_key="catalog_pdf",
                sentiment_score=0.1,
                needs_human=False,
                reasoning="Customer asked for a catalog.",
            )
        )

        assert decision.media_asset_key == "catalog_pdf"
