# Running the notebooks in Google Colab

Colab is the primary environment for the live sessions — nothing to install, all
libraries pre-installed, saves to Drive. Use `my-notes/environment.yml` when you
want to work locally instead.

## Open the instructor's notebook straight from GitHub

Swap the `github.com` host for `colab.research.google.com/github`:

| Module | Colab link |
|---|---|
| 1 — Data Sources | [`[2025]_Module_01_Colab_Introduction_and_Data_Sources.ipynb`](https://colab.research.google.com/github/DataTalksClub/stock-markets-analytics-zoomcamp/blob/main/01-intro-and-data-sources/%5B2025%5D_Module_01_Colab_Introduction_and_Data_Sources.ipynb) |
| 2 — One Dataframe | [`[2025]_Module_02_Colab_Working_with_the_data.ipynb`](https://colab.research.google.com/github/DataTalksClub/stock-markets-analytics-zoomcamp/blob/main/02-dataframe-analysis/%5B2025%5D_Module_02_Colab_Working_with_the_data.ipynb) |
| 3 — The Model | [`[2025]_Module_3_Colab_Time_Series_Modeling.ipynb`](https://colab.research.google.com/github/DataTalksClub/stock-markets-analytics-zoomcamp/blob/main/03-modeling/%5B2025%5D_Module_3_Colab_Time_Series_Modeling.ipynb) |
| 4 — Trading System | [`[2025]_Module_04_Colab_Trading_Simulations.ipynb`](https://colab.research.google.com/github/DataTalksClub/stock-markets-analytics-zoomcamp/blob/main/04-trading-strategy-and-simulation/%5B2025%5D_Module_04_Colab_Trading_Simulations.ipynb) |
| 5 — Automation | [`[2025]_Module_05_Advanced_Strategies_And_Simulation.ipynb`](https://colab.research.google.com/github/DataTalksClub/stock-markets-analytics-zoomcamp/blob/main/05-deployment-and-automation/%5B2025%5D_Module_05_Advanced_Strategies_And_Simulation.ipynb) |

These are the **2025** notebooks — the 2026 ones land in the same directories as
each module airs. Re-run `git fetch upstream && git merge upstream/main`
weekly to pick them up.

Colab opens these read-only. Use **File → Save a copy in Drive** before editing,
or upload your own copy from `my-notes/`.

## Upload a personal notebook

1. <https://colab.research.google.com/> → **Upload**
2. Upload `my-notes/01-intro/Module_01_Enhanced_Learning_Notebook.ipynb`

## Data files

Notebook cells that read `/content/global_stocks.csv` expect the file in Colab's
working directory. Either upload `my-notes/01-intro/data/global_stocks.csv` via
the file browser, or mount Drive:

```python
from google.colab import drive
drive.mount('/content/drive')
```

Running locally instead? Point those cells at
`my-notes/01-intro/data/global_stocks.csv` — the `/content/` prefix is Colab-only.
