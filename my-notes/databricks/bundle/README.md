# `stock_analytics` Asset Bundle

Reproduces the full Unity Catalog layout — 6 schemas, 3 volumes, 8 tables — in any
workspace with one command.

```bash
export DATABRICKS_CONFIG_PROFILE=free-edition
databricks bundle validate -t free-edition
databricks bundle deploy   -t free-edition
databricks bundle run bootstrap_tables -t free-edition
databricks bundle run verify_layout    -t free-edition   # expect "ok": true
```

## Why a bundle and not Terraform

**DAB *is* Terraform.** `strings $(which databricks)` shows `bundle/deploy/terraform`,
`DATABRICKS_TF_EXEC_PATH`, `DATABRICKS_TF_VERSION`, `DATABRICKS_TF_PROVIDER_VERSION`.
`bundle deploy` shells out to a Terraform binary running the `databricks/databricks`
provider. Using DAB keeps that engine and adds workspace-managed state, native notebook
sync, and job definitions. `bundle plan` is the `terraform plan` equivalent.

The two things DAB cannot express cost nothing here:

- **Catalogs** — see the prerequisite below; no API can do it on Free Edition anyway.
- **Tables** — created by the `bootstrap_tables` job. The tradeoff is no drift detection,
  which `04_verify_layout.py` covers by asserting column names and types.

## One-time prerequisite: create the catalog

Free Edition blocks this two different ways, both verified:

```
PERMISSION_DENIED: User does not have CREATE CATALOG on Metastore 'metastore_aws_us_east_2'
Metastore storage root URL does not exist. Default Storage is enabled in your account.
```

The first is a privilege the service principal lacks; the second means the API path wants
a `MANAGED LOCATION` that Free Edition does not expose. Databricks' own error points at
the fix: *"You can use the UI to create a new catalog using Default Storage."*

As a **workspace admin**, in the UI:

1. **Catalog → Create ▾ → Create a catalog** — name `stock_analytics`, type Standard,
   leave **Use default storage** checked
2. **Overview → About this catalog → Owner ✏️** — set to the service principal
   (`mac-claude-desktop`)

Owner implies every privilege on everything beneath, so **no `GRANT` statements are
needed**. Setting the owner does remove the human account's own access — grant it back:

```bash
databricks grants update catalog stock_analytics \
  --json '{"changes":[{"principal":"you@example.com","add":["ALL_PRIVILEGES"]}]}'
```

Verify from the CLI rather than the browser, so the check is independent of what made the
change. The second command is the real test — it proves the *service principal* can create
objects:

```bash
databricks catalogs get stock_analytics --output json | grep owner
databricks schemas create _probe stock_analytics && databricks schemas delete stock_analytics._probe
```

**This bootstrap cannot run in CI** — GitHub Actions cannot drive an authenticated browser
session, so the catalog must pre-exist before `bundle deploy`. On a paid workspace with a
metastore storage root it can be an API call instead.

## Known issue: Terraform download fails

Older Databricks CLI builds (confirmed on v0.280.0) fail to download Terraform:

```
Error: error downloading Terraform: unable to verify checksums signature: openpgp: key expired
```

Two fixes. Either upgrade the CLI (`brew trust databricks/tap && brew upgrade databricks`
— note 0.280 → 1.x is a major bump that may affect other bundles on this machine), or
point the CLI at a locally installed binary, which is scoped to this shell only:

```bash
brew install opentofu
export DATABRICKS_TF_EXEC_PATH="$(which tofu)"
export DATABRICKS_TF_VERSION=1.12.6      # must match the binary, or the CLI refuses
```

OpenTofu works fine as the executor. The version variable is mandatory — without it the
CLI expects exactly 1.5.5 and errors out. CI is unaffected: `databricks/setup-cli`
installs a current CLI that does not have the expired-key bug.

## Layout

Six schemas on a medallion spine; full reasoning in
[`../CATALOG_LAYOUT.md`](../CATALOG_LAYOUT.md).

```
bronze   M1  VOLUME files/ · ohlcv_daily · macro_series · tickers
silver   M2  prices_daily          one row per (ticker, date)
gold     M2  features              schema-on-write, not predefined
ml       M3  VOLUME models/ · model_runs · predictions
sim      M4  trades · equity_curve
project      VOLUME exports/
```

`bronze.files` is the drop-in target for Module 5: set
`data_dir = "/Volumes/stock_analytics/bronze/files/"` and `repo.persist()` /
`repo.load()` work unmodified.

## Files

| Path | Role |
|---|---|
| `databricks.yml` | bundle name, variables, targets |
| `resources/schemas.yml` | 6 schemas + grants |
| `resources/volumes.yml` | 3 volumes + grants |
| `resources/jobs.yml` | `bootstrap_tables`, `verify_layout` |
| `src/03_create_layout.py` | table DDL only — schemas/volumes belong to the bundle |
| `src/04_verify_layout.py` | assertions incl. column names and types |
| `src/0[0-2]_*.py` | egress and environment probes |

## Adding a workspace

Uncomment the `other:` target in `databricks.yml`, set its `host`, then
`databricks bundle validate -t other` to check portability without deploying. The catalog
prerequisite applies there too.

## Troubleshooting

| Symptom | Cause |
|---|---|
| `unknown flag: --profile` | zsh does not word-split unquoted variables. Use `DATABRICKS_CONFIG_PROFILE` instead of building flags in a shell variable. |
| `PERMISSION_DENIED ... CREATE SCHEMA` | Catalog owner was not set to the service principal. |
| `Syntax error at or near 's'` in a DDL comment | An apostrophe inside a single-quoted SQL string. Avoid `course's` in `COMMENT '...'`. |
| `expected version is 1.5.5` | Set `DATABRICKS_TF_VERSION` to match your `DATABRICKS_TF_EXEC_PATH` binary. |
