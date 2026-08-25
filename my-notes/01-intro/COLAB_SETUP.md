# Running the notebooks in Google Colab

Colab is what the course targets for live sessions: nothing to install, and it
saves to Drive. Use [`../environment.yml`](../environment.yml) to work locally
instead, or [`../databricks/`](../databricks/) for the warehouse-shaped work.

## Open any notebook in this repo, in one click

Swap the host `github.com` → `colab.research.google.com/github`, keep the rest of
the path. That works for **any** notebook in **any** public repo, including this
fork — which means personal notebooks under `my-notes/` open the same way as
upstream's, with no manual upload.

```
https://github.com/jschuller/stock-markets-analytics-zoomcamp/blob/main/<path>
https://colab.research.google.com/github/jschuller/stock-markets-analytics-zoomcamp/blob/main/<path>
```

Square brackets in upstream's filenames must be percent-encoded: `[` → `%5B`,
`]` → `%5D`.

### My notebooks

| Notebook | Colab |
|---|---|
| **Homework 1** — the four 2026 answers, reproducible | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jschuller/stock-markets-analytics-zoomcamp/blob/main/my-notes/01-intro/homework1.ipynb) |
| Module 1 annotated walkthrough | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jschuller/stock-markets-analytics-zoomcamp/blob/main/my-notes/01-intro/Module_01_Enhanced_Learning_Notebook.ipynb) |

### The instructor's notebooks

Module 1 has a 2026 notebook; Modules 2–5 are still 2025 until each airs.
Re-run `git fetch upstream && git merge upstream/main` before each session.

| Module | Cohort | Colab |
|---|---|---|
| 1 — Data Sources | **2026** | [`[2026]_Module_01_Colab_Introduction_and_Data_Sources.ipynb`](https://colab.research.google.com/github/DataTalksClub/stock-markets-analytics-zoomcamp/blob/main/01-intro-and-data-sources/%5B2026%5D_Module_01_Colab_Introduction_and_Data_Sources.ipynb) |
| 2 — One Dataframe | 2025 | [`[2025]_Module_02_Colab_Working_with_the_data.ipynb`](https://colab.research.google.com/github/DataTalksClub/stock-markets-analytics-zoomcamp/blob/main/02-dataframe-analysis/%5B2025%5D_Module_02_Colab_Working_with_the_data.ipynb) |
| 3 — The Model | 2025 | [`[2025]_Module_3_Colab_Time_Series_Modeling.ipynb`](https://colab.research.google.com/github/DataTalksClub/stock-markets-analytics-zoomcamp/blob/main/03-modeling/%5B2025%5D_Module_3_Colab_Time_Series_Modeling.ipynb) |
| 4 — Trading System | 2025 | [`[2025]_Module_04_Colab_Trading_Simulations.ipynb`](https://colab.research.google.com/github/DataTalksClub/stock-markets-analytics-zoomcamp/blob/main/04-trading-strategy-and-simulation/%5B2025%5D_Module_04_Colab_Trading_Simulations.ipynb) |
| 5 — Automation | 2025 | [`[2025]_Module_05_Advanced_Strategies_And_Simulation.ipynb`](https://colab.research.google.com/github/DataTalksClub/stock-markets-analytics-zoomcamp/blob/main/05-deployment-and-automation/%5B2025%5D_Module_05_Advanced_Strategies_And_Simulation.ipynb) |

Colab opens these read-only. **File → Save a copy in Drive** before editing.

## Dependencies

Colab preinstalls `numpy`, `pandas`, `requests`, `matplotlib`, `plotly`, `bs4`,
`lxml` and `gdown`. It does **not** preinstall `yfinance`, which is why every
upstream notebook opens with `!pip install yfinance`.

`homework1.ipynb` handles this itself — its setup cell detects Colab, Databricks
or local and installs only what is missing, using `subprocess` rather than a
`!pip`/`%pip` magic so the same cell also works under `nbconvert` and the
Databricks Jobs API.

One gap to know about: upstream's notebooks `import pandas_datareader` but only
install `yfinance`. It works today because Colab happens to ship
`pandas_datareader`, but nothing declares that dependency. If a Colab image drops
it, those notebooks break at the imports cell — add `pandas-datareader==0.10.0`
to the install line. The pin matters: 0.11 removed Stooq support entirely.

## Data files

Upstream's notebooks read `/content/global_stocks.csv`, which is Colab's working
directory. **None of the notebooks under `my-notes/` use a `/content/` path** —
the annotated walkthrough scrapes `global_stocks.csv` into the working directory
itself, and `homework1.ipynb` reads no local files at all.

If a scrape fails and you want the checked-in copy, it is at
[`data/global_stocks.csv`](data/global_stocks.csv) — a 2025 snapshot, 10,000 rows.
Upload it through Colab's file browser, or mount Drive:

```python
from google.colab import drive
drive.mount('/content/drive')
```

Modules 3–5 pull their parquet inputs with `!gdown ... -O /content/`. Keep gdown's
**CLI** form — the Python API's `fuzzy=` keyword is rejected by some versions.
