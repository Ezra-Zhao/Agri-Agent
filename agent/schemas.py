"""Shared data models for the Agri-Agent."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AgentStep:
    """One reason → act → observe cycle of the agent loop."""
    thought: str
    action_tool: str
    action_args: dict
    observation: str
    simulated: bool = True


@dataclass
class RegionDiagnosis:
    region: str
    bloom_change_pct: float
    status: str  # ANOMALY | strong | stable
    weather_flags: list = field(default_factory=list)
    diagnosis: str = ""


@dataclass
class Recommendation:
    region: str
    priority: str  # HIGH | MEDIUM | LOW
    action: str
    rationale: str
