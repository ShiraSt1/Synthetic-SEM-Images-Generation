# llm/factory.py
"""
Factory for LLM adapters.

- Reads config from environment variables (see below).
- Imports adapters so their @register(...) decorators run (registry gets filled).
- Returns a configured LLMClient instance by provider name.
"""
import os
from .registry import PROVIDERS

# Side-effect imports: ensure adapters register themselves into PROVIDERS.
from .adapters import mock
from .adapters import llama 
from .adapters import llama_emb
from .adapters import nlp

def _load_cfg() -> dict:
    """Collect minimal config from env with sensible defaults."""
    return {
        "provider": os.getenv("LLM_PROVIDER", "llama"),
        "base_url": os.getenv("LLM_BASE_URL", "http://localhost:1234/v1"),
        "api_key":  os.getenv("LLM_API_KEY"),
        "model":    os.getenv("LLM_MODEL", "local-llama"),
        "timeout":  int(os.getenv("LLM_TIMEOUT", "120")),
    }

def create_llm(provider: str | None = None):
    """
    Build and return an LLMClient for the requested provider.
    """
    cfg = _load_cfg()
    name = (provider or cfg["provider"]).lower()
    cls = PROVIDERS.get(name)
    if not cls:
        raise ValueError(f"Unknown provider: {name}. Registered: {list(PROVIDERS)}")
    return cls.from_config(cfg)
