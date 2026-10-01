# Agri-Agent

**Multi-step AI Agent for smart agriculture**

A multi-step AI agent that turns weekly bloom-inspection data into grower advice.
It runs a full agent loop — **reason → act with tools → observe** — on every
inspection cycle:

1. **Perceive** — ingest this week's bloom/bud counts per region
2. **Analyze** — compare against last week, flag trend anomalies
3. **Investigate** — pull weather/soil context for anomalous regions
4. **Decide** — diagnose the likely cause (frost, water stress, pests…)
5. **Report** — write an advisory report the grower can act on

Built as the agent layer on top of
[Bloom-Counter](https://github.com/) (bloom/bud counting): counting tells you
*what happened*, Agri-Agent tells you *what to do about it*.

> **Project status: scaffold v0.1 (honest edition).**
> The end-to-end agent loop runs today on **simulated** inspection and weather
> data. What is real: the agent loop (reason → act → observe), the tool
> interface, trend/anomaly math, the report generator.
> What is still TODO (clearly marked in code): the LLM reasoning step
> (currently a deterministic mock planner) and the live Bloom-Counter
> integration. Nothing here pretends to be a production agronomist.

---

## Architecture

```
                    ┌──────────────────────┐
                    │  Weekly inspection   │
                    │  bloom/bud counts    │
                    │     (simulated)      │
                    └──────────┬───────────┘
                               ▼
                    ┌──────────────────────┐
  ┌─────────────────│     AGENT LOOP       │──────────────────┐
  │                 │  reason → act →      │                  │
  │                 │  observe (×N steps)  │                  │
  │                 └──────────┬───────────┘                  │
  │                            │ calls                        │
  │            ┌───────────────┼───────────────┐              │
  │            ▼               ▼               ▼              │
  │   ┌──────────────┐ ┌──────────────┐ ┌──────────────┐      │
  │   │ bloom_stats  │ │ weather_soil │ │    report    │      │
  │   │ counts,      │ │ temp, frost  │ │ advisory     │      │
  │   │ trends,      │ │ risk, soil   │ │ markdown     │      │
  │   │ anomalies    │ │ moisture     │ │              │      │
  │   └──────────────┘ └──────────────┘ └──────────────┘      │
  │                                                          │
  │   ┌──────────────────────────────────────────────┐       │
  └───│ LLMProvider (Protocol)                       │───────┘
      │  • MockLLM — deterministic planner (default) │
      │  • LangChainProvider — TODO (real model)     │
      └──────────────────────────────────────────────┘
```

Every step prints its **THOUGHT → ACTION → OBSERVATION** chain, so you can
watch the agent reason.

## Quickstart

```bash
cd Agri-Agent
pip install -r requirements.txt
python examples/demo.py        # simulated week → agent run → advisory report
python -m pytest tests/ -q     # tests
```

The demo generates one deterministic week of simulated data (seed=42), runs the
agent, and writes `examples/output/advisory_report.md`.

## The demo story

Four regions, one week. Three are healthy — **South** is not: blooms drop ~31%
week-over-week right when a cold snap (min 2 °C) and low soil moisture hit.
Watch the agent notice the anomaly, pull the weather context, and recommend
frost protection + irrigation adjustments.

## Project layout

```
Agri-Agent/
├── agent/
│   ├── loop.py        # AgentLoop: reason → act → observe
│   ├── llm.py         # LLMProvider Protocol; MockLLM (default) + LangChain stub
│   └── schemas.py     # AgentStep, RegionDiagnosis, Recommendation
├── tools/
│   ├── bloom_stats.py # inspection counts, trends, anomaly flags (TODO: live Bloom-Counter)
│   ├── weather_soil.py# simulated weather/soil queries, frost & drought flags
│   ├── report.py      # advisory report generator (markdown)
│   ├── simulator.py   # deterministic simulated-data generator (seed=42)
│   └── base.py        # Tool interface
├── data/              # simulated_week.json, simulated_environment.json (SIMULATED)
├── examples/demo.py   # end-to-end demo
└── tests/             # unit tests
```

## Roadmap

- [ ] `LangChainProvider`: real model driving `decide_next` (structured output)
- [ ] Live `Bloom-Counter` integration: read real detection output instead of simulated counts
- [ ] Real weather/soil APIs (Open-Meteo, on-farm sensors)
- [ ] Multi-week memory: track whether past recommendations worked
- [ ] Alerting: SMS/push when a HIGH-priority anomaly appears

## Ethics

Advisories are decision *support*, not agronomic prescriptions. The demo uses
synthetic data only — no real farm, no real grower affected.
