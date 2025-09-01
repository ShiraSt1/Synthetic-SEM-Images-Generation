# llm/adapters/llama.py
"""
Minimal adapter for OpenAI-compatible `/v1/chat/completions` backends.
Implements your generic LLMClient and hides provider-specific details.
"""
from __future__ import annotations
import requests
from typing import List, Optional
from ..port import LLMClient, ChatMessage, ChatResponse
from ..registry import register

@register("llama")
class LlamaAdapter(LLMClient):
    """Adapter that calls `{base_url}/chat/completions` and returns ChatResponse."""
    def __init__(self, base_url: str, api_key: Optional[str],
                 default_model: str, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_model = default_model
        self.timeout = timeout

    @classmethod
    def from_config(cls, cfg: dict) -> "LlamaAdapter":
        """Build from factory config dict (base_url/model/api_key/timeout)."""
        return cls(
            base_url=cfg["base_url"],      
            api_key=cfg.get("api_key"),    
            default_model=cfg["model"],    
            timeout=cfg.get("timeout", 120),
        )

    def _headers(self):
        """JSON headers (+ Bearer token if api_key exists)."""
        h = {"Content-Type": "application/json"}
        if self.api_key:  
            h["Authorization"] = f"Bearer {self.api_key}"
        return h

    def chat(self, messages: List[ChatMessage], *, max_tokens: int = 500,
         temperature: float = 0.2, model: Optional[str] = None) -> ChatResponse:
        """
        Send messages to an OpenAI-style endpoint and normalize the reply.
        Returns the generated text; keeps original payload in `raw`.
        """
        url = f"{self.base_url}/chat/completions"
        body = {
            "model": model or self.default_model,
            "messages": [m.__dict__ for m in messages],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        r = requests.post(url, json=body, headers=self._headers(), timeout=self.timeout)
        ct = r.headers.get("content-type", "")
        r.raise_for_status()

        try:
            data = r.json()
        except ValueError:

            txt = (r.text or "").strip()
            if not txt:
                raise RuntimeError("Empty body with 200 OK from LLM server")
       
            return ChatResponse(text=txt, raw={"raw_text": txt, "content_type": ct})

        text = (
            (data.get("choices") or [{}])[0].get("message", {}).get("content")
            or (data.get("choices") or [{}])[0].get("text")
            or data.get("content")
            or ""
        )

        return ChatResponse(text=text, raw=data)