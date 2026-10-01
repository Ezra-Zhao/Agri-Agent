"""End-to-end demo: simulated inspection week → agent run → advisory report.

Every agent step prints its THOUGHT → ACTION → OBSERVATION chain.
Run:  python examples/demo.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.loop import AgentLoop
from agent.llm import MockLLM
from tools.bloom_stats import BloomStatsTool
from tools.weather_soil import WeatherSoilTool
from tools.report import ReportTool
from tools.simulator import generate


def main() -> None:
    print("=" * 60)
    print("Agri-Agent demo — multi-step agricultural advisory agent")
    print("Data: SIMULATED (deterministic, seed=42). Planner: MockLLM.")
    print("=" * 60 + "\n")

    paths = generate()
    print(f"Simulated data ready: {paths['week']}\n")

    tools = {
        "bloom_stats": BloomStatsTool(),
        "weather_soil": WeatherSoilTool(),
        "report": ReportTool(),
    }
    loop = AgentLoop(llm=MockLLM(), tools=tools, verbose=True)
    result = loop.run(
        "A week of bloom inspection data arrived. "
        "Find anomalies and advise the grower."
    )
    print(f"Steps taken: {len(result['steps'])}")
    print(f"Report: {result['context'].get('report_path')}")


if __name__ == "__main__":
    main()
