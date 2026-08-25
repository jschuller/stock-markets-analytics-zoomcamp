# Databricks notebook source
# MAGIC %md
# MAGIC # 06 — Cross-check Homework 1 against the bronze layer
# MAGIC
# MAGIC `homework1.ipynb` answers the 2026 Module 1 questions by calling yfinance live.
# MAGIC This notebook answers the same questions **from
# MAGIC `bronze.ohlcv_daily`** and asserts the two agree.
# MAGIC
# MAGIC That is worth doing for two reasons. It validates the ingestion — 1.96M rows
# MAGIC loaded by `05_ingest_bronze` are only useful if they reproduce a known-good
# MAGIC answer — and it is the difference between a warehouse that exists and a
# MAGIC warehouse that is used.
# MAGIC
# MAGIC ### What bronze can and cannot answer
# MAGIC
# MAGIC | Q | From bronze? | Why |
# MAGIC |---|---|---|
# MAGIC | Q1 — S&P 500 additions by year | **no** | index membership dates come from Wikipedia and are not stored |
# MAGIC | Q2 — world indexes YTD | **yes** | all 11 indexes are in `bronze.ohlcv_daily` |
# MAGIC | Q3 — corrections from all-time highs | **yes** | `^GSPC` back to 1950-01-03 |
# MAGIC | Q4 — earnings-surprise correlation | **no** | earnings dates come from `get_earnings_dates()`, not stored |
# MAGIC
# MAGIC Two of four, stated plainly. Extending bronze to cover Q1 and Q4 would mean
# MAGIC ingesting index membership and an earnings calendar — worth doing before the
# MAGIC capstone, not worth pretending is already done.
# MAGIC
# MAGIC ### Needs no extra dependencies
# MAGIC
# MAGIC Reading Delta needs nothing beyond the serverless base image, so unlike
# MAGIC `05_ingest_bronze` this job declares no `environments:` block. That also
# MAGIC sidesteps the base image's pandas 1.5.3 and the `TA-Lib` naming trap.

# COMMAND ----------

dbutils.widgets.text("catalog", "stock_analytics")
dbutils.widgets.text("q2_start", "2026-01-01")
dbutils.widgets.text("q2_end", "2026-08-21")
# The answers homework1.ipynb produced from live yfinance, as of 2026-08-24.
dbutils.widgets.text("expect_q2", "2")
dbutils.widgets.text("expect_q3", "7.99")

CATALOG = dbutils.widgets.get("catalog")
Q2_START = dbutils.widgets.get("q2_start")
Q2_END = dbutils.widgets.get("q2_end")
EXPECT_Q2 = int(dbutils.widgets.get("expect_q2"))
EXPECT_Q3 = float(dbutils.widgets.get("expect_q3"))

SOURCE = "yfinance"
BENCHMARK = "^GSPC"
WORLD_INDEXES = [
    "^GSPC", "000001.SS", "^HSI", "^AXJO", "^NSEI", "^GSPTSE",
    "^GDAXI", "^FTSE", "^N225", "^MXX", "^BVSP",
]

import json
import pandas as pd

R = {"catalog": CATALOG, "checks": {}, "failures": [],
     "not_in_bronze": {"q1": "index membership dates (Wikipedia)",
                       "q4": "earnings dates (yfinance get_earnings_dates)"}}

def check(name, fn):
    try:
        R["checks"][name] = fn()
    except Exception as e:
        R["checks"][name] = f"{type(e).__name__}: {str(e)[:200]}"
        R["failures"].append(name)

# COMMAND ----------

# ------------------------------------------------------------------------ Q2
# First and last close inside the window per ticker, so an exchange shut on a
# boundary date does not silently drop out — same rule the notebook uses.
def q2_from_bronze():
    tickers = "', '".join(WORLD_INDEXES)
    df = spark.sql(f"""
        WITH w AS (
          SELECT ticker, date, close,
                 first(close) OVER (PARTITION BY ticker ORDER BY date
                     ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_close,
                 last(close)  OVER (PARTITION BY ticker ORDER BY date
                     ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_close
          FROM {CATALOG}.bronze.ohlcv_daily
          WHERE source = '{SOURCE}'
            AND ticker IN ('{tickers}')
            AND date BETWEEN '{Q2_START}' AND '{Q2_END}'
        )
        SELECT ticker,
               round((max(last_close) / max(first_close) - 1) * 100, 4) AS return_pct,
               min(date) AS first_date, max(date) AS last_date, count(*) AS bars
        FROM w GROUP BY ticker ORDER BY return_pct DESC
    """).toPandas()

    R["q2_table"] = [
        {"ticker": r.ticker, "return_pct": round(float(r.return_pct), 2),
         "first_date": str(r.first_date), "last_date": str(r.last_date)}
        for r in df.itertuples()
    ]

    bench = df.loc[df["ticker"] == BENCHMARK, "return_pct"]
    if bench.empty:
        raise ValueError(f"{BENCHMARK} has no rows in bronze for the window")
    n_better = int((df["return_pct"] > float(bench.iloc[0])).sum())

    missing = sorted(set(WORLD_INDEXES) - set(df["ticker"]))
    R["q2_missing_tickers"] = missing
    R["q2_benchmark_return_pct"] = round(float(bench.iloc[0]), 2)
    R["q2_from_bronze"] = n_better
    R["q2_expected"] = EXPECT_Q2

    # The window ends on a completed session, so this one must match exactly.
    if n_better != EXPECT_Q2:
        R["failures"].append("q2_mismatch")
        return f"MISMATCH: bronze {n_better} vs yfinance {EXPECT_Q2}"
    return f"ok ({n_better} indexes beat {BENCHMARK}, {len(df)} tickers)"

check("q2_indexes_ytd", q2_from_bronze)

# COMMAND ----------

# ------------------------------------------------------------------------ Q3
# Identical algorithm to homework1.ipynb: walk consecutive all-time highs, take
# the lowest close between one and the next, keep falls of 5% or more, measure
# peak-to-trough (not peak-to-recovery).
def find_corrections(close, threshold_pct=5.0):
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
            episodes.append({"peak_date": start, "trough_date": trough_date,
                             "drawdown_pct": float(dd),
                             "duration_days": int((trough_date - start).days)})
    return pd.DataFrame(episodes)


def q3_from_bronze():
    pdf = spark.sql(f"""
        SELECT date, close FROM {CATALOG}.bronze.ohlcv_daily
        WHERE source = '{SOURCE}' AND ticker = '{BENCHMARK}' AND close IS NOT NULL
        ORDER BY date
    """).toPandas()

    s = pd.Series(pdf["close"].astype(float).values,
                  index=pd.to_datetime(pdf["date"]))
    R["q3_bars"] = len(s)
    R["q3_span"] = [str(s.index.min().date()), str(s.index.max().date())]

    corr = find_corrections(s, 5.0)
    dd50 = float(corr["drawdown_pct"].median())
    R["q3_corrections"] = len(corr)
    R["q3_from_bronze"] = round(dd50, 2)
    R["q3_expected"] = EXPECT_Q3
    R["q3_median_duration_days"] = int(corr["duration_days"].median())

    # Tolerance, unlike Q2: bronze holds a live intraday bar for the ingest date,
    # so the tail of the series can differ slightly from whatever yfinance served
    # the notebook. A drift beyond 0.10pp means something real changed.
    delta = abs(dd50 - EXPECT_Q3)
    R["q3_delta"] = round(delta, 4)
    if delta > 0.10:
        R["failures"].append("q3_mismatch")
        return f"MISMATCH: bronze {dd50:.2f}% vs yfinance {EXPECT_Q3}% (delta {delta:.2f})"
    return f"ok ({dd50:.2f}% median drawdown over {len(corr)} corrections)"

check("q3_median_drawdown", q3_from_bronze)

# COMMAND ----------

# Coverage context: what is actually in bronze behind these answers.
def coverage():
    df = spark.sql(f"""
        SELECT asset_class, count(*) AS rows, count(DISTINCT ticker) AS tickers,
               min(date) AS lo, max(date) AS hi
        FROM {CATALOG}.bronze.ohlcv_daily WHERE source = '{SOURCE}'
        GROUP BY asset_class ORDER BY rows DESC
    """).toPandas()
    return [{"asset_class": r.asset_class, "rows": int(r.rows),
             "tickers": int(r.tickers), "lo": str(r.lo), "hi": str(r.hi)}
            for r in df.itertuples()]

check("bronze_coverage", coverage)

R["ok"] = not R["failures"]
print(json.dumps(R, indent=2, default=str))
dbutils.notebook.exit(json.dumps(R, default=str))
