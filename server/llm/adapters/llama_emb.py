from __future__ import annotations
import json, requests
from typing import List, Optional
from ..port import LLMClient, ChatMessage, ChatResponse
from ..registry import register

@register("llama_emb")
class BridgeLLMAdapter(LLMClient):
    """
    Adapter that communicates with your bridge in source='llm' mode
    (via POST /v1/text-to-image).

    Returns a ChatResponse where `text` is a JSON string:
        {"images_base64":[...], "mime":"image/png"}.

    This ensures compatibility with the LLMClient interface,
    which expects `text` only.
    """
    def __init__(self, base_url: str, model: str, timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    @classmethod
    def from_config(cls, cfg: dict) -> "BridgeLLMAdapter":
        """
        Factory method to initialize the adapter from a config dictionary.
        
        Args:
            cfg (dict): Configuration dictionary containing `base_url`,
                        `model`, and optionally `timeout`.

        Raises:
            ValueError: If no model is provided.

        Returns:
            BridgeLLMAdapter: A configured adapter instance.
        """
        base = cfg["base_url"]
        model = cfg.get("model")
        if not model:
            raise ValueError("bridge_llm requires LLM_MODEL (model path/id) in env")
        return cls(base_url=base, model=model, timeout=cfg.get("timeout", 120))

    def chat(
        self,
        messages: List[ChatMessage],
        *,
        max_tokens: int = 500,
        temperature: float = 0.2,
        model: Optional[str] = None
    ) -> ChatResponse:
        """
        Sends the first user message to the bridge and retrieves image results.

        Args:
            messages (List[ChatMessage]): Conversation history.
            max_tokens (int): Not used here, preserved for API compatibility.
            temperature (float): Not used here, preserved for API compatibility.
            model (Optional[str]): Model name/path override.

        Returns:
            ChatResponse: Response containing JSON-encoded string with image data.
        """
        # Take the first user message as input text
        user = next((m.content for m in messages if m.role == "user"), "")
        if not user:
            return ChatResponse(text=json.dumps({"images_base64": [], "mime": "image/png"}))

        url = f"{self.base_url}/v1/text-to-image"
        payload = {
            "text": user,
            "source": "llm",
            "llm_model": (model or self.model)
        }
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()

        # Return JSON as string to comply with the LLMClient contract
        return ChatResponse(text=json.dumps(data, ensure_ascii=False), raw=data)