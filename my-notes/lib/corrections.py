"""The S&P 500 drawdown algorithm, in one place.

Homework 1 Q3 asks for the median drawdown of significant market corrections. The
algorithm below is the answer to that question, and it is used three times: by the
generated notebook (`my-notes/01-intro/homework1.ipynb`), by the Databricks
cross-check (`my-notes/databricks/bundle/src/06_crosscheck_bronze.py`), and by the
tests in `my-notes/tests/test_corrections.py`.

**This file is the only hand-maintained copy.** The other two carry the block
between the `BEGIN SHARED` / `END SHARED` sentinels verbatim:

* `my-notes/tools/build_homework1.py` slices it out at build time and embeds it in
  the notebook cell, because Colab fetches a single `.ipynb` from GitHub and nothing
  else — the notebook has to stay self-contained.
* `06_crosscheck_bronze.py` carries a pasted copy, because bundle `src/*.py` files
  upload as Databricks *notebook objects* with the extension stripped, so a sibling
  import has nowhere to point.

`my-notes/tests/test_no_drift.py` asserts both copies still match this one, which is
what makes that duplication safe rather than merely tidy. Edit here, then run
`python my-notes/tools/build_homework1.py` and paste the block into the cross-check.
"""

import pandas as pd

# --- BEGIN SHARED: find_corrections ---
CORRECTION_COLUMNS = ["peak_date", "trough_date", "peak", "trough",
                      "drawdown_pct", "duration_days"]


def find_corrections(close: pd.Series, threshold_pct: float = 5.0) -> pd.DataFrame:
    """Drawdown episodes measured from each all-time high.

    Walks consecutive all-time highs; between one ATH and the next, the lowest close
    is the trough. Keeps episodes whose fall reaches `threshold_pct` — inclusive, so
    exactly 5.0% counts, matching the question's "goes down by **at least 5%** from
    the most recent all-time high". Duration is calendar days from ATH to trough —
    peak-to-trough, not peak-to-recovery, which is the convention the published
    table uses.

    An ATH is a close at or above every previous close, so a day that merely matches
    a prior high starts a new episode. Returns one row per episode, and an empty
    frame *with columns* when none qualify.
    """
    close = close.dropna().sort_index()
    ath_dates = list(close.index[close >= close.cummax()])

    episodes = []
    for i, start in enumerate(ath_dates):
        end = ath_dates[i + 1] if i + 1 < len(ath_dates) else close.index[-1]
        window = close.loc[start:end]
        if len(window) < 2:
            continue
        trough_val = window.iloc[1:].min()
        trough_date = window.iloc[1:].idxmin()
        high = close.loc[start]
        dd = (high - trough_val) / high * 100
        if dd >= threshold_pct:
            episodes.append({"peak_date": start.date(), "trough_date": trough_date.date(),
                             "peak": float(high), "trough": float(trough_val),
                             "drawdown_pct": float(dd),
                             "duration_days": int((trough_date - start).days)})
    # columns= matters on the empty path: pd.DataFrame([]) has no columns at all, so
    # a caller reading ["drawdown_pct"] would get KeyError rather than an empty Series.
    return pd.DataFrame(episodes, columns=CORRECTION_COLUMNS)
# --- END SHARED ---
