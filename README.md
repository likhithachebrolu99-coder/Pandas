# Pandas Learning Project: Google Trends Comparison

Compares search interest over time for five competing tech/AI products.
This project focuses specifically on pandas' **time-series toolkit**,
which the sales project didn't touch: resampling, rolling windows,
interpolation, and correlation.

## About the data

`trends_data.csv` is **synthetic** — shaped exactly like Google Trends'
real weekly export (0–100 scaled interest per topic), with realistic
launch spikes, noise, missing weeks, and a couple of duplicate rows to
clean up. It is not real search volume.

**Want real data?** Open `analyze_trends.py` and uncomment the `pytrends`
block at the top of the file. Install it with:
```bash
pip install pytrends
```
Then just re-run the script — every step after loading is unchanged, because
real Google Trends exports have the exact same shape (date + one column per
keyword).

## Files

| File | Purpose |
|---|---|
| `generate_data.py` | Creates the synthetic `trends_data.csv` |
| `trends_data.csv` | Raw weekly interest data (has gaps + duplicate rows) |
| `analyze_trends.py` | **The main script** — read top to bottom |
| `trends_cleaned.csv` | Output: deduplicated, interpolated data |
| `monthly_avg_interest.csv` | Output: resampled to monthly averages |
| `peak_interest_summary.csv` | Output: peak value + date per topic |
| `topic_correlation.csv` | Output: correlation matrix between topics |
| `monthly_long_format.csv` | Output: same monthly data reshaped long (tidy format) |
| `trends_charts.png` | Output: 4-panel chart (raw, smoothed, peaks, correlation) |

## How to run it

```bash
pip install pandas numpy matplotlib
python3 generate_data.py     # (already run — regenerate anytime)
python3 analyze_trends.py
```

## What each section teaches

1. **Load** — `read_csv` with `parse_dates`
2. **Explore** — `.info()`, `.isna().sum()`, `.duplicated()`, `.describe()`
3. **Clean** — `drop_duplicates(subset=...)`, and **`.interpolate()`** — the
   right tool for filling gaps *within* a time series (better than
   `fillna(0)`, which would fake a crash in interest)
4. **Resample & smooth** — `.resample("ME").mean()` to regroup weekly data
   into monthly, and `.rolling(window=4).mean()` for a moving average that
   smooths noise without losing the trend
5. **Rank & peak-finding** — `.max()`, `.idxmax()` to find not just the peak
   value but exactly *when* it happened
6. **Correlation** — `.corr()` to check whether topics move together
7. **Reshape** — `.melt()` to go from wide (one column per topic) to long
   (tidy) format — the shape most plotting/BI tools actually expect
8. **Export** — writing every intermediate result back to CSV
9. **Visualize** — a 4-panel matplotlib figure: raw lines, rolling average,
   bar chart of peaks, and a correlation heatmap drawn by hand with `imshow`

## Ideas to extend it yourself

- [ ] Add a 6th topic of your own choosing and see how it changes the correlation heatmap.
- [ ] Use `.diff()` to compute week-over-week change and find the single biggest weekly jump for each topic.
- [ ] Use `.shift()` to test whether one topic's spike tends to *precede* another's (lagged correlation).
- [ ] Swap `.resample("ME")` for `.resample("QE")` (quarterly) and compare how much smoother it gets.
- [ ] Connect real `pytrends` data (see the commented block) and rerun everything unchanged.
- [ ] Normalize each topic to its own 0-100 range (`(x - x.min()) / (x.max() - x.min()) * 100`) so low-volume topics like Pixel 10 are easier to compare shape-wise against ChatGPT.

## Time-series concepts reference

| Concept | Method(s) |
|---|---|
| Parse dates on load | `pd.read_csv(..., parse_dates=[...])` |
| Set date as index | `.set_index("date")` |
| Fill gaps in a series | `.interpolate()` |
| Regroup by time period | `.resample("ME"/"W"/"QE").mean()` |
| Moving average | `.rolling(window=n).mean()` |
| Week/period-over-period change | `.diff()`, `.pct_change()` |
| Lag a series | `.shift(n)` |
| Peak value + location | `.max()`, `.idxmax()` |
| Relationship between columns | `.corr()` |
| Wide → long reshape | `.melt()` |
