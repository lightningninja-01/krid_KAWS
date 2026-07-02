"""
Dependency container for graph nodes.

LangGraph nodes are plain async functions of (state) -> partial state dict.
To give them access to repositories/services without resorting to global
singletons (which make testing painful) or re-instantiating clients per
node call, each node is built by a factory function that closes over a
GraphDependencies instance. See graph/builder.py for how these are wired.
"""
from dataclasses import dataclass

from app.database.repositories.message_repository import MessageRepository
from app.database.repositories.session_repository import SessionRepository
from app.database.repositories.tenant_repository import TenantRepository
from app.services.llm_service import LLMService
from app.services.typing_heartbeat import TypingHeartbeatService
from app.services.vision_service import VisionService
from app.services.whatsapp_client import WhatsAppClient


@dataclass
class GraphDependencies:
    tenant_repo: TenantRepository
    session_repo: SessionRepository
    message_repo: MessageRepository
    whatsapp_client: WhatsAppClient
    llm_service: LLMService
    vision_service: VisionService
    typing_heartbeat: TypingHeartbeatService
