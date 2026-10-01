"""Advisory report tool.

Turns the agent's accumulated analysis (trends + weather flags in context)
into a grower-facing markdown report with diagnoses and prioritized
recommendations. Rule-based today; TODO(ezra) for LLM-drafted prose.

Advisories are decision support, not agronomic prescriptions.
"""
from __future__ import annotations
import os
from datetime import date

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "examples", "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "advisory_report.md")


class ReportTool:
    name = "report"
    description = ("Generate the grower's advisory report (markdown) from the "
                   "agent's analysis. Rule-based; SIMULATED data.")

    def __init__(self, output_file: str = OUTPUT_FILE):
        self.output_file = output_file

    def run(self, context: dict | None = None, op: str = "generate") -> dict:
        ctx = context or {}
        trends = ctx.get("trends", {})
        weather = ctx.get("weather", {})
        if not trends:
            return {"ok": False, "summary": "No trend analysis in context; nothing to report.",
                    "data": {}, "context_updates": {}}

        diagnoses, recommendations = [], []
        for region, t in trends.items():
            flags = weather.get(region, {}).get("flags", [])
            status, pct = t["status"], t["change_pct"]
            if status == "ANOMALY":
                causes = []
                if any("FROST" in f for f in flags):
                    causes.append("cold snap / frost damage")
                if any("MOISTURE" in f for f in flags):
                    causes.append("water stress")
                cause_txt = " + ".join(causes) if causes else "unknown — needs on-site inspection"
                diagnoses.append(
                    f"**{region}**: {pct}% bloom change [ANOMALY]. Likely cause: {cause_txt}.")
                if any("FROST" in f for f in flags):
                    recommendations.append({
                        "region": region, "priority": "HIGH",
                        "action": "Deploy frost protection tonight (row covers / wind machines); irrigate in the morning, not the evening.",
                        "rationale": f"Min temp {weather[region]['min_temp_c']} C during bloom drop."})
                if any("MOISTURE" in f for f in flags):
                    recommendations.append({
                        "region": region, "priority": "HIGH",
                        "action": "Increase irrigation frequency; bring soil moisture back to 30-40%.",
                        "rationale": f"Soil moisture {weather[region]['avg_soil_moisture_pct']}% (below 25% stress threshold)."})
                if not causes:
                    recommendations.append({
                        "region": region, "priority": "MEDIUM",
                        "action": "Schedule on-site inspection: check for pests, disease, or irrigation faults.",
                        "rationale": "Sharp bloom drop with no adverse weather signal."})
            else:
                diagnoses.append(f"**{region}**: {pct}% [{status}] — no action needed.")
                recommendations.append({
                    "region": region, "priority": "LOW",
                    "action": "Continue routine monitoring.",
                    "rationale": "Trend within normal range."})

        md = self._render(diagnoses, recommendations)
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, "w") as f:
            f.write(md)
        n_high = sum(1 for r in recommendations if r["priority"] == "HIGH")
        return {
            "ok": True,
            "summary": (f"Advisory report written to {self.output_file}: "
                        f"{len(diagnoses)} regions assessed, {n_high} HIGH-priority actions."),
            "data": {"report_path": self.output_file,
                     "recommendations": recommendations},
            "context_updates": {"report_path": self.output_file},
        }

    @staticmethod
    def _render(diagnoses: list[str], recommendations: list[dict]) -> str:
        lines = [
            "# Bloom Advisory Report",
            "",
            f"_Generated {date.today().isoformat()} by Agri-Agent v0.1 — "
            "all data SIMULATED (demo)._",
            "",
            "## Executive summary",
            "",
        ]
        anomalies = [d for d in diagnoses if "ANOMALY" in d]
        if anomalies:
            lines.append("Anomalies detected this week:")
            lines += [f"- {d}" for d in anomalies]
        else:
            lines.append("No anomalies detected this week.")
        lines += ["", "## Region-by-region", ""]
        lines += [f"- {d}" for d in diagnoses]
        lines += ["", "## Recommendations", ""]
        for r in sorted(recommendations,
                        key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["priority"]]):
            lines.append(f"### [{r['priority']}] {r['region']}")
            lines.append(f"- **Action:** {r['action']}")
            lines.append(f"- **Why:** {r['rationale']}")
            lines.append("")
        lines += ["---",
                  "_Decision support only — not an agronomic prescription. "
                  "Verify on site before acting._"]
        return "\n".join(lines) + "\n"
