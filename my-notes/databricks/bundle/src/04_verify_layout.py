# Databricks notebook source
# MAGIC %md
# MAGIC # 04 — Verify the layout
# MAGIC
# MAGIC Assertion-based. Returns JSON with `"ok"` so it works both interactively and as
# MAGIC a CI gate. Checks more than existence: **column names and types** are compared
# MAGIC against spec, because the bootstrap job is idempotent and therefore blind to
# MAGIC drift — a table that already exists with the wrong shape is silently accepted
# MAGIC by `CREATE TABLE IF NOT EXISTS`.

# COMMAND ----------

import json

dbutils.widgets.text("catalog", "stock_analytics")
CATALOG = dbutils.widgets.get("catalog")

R = {"catalog": CATALOG, "schemas": {}, "volumes": {}, "tables": {},
     "columns": {}, "write_access": {}, "failures": []}

def fail(msg):
    R["failures"].append(msg)

# ------------------------------------------------------------------ 1. schemas
EXPECTED_SCHEMAS = ["bronze", "silver", "gold", "ml", "sim", "project"]
try:
    found = {r[0] for r in spark.sql(f"SHOW SCHEMAS IN {CATALOG}").collect()}
except Exception as e:
    found = set()
    fail(f"cannot list schemas: {type(e).__name__}: {str(e)[:120]}")

for s in EXPECTED_SCHEMAS:
    ok = s in found
    R["schemas"][s] = "ok" if ok else "MISSING"
    if not ok:
        fail(f"schema missing: {s}")

# ------------------------------------------------------------------ 2. volumes
EXPECTED_VOLUMES = [("bronze", "files"), ("ml", "models"), ("project", "exports")]
for schema, vol in EXPECTED_VOLUMES:
    key = f"{schema}.{vol}"
    path = f"/Volumes/{CATALOG}/{schema}/{vol}/_verify_probe.txt"
    try:
        with open(path, "w") as f:
            f.write("probe")
        with open(path) as f:
            assert f.read() == "probe"
        dbutils.fs.rm(f"dbfs:{path}".replace("dbfs:/Volumes", "/Volumes"), False)
        R["volumes"][key] = "ok (writable)"
    except Exception as e:
        # Existence without writability still tells us something useful.
        try:
            spark.sql(f"DESCRIBE VOLUME {CATALOG}.{schema}.{vol}")
            R["volumes"][key] = f"EXISTS BUT NOT WRITABLE: {type(e).__name__}"
        except Exception:
            R["volumes"][key] = f"MISSING ({type(e).__name__})"
        fail(f"volume not writable: {key}")

# ------------------------------------------------------- 3. tables and columns
# name -> {column: type}. Types as Spark reports them in DESCRIBE.
EXPECTED = {
    "bronze.ohlcv_daily": {
        "ticker": "string", "date": "date", "open": "double", "high": "double",
        "low": "double", "close": "double", "adj_close": "double",
        "volume": "bigint", "source": "string", "asset_class": "string",
        "ingested_at": "timestamp",
    },
    "bronze.macro_series": {
        "series_id": "string", "date": "date", "value": "double",
        "source": "string", "ingested_at": "timestamp",
    },
    "bronze.tickers": {
        "ticker": "string", "name": "string", "asset_class": "string",
        "exchange": "string", "country": "string", "sector": "string",
        "market_cap": "double", "is_active": "boolean", "added_at": "timestamp",
    },
    "silver.prices_daily": {
        "ticker": "string", "date": "date", "open": "double", "high": "double",
        "low": "double", "close": "double", "adj_close": "double",
        "volume": "bigint", "source": "string", "asset_class": "string",
        "updated_at": "timestamp",
    },
    "ml.model_runs": {
        "run_id": "string", "model_name": "string", "params": "string",
        "trained_at": "timestamp", "train_start": "date", "train_end": "date",
        "val_start": "date", "val_end": "date", "test_start": "date",
        "test_end": "date", "precision": "double", "recall": "double",
        "f1": "double", "roc_auc": "double", "notes": "string",
    },
    "ml.predictions": {
        "run_id": "string", "model_name": "string", "ticker": "string",
        "date": "date", "pred_proba": "double", "pred_class": "int",
        "actual": "int", "created_at": "timestamp",
    },
    "sim.trades": {
        "sim_id": "string", "strategy": "string", "ticker": "string",
        "entry_date": "date", "exit_date": "date", "direction": "string",
        "entry_price": "double", "exit_price": "double", "size": "double",
        "gross_pnl": "double", "fees": "double", "net_pnl": "double",
        "created_at": "timestamp",
    },
    "sim.equity_curve": {
        "sim_id": "string", "strategy": "string", "date": "date",
        "cash": "double", "positions_value": "double", "equity": "double",
        "drawdown": "double",
    },
}

for fq, expected_cols in EXPECTED.items():
    try:
        rows = spark.sql(f"DESCRIBE TABLE {CATALOG}.{fq}").collect()
    except Exception as e:
        R["tables"][fq] = f"MISSING ({type(e).__name__})"
        fail(f"table missing: {fq}")
        continue
    R["tables"][fq] = "ok"

    actual = {}
    for r in rows:
        col = (r[0] or "").strip()
        if not col or col.startswith("#"):
            break            # partition/detail section starts here
        actual[col] = (r[1] or "").strip().lower()

    missing = [c for c in expected_cols if c not in actual]
    extra = [c for c in actual if c not in expected_cols]
    wrong = {c: f"expected {t}, got {actual[c]}"
             for c, t in expected_cols.items()
             if c in actual and actual[c] != t}

    if missing or extra or wrong:
        R["columns"][fq] = {"missing": missing, "unexpected": extra, "wrong_type": wrong}
        fail(f"column drift in {fq}: "
             f"{len(missing)} missing, {len(extra)} unexpected, {len(wrong)} wrong type")
    else:
        R["columns"][fq] = f"ok ({len(actual)} columns)"

# ------------------------------------------------- 4. write access per schema
for s in EXPECTED_SCHEMAS:
    t = f"{CATALOG}.{s}._verify_probe"
    try:
        spark.sql(f"CREATE TABLE IF NOT EXISTS {t} (x INT)")
        spark.sql(f"DROP TABLE IF EXISTS {t}")
        R["write_access"][s] = "ok"
    except Exception as e:
        R["write_access"][s] = f"DENIED ({type(e).__name__})"
        fail(f"cannot create tables in {s}")

# ------------------------------------ 5. gold is present and correctly empty
try:
    gold = [r[1] for r in spark.sql(f"SHOW TABLES IN {CATALOG}.gold").collect()]
    R["gold_tables"] = gold
    if gold:
        # Not a failure — just worth surfacing, since gold.features is created
        # schema-on-write by the pipeline rather than by the bootstrap job.
        R["gold_note"] = f"{len(gold)} table(s) present (expected after a pipeline run)"
    else:
        R["gold_note"] = "empty, as expected before the first pipeline run"
except Exception as e:
    fail(f"cannot inspect gold: {type(e).__name__}")

R["ok"] = not R["failures"]
print(json.dumps(R, indent=2))
dbutils.notebook.exit(json.dumps(R))
