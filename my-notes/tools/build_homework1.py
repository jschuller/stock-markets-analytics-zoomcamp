"""Assemble my-notes/01-intro/homework1.ipynb from cell sources.

Kept as a builder rather than hand-written JSON so the notebook stays diffable
and regenerable; the same reason the rest of my-notes/tools/ exists.

    python my-notes/tools/build_homework1.py
    cd my-notes/01-intro && jupyter nbconvert --execute --to notebook --inplace homework1.ipynb
"""
import json


def _lines(s):
    """nbformat wants every source line to keep its trailing newline but the last."""
    parts = s.strip("\n").split("\n")
    return [x + "\n" for x in parts[:-1]] + [parts[-1]]


md = lambda s: {"cell_type": "markdown", "metadata": {}, "source": _lines(s)}
code = lambda s: {"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": _lines(s)}

cells = []

cells.append(md(r"""
# Module 1 — Homework 1 (2026 cohort)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jschuller/stock-markets-analytics-zoomcamp/blob/main/my-notes/01-intro/homework1.ipynb)

**Due 2026-09-02** · questions in [`cohorts/2026/homework1.md`](../../cohorts/2026/homework1.md)
· submission form was still `TO BE ADDED` when this was written

Four scored questions plus two optional free-text ones. Each scored question gets
its own cell and prints its value in an `ANSWER —` block.

Runs unchanged in **three environments** — local Jupyter, Google Colab, and a
Databricks notebook. The setup cell detects which one it is in and installs only
what is missing; nothing else in the notebook is environment-specific.

## Reproducibility

The lecture notebook derives its window from `date.today()` minus 70 years, so its
numbers change every run. A homework answer cannot do that, so **every window here
is pinned to a constant** declared in the setup cell. Re-running this notebook in
December must print what it printed today.

## Where the questions are ambiguous

Two questions contradict themselves, so this notebook computes both readings and
prints both rather than picking silently:

- **Q2** is titled "as of 21 August 2026" and hints `end_date='2026-08-21'`, but its
  prose says "1 January-1 August 2026". Two signals to one; **2026-08-21 is taken as
  the answer**, with the 08-01 reading printed beside it.
- **Q4**'s heading asks for the *median 2-day change after positive surprises*, while
  its step 4 asks for *the correlation of return vs. surprise*. Both are printed.

## Known traps in this material

- `pd.read_html` on Wikipedia is **HTTP 403** without a browser `User-Agent` — the
  question's own hint says so.
- yfinance wants `%Y-%m-%d` date bounds. Passing `"2026-08-22 00:00:00"` fails with
  `ValueError: unconverted data remains: 00:00:00`, which surfaces as an **empty frame
  for every ticker**, not as an error.
- `get_earnings_dates()` returns a **tz-aware** index (America/New_York) at 16:00, i.e.
  after the close. Comparing it to naive timestamps raises.
- yfinance 404s some live symbols. As of 2026-08-24 `MMC`, `FI` and `BK` all fail at
  Yahoo's own chart endpoint — check there before debugging client code.
- 2025's notebook read `^SPX` from Stooq, which returned rows **reversed**, so it used
  negative shifts. Yahoo is chronological — do not copy that sign convention.
"""))

cells.append(md("## Setup"))

cells.append(code(r'''
import importlib.util
import io
import os
import subprocess
import sys
import datetime as dt


def detect_env():
    """local | colab | databricks — decided once, used by the installer below."""
    if "google.colab" in sys.modules:
        return "colab"
    try:
        dbutils          # noqa: F821 — Databricks injects this into notebook globals
        return "databricks"
    except NameError:
        pass
    if os.environ.get("DATABRICKS_RUNTIME_VERSION"):
        return "databricks"       # classic clusters set this; serverless may not
    return "local"


def ensure(*packages):
    """Install only what is actually missing.

    Deliberately subprocess and not `!pip` or `%pip`. `%pip` aborts the entire run
    on failure with CalledProcessError, and neither magic survives headless
    execution by nbconvert or the Databricks Jobs API — both of which this notebook
    is run under. Same idiom as my-notes/databricks/bundle/src/01_env_probe.py.
    """
    missing = [p for p in packages
               if importlib.util.find_spec(p.split("==")[0].replace("-", "_")) is None]
    if missing:
        print(f"installing: {', '.join(missing)}")
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", *missing],
                       check=True)


ENV = detect_env()
# Colab ships numpy/pandas/requests/lxml but not yfinance; Databricks serverless
# ships none of them; a local conda env built from my-notes/environment.yml has
# them all, so this is a no-op there.
ensure("yfinance")

import numpy as np
import pandas as pd
import requests

import yfinance as yf

pd.set_option("display.width", 130)
pd.set_option("display.max_columns", 40)

# ---------------------------------------------------------------------------
# THE PINS. Everything below derives from these — never from date.today().
# ---------------------------------------------------------------------------
HISTORY_START = dt.date(1950, 1, 1)     # Q3 asks for 1950-present

Q1_MIN_YEAR = 2020                      # "STARTING FROM 2020"
Q2_START    = dt.date(2026, 1, 1)       # hint: start_date='2026-01-01'
Q2_END      = dt.date(2026, 8, 21)      # title + hint; prose says 08-01, see below
Q2_END_ALT  = dt.date(2026, 8, 1)       # the prose reading, printed for comparison
Q4_TICKER   = "AMZN"

ANSWERS = {}        # collected by answer(); emitted as JSON by the final cell

print(f"environment: {ENV}")
print(f"yfinance {yf.__version__} | pandas {pd.__version__} | python {sys.version.split()[0]}")
print(f"Q2 window pinned to {Q2_START} -> {Q2_END}")
''' ))

cells.append(md("### Helpers"))

cells.append(code(r'''
BROWSER_UA = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/91.0.4472.124 Safari/537.36")}


def fetch_tables(url, headers=None, timeout=30):
    """Return every HTML table at `url` as a DataFrame.

    pd.read_html(url) does its own fetch with a urllib User-Agent, which Wikipedia
    answers with 403. Fetching via requests with a browser UA and handing read_html
    the *text* is the way round it — the question's own hint shows the same shape.
    """
    r = requests.get(url, headers=headers or BROWSER_UA, timeout=timeout)
    r.raise_for_status()
    return pd.read_html(io.StringIO(r.text))


def get_ohlcv(tickers, start, end=None, auto_adjust=False):
    """yfinance -> {ticker: DataFrame} with a tz-naive DatetimeIndex.

    Normalises the one-vs-many ticker column shape, which is the usual source of
    silent bugs when a question moves from one ticker to eleven.

    Both bounds are formatted %Y-%m-%d. yfinance parses dates with an exact format
    and rejects the "2026-08-22 00:00:00" that str(pd.Timestamp(...)) produces, with
    ValueError("unconverted data remains: 00:00:00") — which shows up as an empty
    frame for every ticker rather than as an obvious failure.

    `end` is exclusive in yfinance, so it is bumped one day to make the homework's
    inclusive "as of <date>" wording behave as written.
    """
    single = isinstance(tickers, str)
    tickers = [tickers] if single else list(tickers)
    d8 = lambda x: pd.Timestamp(x).strftime("%Y-%m-%d")

    kw = dict(start=d8(start), auto_adjust=auto_adjust, actions=False,
              progress=False, group_by="ticker")
    if end is not None:
        kw["end"] = d8(pd.Timestamp(end) + pd.Timedelta(days=1))

    raw = yf.download(tickers, **kw)
    out = {}
    for t in tickers:
        if isinstance(raw.columns, pd.MultiIndex):
            if t not in raw.columns.get_level_values(0):
                continue
            df = raw[t].copy()
        else:
            df = raw.copy()
        df = df.dropna(subset=["Close"])
        if df.empty:
            continue
        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_localize(None)
        out[t] = df

    missing = [t for t in tickers if t not in out]
    if missing:
        print(f"  !! no data returned for: {missing}")
    return out


def answer(key, label, value, note=""):
    """Print a submitted value unmissably, and record it for the final JSON block.

    The homework is graded on these scalars, so they are worth making impossible
    to miss in a long notebook.
    """
    ANSWERS[key] = value
    bar = "=" * 64
    print(f"\n{bar}\nANSWER — {label}\n  >>> {value} <<<")
    if note:
        print(f"  {note}")
    print(bar)
    return value
''' ))

# ------------------------------------------------------------------ Q1
cells.append(md(r"""
---
## Q1 — S&P 500 additions by year

> Which (full) year had the highest number of additions, **starting from 2020**?

Note the difference from 2025, which excluded only 1957 and searched all history.
The 2020 floor also makes the "full year" wording matter: 2026 is still in progress,
so it is excluded — a partial year cannot win a "highest number of additions" contest
on equal terms.
"""))

cells.append(code(r'''
Q1_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

tables = fetch_tables(Q1_URL)
print(f"tables found: {len(tables)} | shapes: {[t.shape for t in tables[:3]]}")

constituents = tables[0]
constituents.columns = [str(c).strip() for c in constituents.columns]
print(f"columns: {list(constituents.columns)}")
constituents.head(3)
''' ))

cells.append(code(r'''
# The column has been called "Date added" and "Date first added" across revisions,
# and values range from "1976-08-09" to "1957" to "March 4, 1957". Resolve the name,
# then pull a 4-digit year rather than trusting a date parser.
date_col = next(c for c in constituents.columns
                if "date" in c.lower() and "added" in c.lower())
tick_col = next(c for c in constituents.columns
                if "symbol" in c.lower() or "ticker" in c.lower())
print(f"using date column {date_col!r}, ticker column {tick_col!r}")

q1 = constituents[[tick_col, date_col]].copy()
q1.columns = ["ticker", "date_added"]
q1["year_added"] = (q1["date_added"].astype(str)
                    .str.extract(r"(\d{4})")[0].astype("Int64"))

print(f"\nconstituents: {len(q1)} | year parsed for {q1['year_added'].notna().sum()}")

per_year = (q1.dropna(subset=["year_added"])
              .groupby("year_added").size().sort_index())

# "Full year", so the in-progress current year cannot compete on equal footing.
CURRENT_YEAR = int(per_year.index.max())
full_years = per_year[(per_year.index >= Q1_MIN_YEAR) & (per_year.index < CURRENT_YEAR)]

print(f"\nadditions per year from {Q1_MIN_YEAR} "
      f"({CURRENT_YEAR} excluded as incomplete — it has {per_year.get(CURRENT_YEAR, 0)} so far):")
print(full_years.to_string())

best = int(full_years[full_years == full_years.max()].index.max())
answer("q1", "Q1 — year with most additions since 2020", best,
       f"{full_years.max()} additions; ties broken to the most recent year")

# --- structural checks. No published answer key exists for this question. ---
assert 480 <= len(q1) <= 520, f"expected ~500 constituents, got {len(q1)}"
assert q1["year_added"].notna().mean() > 0.90, "too many unparsed dates"
print(f"\n[structural check] {len(q1)} constituents, "
      f"{q1['year_added'].notna().mean():.1%} of dates parsed — plausible.")

# The question's "Additional" prompt.
over_20 = int(((CURRENT_YEAR - q1["year_added"].dropna()) > 20).sum())
print(f"[additional] constituents in the index more than 20 years: {over_20}")
''' ))

# ------------------------------------------------------------------ Q2
cells.append(md(r"""
---
## Q2 — world indexes YTD vs the S&P 500

> How many indexes (out of 10) have better year-to-date returns than the US
> (S&P 500) as of August 21, 2026?

Eleven tickers are listed for a question phrased "out of 10" — the benchmark is one
of them. The count below therefore excludes `^GSPC` explicitly, which is the trap.

Returns use **Close**, as the question instructs, and are measured from the first to
the last available close inside the window so that a market shut on a boundary date
does not silently drop out.
"""))

cells.append(code(r'''
WORLD_INDEXES = {
    "^GSPC":     "United States — S&P 500",
    "000001.SS": "China — Shanghai Composite",
    "^HSI":      "Hong Kong — Hang Seng",
    "^AXJO":     "Australia — S&P/ASX 200",
    "^NSEI":     "India — Nifty 50",
    "^GSPTSE":   "Canada — S&P/TSX Composite",
    "^GDAXI":    "Germany — DAX",
    "^FTSE":     "United Kingdom — FTSE 100",
    "^N225":     "Japan — Nikkei 225",
    "^MXX":      "Mexico — IPC",
    "^BVSP":     "Brazil — Ibovespa",
}


def compare_returns(tickers, start, end, benchmark="^GSPC", labels=None):
    """Rank period returns on Close and count how many beat the benchmark."""
    data = get_ohlcv(list(tickers), start=start, end=end)
    rows = []
    for t, df in data.items():
        first, last = df["Close"].iloc[0], df["Close"].iloc[-1]
        rows.append({"ticker": t, "name": (labels or {}).get(t, t),
                     "first_date": df.index[0].date(), "last_date": df.index[-1].date(),
                     "return_pct": (last / first - 1) * 100})
    out = pd.DataFrame(rows).sort_values("return_pct", ascending=False).reset_index(drop=True)
    bench = out.loc[out["ticker"] == benchmark, "return_pct"]
    if bench.empty:
        raise ValueError(f"benchmark {benchmark} returned no data")
    return out, int((out["return_pct"] > bench.iloc[0]).sum()), float(bench.iloc[0])


table, n_better, bench_ret = compare_returns(
    WORLD_INDEXES, Q2_START, Q2_END, benchmark="^GSPC", labels=WORLD_INDEXES)

print(f"window {Q2_START} -> {Q2_END} | S&P 500 returned {bench_ret:+.2f}%\n")
print(table.to_string(index=False, float_format=lambda v: f"{v:+.2f}"))
answer("q2", "Q2 — indexes beating the S&P 500", n_better,
       f"as of {Q2_END}, out of {len(table) - 1} non-benchmark indexes")

# The question's prose says "1 January-1 August 2026" while its title and hint both
# say 21 August. Print the other reading rather than hiding the ambiguity.
_, n_alt, bench_alt = compare_returns(WORLD_INDEXES, Q2_START, Q2_END_ALT,
                                      benchmark="^GSPC", labels=WORLD_INDEXES)
print(f"\n[ambiguity] using the prose window {Q2_START} -> {Q2_END_ALT} instead: "
      f"S&P 500 {bench_alt:+.2f}%, {n_alt} indexes ahead."
      + ("  Same answer either way." if n_alt == n_better else
         "  DIFFERENT — the title/hint reading (21 Aug) is the one submitted above."))

assert not table["return_pct"].isna().any(), "a NaN return means a broken fetch"
missing = set(WORLD_INDEXES) - set(table["ticker"])
print(f"[structural check] {len(table)}/{len(WORLD_INDEXES)} indexes returned data."
      + (f" Missing: {sorted(missing)}" if missing else ""))
''' ))

# ------------------------------------------------------------------ Q3
cells.append(md(r"""
---
## Q3 — corrections from all-time highs

> Calculate the **median drawdown (in %)** of significant market corrections in the
> S&P 500, where a correction is a fall of more than 5% from the closest all-time high.

Changed from 2025, which asked for median *duration*. Both are computed below; the
drawdown percentile is the submitted answer.

This is the one question with a real numeric self-check: the sheet publishes the top
ten corrections by drawdown, so a correct implementation must reproduce them exactly.
"""))

cells.append(code(r'''
def find_corrections(close, threshold_pct=5.0):
    """Drawdown episodes measured from each all-time high.

    Walks consecutive all-time highs; between one ATH and the next, the lowest close
    is the trough. Keeps episodes whose fall exceeds `threshold_pct`. Duration is
    calendar days from ATH to trough — peak-to-trough, not peak-to-recovery, which is
    the convention the published table uses.
    """
    close = close.dropna().sort_index()
    ath_dates = list(close.index[close >= close.cummax()])

    episodes = []
    for i, start in enumerate(ath_dates):
        end = ath_dates[i + 1] if i + 1 < len(ath_dates) else close.index[-1]
        window = close.loc[start:end]
        if len(window) < 2:
            continue
        trough_val = window.iloc[1:].min()
        trough_date = window.iloc[1:].idxmin()
        high = close.loc[start]
        dd = (high - trough_val) / high * 100
        if dd >= threshold_pct:
            episodes.append({"peak_date": start.date(), "trough_date": trough_date.date(),
                             "peak": float(high), "trough": float(trough_val),
                             "drawdown_pct": float(dd),
                             "duration_days": int((trough_date - start).days)})
    return pd.DataFrame(episodes)


spx = get_ohlcv("^GSPC", start=HISTORY_START)["^GSPC"]
print(f"^GSPC: {len(spx)} bars, {spx.index[0].date()} -> {spx.index[-1].date()}")

corrections = find_corrections(spx["Close"], threshold_pct=5.0)

dd25, dd50, dd75 = corrections["drawdown_pct"].quantile([0.25, 0.50, 0.75])
du25, du50, du75 = corrections["duration_days"].quantile([0.25, 0.50, 0.75])

print(f"\ncorrections >= 5%: {len(corrections)}")
print(f"drawdown %  — 25th {dd25:.2f} | median {dd50:.2f} | 75th {dd75:.2f}")
print(f"duration d  — 25th {du25:.0f} | median {du50:.0f} | 75th {du75:.0f}")

answer("q3", "Q3 — median drawdown of corrections (%)", f"{dd50:.2f}%")
print(f"  (2025 asked for duration instead; that median is {du50:.0f} days)")
''' ))

cells.append(code(r'''
# --- numeric self-check, against the table printed in the question itself ---
PUBLISHED_TOP10 = [
    ("2007-10-09", "2009-03-09", 56.8, 517), ("2000-03-24", "2002-10-09", 49.1, 929),
    ("1973-01-11", "1974-10-03", 48.2, 630), ("1968-11-29", "1970-05-26", 36.1, 543),
    ("2020-02-19", "2020-03-23", 33.9,  33), ("1987-08-25", "1987-12-04", 33.5, 101),
    ("1961-12-12", "1962-06-26", 28.0, 196), ("1980-11-28", "1982-08-12", 27.1, 622),
    ("2022-01-03", "2022-10-12", 25.4, 282), ("1966-02-09", "1966-10-07", 22.2, 240),
]

top10 = corrections.nlargest(10, "drawdown_pct").reset_index(drop=True)
print("computed top 10 by drawdown:")
print(top10.to_string(index=False, float_format=lambda v: f"{v:.2f}"))

print("\nvs published:")
ok = 0
for i, (pk, tr, dd, dur) in enumerate(PUBLISHED_TOP10):
    if i >= len(top10):
        print(f"  {pk}: MISSING from computed top-10")
        continue
    r = top10.loc[i]
    hit = (str(r["peak_date"]) == pk and str(r["trough_date"]) == tr
           and abs(r["drawdown_pct"] - dd) < 0.5 and abs(r["duration_days"] - dur) <= 2)
    ok += hit
    print(f"  {'OK  ' if hit else 'DIFF'} {pk} -> {tr}  {dd}%  {dur}d"
          f"   | computed {r['peak_date']} -> {r['trough_date']} "
          f"{r['drawdown_pct']:.1f}% {r['duration_days']}d")

print(f"\n[numeric check] {ok}/10 published corrections reproduced exactly.")
if ok < 8:
    print("  NOTE: under 8 matches means the ATH/trough definition differs from the "
          "instructor's. Check the 5% threshold and the peak-to-trough (not "
          "peak-to-recovery) duration convention before submitting.")
''' ))

# ------------------------------------------------------------------ Q4
cells.append(md(r"""
---
## Q4 — AMZN earnings surprises

> Load earnings data with `get_earnings_dates()`, compute the 2-day return as
> `Close_Day3 / Close_Day1 - 1` around each announcement, and answer:
> **what is the correlation of stock return vs. earnings surprise?**

The heading of this question asks for the *median 2-day change after positive
surprises* while step 4 asks for the *correlation*. Both are printed; the
correlation is treated as the answer, since it is the numbered step.

Two mechanical details:

- `get_earnings_dates()` returns a **tz-aware** index (America/New_York) stamped
  16:00 — after the close. Comparing that to naive timestamps raises, so it is
  localised away before matching.
- Because the release is after the close, the announcement date is Day 2 and the
  reaction lands on Day 3. `Close_Day3 / Close_Day1 - 1` centred on the announcement
  day captures it, which is exactly what the question specifies.
"""))

cells.append(code(r'''
def two_day_returns(close):
    """Close_Day3 / Close_Day1 - 1, indexed by Day 2 (the announcement day)."""
    return pd.Series(close.shift(-1).values / close.shift(1).values,
                     index=close.index, name="ret_2d") - 1


ticker_obj = yf.Ticker(Q4_TICKER)
earnings = ticker_obj.get_earnings_dates()
print(f"get_earnings_dates(): {earnings.shape} | columns {list(earnings.columns)}")

e = earnings.reset_index()
e.columns = ["earnings_date", "eps_estimate", "eps_actual", "surprise_pct"]

# tz-aware (America/New_York, 16:00) -> naive calendar day, so it can be matched
# against the price index without raising.
e["date"] = pd.to_datetime(e["earnings_date"]).dt.tz_localize(None).dt.normalize()
e = e.dropna(subset=["eps_actual", "surprise_pct"])      # drop the unreported quarter
print(f"reported quarters: {len(e)}  ({e['date'].min().date()} -> {e['date'].max().date()})")

px = get_ohlcv(Q4_TICKER, start=HISTORY_START)[Q4_TICKER]
ret2d = two_day_returns(px["Close"]).dropna()
print(f"{Q4_TICKER}: {len(px)} bars, 2-day returns computed for {len(ret2d)}")

# Snap each announcement to its trading day (or the next one, if it fell on a holiday).
trading_days = pd.DatetimeIndex(ret2d.index)
pos = trading_days.searchsorted(e["date"].values)
keep = pos < len(trading_days)
e = e.loc[keep].copy()
e["match_date"] = trading_days[pos[keep]]
e["ret_2d_pct"] = ret2d.reindex(e["match_date"]).to_numpy() * 100
e = e.dropna(subset=["ret_2d_pct"])

print(f"\nmatched announcements: {len(e)}")
print(e[["date", "eps_estimate", "eps_actual", "surprise_pct", "ret_2d_pct"]]
      .to_string(index=False, float_format=lambda v: f"{v:.2f}"))
''' ))

cells.append(code(r'''
corr = e["ret_2d_pct"].corr(e["surprise_pct"])
answer("q4", "Q4 — correlation of 2-day return vs earnings surprise", f"{corr:.4f}",
       f"Pearson, n = {len(e)}")

# The heading's reading, printed alongside because the question asks both ways.
positive = e[e["surprise_pct"] > 0]
print(f"\n[heading's reading] median 2-day return after a positive surprise: "
      f"{positive['ret_2d_pct'].median():.2f}%  (n = {len(positive)})")
print(f"[baseline]          median 2-day return over all history: "
      f"{ret2d.median() * 100:.2f}%")

# Spearman too: one 215% surprise dominates a Pearson correlation on 25 points.
print(f"\n[robustness] Spearman rank correlation: "
      f"{e['ret_2d_pct'].corr(e['surprise_pct'], method='spearman'):.4f}")
print(f"             largest surprise in the sample: {e['surprise_pct'].max():.1f}%")

assert len(e) >= 20, f"only {len(e)} matched announcements — expected ~24"
print(f"\n[structural check] {len(e)} matched announcements, no NaNs in either series.")
''' ))

# ------------------------------------------------------------------ Q5/Q6
cells.append(md(r"""
---
## Q5 — capstone idea (free text, optional)

**A short-horizon recommendation system for US large caps, built on the lakehouse
this coursework already stands up, with an LLM layer that can only argue from
features that actually exist.**

Concretely:

- **Universe and horizon.** The 190 US large caps already in
  `bronze.ohlcv_daily`, on a 1–4 week horizon. Not a new universe — a deeper one.
- **Close the two gaps this homework exposed.** Q1 needed S&P 500 membership
  history and Q4 needed an earnings calendar; neither is in bronze, which is
  exactly why `crosscheck_bronze` can only answer two of the four questions.
  Ingesting both is the first capstone task, and it is motivated by evidence
  rather than guessed at. Index-addition dates are independently interesting: the
  question's own context notes that new entrants pop on announcement.
- **Features.** TA-Lib indicators from Module 2, plus macro regime features from
  the 17 FRED series already loaded — yield-curve slope (`DGS10 - DGS2`), credit
  spread (`BAA - AAA`), breakeven inflation (`T10YIE`), `VIXCLS`. The macro side
  is free; it is already sitting in `bronze.macro_series`.
- **Model.** sklearn on a strictly temporal split, with the split boundaries
  written to `ml.model_runs` on every run — the schema already has columns for
  them precisely because lookahead bias is the easiest mistake to make here.
- **Simulation.** `sim.trades` with `fees` never null. Fees are what kill
  high-frequency strategies, and a good model that loses money after costs is the
  normal outcome, not the surprising one.
- **The AI layer, and its constraint.** An agent that turns each prediction into a
  written rationale — but restricted to citing features that exist in the feature
  store, so it cannot invent a reason the model did not use. The interesting
  problem is not generating the text, it is making the explanation *faithful* to
  the model. That constraint is the project.

Risk I already know about: TensorFlow will not import on Databricks serverless
(protobuf conflict), so any deep-learning component runs in Colab or locally.

## Q6 — additional metrics (free text, optional)

Seventeen macro series are already loaded, so this question is a `GROUP BY` rather
than a download:

```sql
SELECT series_id, count(*), min(date), max(date)
FROM stock_analytics.bronze.macro_series GROUP BY 1 ORDER BY 1;
```

**Already in, and why each earns its place:**

| Series | Why it matters |
|---|---|
| `DGS1 DGS2 DGS3 DGS5 DGS10 DGS30` | The whole curve, so slope and inversion are derivable rather than assumed. Inversion has preceded every recent US recession |
| `AAA`, `BAA` | Their spread is a clean risk-appetite proxy that widens before equity drawdowns |
| `T10YIE` | Market-implied inflation — separates a nominal rate move from a real one |
| `VIXCLS`, `GVZCLS` | Equity and gold implied volatility; regime labels, and VIX is mean-reverting enough to be a feature rather than noise |
| `FEDFUNDS`, `CPILFESL`, `GDPPOT` | The policy triangle the lectures build up from |
| `DCOILWTICO`, `DCOILBRENTEU` | Input costs; their spread is a transport/logistics signal |

**Worth adding next, in priority order:**

1. **S&P 500 membership history** — the add/drop dates Q1 scrapes from Wikipedia.
   Storing them turns a one-off scrape into a joinable dimension and makes index
   -addition events a tradeable feature.
2. **Earnings calendar with surprise** — `get_earnings_dates()` per ticker, which
   Q4 needs. Note the trap Ivan flags: financial-statement data arrives 1–2 months
   after quarter close, so joining on report date leaks the future into training.
   Store both the announcement date and the period it covers.
3. **Short interest** and **sector-ETF relative strength** — crowding and rotation,
   neither derivable from OHLCV alone.

Alpha Vantage is connected via MCP and covers most of this, but its free tier is
**25 requests/day** — a fallback for specific symbols, not a bulk source. Anything
universe-wide needs a different provider or a lot of patience.
"""))

cells.append(md("""
---
## Submission block
"""))

cells.append(code(r'''
import json

print(json.dumps(ANSWERS, indent=2))

# On Databricks this returns the answers through the Jobs API, which discards
# print() output — so the same notebook works as a scheduled job. Off Databricks
# `dbutils` is simply not defined and this is a no-op. It is deliberately the
# very last statement: notebook.exit() stops execution, so anything after it
# would never run interactively.
try:
    dbutils.notebook.exit(json.dumps(ANSWERS))   # noqa: F821
except NameError:
    pass
''' ))

# nbformat 4.5 requires a cell id; deterministic so the file diffs cleanly.
for _i, _c in enumerate(cells):
    _c["id"] = f"cell-{_i:02d}"

nb = {
    "cells": cells,
    "metadata": {
        # Deliberately the generic python3 kernel, not the local conda env: this
        # notebook is meant to open unchanged in Colab and Databricks, and a
        # `stock-markets-analytics` / 3.11.16 fingerprint is a local artifact.
        "kernelspec": {"display_name": "Python 3",
                       "language": "python", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out = "my-notes/01-intro/homework1.ipynb"
with open(out, "w") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
    f.write("\n")
print(f"wrote {out}: {len(cells)} cells "
      f"({sum(c['cell_type'] == 'code' for c in cells)} code)")
