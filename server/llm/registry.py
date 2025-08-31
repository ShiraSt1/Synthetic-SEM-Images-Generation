# llm/registry.py
"""Tiny registry for LLM adapters.
Note: the factory must import adapter modules so their decorators run.
"""
from typing import Dict, Type
from .port import LLMClient

PROVIDERS: Dict[str, Type[LLMClient]] = {}

def register(name: str):
    """Class decorator: register adapter under 'name' (case-insensitive)."""
    def deco(cls: Type[LLMClient]):
        PROVIDERS[name.lower()] = cls
        return cls
    return deco
