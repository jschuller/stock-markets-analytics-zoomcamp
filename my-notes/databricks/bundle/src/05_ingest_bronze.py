# Databricks notebook source
# MAGIC %md
# MAGIC # 05 — Ingest Module 1 data into `bronze`
# MAGIC
# MAGIC Fills the three fixed-schema bronze tables that `03_create_layout.py` creates:
# MAGIC
# MAGIC | Table | Source | Shape |
# MAGIC |---|---|---|
# MAGIC | `bronze.ohlcv_daily` | yfinance | one row per (ticker, date) per source |
# MAGIC | `bronze.macro_series` | FRED via `pandas_datareader` | long: series_id, date, value |
# MAGIC | `bronze.tickers` | the universe below + `global_stocks.csv` | one row per ticker |
# MAGIC
# MAGIC ### Re-run semantics — read this before changing `mode`
# MAGIC
# MAGIC Bronze is append-only **across sources**: the same `(ticker, date)` arriving from
# MAGIC yfinance and from Alpha Vantage is expected and correct, and `silver` decides which
# MAGIC one wins. That is *not* a licence to append the same source twice — doing so
# MAGIC produces genuine duplicates that no dedupe rule can distinguish.
# MAGIC
# MAGIC So the default `mode=replace_source` deletes this source's rows before writing:
# MAGIC re-running is idempotent, and a partially-completed run self-heals on the next
# MAGIC run rather than leaving half a load behind. Use `mode=append` only when adding a
# MAGIC genuinely different `source` value.
# MAGIC
# MAGIC `bronze.tickers` is a dimension, so it is always fully overwritten.
# MAGIC
# MAGIC ### Why `yf.download` and not `Ticker.history()`
# MAGIC
# MAGIC The lecture uses `.history()` because it returns `Dividends` and `Stock Splits`.
# MAGIC Bronze has no column for either, and `.history()` is one HTTP round trip per
# MAGIC symbol — 200+ serial requests. `yf.download` batches and threads, which is the
# MAGIC difference between minutes and a timeout. `auto_adjust=False` is what keeps both
# MAGIC `Close` and `Adj Close`, which the schema wants as `close` and `adj_close`.
# MAGIC
# MAGIC Returns its report through `dbutils.notebook.exit` — `print()` does not come back
# MAGIC through the Jobs API.

# COMMAND ----------

# Parameters come from the bundle (resources/jobs.yml base_parameters); the defaults
# are the interactive fallback when this is run by hand outside a job.
dbutils.widgets.text("catalog", "stock_analytics")
dbutils.widgets.text("start_date", "1950-01-01")
dbutils.widgets.text("mode", "replace_source")
dbutils.widgets.text("groups", "all")

CATALOG = dbutils.widgets.get("catalog")
START = dbutils.widgets.get("start_date")
MODE = dbutils.widgets.get("mode")
GROUPS = [g.strip() for g in dbutils.widgets.get("groups").split(",") if g.strip()]

SOURCE = "yfinance"
MACRO_SOURCE = "fred"
CHUNK = 50

if MODE not in ("replace_source", "append"):
    raise ValueError(f"mode must be replace_source|append, got {MODE!r}")

# --------------------------------------------------------------------- universe
# The 190 US large caps are copied from
# 05-deployment-and-automation/scripts/data_repo.py, with one correction: upstream
# lists SNYS, which Yahoo 404s. The intended symbol is SNPS (Synopsys). The
# substitution is reported in the exit JSON rather than silently applied.
US_STOCKS = [
    "AAPL", "MSFT", "NVDA", "GOOG", "AMZN", "META", "BRK-B", "LLY", "AVGO",
    "TSLA", "JPM", "WMT", "UNH", "V", "XOM", "MA", "PG", "JNJ", "COST",
    "ORCL", "HD", "ABBV", "BAC", "KO", "MRK", "NFLX", "CVX", "ADBE", "PEP",
    "CRM", "TMUS", "TMO", "AMD", "MCD", "CSCO", "WFC", "ABT", "PM", "DHR",
    "IBM", "TXN", "QCOM", "AXP", "VZ", "GE", "AMGN", "INTU", "NOW", "ISRG",
    "NEE", "CAT", "DIS", "RTX", "MS", "PFE", "SPGI", "UNP", "GS", "CMCSA",
    "AMAT", "UBER", "PGR", "T", "LOW", "SYK", "LMT", "HON", "TJX", "BLK",
    "ELV", "REGN", "BKNG", "COP", "VRTX", "NKE", "BSX", "PLD", "SCHW", "C",
    "PANW", "MMC", "ADP", "KKR", "UPS", "ADI", "AMT", "SBUX", "DE", "ANET",
    "BMY", "HCA", "CI", "KLAC", "FI", "LRCX", "BX", "GILD", "MU", "BA",
    "SO", "MDLZ", "ICE", "MO", "SHW", "DUK", "MCO", "CL", "INTC", "WM",
    "ZTS", "GD", "CTAS", "EQIX", "DELL", "NOC", "CME", "SCCO", "TDG",
    "SNPS", "APH", "WELL", "MCK", "PH", "PYPL", "ITW", "MSI", "PNC", "ABNB",
    "CMG", "USB", "CVS", "MMM", "FDX", "EOG", "ECL", "BDX", "CDNS", "TGT",
    "WDAY", "PLTR", "CSX", "ORLY", "CRWD", "MAR", "RSG", "AJG", "APO",
    "CARR", "EPD", "SPG", "APD", "AFL", "MRVL", "PSA", "DHI", "NEM", "FCX",
    "ROP", "SLB", "TFC", "FTNT", "EMR", "MPC", "NSC", "CEG", "PSX", "ADSK",
    "COF", "WMB", "ET", "IBKR", "GM", "MET", "O", "AEP", "OKE", "AZO",
    "HLT", "GEV", "SRE", "PCG", "DASH", "TRV", "CPRT", "OXY", "ROST", "KDP",
    "ALL", "BK", "DLR",
]
TICKER_FIXES = {"SNYS": "SNPS"}

# ^GSPC and ^SPX are both the S&P 500 — Yahoo carries them as separate quotes
# (real-time vs 15-min delayed) and the 2026 lecture uses both, so both are kept.
# The nine world indexes after ^VIX are the set 2025's homework Q2 asked about;
# holding them in bronze makes that shape answerable from the warehouse.
INDEXES = [
    "^GSPC", "^SPX", "^DJI", "^GDAXI", "^VIX",
    "^HSI", "^N225", "^FTSE", "^AXJO", "^NSEI", "^GSPTSE", "^MXX", "^BVSP",
    "000001.SS",
]
ETFS = ["VOO", "EPI"]
COMMODITIES = ["GC=F", "CL=F", "BZ=F"]
CRYPTO = ["BTC-USD"]

UNIVERSE = {
    "stock": US_STOCKS,
    "index": INDEXES,
    "etf": ETFS,
    "commodity": COMMODITIES,
    "crypto": CRYPTO,
}

# FRED. The first six are what data_repo.py pulls; the next four are what the 2026
# Module 1 notebook actually uses; the rest round out the yield curve and credit
# spreads the lecture points at but never fetches. Long format means adding a
# series costs nothing but a line here.
FRED_SERIES = [
    "GDPPOT", "CPILFESL", "FEDFUNDS", "DGS1", "DGS5", "DGS10",
    "TRESEGCNM052N", "GVZCLS", "DCOILWTICO", "DCOILBRENTEU",
    "DGS2", "DGS3", "DGS30", "T10YIE", "AAA", "BAA", "VIXCLS",
]

GLOBAL_STOCKS_CSV = f"/Volumes/{CATALOG}/bronze/files/global_stocks.csv"

# COMMAND ----------

import json
import time
import datetime as _dt

import pandas as pd
import yfinance as yf
import pandas_datareader as pdr

from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, DateType, DoubleType, TimestampType,
)

log = {
    "catalog": CATALOG,
    "start_date": START,
    "mode": MODE,
    "groups": GROUPS,
    "ticker_fixes": TICKER_FIXES,
    "counts": {},
    "failed_tickers": [],
    "errors": [],
}

# Same error-collecting shape as 03_create_layout.py: one failing step is recorded
# and the run continues, so a single dead ticker cannot cost the whole load.
def step(name, fn):
    try:
        log["counts"][name] = fn()
    except Exception as e:
        log["counts"][name] = f"{type(e).__name__}: {str(e)[:200]}"
        log["errors"].append(name)

def wanted(group):
    return "all" in GROUPS or group in GROUPS

INGESTED_AT = _dt.datetime.now(_dt.timezone.utc).replace(tzinfo=None)

# volume is DoubleType here and cast to bigint on write: yfinance returns NaN for
# gaps, and NaN cannot travel through a LongType field.
OHLCV_SCHEMA = StructType([
    StructField("ticker", StringType(), False),
    StructField("date", DateType(), False),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("adj_close", DoubleType(), True),
    StructField("volume", DoubleType(), True),
    StructField("source", StringType(), False),
    StructField("asset_class", StringType(), True),
    StructField("ingested_at", TimestampType(), False),
])

MACRO_SCHEMA = StructType([
    StructField("series_id", StringType(), False),
    StructField("date", DateType(), False),
    StructField("value", DoubleType(), True),
    StructField("source", StringType(), False),
    StructField("ingested_at", TimestampType(), False),
])

def _flatten(raw, tickers):
    """yfinance -> long OHLCV frame. Column shape differs for one vs many tickers."""
    frames = []
    for t in tickers:
        if isinstance(raw.columns, pd.MultiIndex):
            if t not in raw.columns.get_level_values(0):
                continue
            df = raw[t].copy()
        else:
            df = raw.copy()
        if df.empty:
            continue
        df = df.rename(columns={
            "Open": "open", "High": "high", "Low": "low",
            "Close": "close", "Adj Close": "adj_close", "Volume": "volume",
        })
        for col in ("open", "high", "low", "close", "adj_close", "volume"):
            if col not in df.columns:
                df[col] = float("nan")
        # A row with no close at all is a calendar artifact, not a trading day.
        df = df.dropna(subset=["close"])
        if df.empty:
            continue
        idx = df.index
        if getattr(idx, "tz", None) is not None:
            idx = idx.tz_localize(None)
        df = df.reset_index(drop=True)
        df["date"] = pd.to_datetime(idx).date
        df["ticker"] = t
        frames.append(df[["ticker", "date", "open", "high", "low", "close",
                          "adj_close", "volume"]])
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def _write_ohlcv(pdf, asset_class):
    pdf = pdf.copy()
    pdf["source"] = SOURCE
    pdf["asset_class"] = asset_class
    pdf["ingested_at"] = INGESTED_AT
    for col in ("open", "high", "low", "close", "adj_close", "volume"):
        pdf[col] = pd.to_numeric(pdf[col], errors="coerce").astype(float)
    sdf = spark.createDataFrame(pdf[[f.name for f in OHLCV_SCHEMA.fields]], OHLCV_SCHEMA)
    (sdf.withColumn("volume", F.col("volume").cast("bigint"))
        .write.mode("append").saveAsTable(f"{CATALOG}.bronze.ohlcv_daily"))
    return len(pdf)

def fetch_group(asset_class, tickers):
    """Chunked batch download, falling back to per-ticker only for a failed chunk."""
    written = 0
    for i in range(0, len(tickers), CHUNK):
        chunk = tickers[i:i + CHUNK]
        pdf = pd.DataFrame()
        try:
            raw = yf.download(chunk, start=START, auto_adjust=False, actions=False,
                              group_by="ticker", threads=True, progress=False)
            pdf = _flatten(raw, chunk)
        except Exception as e:
            log["errors"].append(f"chunk {asset_class}[{i}]: {type(e).__name__}")

        got = set(pdf["ticker"].unique()) if not pdf.empty else set()
        missing = [t for t in chunk if t not in got]
        # Retry the stragglers individually so one bad symbol cannot lose 49 good ones.
        for t in missing:
            try:
                one = yf.download(t, start=START, auto_adjust=False, actions=False,
                                  progress=False)
                got_one = _flatten(one, [t])
                if got_one.empty:
                    log["failed_tickers"].append(t)
                else:
                    pdf = pd.concat([pdf, got_one], ignore_index=True)
            except Exception:
                log["failed_tickers"].append(t)

        if not pdf.empty:
            written += _write_ohlcv(pdf, asset_class)
        time.sleep(1)
    return written

def fetch_macro():
    frames = []
    for sid in FRED_SERIES:
        try:
            df = pdr.DataReader(sid, "fred", start=START)
            if df.empty:
                log["failed_tickers"].append(f"fred:{sid}")
                continue
            out = pd.DataFrame({
                "series_id": sid,
                "date": pd.to_datetime(df.index).date,
                "value": pd.to_numeric(df.iloc[:, 0], errors="coerce").astype(float),
            })
            frames.append(out.dropna(subset=["value"]))
        except Exception as e:
            log["failed_tickers"].append(f"fred:{sid} ({type(e).__name__})")
        time.sleep(1)  # data_repo.py does the same — do not hammer FRED
    if not frames:
        return 0
    pdf = pd.concat(frames, ignore_index=True)
    pdf["source"] = MACRO_SOURCE
    pdf["ingested_at"] = INGESTED_AT
    sdf = spark.createDataFrame(pdf[[f.name for f in MACRO_SCHEMA.fields]], MACRO_SCHEMA)
    sdf.write.mode("append").saveAsTable(f"{CATALOG}.bronze.macro_series")
    return len(pdf)

def build_tickers():
    """The universe is the source of truth; global_stocks.csv is enrichment only."""
    rows = [{"ticker": t, "asset_class": ac}
            for ac, lst in UNIVERSE.items() for t in lst]
    pdf = pd.DataFrame(rows)

    enrich = None
    try:
        caps = pd.read_csv(GLOBAL_STOCKS_CSV)
        caps = caps.rename(columns={"Symbol": "ticker", "Name": "name",
                                    "marketcap": "market_cap"})
        caps = caps[["ticker", "name", "market_cap", "country"]].drop_duplicates("ticker")
        enrich = caps
        log["counts"]["global_stocks_csv_rows"] = len(caps)
    except Exception as e:
        log["counts"]["global_stocks_csv_rows"] = f"unavailable: {type(e).__name__}"

    if enrich is not None:
        pdf = pdf.merge(enrich, on="ticker", how="left")
    else:
        pdf["name"] = None
        pdf["market_cap"] = float("nan")
        pdf["country"] = None

    pdf["exchange"] = None
    pdf["sector"] = None
    pdf["is_active"] = True
    pdf["added_at"] = INGESTED_AT
    pdf["market_cap"] = pd.to_numeric(pdf["market_cap"], errors="coerce").astype(float)
    for col in ("name", "country", "exchange", "sector"):
        pdf[col] = pdf[col].astype(object).where(pdf[col].notna(), None)

    cols = ["ticker", "name", "asset_class", "exchange", "country", "sector",
            "market_cap", "is_active", "added_at"]
    sdf = spark.createDataFrame(pdf[cols])
    # A dimension, not an event stream: always replaced whole.
    sdf.write.mode("overwrite").option("overwriteSchema", "false") \
       .saveAsTable(f"{CATALOG}.bronze.tickers")
    return len(pdf)

# COMMAND ----------

def _count(table):
    return spark.sql(f"SELECT count(*) c FROM {CATALOG}.bronze.{table}").collect()[0]["c"]

log["rows_before"] = {t: _count(t) for t in ("ohlcv_daily", "macro_series", "tickers")}

if MODE == "replace_source":
    if any(wanted(g) for g in UNIVERSE):
        spark.sql(f"DELETE FROM {CATALOG}.bronze.ohlcv_daily WHERE source = '{SOURCE}'")
    if wanted("macro"):
        spark.sql(
            f"DELETE FROM {CATALOG}.bronze.macro_series WHERE source = '{MACRO_SOURCE}'")

for asset_class, tickers in UNIVERSE.items():
    if wanted(asset_class):
        step(asset_class, lambda ac=asset_class, ts=tickers: fetch_group(ac, ts))

if wanted("macro"):
    step("macro", fetch_macro)

if wanted("tickers"):
    step("tickers", build_tickers)

log["rows_after"] = {t: _count(t) for t in ("ohlcv_daily", "macro_series", "tickers")}

try:
    span = spark.sql(f"""
        SELECT min(date) lo, max(date) hi, count(DISTINCT ticker) n
        FROM {CATALOG}.bronze.ohlcv_daily WHERE source = '{SOURCE}'
    """).collect()[0]
    log["ohlcv_span"] = {"min_date": str(span["lo"]), "max_date": str(span["hi"]),
                         "tickers": span["n"]}
    dupes = spark.sql(f"""
        SELECT count(*) c FROM (
          SELECT ticker, date FROM {CATALOG}.bronze.ohlcv_daily
          WHERE source = '{SOURCE}' GROUP BY ticker, date HAVING count(*) > 1)
    """).collect()[0]["c"]
    log["within_source_duplicates"] = dupes
    if dupes:
        log["errors"].append("within_source_duplicates")
except Exception as e:
    log["errors"].append(f"summary: {type(e).__name__}: {str(e)[:150]}")

log["ok"] = not log["errors"]
print(json.dumps(log, indent=2, default=str))
dbutils.notebook.exit(json.dumps(log, default=str))
