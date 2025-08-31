# llm/port.py
"""
Generic LLM interface (the PORT) used by your app and all adapters.

- ChatMessage / ChatResponse: simple DTOs.
- LLMClient: abstract contract every adapter must implement.
"""

from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

@dataclass
class ChatMessage:
    """Single chat message with a role ('user'/'system'/'assistant'/...) and text."""
    role: str   
    content: str

@dataclass
class ChatResponse:
    """Normalized model reply: final text + optional raw provider payload."""
    text: str
    raw: Optional[Dict[str, Any]] = None

class LLMClient(ABC):
    """Abstract LLM client: adapters inherit and provide concrete behavior."""

    @abstractmethod
    def chat(self, messages: List[ChatMessage], *,
             max_tokens: int = 500, temperature: float = 0.2,
             model: Optional[str] = None) -> ChatResponse:
        """Send messages and return a normalized ChatResponse."""
        ...

    @classmethod
    @abstractmethod
    def from_config(cls, cfg: dict) -> "LLMClient":
        """Construct an adapter instance from a simple config dict."""
        ...


    def chat_text(self, text: str, **opts) -> ChatResponse:
        """Convenience: send a single user string (wraps it into ChatMessage)."""
        return self.chat([ChatMessage(role="user", content=text)], **opts)
