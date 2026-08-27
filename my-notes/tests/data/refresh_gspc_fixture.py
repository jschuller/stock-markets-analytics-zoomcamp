"""Regenerate the pinned ^GSPC close series used by the Q3 golden test.

Run this by hand, never from CI. The whole point of the committed CSV is that
`test_corrections.py` reproduces the ten published corrections *offline* — yfinance
is an unofficial API that goes down, and the handoff's own rule is not to convert
someone else's outage into a red build.

    python my-notes/tests/data/refresh_gspc_fixture.py

The fetch matches `get_ohlcv()` in my-notes/tools/build_homework1.py exactly:
auto_adjust=False, actions=False, tz-naive index, rows with a null Close dropped.
`END` is inclusive here and bumped by a day for yfinance, same as get_ohlcv does.

Regenerating moves the answer: a longer series can add corrections and shift the
median off the 7.99% that was submitted. If you do regenerate, expect
test_median_drawdown_matches_submitted_answer to fail, and update it deliberately.
"""

import pandas as pd
import yfinance as yf

START = "1950-01-01"
END = "2026-08-24"          # the day Homework 1 was answered; inclusive
OUT = "my-notes/tests/data/gspc_close_1950_2026-08-24.csv"

raw = yf.download("^GSPC", start=START,
                  end=(pd.Timestamp(END) + pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                  auto_adjust=False, actions=False, progress=False, group_by="ticker")
df = raw["^GSPC"] if isinstance(raw.columns, pd.MultiIndex) else raw
df = df.dropna(subset=["Close"])
if getattr(df.index, "tz", None) is not None:
    df.index = df.index.tz_localize(None)

close = df["Close"]
with open(OUT, "w") as fh:
    fh.write(f"# ^GSPC daily close, pinned fixture for Homework 1 Q3.\n")
    fh.write(f"# source: yfinance auto_adjust=False | pulled {END}\n")
    fh.write(f"# rows: {len(close)} | span: {close.index[0].date()} -> {close.index[-1].date()}\n")
    close.rename("close").to_csv(fh, index_label="date", float_format="%.6f")

print(f"wrote {OUT}: {len(close)} rows, "
      f"{close.index[0].date()} -> {close.index[-1].date()}")
