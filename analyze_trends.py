"""
PANDAS PROJECT: Google Trends Comparison
==========================================
Compares search interest over time for competing tech products/AI tools —
a genuinely "trending" topic, and a good excuse to practice pandas' time-series
tools specifically (resampling, rolling windows, correlation).

Workflow:
  1. Load data
  2. Explore data
  3. Clean data (dates, duplicates, missing weeks)
  4. Resample & smooth (rolling average)
  5. Rank topics & find peak interest
  6. Correlation between topics
  7. Pivot: average interest by month
  8. Export results
  9. Visualize

Run it with:  python3 analyze_trends.py

--------------------------------------------------------------------
WANT LIVE DATA INSTEAD OF THE SYNTHETIC CSV? Uncomment the block below
(requires: pip install pytrends) and it plugs into the exact same
pipeline — everything from Section 2 onward is unchanged.
--------------------------------------------------------------------
# from pytrends.request import TrendReq
# pytrends = TrendReq(hl="en-US", tz=360)
# pytrends.build_payload(["iPhone 17", "Pixel 10", "Galaxy S26", "Claude AI", "ChatGPT"],
#                         timeframe="2024-01-01 2026-09-20")
# trends = pytrends.interest_over_time().drop(columns=["isPartial"]).reset_index()
# trends.to_csv("trends_data.csv", index=False)
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

pd.set_option("display.width", 100)

TOPICS = ["iPhone 17", "Pixel 10", "Galaxy S26", "Claude AI", "ChatGPT"]


def section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------------------
section("1. LOAD DATA")

df = pd.read_csv("trends_data.csv", parse_dates=["date"])
print("shape:", df.shape)
print(df.head())


# ---------------------------------------------------------------
# 2. EXPLORE DATA
# ---------------------------------------------------------------
section("2. EXPLORE DATA")

print(df.info())
print()
print("Missing values per column:")
print(df.isna().sum())
print()
print("Duplicate rows:", df.duplicated().sum())
print()
print(df[TOPICS].describe().round(1))


# ---------------------------------------------------------------
# 3. CLEAN DATA
# ---------------------------------------------------------------
section("3. CLEAN DATA")

before = len(df)
df = df.drop_duplicates(subset="date").sort_values("date").reset_index(drop=True)
print(f"Dropped {before - len(df)} duplicate date rows")

# Interpolate missing weeks — for a smooth trend line, linear interpolation
# between neighboring weeks is more honest than fillna(0) or a flat fill.
df[TOPICS] = df[TOPICS].interpolate(method="linear").round(1)
print("Missing values after interpolation:")
print(df.isna().sum())

# Set date as index — the natural move for time-series work
df = df.set_index("date")


# ---------------------------------------------------------------
# 4. RESAMPLE & SMOOTH
# ---------------------------------------------------------------
section("4. RESAMPLE & SMOOTH")

# Monthly average interest (resample = regroup by a time frequency)
monthly = df.resample("ME").mean().round(1)
print("Monthly average interest (last 6 months):")
print(monthly.tail(6))

# 4-week rolling average — smooths weekly noise so real trends stand out
rolling = df.rolling(window=4, min_periods=1).mean().round(1)


# ---------------------------------------------------------------
# 5. RANK TOPICS & FIND PEAK INTEREST
# ---------------------------------------------------------------
section("5. PEAK INTEREST PER TOPIC")

peaks = pd.DataFrame({
    "peak_interest": df[TOPICS].max(),
    "peak_date": df[TOPICS].idxmax(),
    "avg_interest": df[TOPICS].mean().round(1),
}).sort_values("peak_interest", ascending=False)

print(peaks)


# ---------------------------------------------------------------
# 6. CORRELATION BETWEEN TOPICS
# ---------------------------------------------------------------
section("6. CORRELATION BETWEEN TOPICS")

# Do any of these move together? (e.g. do AI assistant searches correlate,
# separate from phone launches?)
corr = df[TOPICS].corr().round(2)
print(corr)


# ---------------------------------------------------------------
# 7. PIVOT: AVERAGE INTEREST BY MONTH x TOPIC (long format)
# ---------------------------------------------------------------
section("7. RESHAPE TO LONG FORMAT")

# melt() turns wide (one column per topic) into long (one row per
# date-topic pair) — the format most plotting/BI tools actually want
long_df = monthly.reset_index().melt(id_vars="date", var_name="topic", value_name="avg_interest")
print(long_df.head(10))


# ---------------------------------------------------------------
# 8. EXPORT RESULTS
# ---------------------------------------------------------------
section("8. EXPORT RESULTS")

df.reset_index().to_csv("trends_cleaned.csv", index=False)
monthly.reset_index().to_csv("monthly_avg_interest.csv", index=False)
peaks.to_csv("peak_interest_summary.csv")
corr.to_csv("topic_correlation.csv")
long_df.to_csv("monthly_long_format.csv", index=False)

print("Saved: trends_cleaned.csv, monthly_avg_interest.csv,")
print("       peak_interest_summary.csv, topic_correlation.csv, monthly_long_format.csv")


# ---------------------------------------------------------------
# 9. VISUALIZE
# ---------------------------------------------------------------
section("9. VISUALIZE")

fig, axes = plt.subplots(2, 2, figsize=(13, 9))

# (a) Raw weekly interest — all topics
df[TOPICS].plot(ax=axes[0, 0], title="Weekly Search Interest (raw)", linewidth=1.2)
axes[0, 0].set_ylabel("Interest (0-100)")
axes[0, 0].legend(fontsize=8)

# (b) Smoothed 4-week rolling average — easier to read trend direction
rolling[TOPICS].plot(ax=axes[0, 1], title="4-Week Rolling Average", linewidth=1.5)
axes[0, 1].set_ylabel("Interest (0-100)")
axes[0, 1].legend(fontsize=8)

# (c) Peak interest bar chart
axes[1, 0].bar(peaks.index, peaks["peak_interest"], color="teal")
axes[1, 0].set_title("Peak Interest by Topic")
axes[1, 0].set_ylabel("Peak Interest")
axes[1, 0].tick_params(axis="x", rotation=30)

# (d) Correlation heatmap
im = axes[1, 1].imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
axes[1, 1].set_xticks(range(len(TOPICS)))
axes[1, 1].set_yticks(range(len(TOPICS)))
axes[1, 1].set_xticklabels(TOPICS, rotation=45, ha="right", fontsize=8)
axes[1, 1].set_yticklabels(TOPICS, fontsize=8)
axes[1, 1].set_title("Correlation Between Topics")
for i in range(len(TOPICS)):
    for j in range(len(TOPICS)):
        axes[1, 1].text(j, i, corr.iloc[i, j], ha="center", va="center", fontsize=8)
fig.colorbar(im, ax=axes[1, 1], fraction=0.046)

plt.tight_layout()
plt.savefig("trends_charts.png", dpi=120)
print("Saved chart: trends_charts.png")

section("DONE")
print("Project complete. Explore the CSVs and PNG that were generated.")
