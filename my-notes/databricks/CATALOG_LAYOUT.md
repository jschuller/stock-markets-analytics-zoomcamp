# `stock_analytics` — catalog layout

## Why this shape

The medallion layers are not imposed convention here — they are what the course
code already does. Module 5's `main.py` runs three stages that persist three
artifacts:

| Course code | Writes | Layer |
|---|---|---|
| `DataRepository.fetch()` → `.persist()` | `tickers_df.parquet`, `indexes_df.parquet`, `macro_df.parquet` | **bronze** |
| `TransformData.transform()` → `.persist()` | `transformed_df.parquet` | **gold** |
| `TrainModel.train_random_forest()` → `.persist()` | model artifact + predictions | **ml** |

So bronze/gold/ml fall straight out of the existing pipeline. Two layers are
added deliberately:

- **`silver`** exists for one concrete reason: deduping prices across sources.
  yfinance is unofficial and goes down (Ivan's warning), Stooq is dead on every
  network tested, and Alpha Vantage is the working fallback. Something has to
  decide which source wins for a given `(ticker, date)`, and that is silver's
  whole job. Without a multi-source problem it would be ceremony; with one it
  earns its place.
- **`sim`** keeps Module 4's trading results out of `ml`. Model quality and
  strategy profitability are different questions, and Ivan is explicit that a
  good model can still lose money once fees are counted.

## Layout

```
stock_analytics                       owned by the service principal
│
├── bronze      M1 — raw, source-shaped, append-only, never edited in place
│   ├── VOLUME files/                 drop-in for pd.read_parquet(data_dir)
│   ├── ohlcv_daily                   + source, asset_class, ingested_at
│   ├── macro_series                  long: series_id, date, value
│   └── tickers                       universe + scraped market caps
│
├── silver      M2 — cleaned, deduped
│   └── prices_daily                  exactly one row per (ticker, date)
│
├── gold        M2/M3 — model-ready
│   └── features                      == transformed_df (schema-on-write)
│
├── ml          M3 — modeling
│   ├── VOLUME models/                sklearn artifacts
│   ├── model_runs                    one row per training run + temporal splits
│   └── predictions                   keyed by run_id
│
├── sim         M4 — simulation
│   ├── trades                        one row per simulated trade
│   └── equity_curve                  daily portfolio state
│
└── project     capstone, kept separate from coursework
    └── VOLUME exports/
```

## Decisions worth knowing

**`bronze.files` is a Volume, not a table.** Point Module 5's `data_dir` at
`/Volumes/stock_analytics/bronze/files/` and `repo.persist()` / `repo.load()`
work **unchanged** — no porting at all. Tables are for the analytical layers
where SQL and time travel actually buy something.

**`gold.features` is not predefined.** It is `transformed_df`, which carries 200+
TA-Lib indicator columns. Hand-writing that DDL would be wrong on day one and
would drift every time an indicator is added. It gets created schema-on-write.

**`bronze` is append-only and may hold duplicate `(ticker, date)` rows** from
different sources. That is intended — bronze records what each source said, and
silver decides who wins. Never edit bronze in place; it is the audit trail for
"why did this number change?"

**`macro_series` is long, not wide.** FRED series run at different frequencies —
`FEDFUNDS` monthly, `DGS10` daily, `GDPPOT` quarterly. A wide table would be
mostly nulls, and adding a series would be a schema migration.

**Liquid clustering, not partitioning.** ~190 tickers × 25 years is only a few
million rows. Partitioning by date would produce thousands of tiny files and
make things slower. `CLUSTER BY (ticker, date)` matches how every query filters.

**`ml.model_runs` records the temporal splits explicitly.** Lookahead bias is the
easiest mistake to make in this course, and Ivan flags it twice — financial
statements land 1–2 months after quarter close. Writing the split boundaries down
makes the mistake auditable after the fact.

**`sim.trades.fees` should never be null.** Ivan's direct experience: fees are
what killed his hourly and minute-frequency crypto strategies. A backtest without
fees is a fiction.

## Creating it

The layout is defined by the **Asset Bundle** in [`bundle/`](bundle/) — that is the source
of truth. `bundle/src/03_create_layout.py` is what the bundle *runs* to create tables (DAB
has no Unity Catalog table resource); it is not a parallel path, and it deliberately does
**not** create schemas or volumes, which belong to `resources/schemas.yml` and
`resources/volumes.yml`.

```bash
export DATABRICKS_CONFIG_PROFILE=free-edition
cd my-notes/databricks/bundle
databricks bundle deploy -t free-edition
databricks bundle run bootstrap_tables -t free-edition
databricks bundle run verify_layout    -t free-edition   # expect "ok": true
```

The catalog itself must exist first and be owned by the service principal — Free Edition
permits neither `CREATE CATALOG` via API nor a metastore storage root, so it is a one-time
UI step. Full detail, including the verified error messages, in
[`bundle/README.md`](bundle/README.md).
