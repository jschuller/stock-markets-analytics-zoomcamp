# Databricks notebook source
# MAGIC %md
# MAGIC # 03 — Create the `stock_analytics` layout
# MAGIC
# MAGIC Idempotent — creates only the **tables**. Re-running is safe.
# MAGIC
# MAGIC Schemas and volumes are owned by the Asset Bundle
# MAGIC (`resources/schemas.yml`, `resources/volumes.yml`); creating them here too
# MAGIC would be a second source of truth. DAB has no Unity Catalog table resource,
# MAGIC which is the only reason tables are done in a notebook at all.
# MAGIC
# MAGIC **Prerequisite:** the catalog exists and is owned by this service principal —
# MAGIC Free Edition blocks `CREATE CATALOG` on the metastore, so it is made once in
# MAGIC the UI (Catalog → Create catalog → Default Storage).
# MAGIC
# MAGIC `gold.features` is deliberately **not** predefined: it is the course's
# MAGIC `transformed_df`, which carries 200+ TA-Lib indicator columns. Hand-writing that
# MAGIC DDL would be wrong and would drift. It gets created schema-on-write by the
# MAGIC pipeline instead.

# COMMAND ----------

# Catalog comes from the bundle so a second workspace can use a different
# name without editing this notebook. Falls back to the default when run
# interactively outside a job.
dbutils.widgets.text("catalog", "stock_analytics")
CATALOG = dbutils.widgets.get("catalog")
print(f"target catalog: {CATALOG}")

import json
log = {"tables": {}, "errors": []}

def run(kind, name, sql):
    try:
        spark.sql(sql)
        log[kind][name] = "ok"
    except Exception as e:
        log[kind][name] = f"{type(e).__name__}: {str(e)[:160]}"
        log["errors"].append(name)

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
  asset_class STRING              COMMENT 'stock | index | etf | commodity | crypto',
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

run("tables", "ops.job_runs", f"""
CREATE TABLE IF NOT EXISTS {CATALOG}.ops.job_runs (
  run_id       BIGINT    NOT NULL  COMMENT 'the task run id, unique per attempt',
  job_id       BIGINT,
  job_name     STRING,
  task_key     STRING,
  started_at   TIMESTAMP,
  ended_at     TIMESTAMP,
  duration_ms  BIGINT,
  result_state STRING              COMMENT 'SUCCESS | FAILED | TIMEDOUT | CANCELED',
  trigger      STRING              COMMENT 'what started it: schedule, manual, CI',
  ok           BOOLEAN             COMMENT 'the report ok flag, lifted out so it is queryable',
  failures     STRING              COMMENT 'the report problem list as JSON text: its
                                              failures key, or errors where the
                                              notebook uses that name instead',
  report       STRING              COMMENT 'the full notebook exit JSON, verbatim',
  collected_at TIMESTAMP NOT NULL
)
CLUSTER BY (job_name, started_at)
COMMENT 'Harvested notebook exit reports. ok and failures are lifted out of the
         report so trends can be queried without parsing JSON on every read;
         report keeps the original so nothing is lost by that projection.'
""")

# ---------------------------------------------------------------- comments
# CREATE TABLE IF NOT EXISTS does not update a comment on a table that already
# exists, so a column comment changed above would silently drift from the live
# table. This one ALTER keeps code and catalog in step. Idempotent.

run("tables", "ops.job_runs.failures_comment", f"""
ALTER TABLE {CATALOG}.ops.job_runs ALTER COLUMN failures
COMMENT 'the report problem list as JSON text: its failures key, or errors where the
         notebook uses that name instead'
""")

run("tables", "bronze.ohlcv_daily.asset_class_comment", f"""
ALTER TABLE {CATALOG}.bronze.ohlcv_daily ALTER COLUMN asset_class
COMMENT 'stock | index | etf | commodity | crypto'
""")

# ------------------------------------------------------------------- verify
try:
    log["final_tables"] = [
        f"{sch}.{r[1]}"
        for sch in ("bronze", "silver", "gold", "ml", "sim", "ops", "project")
        for r in spark.sql(f"SHOW TABLES IN {CATALOG}.{sch}").collect()
    ]
except Exception as e:
    log["verify_error"] = f"{type(e).__name__}: {str(e)[:150]}"

log["ok"] = not log["errors"]
print(json.dumps(log, indent=2))
dbutils.notebook.exit(json.dumps(log))
