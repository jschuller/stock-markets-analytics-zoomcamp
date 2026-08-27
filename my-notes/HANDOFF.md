# Handoff — 2026 cohort, week 1

**State as of 2026-08-26.** Read [`../CLAUDE.md`](../CLAUDE.md) first; it has the
conventions and the gotchas. This file is the task list, and goes stale — update it.

---

## Where things stand

Repo synced to upstream `03075c1`. Personal work is isolated in `my-notes/`, upstream
directories verified pristine.

**Homework 1 is answered and correct — but not yet submitted.** That is the one job
with a clock on it. See below.

**Upstream corrected the questions after they were published.** Four commits landed on
2026-08-24 between 21:26 and 22:16 UTC, all to `cohorts/2026/homework1.md`: `fde0cbe`
Q1, `a6987b0` Q2, `a5cf53a` Q3–Q4, and `03075c1` adding the submit and leaderboard
links. **One of them changed a scored answer.** If you are reading this after another
sync, check for more.

**The Databricks bronze layer is loaded and now checked.** `stock_analytics` holds:

| Table | Rows | Span |
|---|---|---|
| `bronze.ohlcv_daily` | 1,961,457 | 1950-01-03 → 2026-08-24, 207 tickers |
| `bronze.macro_series` | 133,850 | 17 FRED series |
| `bronze.tickers` | 210 | universe + market caps for all 190 stocks |

**There is a test suite now**, the first in this repo. `my-notes/lib/corrections.py` is
the single hand-maintained copy of the Q3 algorithm; `my-notes/tests/` asserts it
against the ten published corrections using pinned price data, and `tests.yml` runs
that on every PR.

## Do these, roughly in order

### 1. Submit Homework 1 — the only thing with a deadline

**Form: <https://courses.datatalks.club/sma-zoomcamp-2026/homework/hw01>** ·
**due 2026-09-14, 22:59.** (An earlier version of this file said 2026-09-02. Wrong.)

It is **multiple choice**, and it asks for **no notebook URL** — so the old note here
about needing a public link before submitting does not apply to this platform.

| Q | Answer | Points | Confidence |
|---|---|---|---|
| 1 | **2025** | 2 | high — 18 additions, 503 constituents, 100% of dates parsed |
| 2 | **2** | 3 | high — the date ambiguity was resolved upstream in our favour |
| 3 | **8** (computed 7.99%) | 3 | high — reproduces all 10 published corrections, asserted in CI |
| 4 | **0.35** | 2 | high — the corrected step 4 asks for the median; 0.35 is on the ballot |

Q5 and Q6 are free text, 1 point each, and **are already drafted** — notebook cells 16
and 17. Paste them. (A previous version of this file claimed they were not drafted. It
contradicted its own section 5 and was wrong.)

**What the corrections did.** Worth understanding, because one of them cost a point:

- **Q4 — the answer changed.** Step 4 used to ask only "what's the correlation of a
  stock return vs. earnings surprise?", contradicting the question's own heading. This
  notebook resolved that in favour of the numbered step and held **0.2191**. `a5cf53a`
  rewrote step 4 to ask for the **median first** and the correlation second, and the
  form's options are 3.35 / 2.35 / 1.35 / 0.35 — 0.2191 was never on the ballot. Now
  **0.35%** (n = 20 of 24), with the correlation kept underneath because corrected
  step 4 genuinely asks for both.
- **Q2 — ambiguity dissolved.** The prose moved from "1 January-1 August" to "1
  January-21 August", agreeing with the title and hint. The answer was already **2**;
  the rival reading (4) is dead. The 08-01 window is still printed, now as a
  sensitivity check.
- **Q3 — wording tightened, answer unmoved.** "more than 5%" became "at least 5%", and
  all-time highs are now explicitly closing-price based. Both already matched the code,
  which filters `>=`. Still **7.99%**.
- **Q1 — no change.** The heading gained "(starting from 2020)", which was already the
  scoping used.

Edit via `my-notes/tools/build_homework1.py` and regenerate — never hand-edit the
`.ipynb`. Re-run with:

```bash
python my-notes/tools/build_homework1.py
cd my-notes/01-intro && jupyter nbconvert --execute --to notebook --inplace homework1.ipynb
```

### 2. ~~Colab~~ — done, and it is the strongest parity result of the three
Executed top to bottom in Colab on 2026-08-27, from the badge on `main`. **All four
answers identical to local and Databricks**, and the Q3 self-check still printed
`10/10 published corrections reproduced exactly`.

What makes it worth more than a green tick is how *different* the stack underneath was:

| | Local | Colab |
|---|---|---|
| Python | 3.11.16 | **3.13.15** |
| pandas | 2.3.3 | **2.2.3** |
| yfinance | 1.6.0 | **0.2.66** |

Three minor-version gaps, including a yfinance that is a whole major version behind,
and the answers did not move. "Runs unchanged in three environments" is now measured
rather than asserted.

One operational note if you automate this: Colab gates any GitHub-loaded notebook
behind a *"This notebook was not authored by Google"* dialog, and it will not take a
synthetic click at its coordinates — it needs either a real gesture or a DOM-level
`.click()` on the button inside the shadow root.

### 3. Rotate the Databricks service-principal secret
The last credential job, and it needs you in a console.

The secret was pasted into a chat transcript, and the current value is also in GitHub
Actions secrets. Deliberate — the working value was set first to verify CI, on the
agreement that it would be rotated straight after. Databricks account console →
Service principals → `mac-claude-desktop` → Secrets → generate new, delete old. Then
update **both** places:

```bash
R=jschuller/stock-markets-analytics-zoomcamp     # without -R, gh talks to DataTalksClub
gh secret set DATABRICKS_CLIENT_SECRET -R "$R"   # the new value
databricks configure --profile free-edition      # or edit ~/.databrickscfg
```

Re-run `gh workflow run bundle-deploy.yml -R "$R"` afterwards to confirm.

Also still open: the **Perplexity API key** in
`~/construction-mcp/databricks-sandbox/.mcp.json`, committed across 3 commits and live
at HEAD. Private repo, so contained, not urgent. Move it to an env-var reference and
gitignore the file.

### 4. Build `silver.prices_daily`
Still deliberately skipped: with yfinance as the only source, the dedupe is a no-op. It
becomes real as soon as a second source lands — which is the natural way to close the
three-ticker gap below.

### 5. Extend bronze to cover Q1 and Q4
`crosscheck_bronze` can only answer two of four questions, because index membership
dates (Wikipedia) and earnings dates (`get_earnings_dates()`) are not stored. Ingesting
both is the first capstone task — motivated by evidence rather than guessed at. See the
Q5 draft in the notebook.

## Testing and observability — what exists now

**`my-notes/lib/corrections.py`** is the only hand-maintained copy of the Q3 algorithm.
Neither consumer can import it: Colab fetches a single `.ipynb` from GitHub and nothing
else, and bundle `src/*.py` upload as Databricks *notebook objects* with the extension
stripped. So both carry the text between `BEGIN SHARED` / `END SHARED` sentinels —
`build_homework1.py` splices it in at build time, `06_crosscheck_bronze.py` holds a
pasted copy — and `tests/test_no_drift.py` asserts they still match.

They already did not. The cross-check's copy had quietly lost the `peak`/`trough`
columns and returned `Timestamp` where the notebook returned `date`. Nothing caught it,
because nothing compared them.

| File | What it does |
|---|---|
| `tests/test_corrections.py` | the ten published corrections against a pinned ^GSPC series, 0.05pp and exact durations; plus the semantics the prose leaves implicit — the inclusive 5% boundary, `>=` against `cummax`, the open final episode, calendar-not-trading days |
| `tests/test_no_drift.py` | the two carried copies still equal the canonical one |
| `tests/data/gspc_close_1950_2026-08-24.csv` | 19,282 rows, pinned. Regenerate with `refresh_gspc_fixture.py` — and expect the 7.99% assertion to need updating if you do |

`python -m pytest my-notes/tests` — **never bare `pytest`**, which on this machine
resolves to base miniforge rather than the project env.

**`src/07_data_quality.py`** asserts the data is usable, not just that the layout is the
right shape — freshness, row and ticker counts per asset class, `(ticker, date)`
uniqueness, OHLC internal consistency, null rates, universe drift both ways, and the
macro side. Run it with `databricks bundle run data_quality -t free-edition`.

Two things it taught us on its first run, both real:

- **Futures settle outside the day's traded range.** 519 bars in `GC=F`/`CL=F` have a
  close below the low or above the high, 2001–2020. That is the settlement price, not
  corruption, so `commodity` carries its own documented tolerance while equities and
  indexes are held to **zero** — and pass, across 1.78M stock and 151k index bars.
- **The latest date holds a partial bar.** 16 stock bars dated 2026-08-24, the ingest
  date, are internally inconsistent because ingestion runs during the session. The
  most recent date is excluded from the check and reported separately.

Two invariants are asserted rather than logged, so a known gap stays known: the tickers
with no bars must be exactly `{BK, FI, MMC}`, and macro must hold 17 series.

**The job is deliberately not in the deploy gate.** `ingest_bronze`'s schedule is
paused, so bronze goes stale by design and freshness will go red on purpose.
`verify_layout` stays the gate.

> Note for anyone following the old plan in this file: it said to copy
> `04_verify_layout`'s "`run()` helper". `04_verify_layout` has **`fail(msg)`**;
> `run(kind, name, sql)` is in `03_create_layout`. The template actually used is
> `06_crosscheck_bronze`'s `check(name, fn)`.

**`src/08_collect_run_reports.py`** harvests every notebook's exit JSON into
`ops.job_runs`. It reads the **Jobs API** rather than having each notebook write its
own row, which matters for three reasons: `notebook.exit()` stops execution so the
write would have to precede it in all five notebooks; bundle `src/*.py` cannot import
a shared helper, so it would be a sixth copy-pasted block; and a notebook that dies
before its exit line would record nothing — the run you most want. Reading the API
costs zero changes to the emitters, captures runs triggered from anywhere, records
**failed** runs, and backfilled history that had already happened. `MERGE` on
`run_id`, so it is safe to schedule.

It earned its keep on the first run, with a query worth keeping:

```sql
SELECT * FROM stock_analytics.ops.job_runs
WHERE result_state = 'SUCCESS' AND ok = false;
```

That is a run the Jobs API called SUCCESS — task exited 0, nothing alerted — while the
notebook's own checks reported `ok:false`. Three showed up. Two were `data_quality`
before its price check learned about futures settlement. The third was a `bootstrap`
run from 2026-08-24 13:16 with `errors: ["gold"]`, a fossil from when `03` still
created schemas itself, before they moved to `resources/schemas.yml`. Benign — but
nothing would ever have told you.

**Note the key inconsistency it exposed:** `04`, `06` and `07` report problems under
`failures`, while `03` and `05` use `errors`. The collector lifts whichever is present
into one column. Worth unifying if a sixth notebook appears.

### Still to do

1. **`email_notifications` on the jobs** in `resources/jobs.yml`. A paused schedule that
   fails silently is worse than no schedule.
2. **A scheduled source-liveness probe.** `00_egress_probe.py` already does this shape
   ad hoc. On a schedule it means you find out Yahoo changed *before* homework night.
3. **Schedule `data_quality` and `collect_run_reports`** when Module 5 unpauses the
   pipeline, and tighten `max_staleness_days` at the same time. Note the collector's
   30-day `lookback_days` is also the Jobs API's practical retention horizon — run it
   at least monthly or history is lost for good.
4. **Unify the `failures` / `errors` key** across the notebooks (see above).

### Deliberately not

**Do not run `nbconvert --execute` against live yfinance in per-PR CI.** yfinance is an
unofficial API that goes down — the instructor says so, and three tickers 404 right now.
Wiring it into a required check converts someone else's outage into your red build. The
part that can actually regress, the Q3 algorithm, is covered by `test_corrections.py`
against pinned data instead.

## Environment parity — what is actually the same

"Runs everywhere" is true of exactly one file. Be precise about the rest.

| | Local | Colab | Databricks |
|---|---|---|---|
| `01-intro/homework1.ipynb` | **verified** | **verified 2026-08-27** — same 4 answers on py3.13/pandas 2.2.3/yfinance 0.2.66 | **verified**, same answers |
| `01-intro/Module_01_Enhanced_Learning_Notebook.ipynb` | works | **verified 2026-08-24** | untested — writes `global_stocks.csv` to cwd, which may not be writable |
| `lib/corrections.py` + `tests/` | **verified** | n/a | n/a — pure Python, no `spark`/`dbutils`, which is why stock pytest is enough |
| `databricks/bundle/src/*.py` | no | no | Databricks only — needs `spark`/`dbutils` |
| pandas | 2.3.3 | 2.x | **1.5.3** on the serverless base |
| TA-Lib | conda-forge `ta-lib` | preinstalled | pip `TA-Lib` (**not** `ta-lib-binary`) |
| TensorFlow | works | works | installs, **will not import** |

So: the *homework* is portable, the *infrastructure* is not, and the base library
versions differ in ways that will bite in Module 2 (TA-Lib) and Module 3 (TensorFlow).

## Known data gaps

- **`MMC`, `FI`, `BK` are missing from bronze.** Yahoo's own chart endpoint 404s all
  three, from two networks, at every start date — not a client bug and not transient.
  187 of 190 `data_repo.py` stocks loaded. **Now asserted** by `07_data_quality`, so if
  the set changes you find out. Backfill via Alpha Vantage when `silver` exists.
- **`bronze.tickers` market caps are a 2025 snapshot.** `global_stocks.csv` has 10,000
  rows with MSFT at $3.38T; the 2026 lecture's live scrape returns 11,275 rows with
  NVDA at $5.2T. Pinned deliberately for reproducibility — re-scrape when it matters.
- **`cohorts/2025/ha1_Amazon.csv` is partly mojibake** — four rows carry `???.36` where
  the EPS digits should be, and a naive `to_numeric` silently drops them. 2026's Q4 uses
  `get_earnings_dates()` instead, so it no longer bites. That method returns 25 quarters
  (2020-10 onward, one of them a future date with no reported EPS) and a **tz-aware**
  index at 16:00 America/New_York.

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
databricks bundle run data_quality      -t free-edition  # expect "ok": true
databricks bundle run collect_run_reports -t free-edition # -> ops.job_runs
```

Ad hoc queries against the catalog go through `./run_notebook.sh <file.py>`, which
uploads a local notebook and returns its exit JSON — the workspace has no SQL editor
worth using on Free Edition.

**Keep stray files out of `bundle/`.** `databricks.yml` declares no `sync:` block, so
the entire bundle root is uploaded on every deploy.

`ingest_bronze` has a **paused** daily schedule (06:30 America/New_York). Unpause it in
`resources/jobs.yml` when Module 5 wants a live pipeline.

## Looking ahead

| Module | Homework due | Prepare |
|---|---|---|
| 2 — One Dataframe | 2026-09-16 | Pandas joins; TA-Lib indicators. TA-Lib install differs local vs Databricks. `gold.features` is schema-on-write by design. Note this is **two days** after HW1 is due. |
| 3 — The Model | 2026-09-30 | sklearn. **TensorFlow will not import on Databricks serverless** (protobuf conflict) — use Colab or local for the DNN section. |
| 4 — Trading System | 2026-10-14 | `sim.trades` is ready. Never leave `fees` null; fees are what kill high-frequency strategies. |
| 5 — Automation | 2026-10-28 | Port `05-deployment-and-automation/scripts/*.py`. `05_ingest_bronze.py` already covers `DataRepository.fetch`; the remaining work is `transform.py` and `train.py`. Its Stooq fallback is dead — substitute Alpha Vantage. Natural point to add `databrickslabs/pylint-plugin` to CI. |
| Capstone | 11-02 / 11-30 | **The only thing required for a certificate.** 6 of 36 points passes. Budget 15–50 h. Rubric in `projects/README.md`. A strong README with screenshots and a live link is what distinguished the 2025 top projects. |

Two weeks per module, 7–10 h/week. Historic completion drops 36% → 8%; finishing is the
hard part, not the difficulty.
