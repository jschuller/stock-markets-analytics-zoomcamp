# Handoff — 2026 cohort, week 1

**State as of 2026-08-24 13:30 EDT.** Read [`../CLAUDE.md`](../CLAUDE.md) first; it has the
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
runs top to bottom and prints all four scored answers, plus drafted Q5/Q6.

**All three environments now genuinely work.** The same notebook returns the same four
answers on local Jupyter and on Databricks serverless — verified, not assumed. Its setup
cell calls `detect_env()` and installs only what is missing, using `subprocess` rather
than a `!pip`/`%pip` magic so it also survives `nbconvert` and the Jobs API. Colab is
made correct by construction and has a one-click badge, but has not been executed from
here — **that one is still a manual check**.

**The fork has a front page.** [`.github/README.md`](../.github/README.md) is what GitHub
renders instead of upstream's README, so the root `README.md` stays byte-identical and
the mirror check still passes.

**bronze is cross-validated.** `crosscheck_bronze` re-answers Q2 and Q3 from
`bronze.ohlcv_daily` instead of from live yfinance: Q2 matches exactly, Q3 to within
0.004 percentage points.

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

- **Q2 dates.** The heading, the bold question and the hint
  (`end_date='2026-08-21'`) all say 21 August; only a prose parenthetical says
  "1 January-1 August 2026". Three signals to one, so 08-21 is the submitted answer
  → **2**. The 08-01 reading gives **4**. Still worth a Slack question, but the
  reading is not close.
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

### 3. Click the homework1 Colab badge — after the PR merges
`Module_01_Enhanced_Learning_Notebook.ipynb` was opened in Colab and works. **That is a
different file.** `homework1.ipynb` exists only on the branch, so its badge — which
points at `blob/main/...` — returns 404 until PR #2 merges. Once merged, open it and run
top to bottom.

If it fails, the fix belongs in [`tools/build_homework1.py`](tools/build_homework1.py),
never in the `.ipynb` — the notebook is generated and hand edits are lost on rebuild.

### 4. Build `silver.prices_daily`
Deliberately skipped: with yfinance as the only source, the dedupe is a no-op. It becomes
real as soon as a second source lands — which is the natural way to close the three-ticker
gap below, and the natural next step for `crosscheck_bronze` to validate.

### 5. Extend bronze to cover Q1 and Q4
`crosscheck_bronze` can only answer two of the four homework questions, because index
membership dates (Wikipedia) and earnings dates (`get_earnings_dates()`) are not stored.
Ingesting both is the first capstone task — motivated by evidence rather than guessed at.
See the Q5 draft in the notebook.

### 6. CI works now — and rotating is the last credential job

**GitHub CI is green end to end**, on PR #2. The full chain runs: deploy → create
tables → verify layout, with `layout verified: ok`. Both claims that had never been
tested now hold — a PR runs validate + plan and comments, and **no deploy fires from a
PR**; deploy only runs on merge or dispatch.

Getting there uncovered two failures stacked behind the credentials, neither of which
anyone could have seen while CI failed at authentication:

1. `databricks/setup-cli` with no `version` installs the newest CLI, which requests
   provider `1.129.0` — OpenTofu rejects its signature outright.
2. Pinning to 0.280.0 (matching local) fixes that and exposes the next one: 0.280.0
   cannot download Terraform at all, `openpgp: key expired` — the same bug `CLAUDE.md`
   documents for local.

So CI now pins the CLI **and** installs OpenTofu 1.12.6 itself, setting
`DATABRICKS_TF_EXEC_PATH` / `DATABRICKS_TF_VERSION` exactly as you would in a shell.
`bundle/README.md` used to say CI was unaffected by this; it was never true, just
untested. Corrected.

Also worth knowing: the validate workflow's `Plan` step ends in `|| true`, so a broken
plan still reports success. It is informational. `Validate bundle` is the real gate.

**Still to do — the last credential job:**

- **Rotate the Databricks service-principal secret.** It was pasted into a chat
  transcript, and the current value is now also in GitHub Actions secrets. Deliberate:
  we set the working value first to verify CI, and agreed to rotate straight after.
  Databricks account console → Service principals → `mac-claude-desktop` → Secrets →
  generate new, delete old. Then update **both** places:
  ```bash
  R=jschuller/stock-markets-analytics-zoomcamp     # without -R, gh talks to DataTalksClub
  gh secret set DATABRICKS_CLIENT_SECRET -R "$R"   # the new value
  databricks configure --profile free-edition      # or edit ~/.databrickscfg
  ```
  Re-run `gh workflow run bundle-deploy.yml -R "$R"` afterwards to confirm CI still works.
- **Rotate the Perplexity API key** in `~/construction-mcp/databricks-sandbox/.mcp.json` —
  committed across 3 commits and live at HEAD. Private repo, so contained, not urgent.
  Move it to an env-var reference and gitignore the file.

## Environment parity — what is actually the same

"Runs everywhere" is true of exactly one file. Be precise about the rest.

| | Local | Colab | Databricks |
|---|---|---|---|
| `01-intro/homework1.ipynb` | **verified** | badge added, **not yet clicked** | **verified**, same 4 answers |
| `01-intro/Module_01_Enhanced_Learning_Notebook.ipynb` | works | **verified 2026-08-24** | untested — writes `global_stocks.csv` to cwd, which may not be writable |
| `databricks/bundle/src/*.py` | no | no | Databricks only — needs `spark`/`dbutils` |
| pandas | 2.3.3 | 2.x | **1.5.3** on the serverless base |
| TA-Lib | conda-forge `ta-lib` | preinstalled | pip `TA-Lib` (**not** `ta-lib-binary`) |
| TensorFlow | works | works | installs, **will not import** |
| Data source | live yfinance | live yfinance | live yfinance **or** `bronze.ohlcv_daily` |

So: the *homework* is portable, the *infrastructure* is not, and the base library
versions differ in ways that will bite in Module 2 (TA-Lib) and Module 3 (TensorFlow).
Assume nothing else is portable without running it.

## Next session — testing and observability

This is a data project, so the tests that matter are about data, not code. Nothing here
is tested today: CI only checks that notebook JSON parses, and there is no `tests/`
directory or pytest anywhere.

### Do first

1. **Extract `find_corrections` into a module and unit-test it.** It is currently
   copy-pasted into three files (`tools/build_homework1.py`,
   `databricks/bundle/src/06_crosscheck_bronze.py`, and the generated notebook). That
   duplication quietly weakens the cross-check: it validates that *bronze data*
   reproduces the answer, not that the *algorithm* is right, because both sides run the
   same copied code. Fix by making the algorithm a real module with its own test, and
   let the cross-check keep doing the data half.

   The golden fixture already exists: the ten corrections published in the question text
   (`cohorts/2026/homework1.md`). Assert against those. Also worth a rubric point —
   "code is well designed and commented on in modules."

2. **A data-quality job, `src/07_data_quality.py`.** Same house style as
   `04_verify_layout` — `run()` helper, exit JSON with `ok`. Checks worth having:

   | Check | Catches |
   |---|---|
   | freshness — `max(date)` within N business days | a silently stopped pipeline |
   | row-count bounds per asset class | a partial load that "succeeded" |
   | uniqueness of `(ticker, date)` per source | the append-vs-replace trap |
   | `high >= low`, `low <= close <= high`, no negative prices | upstream data corruption |
   | null rate on `close`, `volume` | quiet degradation |
   | every `ohlcv_daily.ticker` present in `bronze.tickers` | universe drift |

3. **Run pytest in CI.** `bundle-validate.yml` currently proves only that notebooks are
   valid JSON. Once (1) exists there is something real to run.

### Then

4. **Persist the run reports.** Every notebook already ends with
   `dbutils.notebook.exit(json.dumps(...))`, and every one of those reports is thrown
   away. Writing them to a small `ops.job_runs` table turns existing discipline into
   actual observability — "when did ingest last succeed", "is the failed-ticker list
   growing", "how long has `MMC` been 404ing". Cheap, because the JSON already exists.
5. **`email_notifications` on the jobs** in `resources/jobs.yml`. A paused schedule that
   fails silently is worse than no schedule.
6. **A scheduled source-liveness probe.** `00_egress_probe.py` already does this shape
   ad hoc. On a schedule it means you find out Yahoo changed *before* homework night.

### Deliberately not

**Do not run `nbconvert --execute` against live yfinance in per-PR CI.** yfinance is an
unofficial API that goes down — the instructor says so, and three tickers 404 right now.
Wiring it into a required check converts someone else's outage into your red build. Run
it nightly and allow failure, or run it against `bronze` where the data is pinned.

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

cd my-notes/databricks
./push_notebooks.sh                                      # coursework .ipynb -> workspace
cd bundle
databricks bundle deploy -t free-edition
databricks bundle run ingest_bronze     -t free-edition  # idempotent; ~3 min
databricks bundle run crosscheck_bronze -t free-edition  # expect "ok": true
```

**Keep stray files out of `bundle/`.** `databricks.yml` declares no `sync:` block, so the
entire bundle root is uploaded on every deploy — anything dropped there goes to the
workspace.

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
