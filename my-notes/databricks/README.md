# Running the course on Databricks Free Edition

**Verdict: it works.** Verified by execution on
`dbc-bf7dd89d-daac.cloud.databricks.com` (2026-08-24), not inferred from docs.

The docs say Free Edition restricts outbound internet "to a limited set of trusted
domains." On this workspace that is **not** what happens — a control probe to
`example.com` succeeded, as did every domain the course needs. Verify with
`00_egress_probe` before assuming; the restriction may be account-dependent.

## Verified working

| Check | Result |
|---|---|
| `yfinance.download("AAPL")` | 5 rows |
| FRED `CPILFESL` via pandas-datareader | 31 rows |
| `pd.read_html` on Wikipedia (with UA header) | 503 rows |
| PyPI installs | all course deps except `ta-lib-binary` |
| Egress control (`example.com`) | HTTP 200 — general internet, not a whitelist |

## The five things that bite

**1. Use `TA-Lib`, not `ta-lib-binary`.** `ta-lib-binary` fails (`rc=1`) — and because
`%pip` raises `CalledProcessError`, it aborts the whole notebook run. Plain `TA-Lib`
installs and imports cleanly as `talib` 0.7.1 (manylinux wheel, no C toolchain needed).
This is the opposite of the local macOS situation, where the conda-forge build is
required.

**2. The base environment ships pandas 1.5.3** — *older* than the course's pandas 2.x
target, on both serverless client `1` and `3`. Pin it explicitly. (numpy and sklearn do
move with the client version: 1.23.5/1.3.0 on client 1, 1.26.4/1.4.2 on client 3.)

**3. `bs4` and `tqdm` are not preinstalled** despite being core course dependencies.

**4. TensorFlow installs but will not import.** `google.protobuf.runtime_version.VersionError:
Detected mismatched Protobuf Gencode/Runtime major versions` — TF's bundled protobuf
gencode conflicts with the runtime's own protobuf under `/databricks/python/lib`.
Affects the Module 3 deep-neural-network section only; the sklearn models are unaffected.
Try `%pip install --upgrade protobuf` then `dbutils.library.restartPython()`.

**5. Stooq is broken here too.** Returns a MySQL backend error
(`mysqli_query() expects parameter 1...`) from Databricks, and a JavaScript
proof-of-work challenge from a home IP. Two networks, both dead — so the Stooq middle
tier of `data_repo.py`'s yfinance → Stooq → FRED fallback cannot be relied on anywhere.
See [`../2026-prep-brief.md`](../2026-prep-brief.md).

## Setup cell

Put this at the top of any ported course notebook:

```python
%pip install -q "pandas>=2.2,<3" yfinance "pandas-datareader==0.10.0" \
                beautifulsoup4 tqdm lxml html5lib gdown TA-Lib
dbutils.library.restartPython()
```

`pandas-datareader` is pinned to 0.10.0 because 0.11 removed Stooq support entirely,
so `pdr.get_data_stooq()` raises `AttributeError` rather than attempting the call.

## Porting the Colab notebooks

No `google.colab` imports, no `drive.mount`, no `files.upload` anywhere in the course —
the coupling is shallow and mechanical:

| Colab | Databricks | Sites |
|---|---|---|
| `!pip install X` | `%pip install X` + `dbutils.library.restartPython()` | 26 |
| `/content/...` | `/tmp/...` or a Unity Catalog Volume | 22 |
| `!gdown <url> --fuzzy -O /content/` | same CLI form, `-O /tmp/` | 28 |

Keep `gdown`'s **CLI** form. The Python API's `fuzzy=` keyword was rejected by the
version that installed here.

## Storage — Unity Catalog

Diagnosis: the service principal is in the `users` group, which holds only
`USE_CATALOG` on `workspace`. The catalog is owned by
`_workspace_admins_workspace_<id>`, and the metastore owner is `System user`
(Databricks-managed on Free Edition). The SP cannot grant to itself —
`grants update` returns `User does not have MANAGE on Catalog 'workspace'`.
So a workspace admin has to run the grant once.

**Run this as your admin user** — Databricks UI → **SQL Editor**, with the
"Serverless Starter Warehouse" (it will auto-start):

```sql
GRANT USE CATALOG   ON CATALOG workspace TO `fe103a46-947d-4263-899e-58c73fb750f3`;
GRANT CREATE SCHEMA ON CATALOG workspace TO `fe103a46-947d-4263-899e-58c73fb750f3`;
```

Two statements, and that is the whole fix. The service principal then creates
`workspace.sma` itself, becomes its owner, and inherits every privilege inside
it — volumes, tables, the lot — with no further grants needed.

Prefer to keep catalog-level permissions tight? Create the objects yourself and
grant only on them:

```sql
CREATE SCHEMA IF NOT EXISTS workspace.sma;
CREATE VOLUME IF NOT EXISTS workspace.sma.data;
GRANT USE CATALOG ON CATALOG workspace          TO `fe103a46-947d-4263-899e-58c73fb750f3`;
GRANT USE SCHEMA, CREATE TABLE
                  ON SCHEMA  workspace.sma      TO `fe103a46-947d-4263-899e-58c73fb750f3`;
GRANT READ VOLUME, WRITE VOLUME
                  ON VOLUME  workspace.sma.data TO `fe103a46-947d-4263-899e-58c73fb750f3`;
```

Verify afterwards with:

```bash
databricks grants get-effective catalog workspace \
  --principal fe103a46-947d-4263-899e-58c73fb750f3
```

Until then, writable paths are `/tmp` (ephemeral, per-run) and
`/Workspace/Users/<id>/` (persistent). The `mycat` catalog is not visible to the
SP at all — `workspace` is the right target.

## Layout as code

The `stock_analytics` catalog layout is defined by a **Databricks Asset Bundle** in
[`bundle/`](bundle/), deployable to any workspace. See
[`bundle/README.md`](bundle/README.md) and [`CATALOG_LAYOUT.md`](CATALOG_LAYOUT.md).

**Why DAB and not Terraform** — recorded here so it is not re-litigated: DAB *is*
Terraform. `strings $(which databricks)` shows `bundle/deploy/terraform`,
`DATABRICKS_TF_EXEC_PATH`, `DATABRICKS_TF_VERSION`. The CLI shells out to a Terraform
binary running the `databricks/databricks` provider, so a bundle keeps that engine while
adding workspace-managed state, notebook sync, and job definitions. `bundle plan` is the
`terraform plan` equivalent. DAB cannot express catalogs (impossible on Free Edition
anyway) or tables (done by a job); everything else it covers natively, grants included.

CI/CD lives in [`../../.github/workflows/`](../../.github/workflows/): validate + plan on
PRs, deploy + verify on merge to main.

## Notebooks here

| File | Purpose |
|---|---|
| `bundle/src/00_egress_probe.py` | DNS/HTTPS per domain, preinstalled deps, installability, real course calls |
| `bundle/src/01_env_probe.py` | base versions by serverless client, TF/keras, Stooq, gdown |
| `bundle/src/02_final_probe.py` | real gdown IDs, pandas upgrade, TF traceback, writable paths |
| `bundle/src/03_create_layout.py` | table DDL, run by the bundle's `bootstrap_tables` job |
| `bundle/src/04_verify_layout.py` | assertions incl. column names and types; CI gate |

All return results via `dbutils.notebook.exit(json.dumps(...))` — `print()` output does
not come back through the Jobs API. Run one ad hoc with `./run_notebook.sh <file.py>`,
or through the bundle with `databricks bundle run <job> -t free-edition`.

## Auth

Profile `free-edition` in `~/.databrickscfg` (mode 0600, outside the repo), using
OAuth M2M with a service principal client id + secret. Free Edition is serverless-only:
zero clusters, one 2X-Small "Serverless Starter Warehouse".

## Operational tooling

`run_notebook.sh` collapses the four-step CLI cycle — `workspace import` →
`jobs submit` → poll → `get-run-output` — into one command:

```bash
cd my-notes/databricks
./run_notebook.sh 00_egress_probe.py        # default base environment
./run_notebook.sh 01_env_probe.py 3         # pin serverless client version 3
```

It resolves the calling identity via `current-user me` rather than hardcoding an
id, and pretty-prints the JSON the notebook returns.

Two CLI gotchas worth knowing:

- **The `--profile` flag does not survive shell variables in zsh.** `P="--profile x"; databricks ... $P`
  passes one argument, not two, and fails with `unknown flag`. Export
  `DATABRICKS_CONFIG_PROFILE=free-edition` instead.
- **`%pip install` aborts the whole run on failure** — it raises
  `CalledProcessError`. In probe notebooks, shell out via
  `subprocess.run([sys.executable, "-m", "pip", ...])` and inspect the return code
  so one bad package cannot kill the run.

## Data sources: the Alpha Vantage option

The Alpha Vantage MCP server is already connected in this Claude Code session and
covers every data need in the course — `TIME_SERIES_DAILY` (20+ years OHLCV),
plus `CPI`, `FEDERAL_FUNDS_RATE`, and `TREASURY_YIELD`, which are the same macro
series Module 1 pulls from FRED. It also carries fundamentals, earnings, and
technical indicators.

Verified working: `TIME_SERIES_DAILY(AAPL)` returned 100 days through 2026-08-21.

That makes it a credible replacement for the **Stooq** tier of `data_repo.py`'s
fallback chain, which is dead on both networks tested. It is a real API with an
SLA rather than a scraped endpoint — exactly what Ivan recommended in the
Pre-Course Q&A when he said to prefer paid sources if you have them.
