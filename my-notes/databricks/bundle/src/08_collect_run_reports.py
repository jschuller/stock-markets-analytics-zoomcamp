# Databricks notebook source
# MAGIC %md
# MAGIC # 08 — Harvest notebook run reports into `ops.job_runs`
# MAGIC
# MAGIC Every notebook in this bundle already ends with
# MAGIC `dbutils.notebook.exit(json.dumps(...))`, because `print()` does not survive the
# MAGIC Jobs API. That discipline was already there — but the Jobs API keeps run output
# MAGIC for a limited window and then discards it, so every one of those reports was
# MAGIC being thrown away. This turns them into a table.
# MAGIC
# MAGIC ### Why this reads the API instead of having each notebook write
# MAGIC
# MAGIC The obvious design is a shared `record_run()` that every notebook calls before
# MAGIC its exit. That is worse here, for three reasons:
# MAGIC
# MAGIC 1. `dbutils.notebook.exit()` **stops execution**, so the write has to happen
# MAGIC    before it in all five notebooks — five places to get wrong.
# MAGIC 2. Bundle `src/*.py` upload as notebook objects and cannot import a helper, so
# MAGIC    that shared function would be a sixth copy-pasted block to keep in sync.
# MAGIC 3. A notebook that dies before its exit line writes nothing — exactly the run
# MAGIC    you most want recorded.
# MAGIC
# MAGIC Reading `jobs/runs/get-output` instead costs zero changes to the emitters,
# MAGIC captures runs triggered from anywhere (CI, schedule, CLI, the UI), records
# MAGIC **failed** runs too, and picks up history that already happened.
# MAGIC
# MAGIC ### Idempotent
# MAGIC
# MAGIC `MERGE` on `run_id`, so re-running re-reads the same window and updates rather
# MAGIC than duplicating. Safe to schedule as often as you like.

# COMMAND ----------

dbutils.widgets.text("catalog", "stock_analytics")
dbutils.widgets.text("lookback_days", "30")
# Bundle job names all carry this prefix; anything else in the workspace is not ours.
dbutils.widgets.text("job_name_prefix", "[SMA]")

CATALOG = dbutils.widgets.get("catalog")
LOOKBACK_DAYS = int(dbutils.widgets.get("lookback_days"))
JOB_NAME_PREFIX = dbutils.widgets.get("job_name_prefix")

import datetime as dt
import json

from pyspark.sql.types import (BooleanType, LongType, StringType, StructField,
                               StructType, TimestampType)

R = {"catalog": CATALOG, "lookback_days": LOOKBACK_DAYS, "checks": {},
     "metrics": {}, "failures": []}

def check(name, fn):
    try:
        R["checks"][name] = fn()
    except Exception as e:
        R["checks"][name] = f"{type(e).__name__}: {str(e)[:200]}"
        R["failures"].append(name)

def failed(name, msg):
    R["failures"].append(name)
    return f"FAIL: {msg}"

SCHEMA = StructType([
    StructField("run_id", LongType(), False),
    StructField("job_id", LongType(), True),
    StructField("job_name", StringType(), True),
    StructField("task_key", StringType(), True),
    StructField("started_at", TimestampType(), True),
    StructField("ended_at", TimestampType(), True),
    StructField("duration_ms", LongType(), True),
    StructField("result_state", StringType(), True),
    StructField("trigger", StringType(), True),
    StructField("ok", BooleanType(), True),
    StructField("failures", StringType(), True),
    StructField("report", StringType(), True),
    StructField("collected_at", TimestampType(), False),
])

def ms_to_ts(ms):
    """Job timestamps are epoch milliseconds; 0 means "never"."""
    if not ms:
        return None
    return dt.datetime.fromtimestamp(ms / 1000, tz=dt.timezone.utc)

def as_text(v):
    """Enum, dataclass or None -> a stable short string."""
    if v is None:
        return None
    return getattr(v, "value", None) or getattr(v, "name", None) or str(v)

# COMMAND ----------

# ------------------------------------------------------------------ harvest
def collect():
    from databricks.sdk import WorkspaceClient

    w = WorkspaceClient()
    now = dt.datetime.now(tz=dt.timezone.utc)
    since_ms = int((now - dt.timedelta(days=LOOKBACK_DAYS)).timestamp() * 1000)

    jobs = [j for j in w.jobs.list(expand_tasks=False)
            if (j.settings and j.settings.name or "").startswith(JOB_NAME_PREFIX)]
    R["metrics"]["jobs_matched"] = [j.settings.name for j in jobs]
    if not jobs:
        return failed("collect", f"no jobs matching prefix {JOB_NAME_PREFIX!r}")

    rows, skipped = [], {"still_running": 0, "no_output": 0}
    for job in jobs:
        name = job.settings.name
        for run in w.jobs.list_runs(job_id=job.job_id, start_time_from=since_ms,
                                    expand_tasks=True):
            state = as_text(run.state.result_state if run.state else None)
            if state is None:
                skipped["still_running"] += 1      # in flight; catch it next time
                continue

            for task in (run.tasks or []):
                report_text, ok, failures = None, None, None
                try:
                    out = w.jobs.get_run_output(run_id=task.run_id)
                    if out.notebook_output and out.notebook_output.result:
                        report_text = out.notebook_output.result
                        try:
                            parsed = json.loads(report_text)
                            ok = parsed.get("ok")
                            # The notebooks are not consistent about the key: 04, 06
                            # and 07 use "failures", while 03 and 05 use "errors".
                            # Lift whichever is present, so the *reason* a run went
                            # bad is queryable and not just the fact that it did.
                            issues = parsed.get("failures")
                            if issues is None:
                                issues = parsed.get("errors")
                            if issues is not None:
                                failures = json.dumps(issues)
                        except json.JSONDecodeError:
                            pass          # not every notebook exits with JSON
                    elif out.error:
                        report_text = json.dumps({"error": out.error[:2000]})
                except Exception as e:
                    # Output expires after a retention window; the run row is still
                    # worth keeping, so record it with a null report rather than
                    # dropping it.
                    skipped["no_output"] += 1
                    report_text = json.dumps(
                        {"output_unavailable": f"{type(e).__name__}: {str(e)[:150]}"})

                rows.append((
                    int(task.run_id), int(job.job_id), name, task.task_key,
                    ms_to_ts(run.start_time), ms_to_ts(run.end_time),
                    int(run.run_duration or 0) or None,
                    state, as_text(run.trigger),
                    ok, failures, report_text, now,
                ))

    R["metrics"]["skipped"] = skipped
    R["metrics"]["rows_harvested"] = len(rows)
    if not rows:
        return f"ok (nothing to collect in the last {LOOKBACK_DAYS} days)"

    df = spark.createDataFrame(rows, schema=SCHEMA)
    df.createOrReplaceTempView("_incoming_runs")
    spark.sql(f"""
        MERGE INTO {CATALOG}.ops.job_runs t
        USING _incoming_runs s ON t.run_id = s.run_id
        WHEN MATCHED THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)
    return f"ok ({len(rows)} run(s) merged from {len(jobs)} job(s))"

check("collect", collect)

# COMMAND ----------

# --------------------------------------------------- what the table now knows
def summarise():
    """The point of the table, demonstrated: per job, when it last ran and how often
    it succeeded. If this is not useful to read, the table is not worth keeping."""
    rows = spark.sql(f"""
        SELECT job_name,
               count(*)                                        AS runs,
               sum(CASE WHEN ok THEN 1 ELSE 0 END)             AS reported_ok,
               sum(CASE WHEN result_state = 'SUCCESS' THEN 1 ELSE 0 END) AS succeeded,
               max(started_at)                                 AS last_run,
               round(avg(duration_ms) / 1000, 1)               AS avg_seconds
        FROM {CATALOG}.ops.job_runs
        GROUP BY job_name ORDER BY job_name
    """).collect()
    R["metrics"]["by_job"] = [r.asDict() for r in rows]

    total = spark.sql(f"SELECT count(*) c FROM {CATALOG}.ops.job_runs").collect()[0]["c"]
    R["metrics"]["table_rows"] = total

    # A run that the Jobs API called SUCCESS while the notebook reported ok:false is
    # the interesting case: the task exited 0, so nothing alerted, but the check
    # inside it failed. That is exactly what this table exists to surface.
    silent = spark.sql(f"""
        SELECT count(*) c FROM {CATALOG}.ops.job_runs
        WHERE result_state = 'SUCCESS' AND ok = false
    """).collect()[0]["c"]
    R["metrics"]["succeeded_but_reported_not_ok"] = silent

    return (f"ok ({total} rows across {len(rows)} jobs"
            + (f"; {silent} run(s) succeeded while reporting ok:false" if silent else "")
            + ")")

check("summarise", summarise)

# COMMAND ----------

R["ok"] = not R["failures"]
print(json.dumps(R, indent=2, default=str))
dbutils.notebook.exit(json.dumps(R, default=str))
