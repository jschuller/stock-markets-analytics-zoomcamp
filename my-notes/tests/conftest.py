"""Test configuration.

No package, no pyproject: the repo has neither, and these tests do not need one.
`my-notes/lib` goes on sys.path here so `import corrections` works from anywhere.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[2]
LIB = REPO / "my-notes" / "lib"
sys.path.insert(0, str(LIB))

FIXTURE = Path(__file__).parent / "data" / "gspc_close_1950_2026-08-24.csv"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO


@pytest.fixture(scope="session")
def gspc() -> pd.Series:
    """^GSPC daily close, 1950-01-03 -> 2026-08-24, exactly as Homework 1 saw it.

    Pinned on disk rather than downloaded: yfinance is an unofficial API that goes
    down, and a golden test that needs the network is a golden test that will not
    run when it matters. Regenerate with data/refresh_gspc_fixture.py.
    """
    return pd.read_csv(FIXTURE, comment="#", parse_dates=["date"],
                       index_col="date")["close"]
