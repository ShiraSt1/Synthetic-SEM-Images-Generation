from __future__ import annotations
import json, requests
from typing import List, Optional, Dict, Any
from ..port import LLMClient, ChatMessage, ChatResponse
from ..registry import register

@register("nlp")
class BridgeNLPAdapter(LLMClient):
    """
    Provider שמדבר עם ה-bridge שלך במצב source='nlp'.
    מחזיר ChatResponse.text כ-JSON-STRING עם images_base64/mime.
    """
    def __init__(self, base_url: str, timeout: int = 120, default_nlp_params: Optional[Dict[str, Any]] = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_nlp_params = default_nlp_params or {
            "use_lemma": True,
            "keep_pos": ["NOUN", "ADJ"],
            "weighted": True
        }

    @classmethod
    def from_config(cls, cfg: dict) -> "BridgeNLPAdapter":
        return cls(
            base_url=cfg["base_url"],
            timeout=cfg.get("timeout", 120),
            default_nlp_params=cfg.get("nlp_params")  # לא חובה; אפשר להביא רק מה-bridge
        )

    def chat(self, messages: List[ChatMessage], *, max_tokens: int = 500,
             temperature: float = 0.2, model: Optional[str] = None) -> ChatResponse:
        user = next((m.content for m in messages if m.role == "user"), "")
        if not user:
            return ChatResponse(text=json.dumps({"images_base64": [], "mime": "image/png"}))

        url = f"{self.base_url}/v1/text-to-image"
        payload = {
            "text": user,
            "source": "nlp",
            "nlp_params": self.default_nlp_params
        }
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        return ChatResponse(text=json.dumps(data, ensure_ascii=False), raw=data)