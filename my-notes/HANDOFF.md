# Handoff — 2026 cohort, week 1

**State as of 2026-08-24 09:35 EDT.** Read [`../CLAUDE.md`](../CLAUDE.md) first; it has the
conventions and the gotchas. This file is the task list, and goes stale — update it.

---

## Where things stand

Repo synced to upstream `cac6821`; the **2026 Module 1 Colab notebook** (65 code cells) and
the 2026 README section are local. Personal work is isolated in `my-notes/`, upstream
directories verified pristine.

Three environments are ready. Colab links resolve. The local conda env
`stock-markets-analytics` is built and smoke-tested against yfinance, FRED, and Wikipedia
scraping. Databricks Free Edition has catalog `stock_analytics` — 6 schemas, 3 volumes,
8 tables — deployed by an Asset Bundle and verified at column level (`ok: true`), with
`bundle plan` reporting `0 to add, 0 to change, 0 to delete`.

**The Databricks layout is empty.** Nothing has been ingested yet.

## Do these, roughly in order

### 1. Module 1 livestream — today, 11:00 EDT
<https://www.youtube.com/watch?v=66T0fbf5rdc> · [2026 slides](https://docs.google.com/presentation/d/e/2PACX-1vQO0dtA4iFel1d1XoPr5pqVB1XZ5C9yQRf5UfDcIp8NbSinINCevBrEzes_lEr5uoDqZ8__8IxrxNzl/pub)
· ask questions at <https://qna.dtcdev.click/r/sma>

Recorded, so not attending live costs nothing but the Q&A.

### 2. Sync afterwards
`cohorts/2026/homework1.md` is still a **three-line placeholder** — the questions land
after the session. Sync, then read it before doing anything else:

```bash
git fetch upstream && git merge upstream/main      # not --ff-only
cat cohorts/2026/homework1.md
```

### 3. Homework 1 — due 2026-09-02
Submit at <https://courses.datatalks.club/sma-zoomcamp-2026/>.

Work in `my-notes/01-intro/`. Suggested: a `homework1.ipynb` that answers each question in
its own cell, printing the submitted value clearly, so the answers are reproducible rather
than remembered. Do **not** put anything in `cohorts/`, which is upstream's.

The 2026 notebook uses `EPI, VOO, NVDA, ^GSPC, ^DJI, ^GDAXI, ^SPX` and FRED series
`GDPPOT, GVZCLS`; imports are `yfinance, pandas_datareader, bs4, requests, pandas, numpy,
matplotlib, plotly`. All available in the local env.

Two known traps in this material: `pd.read_html` on Wikipedia needs a `User-Agent`, and
anything routed through Stooq will fail.

### 4. Ingest Module 1 data into bronze
The highest-value week-1 wrap. Turns the empty layout into something real and is the
foundation for Modules 2–5, which build on the same data.

Target the tables that already exist, per
[`databricks/CATALOG_LAYOUT.md`](databricks/CATALOG_LAYOUT.md):

- `bronze.ohlcv_daily` — yfinance bars, with `source` and `ingested_at` set. Append-only;
  duplicate `(ticker, date)` across sources is expected and correct.
- `bronze.macro_series` — FRED, long format (`series_id, date, value`).
- `bronze.tickers` — the universe, plus `my-notes/01-intro/data/global_stocks.csv`.

Add it as a job in `databricks/bundle/resources/jobs.yml` so it deploys with everything
else. Then `silver.prices_daily` is the dedupe step — one row per `(ticker, date)`,
resolving yfinance vs Alpha Vantage by source preference.

### 5. Loose ends
- **GitHub CI has never run.** It needs config that was deliberately not set unilaterally,
  because this repo is public:
  ```bash
  gh variable set DATABRICKS_HOST --body 'https://dbc-bf7dd89d-daac.cloud.databricks.com'
  gh secret set DATABRICKS_CLIENT_ID
  gh secret set DATABRICKS_CLIENT_SECRET
  ```
  Plus a GitHub Environment named `free-edition`. Then prove it with a throwaway PR
  touching `my-notes/databricks/`: validate + plan should run and comment, **and no deploy
  should fire from the PR**.
- **Rotate the Databricks service-principal secret.** It was pasted into a chat transcript.
- **Rotate the Perplexity API key** in `~/construction-mcp/databricks-sandbox/.mcp.json` —
  committed across 3 commits and live at HEAD. That repo is private, so contained, not
  urgent. Move it to an env-var reference and gitignore the file.

## Looking ahead

| Module | Homework due | Prepare |
|---|---|---|
| 2 — One Dataframe | 2026-09-16 | Pandas joins; TA-Lib indicators. TA-Lib install differs local vs Databricks. |
| 3 — The Model | 2026-09-30 | sklearn. **TensorFlow will not import on Databricks serverless** (protobuf conflict) — use Colab or local for the DNN section. |
| 4 — Trading System | 2026-10-14 | `sim.trades` is ready. Never leave `fees` null; fees are what kill high-frequency strategies. |
| 5 — Automation | 2026-10-28 | Port `05-deployment-and-automation/scripts/*.py`. Point `data_dir` at `/Volumes/stock_analytics/bronze/files/` and `repo.persist()`/`load()` work unchanged. Its Stooq fallback is dead — substitute Alpha Vantage. Natural point to add `databrickslabs/pylint-plugin` + `pytester` to CI, once there is importable Python. |
| Capstone | 11-02 / 11-30 | **The only thing required for a certificate.** 6 of 36 points passes. Budget 15–50 h. Rubric in `projects/README.md`. A strong README with screenshots and a live link is what distinguished the 2025 top projects. |

Two weeks per module, 7–10 h/week. Historic completion drops 36% → 8%; finishing is the
hard part, not the difficulty.
