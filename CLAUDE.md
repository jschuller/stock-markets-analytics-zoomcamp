# Stock Markets Analytics Zoomcamp — working notes for Claude

Durable facts about this repo. Task-of-the-day lives in
[`my-notes/HANDOFF.md`](my-notes/HANDOFF.md).

> This file sits at the repo root because that is where Claude Code auto-loads it.
> Upstream has no `CLAUDE.md`; if it ever adds one, resolve the conflict in favour of
> keeping both.

## What this repo is

A personal fork of [DataTalksClub/stock-markets-analytics-zoomcamp](https://github.com/DataTalksClub/stock-markets-analytics-zoomcamp)
for the **2026 cohort** (started 2026-08-24). GitHub account is **`jschuller`** — two
L's. The local macOS username is `jschulle`, one L shorter; building a remote URL from
`$HOME` or `whoami` produces a repo that does not exist and a misleading
`Repository not found` on push.

- `origin` → `git@github.com:jschuller/stock-markets-analytics-zoomcamp.git` (the fork)
- `upstream` → `https://github.com/DataTalksClub/...` (read-only)

**`gh` resolves to upstream, not the fork.** With two remotes the CLI picks
`DataTalksClub`, so `gh variable list` returns `HTTP 403` and `gh secret list`
errors on ambiguity — both look like auth failures and are not. Every `gh`
invocation in this repo needs the repo pinned:

```bash
gh run list -R jschuller/stock-markets-analytics-zoomcamp
```

## The one structural rule

**Everything outside `my-notes/` is an unmodified mirror of upstream. All personal work
lives in `my-notes/`.** That is what keeps syncing painless. Before committing anything
that touches a course directory, ask whether it belongs in `my-notes/` instead.

Check the mirror is intact:

```bash
git diff --stat upstream/main -- 01-intro-and-data-sources 02-dataframe-analysis \
  03-modeling 04-trading-strategy-and-simulation 05-deployment-and-automation \
  cohorts projects README.md      # empty output = pristine
```

## Syncing

```bash
git fetch upstream && git merge upstream/main
```

**Not `--ff-only`.** That worked only while `my-notes/` was untracked. The fork now
carries its own commits, so the branches have diverged and `--ff-only` refuses with
`Diverging branches can't be fast-forwarded`. A plain merge is clean because of the
structural rule above.

New module materials appear upstream on the day of each livestream — sync before working.

## Three environments

| | Use for | Notes |
|---|---|---|
| **Colab** | Following live sessions | What the course targets. Links in `my-notes/01-intro/COLAB_SETUP.md` |
| **Local conda** | Homework, capstone | env `stock-markets-analytics`, Python 3.11. Built and smoke-tested |
| **Databricks Free Edition** | Warehouse-shaped work | Catalog `stock_analytics` deployed via Asset Bundle |

Local env: `conda activate stock-markets-analytics`. Definition in
`my-notes/environment.yml` — **read the comments before changing pins**.

## Data sources — verified state

- **yfinance works** but is an unofficial API that goes down (the instructor says so
  explicitly). Expect intermittent failures, not correctness bugs.
- **FRED works** via `pandas_datareader`.
- **Stooq is dead.** JS proof-of-work challenge from a home IP, MySQL backend error from
  Databricks. Two networks, both broken. The Stooq tier of `data_repo.py`'s
  yfinance → Stooq → FRED fallback cannot be relied on anywhere.
- **Alpha Vantage MCP is connected in Claude Code** and is the practical replacement:
  `TIME_SERIES_DAILY` plus `CPI`, `FEDERAL_FUNDS_RATE`, `TREASURY_YIELD` — the same
  macro series Module 1 pulls from FRED. Free tier is **25 requests/day**, so it is a
  fallback for specific symbols, not a bulk source.
- **yfinance 404s some live symbols.** Verified 2026-08-24: `MMC`, `FI` and `BK` return
  `Not Found` from Yahoo's own chart endpoint (`query2.finance.yahoo.com/v8/finance/chart/`),
  from two networks, at every start date. Not a yfinance bug and not transient — check
  the raw endpoint before debugging client code. 187 of the 190 `data_repo.py` tickers load.
- **`data_repo.py` lists `SNYS`, which does not exist.** The intended symbol is `SNPS`
  (Synopsys). Fixed in `05_ingest_bronze.py` and reported in its exit JSON.
- `pd.read_html` on Wikipedia returns **403** without a browser `User-Agent`; fetch with
  `requests` and pass the text to `read_html`.

## Package pins that matter

| Package | Pin | Why |
|---|---|---|
| `pandas` | `>=2.2,<3` | A bare solve resolves to 3.0.5; notebooks and Colab are on 2.x. Databricks serverless base is **1.5.3**, older still — pin explicitly there too. |
| `pandas-datareader` | `==0.10.0` | 0.11 removed Stooq entirely, so `pdr.get_data_stooq()` raises `AttributeError` before touching the network. |
| TA-Lib | **platform-dependent** | Locally: conda-forge `ta-lib`. On Databricks: pip **`TA-Lib`** — `ta-lib-binary` fails there. The two are opposite; do not unify them. |
| `tensorflow` | broken on Databricks | Installs, will not import: its bundled protobuf gencode conflicts with the runtime's. Module 3 DNN section only; sklearn models are fine. |

## Databricks specifics

```bash
export DATABRICKS_CONFIG_PROFILE=free-edition     # NOT --profile in a shell variable
```

zsh does not word-split unquoted variables, so `P="--profile x"; databricks ... $P` sends
one argument and fails with `unknown flag`.

- **`print()` output does not come back through the Jobs API.** Notebooks meant to be run
  as jobs must end with `dbutils.notebook.exit(json.dumps(...))`.
- **`%pip install` aborts the entire run on failure** (`CalledProcessError`). In probe
  notebooks shell out via `subprocess.run([sys.executable, "-m", "pip", ...])` and inspect
  the return code instead.
- **Apostrophes break SQL string literals** — `COMMENT 'the course's df'` throws
  `[PARSE_SYNTAX_ERROR]`.
- The installed CLI (v0.280.0) cannot download Terraform: `openpgp: key expired`. Work
  around it per-shell rather than upgrading, since a 0.280 → 1.x bump could break the
  Azure bundles in `~/construction-mcp/databricks-sandbox`:

```bash
export DATABRICKS_TF_EXEC_PATH="$(which tofu)"
export DATABRICKS_TF_VERSION=1.12.6      # must match the binary exactly
```

- **Bronze is append-only across sources, not within one.** The same `(ticker, date)`
  from yfinance *and* Alpha Vantage is expected; `silver` resolves it. The same row from
  yfinance twice is a duplicate no rule can undo. `05_ingest_bronze.py` therefore defaults
  to `mode=replace_source`, which deletes that source's rows before writing — re-running
  reloads rather than doubling. Never switch it to `append` for a source already loaded.

Layout, bundle, and CI are documented in `my-notes/databricks/`. **DAB is Terraform**
underneath — that is why there is no separate Terraform config, and the decision should
not be re-litigated.

## Course logistics

Deadlines, links, certification rules, and time budget: **`my-notes/2026-prep-brief.md`**.
Only the capstone project is required for a certificate; homeworks feed the leaderboard.
