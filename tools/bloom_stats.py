"""Bloom inspection statistics tool.

Reads weekly bloom/bud counts per region, computes week-over-week trends,
and flags anomalies (drop >= 30% vs prior week).

TODO(ezra): point this at the real Bloom-Counter output — e.g. parse its
bloom_report.json / CSV instead of the simulated JSON used here. Keep the
same op interface so the agent loop does not change.
"""
from __future__ import annotations
import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data",
                          "simulated_week.json")

ANOMALY_THRESHOLD_PCT = -30.0


class BloomStatsTool:
    name = "bloom_stats"
    description = ("Query bloom/bud inspection counts by region and "
                   "week-over-week trends. Data is SIMULATED.")

    def __init__(self, data_path: str = DATA_PATH):
        with open(data_path) as f:
            self.data = json.load(f)

    def run(self, context: dict | None = None, op: str = "list_regions",
            region: str | None = None) -> dict:
        if op == "list_regions":
            regions = list(self.data["regions"].keys())
            return {
                "ok": True,
                "summary": (f"{len(regions)} regions reporting: "
                            f"{', '.join(regions)} (SIMULATED data)."),
                "data": {"regions": regions},
                "context_updates": {"regions": regions},
            }
        if op == "weekly_summary":
            summaries, parts = {}, []
            for r, days in self.data["regions"].items():
                total_bloom = sum(d["blooms"] for d in days)
                total_bud = sum(d["buds"] for d in days)
                summaries[r] = {
                    "total_blooms": total_bloom,
                    "total_buds": total_bud,
                    "avg_daily_blooms": round(total_bloom / len(days), 1),
                }
                parts.append(f"{r}: {total_bloom} blooms / {total_bud} buds")
            return {
                "ok": True,
                "summary": "Weekly totals — " + "; ".join(parts) + " (SIMULATED).",
                "data": summaries,
                "context_updates": {"weekly_summaries": summaries},
            }
        if op == "trend_analysis":
            trends, parts = {}, []
            for r, days in self.data["regions"].items():
                avg = sum(d["blooms"] for d in days) / len(days)
                prior = self.data["prior_week_avg"][r]
                pct = round((avg - prior) / prior * 100, 1)
                status = ("ANOMALY" if pct <= ANOMALY_THRESHOLD_PCT
                          else "strong" if pct >= 20 else "stable")
                trends[r] = {"change_pct": pct, "status": status}
                parts.append(f"{r}: {pct}% [{status}]")
            worst = min(trends, key=lambda r: trends[r]["change_pct"])
            best = max(trends, key=lambda r: trends[r]["change_pct"])
            return {
                "ok": True,
                "summary": ("Week-over-week bloom change — " + "; ".join(parts)
                            + f". Worst: {worst} ({trends[worst]['change_pct']}%). "
                              "(SIMULATED)."),
                "data": trends,
                "context_updates": {
                    "trends": trends,
                    "worst_region": worst,
                    "worst_change_pct": trends[worst]["change_pct"],
                    "best_region": best,
                },
            }
        return {"ok": False, "summary": f"Unknown op: {op}",
                "data": {}, "context_updates": {}}
