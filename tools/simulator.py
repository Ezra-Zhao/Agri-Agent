"""Deterministic simulated-data generator (seed=42).

Produces one week of bloom/bud inspection counts plus matching weather/soil
data for four regions. A cold snap + dry spell is baked into South mid-week
so the agent has a real anomaly to find. Every record is tagged simulated.

Run:  python tools/simulator.py   (also called automatically by the demo)
"""
from __future__ import annotations
import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
REGIONS = ["North", "East", "South", "West"]

# Daily bloom counts per region (7 days). South collapses mid-week.
BLOOMS = {
    "North": [120, 130, 140, 150, 160, 170, 180],
    "East":  [98, 102, 100, 99, 101, 100, 100],
    "South": [140, 138, 130, 92, 60, 55, 60],
    "West":  [90, 92, 95, 98, 102, 105, 110],
}
PRIOR_WEEK_AVG = {"North": 130, "East": 100, "South": 140, "West": 95}

# (min_temp_c, max_temp_c, soil_moisture_pct, rain_mm) per region per day.
# South days 4-5: cold snap + dry soil.
ENV = {
    "North": [(13, 22, 34, 1), (14, 23, 35, 0), (12, 21, 33, 2), (13, 22, 36, 0),
              (14, 24, 34, 1), (13, 23, 35, 0), (14, 22, 34, 1)],
    "East":  [(12, 21, 32, 0), (13, 22, 33, 1), (11, 20, 31, 0), (12, 21, 32, 0),
              (13, 22, 34, 2), (12, 21, 33, 0), (13, 22, 32, 1)],
    "South": [(12, 21, 30, 0), (12, 20, 29, 0), (11, 19, 28, 0), (3, 12, 20, 0),
              (2, 11, 18, 0), (8, 16, 22, 1), (9, 17, 24, 0)],
    "West":  [(14, 23, 35, 1), (15, 24, 36, 0), (13, 22, 34, 2), (14, 23, 35, 0),
              (15, 25, 37, 1), (14, 24, 36, 0), (15, 23, 35, 1)],
}


def generate(seed: int = 42, out_dir: str = DATA_DIR) -> dict:
    rng = random.Random(seed)
    os.makedirs(out_dir, exist_ok=True)

    regions = {}
    for r in REGIONS:
        days = []
        for i, blooms in enumerate(BLOOMS[r]):
            buds = int(blooms * rng.uniform(1.3, 1.7))
            days.append({"day": i + 1, "blooms": blooms, "buds": buds,
                         "simulated": True})
        regions[r] = days

    week = {
        "meta": {"period": "simulated week (7 days)", "seed": seed,
                 "simulated": True,
                 "note": "Synthetic inspection data. South has a baked-in "
                         "mid-week bloom collapse for the agent to diagnose."},
        "regions": regions,
        "prior_week_avg": PRIOR_WEEK_AVG,
    }
    with open(os.path.join(out_dir, "simulated_week.json"), "w") as f:
        json.dump(week, f, indent=2)

    env_regions = {}
    for r in REGIONS:
        days = []
        for i, (tmin, tmax, moist, rain) in enumerate(ENV[r]):
            days.append({"day": i + 1, "min_temp_c": tmin, "max_temp_c": tmax,
                         "soil_moisture_pct": moist, "rain_mm": rain,
                         "simulated": True})
        env_regions[r] = days
    env = {"meta": {"seed": seed, "simulated": True,
                    "note": "Synthetic weather/soil data matching the inspection week."},
           "regions": env_regions}
    with open(os.path.join(out_dir, "simulated_environment.json"), "w") as f:
        json.dump(env, f, indent=2)

    return {"week": os.path.join(out_dir, "simulated_week.json"),
            "environment": os.path.join(out_dir, "simulated_environment.json")}


if __name__ == "__main__":
    paths = generate()
    print("Wrote simulated data:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
