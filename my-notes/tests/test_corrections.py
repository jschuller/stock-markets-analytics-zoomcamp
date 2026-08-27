"""Tests for the Homework 1 Q3 drawdown algorithm.

Two halves, and the split is the point.

The **golden** tests assert that `find_corrections` reproduces the ten corrections
DataTalksClub publishes in the question text (`cohorts/2026/homework1.md`) and the
7.99% median that was submitted. That is an independent check: the fixture is pinned
price data and the expected values come from the instructor, not from this code.

The **semantics** tests pin the decisions the question's prose leaves implicit — the
inclusive 5% boundary, what counts as an all-time high, whether the final unfinished
drawdown counts, and whether duration is calendar or trading days. Those are the
things a well-meaning refactor would quietly change.

Note what this does *not* replace: `06_crosscheck_bronze.py` still re-answers Q3 from
`bronze.ohlcv_daily`. That validates the *data*; this validates the *algorithm*.
Before this file existed only the first check ran, and both sides of it ran the same
copied code.
"""

import datetime as dt

import pandas as pd
import pytest

from corrections import CORRECTION_COLUMNS, find_corrections

# From cohorts/2026/homework1.md, "Hint (use this data to compare with your results)":
# (peak, trough, drawdown %, duration in days)
PUBLISHED_TOP10 = [
    ("2007-10-09", "2009-03-09", 56.8, 517), ("2000-03-24", "2002-10-09", 49.1, 929),
    ("1973-01-11", "1974-10-03", 48.2, 630), ("1968-11-29", "1970-05-26", 36.1, 543),
    ("2020-02-19", "2020-03-23", 33.9,  33), ("1987-08-25", "1987-12-04", 33.5, 101),
    ("1961-12-12", "1962-06-26", 28.0, 196), ("1980-11-28", "1982-08-12", 27.1, 622),
    ("2022-01-03", "2022-10-12", 25.4, 282), ("1966-02-09", "1966-10-07", 22.2, 240),
]

SUBMITTED_MEDIAN_PCT = 7.99
SUBMITTED_CORRECTION_COUNT = 74


def series(values, start="2020-01-01"):
    """A close series on consecutive calendar days, for the semantics tests."""
    idx = pd.date_range(start, periods=len(values), freq="D")
    return pd.Series(values, index=idx, dtype=float)


# --------------------------------------------------------------- golden fixture

@pytest.fixture(scope="module")
def top10(gspc):
    return find_corrections(gspc, 5.0).nlargest(10, "drawdown_pct").reset_index(drop=True)


@pytest.mark.parametrize("rank,expected", list(enumerate(PUBLISHED_TOP10)),
                         ids=[p[0] for p in PUBLISHED_TOP10])
def test_reproduces_published_correction(top10, rank, expected):
    """Each of the ten published corrections, by rank, from pinned ^GSPC data."""
    peak, trough, drawdown_pct, duration_days = expected
    row = top10.loc[rank]

    assert str(row.peak_date) == peak
    assert str(row.trough_date) == trough
    # The published figures are given to one decimal place, so 0.05pp is as tight as
    # the source allows. Durations are integers and must match exactly.
    assert row.drawdown_pct == pytest.approx(drawdown_pct, abs=0.05)
    assert row.duration_days == duration_days


def test_median_drawdown_matches_submitted_answer(gspc):
    """7.99% is what went on the form. If this moves, the submission was wrong."""
    corrections = find_corrections(gspc, 5.0)
    assert len(corrections) == SUBMITTED_CORRECTION_COUNT
    assert round(corrections["drawdown_pct"].median(), 2) == SUBMITTED_MEDIAN_PCT


def test_fixture_is_the_series_the_homework_saw(gspc):
    """Guards the fixture itself: a silent regeneration would move the answer."""
    assert len(gspc) == 19282
    assert gspc.index[0].date() == dt.date(1950, 1, 3)
    assert gspc.index[-1].date() == dt.date(2026, 8, 24)


def test_trough_never_falls_on_its_own_peak(gspc):
    """The trough search starts the day *after* the high, so they cannot coincide."""
    corrections = find_corrections(gspc, 5.0)
    assert (corrections["peak_date"] != corrections["trough_date"]).all()


def test_peak_dates_are_plain_dates_not_timestamps(gspc):
    """The notebook's self-check compares str(peak_date) to "2007-10-09".

    A Timestamp would stringify as "2007-10-09 00:00:00" and every comparison would
    silently start failing, so the type is part of the contract.
    """
    corrections = find_corrections(gspc, 5.0)
    assert isinstance(corrections["peak_date"].iloc[0], dt.date)
    assert not isinstance(corrections["peak_date"].iloc[0], pd.Timestamp)


# -------------------------------------------------------------------- semantics

def test_exactly_five_percent_is_kept():
    """The question says "at least 5%", so the boundary is inclusive."""
    result = find_corrections(series([100, 95, 101]), 5.0)
    assert len(result) == 1
    assert result.loc[0, "drawdown_pct"] == pytest.approx(5.0)


def test_just_under_five_percent_is_dropped():
    assert len(find_corrections(series([100, 95.01, 101]), 5.0)) == 0


def test_no_corrections_returns_an_empty_frame_that_still_has_columns():
    """Regression: pd.DataFrame([]) has no columns, so callers hit KeyError.

    Both callers immediately read ["drawdown_pct"], which on a flat market would
    have raised instead of yielding an empty Series.
    """
    result = find_corrections(series([100, 99, 101]), 5.0)
    assert result.empty
    assert list(result.columns) == CORRECTION_COLUMNS
    assert len(result["drawdown_pct"]) == 0


def test_matching_a_previous_high_starts_a_new_episode():
    """ATHs use `close >= cummax()`, so a day that ties a prior high counts.

    Under a strict `>` the middle 100 would not be an ATH and these two drawdowns
    would merge into one, so this distinguishes the two readings.
    """
    result = find_corrections(series([100, 90, 100, 85, 101]), 5.0)
    assert len(result) == 2
    assert result["drawdown_pct"].tolist() == pytest.approx([10.0, 15.0])


def test_final_unrecovered_drawdown_is_counted():
    """The last episode runs to the end of the series, not to the next high.

    Without it, a market currently in a correction would report nothing at all.
    """
    result = find_corrections(series([100, 101, 90]), 5.0)
    assert len(result) == 1
    assert result.loc[0, "peak_date"] == dt.date(2020, 1, 2)
    assert result.loc[0, "trough_date"] == dt.date(2020, 1, 3)


def test_duration_is_calendar_days_not_trading_days():
    """Friday to Monday is 3 days, not 1 — the convention the published table uses."""
    idx = pd.DatetimeIndex(["2026-01-02", "2026-01-05"])   # Fri, Mon
    result = find_corrections(pd.Series([100.0, 90.0], index=idx), 5.0)
    assert result.loc[0, "duration_days"] == 3


def test_nulls_are_dropped_and_input_order_does_not_matter():
    clean = series([100, 90, 100, 85, 101])
    messy = clean.copy()
    messy.loc[pd.Timestamp("2020-01-06")] = float("nan")
    messy = messy.sample(frac=1.0, random_state=0)          # shuffle

    pd.testing.assert_frame_equal(find_corrections(messy, 5.0),
                                  find_corrections(clean, 5.0))


def test_threshold_is_configurable():
    prices = series([100, 92, 101])
    assert len(find_corrections(prices, 5.0)) == 1
    assert len(find_corrections(prices, 10.0)) == 0
