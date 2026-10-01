"""LLM provider interface.

The agent's "reason" step goes through an LLMProvider. Default is a
deterministic mock planner (SIMULATED) so the repo runs with zero API keys.
Swap in LangChainProvider for a real model — see the TODO below.
"""
from __future__ import annotations
from typing import Protocol


class LLMProvider(Protocol):
    name: str

    def decide_next(self, goal: str, history: list, context: dict,
                    available_tools: list[str]) -> dict:
        """Return either {"thought": ..., "tool": name, "args": {...}}
        or {"final": summary} to end the loop."""
        ...


class MockLLM:
    """Deterministic mock planner (SIMULATED).

    Follows a fixed but sensible investigation policy: survey regions →
    weekly summary → trend analysis → weather context for the anomalous
    region → control-region check → report. Thoughts are template-based and
    reference real values from the agent's context, so the printed chain
    reads like reasoning. This is a stand-in, not a language model.
    """
    name = "mock-deterministic (SIMULATED)"

    def decide_next(self, goal: str, history: list, context: dict,
                    available_tools: list[str]) -> dict:
        n = len(history)
        if n == 0:
            return {
                "thought": "Inspection data just arrived. First, survey which regions reported data this week.",
                "tool": "bloom_stats", "args": {"op": "list_regions"},
            }
        if n == 1:
            return {
                "thought": "Regions confirmed. Pull this week's bloom summary for every region.",
                "tool": "bloom_stats", "args": {"op": "weekly_summary"},
            }
        if n == 2:
            return {
                "thought": "Now compare against last week to spot trend anomalies.",
                "tool": "bloom_stats", "args": {"op": "trend_analysis"},
            }
        if n == 3:
            worst = context.get("worst_region", "?")
            pct = context.get("worst_change_pct", "?")
            return {
                "thought": f"{worst} dropped {pct}% week-over-week — that needs environmental context before I advise anything.",
                "tool": "weather_soil", "args": {"op": "query", "region": worst},
            }
        if n == 4:
            best = context.get("best_region", "?")
            return {
                "thought": f"Check {best} (healthiest region) as a control, to isolate whether this is weather-driven or local.",
                "tool": "weather_soil", "args": {"op": "query", "region": best},
            }
        if n == 5:
            return {
                "thought": "Diagnosis complete: the weather explains the anomaly. Compile the advisory report for the grower.",
                "tool": "report", "args": {"op": "generate"},
            }
        return {"final": "Advisory report generated and ready for the grower."}


class LangChainProvider:
    """TODO(ezra): wire up a real model here.

    Suggested implementation:
      1. `pip install langchain langchain-openai` (or langchain-ollama for local).
      2. Build a system prompt describing the goal, the available tools
         (name + description + JSON schema of args), and the required output
         format: {"thought": str, "tool": str, "args": dict} or {"final": str}.
      3. Use structured output (e.g. `with_structured_output`) so
         `decide_next` returns a validated dict.
      4. Keep the printed THOUGHT/ACTION/OBSERVATION chain — it is the
         portfolio's showpiece.

    Until then, MockLLM keeps the demo runnable with no API key.
    """
    name = "langchain (TODO)"

    def __init__(self, model: str = "gpt-4o-mini"):
        raise NotImplementedError(
            "TODO(ezra): implement LangChainProvider — see the docstring recipe above."
        )

    def decide_next(self, goal: str, history: list, context: dict,
                    available_tools: list[str]) -> dict:
        raise NotImplementedError(
            "TODO(ezra): implement LangChainProvider — see the docstring recipe above."
        )
