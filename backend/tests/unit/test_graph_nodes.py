"""
Unit tests for graph nodes — dependencies are mocked so these test the
node's own logic (what it saves, what it returns) in isolation from real
Mongo/Meta/OpenAI calls.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.graph.dependencies import GraphDependencies
from app.graph.nodes.acknowledge import build_acknowledge_node
from app.graph.nodes.dispatcher import build_dispatcher_node
from app.graph.nodes.llm_reasoning import build_llm_reasoning_node
from app.graph.nodes.llm_reasoning import should_handover
from app.graph.nodes.media_interpreter import should_interpret_media
from app.graph.state import IncomingMessage, ReplyDecision
from app.models.session import SessionStatus


def make_mock_deps() -> GraphDependencies:
    return GraphDependencies(
        tenant_repo=AsyncMock(),
        session_repo=AsyncMock(),
        message_repo=AsyncMock(),
        whatsapp_client=AsyncMock(),
        llm_service=AsyncMock(),
        vision_service=AsyncMock(),
        typing_heartbeat=AsyncMock(),
    )


class TestAcknowledgeNode:
    async def test_saves_message_and_starts_typing(self):
        deps = make_mock_deps()
        node = build_acknowledge_node(deps)
        state = {
            "tenant_id": "t1",
            "session_id": "s1",
            "phone_number_id": "phone-123",
            "incoming_message": IncomingMessage(
                meta_message_id="wamid.123",
                from_phone="15551234567",
                message_type="text",
                text_body="hello",
            ),
        }

        result = await node(state)

        deps.message_repo.insert.assert_awaited_once()
        deps.whatsapp_client.mark_as_read.assert_awaited_once_with("wamid.123", phone_number_id="phone-123")
        deps.typing_heartbeat.start.assert_awaited_once_with("s1", "wamid.123", "phone-123")
        # Session must flip to AGENT_RESPONDING — this is what the dashboard
        # polls for to render the typing indicator.
        deps.session_repo.update_status.assert_awaited_once_with("t1", "s1", SessionStatus.AGENT_RESPONDING)
        assert "inbound_message_doc_id" in result

    async def test_does_not_raise_when_meta_call_fails(self):
        deps = make_mock_deps()
        deps.whatsapp_client.mark_as_read.side_effect = RuntimeError("Meta is down")
        node = build_acknowledge_node(deps)
        state = {
            "tenant_id": "t1",
            "session_id": "s1",
            "incoming_message": IncomingMessage(
                meta_message_id="wamid.123", from_phone="1555", message_type="text", text_body="hi"
            ),
        }

        # Must not raise — a failed read receipt should never crash the graph.
        result = await node(state)
        assert "inbound_message_doc_id" in result


class TestDispatcherNode:
    async def test_sends_text_reply_and_records_message(self):
        deps = make_mock_deps()
        deps.whatsapp_client.send_text.return_value = "wamid.reply"
        node = build_dispatcher_node(deps)
        state = {
            "tenant_id": "t1",
            "session_id": "s1",
            "customer_phone": "1555",
            "phone_number_id": "phone-123",
            "media_library": {},
            "reply_decision": ReplyDecision(
                reply_type="text", text_content="Thanks for reaching out!", sentiment_score=0.1, needs_human=False
            ),
        }

        result = await node(state)

        deps.whatsapp_client.send_text.assert_awaited_once_with(
            "1555", "Thanks for reaching out!", phone_number_id="phone-123"
        )
        deps.typing_heartbeat.stop.assert_awaited_once_with("s1")
        deps.session_repo.update_status.assert_awaited_once_with("t1", "s1", SessionStatus.WAITING_FOR_BOT)
        assert result["dispatch_result"]["success"] is True

    async def test_records_failure_when_media_key_missing(self):
        deps = make_mock_deps()
        node = build_dispatcher_node(deps)
        state = {
            "tenant_id": "t1",
            "session_id": "s1",
            "customer_phone": "1555",
            "media_library": {"catalog": "https://example.com/catalog.pdf"},
            "reply_decision": ReplyDecision(
                reply_type="document",
                text_content="Here you go",
                media_asset_key="nonexistent_key",
                sentiment_score=0.1,
                needs_human=False,
            ),
        }

        result = await node(state)

        # Must not raise — a hallucinated media key becomes a recorded failure, not a crash.
        assert result["dispatch_result"]["success"] is False
        deps.message_repo.insert.assert_awaited_once()


class TestConditionalRouters:
    def test_should_handover_routes_to_handover_when_flagged(self):
        state = {"reply_decision": ReplyDecision(reply_type="text", text_content="x", sentiment_score=0.9, needs_human=True)}
        assert should_handover(state) == "handover"

    def test_should_handover_routes_to_dispatch_by_default(self):
        state = {"reply_decision": ReplyDecision(reply_type="text", text_content="x", sentiment_score=0.1, needs_human=False)}
        assert should_handover(state) == "dispatch"

    def test_should_interpret_media_for_image(self):
        state = {"incoming_message": IncomingMessage(meta_message_id="1", from_phone="1", message_type="image")}
        assert should_interpret_media(state) == "interpret"

    def test_should_interpret_media_skips_for_text(self):
        state = {"incoming_message": IncomingMessage(meta_message_id="1", from_phone="1", message_type="text")}
        assert should_interpret_media(state) == "skip"


class TestLLMReasoningNode:
    async def test_returns_fallback_decision_when_llm_fails(self):
        deps = make_mock_deps()
        deps.llm_service.decide_reply.side_effect = RuntimeError("provider down")
        node = build_llm_reasoning_node(deps)

        result = await node({
            "tenant_id": "t1",
            "session_id": "s1",
            "tenant_system_prompt": "Be helpful.",
            "media_library": {},
            "history": [],
            "incoming_message": IncomingMessage(
                meta_message_id="wamid.123",
                from_phone="1555",
                message_type="text",
                text_body="hello",
            ),
        })

        decision = result["reply_decision"]
        assert decision.reply_type == "text"
        assert decision.needs_human is False
        assert "received your message" in decision.text_content
