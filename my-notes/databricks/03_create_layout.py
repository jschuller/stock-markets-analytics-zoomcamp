# Databricks notebook source
# MAGIC %md
# MAGIC # 03 — Create the `stock_analytics` layout
# MAGIC
# MAGIC Idempotent. Creates six schemas, three volumes, and the tables whose columns
# MAGIC are knowable up front. Re-running is safe.
# MAGIC
# MAGIC **Prerequisite:** the catalog must already exist and be owned by this service
# MAGIC principal — Free Edition blocks `CREATE CATALOG` on the metastore, so it has to
# MAGIC be made in the UI (Catalog → Create catalog → Default Storage).
# MAGIC
# MAGIC `gold.features` is deliberately **not** predefined: it is the course's
# MAGIC `transformed_df`, which carries 200+ TA-Lib indicator columns. Hand-writing that
# MAGIC DDL would be wrong and would drift. It gets created schema-on-write by the
# MAGIC pipeline instead.

# COMMAND ----------

CATALOG = "stock_analytics"

import json
log = {"schemas": {}, "volumes": {}, "tables": {}, "errors": []}

def run(kind, name, sql):
    try:
        spark.sql(sql)
        log[kind][name] = "ok"
    except Exception as e:
        log[kind][name] = f"{type(e).__name__}: {str(e)[:160]}"
        log["errors"].append(name)

# ------------------------------------------------------------------ schemas
SCHEMAS = {
    "bronze":  "M1 — raw source-shaped pulls, append-only. Never edited in place.",
    "silver":  "M2 — cleaned and deduped across sources. One row per (ticker, date).",
    "gold":    "M2/M3 — model-ready features and targets. The course's transformed_df.",
    "ml":      "M3 — predictions, run metrics, serialized model artifacts.",
    "sim":     "M4 — trading simulation output: trades and equity curves.",
    "project": "Capstone workspace, kept separate from coursework.",
}
for s, comment in SCHEMAS.items():
    run("schemas", s, f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{s} COMMENT '{comment}'")

# ------------------------------------------------------------------ volumes
# bronze.files is the drop-in target for Module 5's pd.read_parquet(data_dir):
#   data_dir = "/Volumes/stock_analytics/bronze/files/"
VOLUMES = {
    "bronze.files":    "Raw files: tickers_df/indexes_df/macro_df parquet, gdown downloads, scraped CSVs.",
    "ml.models":       "Serialized sklearn artifacts written by TrainModel.persist().",
    "project.exports": "Capstone deliverables: submission CSVs, plots, report assets.",
}
for v, comment in VOLUMES.items():
    run("volumes", v, f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{v} COMMENT '{comment}'")

# ------------------------------------------------------------------- tables
# Liquid clustering rather than partitioning: ~190 tickers x 25y is only a few
# million rows, and date-partitioning that would produce thousands of tiny files.

run("tables", "bronze.ohlcv_daily", f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.bronze.ohlcv_daily (
  ticker      STRING    NOT NULL,
  date        DATE      NOT NULL,
  open        DOUBLE,
  high        DOUBLE,
  low         DOUBLE,
  close       DOUBLE,
  adj_close   DOUBLE,
  volume      BIGINT,
  source      STRING    NOT NULL  COMMENT 'yfinance | alphavantage | stooq',
  asset_class STRING              COMMENT 'stock | index | etf',
  ingested_at TIMESTAMP NOT NULL
)
CLUSTER BY (ticker, date)
COMMENT 'Raw daily bars as fetched. Append-only; the same (ticker,date) may appear
         more than once from different sources. Deduping happens in silver.'
""")

run("tables", "bronze.macro_series", f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.bronze.macro_series (
  series_id   STRING    NOT NULL  COMMENT 'GDPPOT, CPILFESL, FEDFUNDS, DGS1/5/10, ...',
  date        DATE      NOT NULL,
  value       DOUBLE,
  source      STRING    NOT NULL  COMMENT 'fred | alphavantage',
  ingested_at TIMESTAMP NOT NULL
)
CLUSTER BY (series_id, date)
COMMENT 'Long format on purpose: FRED series have different frequencies (daily,
         monthly, quarterly). A wide table would be mostly nulls.'
""")

run("tables", "bronze.tickers", f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.bronze.tickers (
  ticker      STRING NOT NULL,
  name        STRING,
  asset_class STRING,
  exchange    STRING,
  country     STRING,
  sector      STRING,
  market_cap  DOUBLE,
  is_active   BOOLEAN,
  added_at    TIMESTAMP
)
COMMENT 'The universe under study, plus the scraped market-cap data from
         companiesmarketcap.com (global_stocks.csv).'
""")

run("tables", "silver.prices_daily", f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.silver.prices_daily (
  ticker      STRING    NOT NULL,
  date        DATE      NOT NULL,
  open        DOUBLE,
  high        DOUBLE,
  low         DOUBLE,
  close       DOUBLE,
  adj_close   DOUBLE,
  volume      BIGINT,
  source      STRING              COMMENT 'which source won the dedupe',
  asset_class STRING,
  updated_at  TIMESTAMP
)
CLUSTER BY (ticker, date)
COMMENT 'Exactly one row per (ticker, date). This is where the yfinance ->
         alphavantage fallback is resolved, by source preference. Stooq is
         excluded: it is dead on every network tested (2026-08).'
""")

run("tables", "ml.model_runs", f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.ml.model_runs (
  run_id      STRING NOT NULL,
  model_name  STRING,
  params      STRING  COMMENT 'JSON blob of hyperparameters',
  trained_at  TIMESTAMP,
  train_start DATE, train_end DATE,
  val_start   DATE, val_end   DATE,
  test_start  DATE, test_end  DATE,
  precision   DOUBLE, recall  DOUBLE, f1 DOUBLE, roc_auc DOUBLE,
  notes       STRING
)
COMMENT 'One row per training run. Temporal splits are recorded explicitly because
         lookahead bias is the easiest mistake to make in this course.'
""")

run("tables", "ml.predictions", f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.ml.predictions (
  run_id     STRING NOT NULL,
  model_name STRING,
  ticker     STRING NOT NULL,
  date       DATE   NOT NULL,
  pred_proba DOUBLE,
  pred_class INT,
  actual     INT,
  created_at TIMESTAMP
)
CLUSTER BY (run_id, ticker, date)
COMMENT 'Predictions keyed by run_id so competing models stay comparable.'
""")

run("tables", "sim.trades", f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.sim.trades (
  sim_id      STRING NOT NULL,
  strategy    STRING,
  ticker      STRING,
  entry_date  DATE, exit_date DATE,
  direction   STRING  COMMENT 'long | short',
  entry_price DOUBLE, exit_price DOUBLE,
  size        DOUBLE,
  gross_pnl   DOUBLE,
  fees        DOUBLE  COMMENT 'Ivan: fees dominate at high frequency. Never leave null.',
  net_pnl     DOUBLE,
  created_at  TIMESTAMP
)
CLUSTER BY (sim_id, ticker)
COMMENT 'One row per simulated trade.'
""")

run("tables", "sim.equity_curve", f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.sim.equity_curve (
  sim_id          STRING NOT NULL,
  strategy        STRING,
  date            DATE   NOT NULL,
  cash            DOUBLE,
  positions_value DOUBLE,
  equity          DOUBLE,
  drawdown        DOUBLE
)
CLUSTER BY (sim_id, date)
COMMENT 'Daily portfolio state per simulation, for drawdown and Sharpe.'
""")

# ------------------------------------------------------------------- verify
try:
    log["final_schemas"] = [r[0] for r in spark.sql(f"SHOW SCHEMAS IN {CATALOG}").collect()]
    log["final_tables"] = [f"{s}.{r[1]}"
                           for s in ("bronze", "silver", "gold", "ml", "sim", "project")
                           for r in spark.sql(f"SHOW TABLES IN {CATALOG}.{s}").collect()]
    log["final_volumes"] = [f"{s}.{r[2]}"
                            for s in ("bronze", "ml", "project")
                            for r in spark.sql(f"SHOW VOLUMES IN {CATALOG}.{s}").collect()]
except Exception as e:
    log["verify_error"] = str(e)[:200]

log["ok"] = not log["errors"]
dbutils.notebook.exit(json.dumps(log))
