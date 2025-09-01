"""
MockAdapter — minimal in-memory adapter for testing the LLM flow.

Purpose:
- No HTTP calls, no external deps.
- Always returns: "<prefix> <user_text>".
- Registered as "mock" so the factory can pick it via LLM_PROVIDER=mock.
"""
from __future__ import annotations
from typing import List, Optional
from ..port import LLMClient, ChatMessage, ChatResponse
from ..registry import register

@register("mock")
class MockAdapter(LLMClient):
    """Deterministic adapter for tests and local debugging."""
    def __init__(self, prefix: str = "MOCK:", timeout: int = 1):
        self.prefix = prefix
        self.timeout = timeout

    @classmethod
    def from_config(cls, cfg: dict) -> "MockAdapter":
        """Create from config dict; honors optional 'mock_prefix'."""
        return cls(prefix=cfg.get("mock_prefix", "MOCK:"), timeout=1)

    def chat(self, messages: List[ChatMessage], *, max_tokens: int = 500,
             temperature: float = 0.2, model: Optional[str] = None) -> ChatResponse:
        """
        Return "<prefix> <first user message>".
        Ignores generation options; intended only for wiring/tests.
        """
        user = next((m.content for m in messages if m.role == "user"), "")
        return ChatResponse(text=f"{self.prefix} {user}")
