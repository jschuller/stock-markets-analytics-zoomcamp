# Handoff — 2026 cohort, week 1

**State as of 2026-08-24 10:25 EDT.** Read [`../CLAUDE.md`](../CLAUDE.md) first; it has the
conventions and the gotchas. This file is the task list, and goes stale — update it.

---

## Where things stand

Repo synced to upstream `28a52a7` ("HA1 2026"). The **2026 Module 1 Colab notebook** (65 code cells)
and the 2026 README section are local. Personal work is isolated in `my-notes/`, upstream
directories verified pristine.

**The Databricks bronze layer is loaded.** `stock_analytics` now holds:

| Table | Rows | Span |
|---|---|---|
| `bronze.ohlcv_daily` | 1,961,457 | 1950-01-03 → 2026-08-24, 207 tickers |
| `bronze.macro_series` | 133,850 | 17 FRED series |
| `bronze.tickers` | 210 | universe + market caps for all 190 stocks |

Loaded by `ingest_bronze`, a bundle job. Verified: zero within-source duplicates,
`^GSPC` closes match yfinance exactly, and a second run left the row count unchanged
rather than doubling it. `verify_layout` still returns `ok: true`.

**Homework 1 is answered.** Upstream published the questions (`28a52a7`, "HA1 2026") at
~10:10 EDT, ahead of the livestream. [`01-intro/homework1.ipynb`](01-intro/homework1.ipynb)
runs top to bottom and prints all four scored answers.

## Do these, roughly in order

### 1. Submit Homework 1 — computed, not yet submitted
**The form link does not exist yet.** `cohorts/2026/homework1.md` says
`Form for submitting: TO BE ADDED`, as does the leaderboard link. Re-sync before
submitting, and check the platform at <https://courses.datatalks.club/sma-zoomcamp-2026/>.
**Due 2026-09-02.**

Answers from `my-notes/01-intro/homework1.ipynb`, run 2026-08-24:

| Q | Question | Answer | Confidence |
|---|---|---|---|
| 1 | Year with most S&P 500 additions since 2020 | **2025** (18 additions) | high — 503 constituents, 100% of dates parsed, and the question's own context note cites DASH/WSM/EXE/TKO joining in 2025 |
| 2 | Indexes beating the S&P 500 YTD | **2** (Nikkei 225, S&P/TSX) | see the date ambiguity below |
| 3 | Median drawdown of >5% corrections | **7.99%** | high — reproduces **all 10** published corrections exactly |
| 4 | Correlation, 2-day return vs surprise | **0.2191** (Pearson, n=24) | see the wording ambiguity below |

**Two ambiguities are in the question sheet itself, not in the working.** The notebook
prints both readings rather than choosing silently:

- **Q2 dates.** The title says "as of 21 August 2026" and the hint says
  `end_date='2026-08-21'`, but the prose says "1 January-1 August 2026". Two signals to
  one, so 08-21 is the submitted answer → **2**. The 08-01 reading gives **4**. Worth
  asking in Slack; this changes the answer.
- **Q4 wording.** The heading asks for the *median 2-day change after positive surprises*
  (**0.35%**, n=20); step 4 asks for the *correlation* (**0.2191**). The numbered step is
  taken as the question. Spearman is 0.2835 — the sample carries a 657% surprise outlier
  (2022-02-03), so the rank correlation is the more honest number if asked to defend it.

The form wants numbers **plus a public URL** to the notebook — push before submitting. Do
**not** put anything in `cohorts/`, which is upstream's.

Edit the notebook via `my-notes/tools/build_homework1.py` and regenerate, rather than
hand-editing JSON. Re-run with:

```bash
cd my-notes/01-intro && jupyter nbconvert --execute --to notebook --inplace homework1.ipynb
```

Q5 and Q6 are optional free text and are **not** drafted — leaderboard points only.

### 2. Watch the Module 1 livestream — 11:00 EDT today
<https://www.youtube.com/watch?v=66T0fbf5rdc> · [2026 slides](https://docs.google.com/presentation/d/e/2PACX-1vQO0dtA4iFel1d1XoPr5pqVB1XZ5C9yQRf5UfDcIp8NbSinINCevBrEzes_lEr5uoDqZ8__8IxrxNzl/pub)
· Q&A at <https://qna.dtcdev.click/r/sma>

Recorded, so the only thing missed by not attending live is the Q&A.

### 3. Build `silver.prices_daily`
Deliberately skipped this pass: with yfinance as the only source, the dedupe is a no-op.
It becomes real as soon as a second source lands — which is the natural way to close the
three-ticker gap below.

### 4. Loose ends — your call, deliberately not done

- **GitHub CI has run once, and failed.** Correcting the previous handoff, which said it
  never had. `Bundle deploy` fired on push to main (2026-08-24T13:23:41Z) and failed in
  16s with `default auth: cannot configure default credentials` — the secrets are empty.
  The `free-edition` Environment already exists. Note the `-R` flag; without it `gh` talks
  to DataTalksClub:
  ```bash
  R=jschuller/stock-markets-analytics-zoomcamp
  gh variable set DATABRICKS_HOST -R $R --body 'https://dbc-bf7dd89d-daac.cloud.databricks.com'
  gh secret set DATABRICKS_CLIENT_ID -R $R
  gh secret set DATABRICKS_CLIENT_SECRET -R $R
  ```
  Then prove it with a throwaway PR touching `my-notes/databricks/`: validate + plan should
  run and comment, **and no deploy should fire from the PR**.
- **Rotate the Databricks service-principal secret.** It was pasted into a chat transcript.
- **Rotate the Perplexity API key** in `~/construction-mcp/databricks-sandbox/.mcp.json` —
  committed across 3 commits and live at HEAD. Private repo, so contained, not urgent.
  Move it to an env-var reference and gitignore the file.

## Known data gaps

- **`MMC`, `FI`, `BK` are missing from bronze.** Yahoo's own chart endpoint 404s all three,
  from two networks, at every start date — not a client bug and not transient. 187 of 190
  `data_repo.py` stocks loaded. Backfill via Alpha Vantage when `silver` exists.
- **`bronze.tickers` market caps are a 2025 snapshot.** `global_stocks.csv` has 10,000 rows
  with MSFT at $3.38T; the 2026 lecture's live scrape returns 11,275 rows with NVDA at
  $5.2T. Pinned deliberately for reproducibility — re-scrape when the numbers matter.
- **`cohorts/2025/ha1_Amazon.csv` is partly mojibake** — four rows carry `???.36` where the
  EPS digits should be, and a naive `to_numeric` silently drops them. 2026's Q4 uses
  `yf.Ticker(...).get_earnings_dates()` instead of that CSV, so it no longer bites; noted
  in case the file is reused. `get_earnings_dates()` returns only 25 quarters (2020-10
  onward) and a **tz-aware** index at 16:00 America/New_York.

## Databricks quick reference

```bash
export DATABRICKS_CONFIG_PROFILE=free-edition
export DATABRICKS_TF_EXEC_PATH="$(which tofu)"
export DATABRICKS_TF_VERSION=1.12.6
cd my-notes/databricks/bundle
databricks bundle deploy -t free-edition
databricks bundle run ingest_bronze -t free-edition    # idempotent; ~3 min
```

`ingest_bronze` has a **paused** daily schedule (06:30 America/New_York). Unpause it in
`resources/jobs.yml` when Module 5 wants a live pipeline.

## Looking ahead

| Module | Homework due | Prepare |
|---|---|---|
| 2 — One Dataframe | 2026-09-16 | Pandas joins; TA-Lib indicators. TA-Lib install differs local vs Databricks. `gold.features` is schema-on-write by design. |
| 3 — The Model | 2026-09-30 | sklearn. **TensorFlow will not import on Databricks serverless** (protobuf conflict) — use Colab or local for the DNN section. |
| 4 — Trading System | 2026-10-14 | `sim.trades` is ready. Never leave `fees` null; fees are what kill high-frequency strategies. |
| 5 — Automation | 2026-10-28 | Port `05-deployment-and-automation/scripts/*.py`. `05_ingest_bronze.py` already covers `DataRepository.fetch`; the remaining work is `transform.py` and `train.py`. Its Stooq fallback is dead — substitute Alpha Vantage. Natural point to add `databrickslabs/pylint-plugin` + `pytester` to CI. |
| Capstone | 11-02 / 11-30 | **The only thing required for a certificate.** 6 of 36 points passes. Budget 15–50 h. Rubric in `projects/README.md`. A strong README with screenshots and a live link is what distinguished the 2025 top projects. |

Two weeks per module, 7–10 h/week. Historic completion drops 36% → 8%; finishing is the
hard part, not the difficulty.
