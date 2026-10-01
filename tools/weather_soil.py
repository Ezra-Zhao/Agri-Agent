"""Weather & soil context tool (SIMULATED data).

Returns daily temperature, soil moisture and rainfall for a region, and
raises agronomic flags: frost risk (min temp < 5 C) and low soil moisture
(< 25%).

TODO(ezra): replace the simulated JSON with a real source — e.g. Open-Meteo
API for weather and on-farm sensor feeds for soil moisture. Keep the same
flag semantics so downstream diagnosis does not change.
"""
from __future__ import annotations
import json
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data",
                          "simulated_environment.json")

FROST_MIN_TEMP_C = 5.0
LOW_MOISTURE_PCT = 25.0


class WeatherSoilTool:
    name = "weather_soil"
    description = ("Query SIMULATED weather and soil data for a region; "
                   "flags frost risk and low soil moisture.")

    def __init__(self, data_path: str = DATA_PATH):
        with open(data_path) as f:
            self.data = json.load(f)

    def run(self, context: dict | None = None, op: str = "query",
            region: str | None = None) -> dict:
        if op != "query" or not region:
            return {"ok": False, "summary": "weather_soil needs op='query' and a region.",
                    "data": {}, "context_updates": {}}
        days = self.data["regions"][region]
        min_t = min(d["min_temp_c"] for d in days)
        max_t = max(d["max_temp_c"] for d in days)
        avg_moist = sum(d["soil_moisture_pct"] for d in days) / len(days)
        total_rain = sum(d["rain_mm"] for d in days)
        flags = []
        if min_t < FROST_MIN_TEMP_C:
            flags.append(f"FROST RISK (min {min_t} C)")
        if avg_moist < LOW_MOISTURE_PCT:
            flags.append(f"LOW SOIL MOISTURE ({avg_moist:.0f}% avg)")
        flag_txt = "; ".join(flags) if flags else "no adverse flags"
        summary = (f"{region}: min {min_t} C / max {max_t} C, "
                   f"soil moisture {avg_moist:.0f}% avg, rain {total_rain} mm — "
                   f"{flag_txt} (SIMULATED).")
        weather = dict(self.data.get("weather", {}).get(region, {}))
        weather.update({"flags": flags})
        return {
            "ok": True,
            "summary": summary,
            "data": {"region": region, "min_temp_c": min_t,
                     "avg_soil_moisture_pct": round(avg_moist, 1),
                     "total_rain_mm": total_rain, "flags": flags},
            "context_updates": {"weather": {**(context or {}).get("weather", {}),
                                            region: {"flags": flags,
                                                     "min_temp_c": min_t,
                                                     "avg_soil_moisture_pct": round(avg_moist, 1)}}},
        }
