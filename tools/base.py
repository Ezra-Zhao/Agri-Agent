"""Tool interface. Every tool returns a dict with:
  ok, summary (human-readable observation text), data (structured),
  context_updates (merged into the agent's shared context).
"""
from __future__ import annotations
from typing import Protocol, Any


class Tool(Protocol):
    name: str
    description: str

    def run(self, context: dict | None = None, **kwargs: Any) -> dict:
        ...
