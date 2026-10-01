"""Unit tests for Agri-Agent (all on simulated data)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.loop import AgentLoop
from agent.llm import MockLLM
from tools.bloom_stats import BloomStatsTool
from tools.weather_soil import WeatherSoilTool
from tools.report import ReportTool
from tools.simulator import generate, REGIONS

TMP = "/tmp/agri-agent-test"


def _fresh_tools(out=None):
    generate(out_dir=TMP)
    week = os.path.join(TMP, "simulated_week.json")
    env = os.path.join(TMP, "simulated_environment.json")
    report_path = out or os.path.join(TMP, "advisory_report.md")
    return {
        "bloom_stats": BloomStatsTool(data_path=week),
        "weather_soil": WeatherSoilTool(data_path=env),
        "report": ReportTool(output_file=report_path),
    }, report_path


def test_simulator_shape():
    paths = generate(out_dir=TMP)
    with open(paths["week"]) as f:
        week = json.load(f)
    assert set(week["regions"].keys()) == set(REGIONS)
    for days in week["regions"].values():
        assert len(days) == 7
        assert all(d["simulated"] for d in days)


def test_trend_flags_south_anomaly():
    tools, _ = _fresh_tools()
    res = tools["bloom_stats"].run(op="trend_analysis")
    assert res["ok"]
    assert res["data"]["South"]["status"] == "ANOMALY"
    assert res["context_updates"]["worst_region"] == "South"
    for r in ("North", "East", "West"):
        assert res["data"][r]["status"] in ("stable", "strong")


def test_weather_flags_south_frost_and_dry():
    tools, _ = _fresh_tools()
    res = tools["weather_soil"].run(op="query", region="South")
    flags = " ".join(res["data"]["flags"])
    assert "FROST" in flags
    assert "MOISTURE" in flags
    ok = tools["weather_soil"].run(op="query", region="North")
    assert ok["data"]["flags"] == []


def test_mock_llm_action_sequence():
    llm = MockLLM()
    history, context = [], {}
    seq = []
    for _ in range(6):
        d = llm.decide_next("goal", history, context, ["bloom_stats", "weather_soil", "report"])
        assert "tool" in d
        seq.append(d["tool"])
        history.append(object())
    assert seq == ["bloom_stats", "bloom_stats", "bloom_stats",
                   "weather_soil", "weather_soil", "report"]
    assert llm.decide_next("goal", history, context, [])["final"]


def test_full_loop_produces_report():
    tools, report_path = _fresh_tools()
    loop = AgentLoop(llm=MockLLM(), tools=tools, verbose=False)
    result = loop.run("Find anomalies and advise the grower.")
    assert result["final"]
    assert len(result["steps"]) == 6
    assert os.path.exists(report_path)
    with open(report_path) as f:
        md = f.read()
    assert "South" in md and "ANOMALY" in md
    assert "frost protection" in md.lower()
    assert "SIMULATED" in md
