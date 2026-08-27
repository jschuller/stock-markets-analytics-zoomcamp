# CI/CD

Three workflows, deliberately split so that **nothing deploys from a pull request**.

| Workflow | Trigger | Does |
|---|---|---|
| `tests.yml` | every PR and push to `main` | `pytest my-notes/tests` — needs no Databricks credentials |
| `bundle-validate.yml` | PRs and non-main pushes touching `my-notes/databricks/**` | `bundle validate`, notebook JSON check, `bundle plan` posted as a PR comment |
| `bundle-deploy.yml` | push to `main` (same paths), or manual | `bundle deploy` → `bootstrap_tables` → `verify_layout`, failing unless the verifier returns `"ok": true` |

`tests.yml` takes no paths filter. `test_no_drift.py` compares three copies of the
same code block across `my-notes/lib/`, the notebook and the bundle, so any filter
narrow enough to be useful would leave a hole exactly where drift gets in.

## Required configuration

Repository **variable**:

| Name | Value |
|---|---|
| `DATABRICKS_HOST` | `https://dbc-bf7dd89d-daac.cloud.databricks.com` |

Repository **secrets**:

| Name | Where from |
|---|---|
| `DATABRICKS_CLIENT_ID` | service principal application ID |
| `DATABRICKS_CLIENT_SECRET` | its OAuth secret |

Also create a GitHub **Environment** named `free-edition`. `bundle-deploy.yml` references
it, which is what lets you add a required reviewer without editing the workflow.

```bash
gh variable set DATABRICKS_HOST --body 'https://dbc-bf7dd89d-daac.cloud.databricks.com'
gh secret set DATABRICKS_CLIENT_ID
gh secret set DATABRICKS_CLIENT_SECRET
```

## Why not OIDC

Databricks officially recommends OIDC workload identity federation over stored
credentials, and they are right — it avoids a long-lived secret entirely. It is
unavailable here.

OIDC needs a **GitHub Actions federation policy on the service principal**, which is an
account-level operation. Databricks Free Edition has no account API. Both probes fail:

```
$ databricks account service-principals list
Error: invalid Databricks Account configuration - host incorrect or account_id missing

$ databricks api get /api/2.0/accounts/self/servicePrincipals
Error: Not Found
```

So CI uses OAuth M2M with the client ID and secret. **On a paid workspace, switching is
three lines** — in both workflows:

1. Delete `DATABRICKS_CLIENT_SECRET`
2. Add `DATABRICKS_AUTH_TYPE: github-oidc`
3. Add `id-token: write` to that job's `permissions`

Keep `DATABRICKS_CLIENT_ID` and `DATABRICKS_HOST`. Then create the federation policy on
the service principal, scoped to this repository.

## Hardening in place

- **Actions pinned to full commit SHAs**, matching `databricks-sandbox` commit `4e70f2c`.
  Tags are mutable; SHAs are not.
- **Repository guard** on deploy — `if: github.repository == 'jschuller/...'` — so anyone
  who forks this fork cannot fire jobs at the workspace.
- **Least-privilege `permissions`**: `contents: read` by default; `pull-requests: write`
  only on the job that comments a plan.
- **Concurrency**: validate runs supersede each other; deploys never cancel mid-flight.
  Free Edition caps at 5 concurrent job tasks with limited compute, so stacked runs would
  burn quota.
- **Paths filters** so course-notes commits do not trigger infrastructure runs.

## What is deliberately not here

- **The catalog bootstrap.** It needs an authenticated browser session, which CI cannot
  provide. See [`../../my-notes/databricks/bundle/README.md`](../../my-notes/databricks/bundle/README.md).
- **The Module 5 daily pipeline.** That is a Databricks job schedule declared in
  `resources/jobs.yml`. GitHub deploys; Databricks schedules.
- **Linting.** `databrickslabs/pylint-plugin` is the right tool, and there is finally
  something for it to lint. Add it when Module 5's `scripts/*.py` are ported.
- **`databrickslabs/pytester`.** Unit tests arrived without it: `my-notes/lib/` is
  plain Python needing no `spark` or `dbutils`, so it runs under stock pytest.
  pytester earns its place when a test needs a real workspace.
- **Executing notebooks in CI.** `nbconvert --execute` hits live yfinance, an
  unofficial API that goes down — three tickers 404 right now. Wiring that into a
  required check turns someone else's outage into a red build. The part that can
  actually regress, the Q3 algorithm, is covered by `test_corrections.py` against a
  pinned price series instead.
