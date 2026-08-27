# Databricks notebook source
# MAGIC %md
# MAGIC # 07 — Data quality checks on `bronze`
# MAGIC
# MAGIC `04_verify_layout` asserts the layout is the right *shape*. This asserts the
# MAGIC data in it is the right *data* — the two failure modes are unrelated, and a
# MAGIC table can pass column-type verification while holding half a load.
# MAGIC
# MAGIC Same contract as the other check notebooks: JSON out with `"ok"`, one failing
# MAGIC check recorded rather than aborting the run, so a single bad rule cannot hide
# MAGIC the other nine.
# MAGIC
# MAGIC ### What each check is actually for
# MAGIC
# MAGIC | Check | Catches |
# MAGIC |---|---|
# MAGIC | freshness | a pipeline that silently stopped |
# MAGIC | row and ticker counts | a partial load that "succeeded" |
# MAGIC | `(ticker, date)` uniqueness per source | the append-vs-replace trap |
# MAGIC | OHLC internal consistency | upstream data corruption |
# MAGIC | null rates | quiet degradation |
# MAGIC | universe drift both ways | a ticker loaded that nothing knows about, or a known one that stopped loading |
# MAGIC
# MAGIC ### Freshness will go red, and that is correct
# MAGIC
# MAGIC `ingest_bronze`'s daily schedule is deliberately **PAUSED** until Module 5, so
# MAGIC bronze goes stale by design. This job is therefore **not** wired into the
# MAGIC deploy gate in `.github/workflows/bundle-deploy.yml` — `verify_layout` stays
# MAGIC the gate. Run this on demand now; put it on a schedule when the pipeline is
# MAGIC unpaused. Widen `max_staleness_days` only if you mean it.
# MAGIC
# MAGIC ### Needs no extra dependencies
# MAGIC
# MAGIC Reading Delta needs nothing beyond the serverless base image, so like
# MAGIC `06_crosscheck_bronze` this job declares no `environments:` block.

# COMMAND ----------

# Defaults are the interactive fallback; the job passes these from resources/jobs.yml.
# All widget values are strings and are cast here, matching the other notebooks.
dbutils.widgets.text("catalog", "stock_analytics")
dbutils.widgets.text("max_staleness_days", "5")
dbutils.widgets.text("macro_max_staleness_days", "10")
dbutils.widgets.text("min_ohlcv_rows", "1900000")
dbutils.widgets.text("min_tickers", "200")
dbutils.widgets.text("max_null_rate_pct", "1.0")
# Equities and indexes must be internally consistent; futures settle outside the
# day's traded range, so commodity gets an explicit, documented allowance.
dbutils.widgets.text("max_violation_rate_pct", "0.0")
dbutils.widgets.text("commodity_max_violation_rate_pct", "5.0")
dbutils.widgets.text("expect_macro_series", "17")
# The three Yahoo 404s, recorded so a KNOWN gap stays known: if this list stops
# matching, either a ticker came back or a new one broke, and both are news.
dbutils.widgets.text("expect_no_data_tickers", "BK,FI,MMC")

CATALOG = dbutils.widgets.get("catalog")
MAX_STALENESS_DAYS = int(dbutils.widgets.get("max_staleness_days"))
MACRO_MAX_STALENESS_DAYS = int(dbutils.widgets.get("macro_max_staleness_days"))
MIN_OHLCV_ROWS = int(dbutils.widgets.get("min_ohlcv_rows"))
MIN_TICKERS = int(dbutils.widgets.get("min_tickers"))
MAX_NULL_RATE_PCT = float(dbutils.widgets.get("max_null_rate_pct"))
MAX_VIOLATION_RATE_PCT = float(dbutils.widgets.get("max_violation_rate_pct"))
COMMODITY_MAX_VIOLATION_RATE_PCT = float(
    dbutils.widgets.get("commodity_max_violation_rate_pct"))
EXPECT_MACRO_SERIES = int(dbutils.widgets.get("expect_macro_series"))
EXPECT_NO_DATA_TICKERS = sorted(
    t.strip() for t in dbutils.widgets.get("expect_no_data_tickers").split(",") if t.strip())

SOURCE = "yfinance"
MACRO_SOURCE = "fred"

import datetime as dt
import json

import numpy as np

R = {"catalog": CATALOG, "source": SOURCE, "checks": {}, "metrics": {}, "failures": []}

def check(name, fn):
    try:
        R["checks"][name] = fn()
    except Exception as e:
        R["checks"][name] = f"{type(e).__name__}: {str(e)[:200]}"
        R["failures"].append(name)

def failed(name, msg):
    """Record a failure and return the string that goes in the report."""
    R["failures"].append(name)
    return f"FAIL: {msg}"

def one(sql):
    """First row of a query, as a dict."""
    return spark.sql(sql).collect()[0].asDict()

# COMMAND ----------

# ------------------------------------------------------------------- freshness
def ohlcv_freshness():
    row = one(f"""
        SELECT max(date) AS hi, min(date) AS lo, count(*) AS n
        FROM {CATALOG}.bronze.ohlcv_daily WHERE source = '{SOURCE}'
    """)
    if row["n"] == 0:
        return failed("ohlcv_freshness", "no rows at all")

    hi = row["hi"]
    # Business days, so a Monday run does not report the weekend as staleness.
    lag = int(np.busday_count(hi, dt.date.today()))
    R["metrics"]["ohlcv_span"] = [str(row["lo"]), str(hi)]
    R["metrics"]["ohlcv_staleness_business_days"] = lag

    if lag > MAX_STALENESS_DAYS:
        return failed("ohlcv_freshness",
                      f"latest bar {hi} is {lag} business days old "
                      f"(limit {MAX_STALENESS_DAYS}). The ingest schedule is PAUSED — "
                      f"unpause it in resources/jobs.yml or run ingest_bronze.")
    return f"ok (latest {hi}, {lag} business days old)"

check("ohlcv_freshness", ohlcv_freshness)

# COMMAND ----------

# ------------------------------------------------------- volume of what loaded
def ohlcv_volume():
    row = one(f"""
        SELECT count(*) AS rows, count(DISTINCT ticker) AS tickers
        FROM {CATALOG}.bronze.ohlcv_daily WHERE source = '{SOURCE}'
    """)
    by_class = spark.sql(f"""
        SELECT asset_class, count(*) AS rows, count(DISTINCT ticker) AS tickers
        FROM {CATALOG}.bronze.ohlcv_daily WHERE source = '{SOURCE}'
        GROUP BY asset_class ORDER BY asset_class
    """).collect()
    R["metrics"]["ohlcv_rows"] = row["rows"]
    R["metrics"]["ohlcv_tickers"] = row["tickers"]
    R["metrics"]["by_asset_class"] = {
        r["asset_class"]: {"rows": r["rows"], "tickers": r["tickers"]} for r in by_class}

    problems = []
    if row["rows"] < MIN_OHLCV_ROWS:
        problems.append(f"{row['rows']} rows < {MIN_OHLCV_ROWS}")
    if row["tickers"] < MIN_TICKERS:
        problems.append(f"{row['tickers']} tickers < {MIN_TICKERS}")
    # An asset class present in the table but empty means a group failed to load.
    empty = [r["asset_class"] for r in by_class if r["rows"] == 0]
    if empty:
        problems.append(f"empty asset classes: {empty}")

    if problems:
        return failed("ohlcv_volume", "; ".join(problems))
    return (f"ok ({row['rows']:,} rows, {row['tickers']} tickers, "
            f"{len(by_class)} asset classes)")

check("ohlcv_volume", ohlcv_volume)

# COMMAND ----------

# ------------------------------------------------------------- the append trap
def ohlcv_uniqueness():
    """One (ticker, date) per source.

    Bronze is append-only ACROSS sources by design — the same bar from yfinance and
    from Alpha Vantage is expected, and silver resolves it. The same bar from
    yfinance twice is a duplicate no rule can undo, which is why 05_ingest_bronze
    defaults to mode=replace_source.
    """
    dupes = one(f"""
        SELECT count(*) AS n FROM (
            SELECT ticker, date FROM {CATALOG}.bronze.ohlcv_daily
            WHERE source = '{SOURCE}' GROUP BY ticker, date HAVING count(*) > 1)
    """)["n"]
    R["metrics"]["ohlcv_duplicate_keys"] = dupes
    if dupes:
        return failed("ohlcv_uniqueness",
                      f"{dupes} (ticker, date) keys appear more than once for "
                      f"source '{SOURCE}' — someone ran with mode=append")
    return "ok (no within-source duplicates)"

check("ohlcv_uniqueness", ohlcv_uniqueness)

# COMMAND ----------

# ------------------------------------------------------ is a bar a valid bar
# high >= low, open and close inside the range, nothing at or below zero.
BAD_BAR = """(high < low OR close > high OR close < low
              OR open > high OR open < low
              OR least(open, high, low, close) <= 0)"""

def ohlcv_price_sanity():
    """OHLC bars must be internally consistent — with two documented exceptions.

    **The latest date holds a partial bar.** `05_ingest_bronze` runs during the
    session, so the most recent row's close is a live quote against a high/low that
    has not finished forming, and the three can legitimately disagree. Those rows
    are excluded here and reported separately rather than counted as corruption.

    **Futures settle outside the traded range.** For `GC=F` and `CL=F`, `close` is
    the exchange settlement price, not the last trade, so it sits below the low or
    above the high fairly often — 2001 through 2020 in this table. That is a
    property of the instrument, not bad data, so `commodity` is held to its own
    tolerance instead of to the equity rule.

    Everything else is held to zero: for a stock or an index, a bar that contradicts
    itself is news.
    """
    latest = one(f"""
        SELECT max(date) AS hi FROM {CATALOG}.bronze.ohlcv_daily
        WHERE source = '{SOURCE}'
    """)["hi"]

    partial = one(f"""
        SELECT count(*) AS n FROM {CATALOG}.bronze.ohlcv_daily
        WHERE source = '{SOURCE}' AND date = '{latest}' AND {BAD_BAR}
    """)["n"]
    R["metrics"]["partial_bar_violations"] = {"date": str(latest), "rows": int(partial)}

    rows = spark.sql(f"""
        SELECT asset_class, count(*) AS total,
               sum(CASE WHEN {BAD_BAR} THEN 1 ELSE 0 END) AS bad
        FROM {CATALOG}.bronze.ohlcv_daily
        WHERE source = '{SOURCE}' AND date < '{latest}'
        GROUP BY asset_class ORDER BY asset_class
    """).collect()

    breakdown, over = {}, []
    for r in rows:
        rate = round(100.0 * (r["bad"] or 0) / r["total"], 4) if r["total"] else 0.0
        limit = (COMMODITY_MAX_VIOLATION_RATE_PCT if r["asset_class"] == "commodity"
                 else MAX_VIOLATION_RATE_PCT)
        breakdown[r["asset_class"]] = {"bad": int(r["bad"] or 0), "of": int(r["total"]),
                                       "rate_pct": rate, "limit_pct": limit}
        if rate > limit:
            over.append(f"{r['asset_class']} {rate}% > {limit}%")
    R["metrics"]["price_violations_by_class"] = breakdown

    if over:
        # A count alone is not actionable — sample the rows so the report says which
        # ticker and which decade, which is usually enough to tell a corrupt bar from
        # a whole-source problem.
        sample = spark.sql(f"""
            SELECT ticker, date, open, high, low, close, asset_class
            FROM {CATALOG}.bronze.ohlcv_daily
            WHERE source = '{SOURCE}' AND date < '{latest}' AND {BAD_BAR}
            ORDER BY date DESC LIMIT 10
        """).collect()
        R["metrics"]["price_violation_sample"] = [r.asDict() for r in sample]
        return failed("ohlcv_price_sanity", "; ".join(over))

    known = breakdown.get("commodity", {}).get("bad", 0)
    return (f"ok (equities and indexes internally consistent; {known} known futures "
            f"settlement bars within tolerance; {partial} partial bars on {latest} "
            f"excluded)")

check("ohlcv_price_sanity", ohlcv_price_sanity)

# COMMAND ----------

# ------------------------------------------------------------------ null rates
def ohlcv_null_rates():
    row = one(f"""
        SELECT
          100.0 * sum(CASE WHEN close  IS NULL THEN 1 ELSE 0 END) / count(*) AS close_pct,
          100.0 * sum(CASE WHEN volume IS NULL THEN 1 ELSE 0 END) / count(*) AS volume_pct
        FROM {CATALOG}.bronze.ohlcv_daily WHERE source = '{SOURCE}'
    """)
    rates = {k: round(float(v), 4) for k, v in row.items()}
    R["metrics"]["null_rate_pct"] = rates
    over = {k: v for k, v in rates.items() if v > MAX_NULL_RATE_PCT}
    if over:
        return failed("ohlcv_null_rates",
                      f"null rate above {MAX_NULL_RATE_PCT}%: {over}")
    return f"ok (close {rates['close_pct']}%, volume {rates['volume_pct']}%)"

check("ohlcv_null_rates", ohlcv_null_rates)

# COMMAND ----------

# --------------------------------------------------------------- universe drift
def universe_drift():
    """Both directions, because they mean different things.

    A ticker in ohlcv_daily but not in bronze.tickers is a real fault — the
    dimension is incomplete and joins will drop rows. A ticker in bronze.tickers
    with no bars is expected for exactly three symbols Yahoo 404s, so it is asserted
    against that list rather than merely reported: if the set changes, either a
    ticker came back or a new one broke.
    """
    orphans = [r["ticker"] for r in spark.sql(f"""
        SELECT DISTINCT o.ticker FROM {CATALOG}.bronze.ohlcv_daily o
        LEFT ANTI JOIN {CATALOG}.bronze.tickers t ON o.ticker = t.ticker
        ORDER BY o.ticker
    """).collect()]
    no_data = sorted(r["ticker"] for r in spark.sql(f"""
        SELECT t.ticker FROM {CATALOG}.bronze.tickers t
        LEFT ANTI JOIN (SELECT DISTINCT ticker FROM {CATALOG}.bronze.ohlcv_daily) o
          ON t.ticker = o.ticker
    """).collect())
    R["metrics"]["tickers_without_ohlcv"] = no_data
    R["metrics"]["ohlcv_tickers_not_in_dimension"] = orphans

    problems = []
    if orphans:
        problems.append(f"in ohlcv_daily but not bronze.tickers: {orphans}")
    if no_data != EXPECT_NO_DATA_TICKERS:
        gained = sorted(set(EXPECT_NO_DATA_TICKERS) - set(no_data))
        lost = sorted(set(no_data) - set(EXPECT_NO_DATA_TICKERS))
        problems.append(
            f"tickers with no bars changed: {no_data} != {EXPECT_NO_DATA_TICKERS}"
            + (f"; now loading: {gained}" if gained else "")
            + (f"; newly missing: {lost}" if lost else ""))
    if problems:
        return failed("universe_drift", "; ".join(problems))
    return (f"ok (no orphans; the {len(no_data)} tickers without bars are the "
            f"known Yahoo 404s {no_data})")

check("universe_drift", universe_drift)

# COMMAND ----------

# ------------------------------------------------------------------ macro side
def macro_quality():
    """FRED series lag by different amounts, so freshness is judged on the fastest.

    DGS10 and VIXCLS are daily; CPILFESL is monthly and GDPPOT quarterly. A single
    threshold across all seventeen would either be uselessly loose or permanently
    red, so this asserts that the *most recent* series is current — which is what
    proves the macro pull ran — and reports every series' lag for inspection.
    """
    row = one(f"""
        SELECT count(*) AS rows, count(DISTINCT series_id) AS series, max(date) AS hi
        FROM {CATALOG}.bronze.macro_series WHERE source = '{MACRO_SOURCE}'
    """)
    dupes = one(f"""
        SELECT count(*) AS n FROM (
            SELECT series_id, date FROM {CATALOG}.bronze.macro_series
            WHERE source = '{MACRO_SOURCE}' GROUP BY series_id, date HAVING count(*) > 1)
    """)["n"]
    per_series = spark.sql(f"""
        SELECT series_id, count(*) AS rows, max(date) AS hi
        FROM {CATALOG}.bronze.macro_series WHERE source = '{MACRO_SOURCE}'
        GROUP BY series_id ORDER BY series_id
    """).collect()

    R["metrics"]["macro_rows"] = row["rows"]
    R["metrics"]["macro_series"] = row["series"]
    R["metrics"]["macro_latest_by_series"] = {r["series_id"]: str(r["hi"]) for r in per_series}
    R["metrics"]["macro_duplicate_keys"] = dupes

    problems = []
    if dupes:
        problems.append(f"{dupes} duplicate (series_id, date) keys")
    if row["series"] != EXPECT_MACRO_SERIES:
        problems.append(f"{row['series']} series, expected {EXPECT_MACRO_SERIES}")
    if row["hi"] is not None:
        lag = int(np.busday_count(row["hi"], dt.date.today()))
        R["metrics"]["macro_staleness_business_days"] = lag
        if lag > MACRO_MAX_STALENESS_DAYS:
            problems.append(f"freshest series is {lag} business days old "
                            f"(limit {MACRO_MAX_STALENESS_DAYS})")

    if problems:
        return failed("macro_quality", "; ".join(problems))
    return f"ok ({row['rows']:,} rows, {row['series']} series, freshest {row['hi']})"

check("macro_quality", macro_quality)

# COMMAND ----------

R["ok"] = not R["failures"]
print(json.dumps(R, indent=2, default=str))
dbutils.notebook.exit(json.dumps(R, default=str))
