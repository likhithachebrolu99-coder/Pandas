"""
Generates trends_data.csv — a synthetic dataset shaped exactly like what
Google Trends' `interest_over_time()` returns, so you can learn the pandas
workflow now and swap in live data later with zero code changes.

Topics chosen to mirror real 2026 tech-product rivalries (data is synthetic,
not real search volume).

Run once: python3 generate_data.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

weeks = pd.date_range("2024-01-07", "2026-09-20", freq="W-SUN")
topics = ["iPhone 17", "Pixel 10", "Galaxy S26", "Claude AI", "ChatGPT"]

data = {"date": weeks}

# Each topic gets a baseline level, a slow trend (growing/declining),
# a couple of "viral spike" launch events, and weekly noise — just like
# real search interest.
topic_params = {
    "iPhone 17":   {"base": 15, "trend": 0.03, "spikes": [("2025-09-14", 90), ("2025-09-21", 55)]},
    "Pixel 10":    {"base": 8,  "trend": 0.02, "spikes": [("2025-08-17", 60), ("2025-08-24", 30)]},
    "Galaxy S26":  {"base": 10, "trend": 0.015,"spikes": [("2026-01-25", 70), ("2026-02-01", 35)]},
    "Claude AI":   {"base": 12, "trend": 0.08, "spikes": [("2026-06-09", 80), ("2026-06-16", 40)]},
    "ChatGPT":     {"base": 35, "trend": 0.04, "spikes": [("2024-05-13", 65), ("2025-12-05", 55)]},
}

for topic, p in topic_params.items():
    n = len(weeks)
    trend_line = p["base"] + np.arange(n) * p["trend"]
    noise = rng.normal(0, 3, n)
    series = trend_line + noise

    for spike_date, height in p["spikes"]:
        idx = weeks.get_indexer([pd.Timestamp(spike_date)], method="nearest")[0]
        # spike decays over ~3 weeks
        for offset, decay in enumerate([1.0, 0.5, 0.2]):
            if 0 <= idx + offset < n:
                series[idx + offset] += height * decay

    series = np.clip(series, 0, 100)
    data[topic] = series.round().astype(int)

df = pd.DataFrame(data)

# --- inject realistic messiness ---
# 1. A few missing weeks (Google Trends sometimes has gaps in exports)
missing_rows = rng.choice(df.index[10:-10], size=6, replace=False)
for col in topics:
    for r in rng.choice(missing_rows, size=2, replace=False):
        df.loc[r, col] = np.nan

# 2. Duplicate a couple of rows (common copy-paste export error)
dupes = df.sample(3, random_state=3)
df = pd.concat([df, dupes], ignore_index=True).sort_values("date").reset_index(drop=True)

# 3. Store date as string, mixed format, to practice datetime parsing
df["date"] = df["date"].dt.strftime("%Y-%m-%d")

df.to_csv("trends_data.csv", index=False)
print("Created trends_data.csv:", df.shape)
print(df.head())
