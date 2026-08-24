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

## Storage

Writable by the service principal: `/tmp` (ephemeral, per-run) and
`/Workspace/Users/<sp-id>/` (persistent).

Creating a Unity Catalog schema or volume fails with `PERMISSION_DENIED` for the
`mac-claude-desktop` service principal. Catalogs present: `mycat`, `workspace`,
`samples`, `system`. To pre-stage data in a volume, grant the SP `USE CATALOG` +
`CREATE SCHEMA` on a catalog, or create the volume from the UI and grant `WRITE VOLUME`.

## Notebooks here

| File | Purpose |
|---|---|
| `00_egress_probe.py` | DNS/HTTPS per domain, preinstalled deps, installability, real course calls |
| `01_env_probe.py` | Base versions by serverless client, TF/keras, Stooq, gdown, UC volume |
| `02_final_probe.py` | Real gdown IDs, pandas upgrade, full TF traceback, writable paths |

All three return results via `dbutils.notebook.exit(json.dumps(...))` — `print()` output
does not come back through the Jobs API. Run one with:

```bash
export DATABRICKS_CONFIG_PROFILE=free-edition
SP=/Users/<service-principal-id>
databricks workspace import "$SP/sma-zoomcamp/00_egress_probe" \
  --file my-notes/databricks/00_egress_probe.py \
  --format SOURCE --language PYTHON --overwrite
databricks jobs submit --no-wait --json \
  "{\"run_name\":\"probe\",\"tasks\":[{\"task_key\":\"p\",\"notebook_task\":{\"notebook_path\":\"$SP/sma-zoomcamp/00_egress_probe\"}}]}"
```

Omitting any cluster spec is what selects serverless. Add
`"environments":[{"environment_key":"default","spec":{"client":"3"}}]` and
`"environment_key":"default"` on the task to pin a newer base environment.

## Auth

Profile `free-edition` in `~/.databrickscfg` (mode 0600, outside the repo), using
OAuth M2M with a service principal client id + secret. Free Edition is serverless-only:
zero clusters, one 2X-Small "Serverless Starter Warehouse".
