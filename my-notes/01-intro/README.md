# Module 1 — Introduction and Data Sources

**Homework due 2026-09-02** · submit at <https://courses.datatalks.club/sma-zoomcamp-2026/>

| | |
|---|---|
| Upstream materials | [`../../01-intro-and-data-sources/`](../../01-intro-and-data-sources/) |
| Module README | [`../../01-intro-and-data-sources/README.md`](../../01-intro-and-data-sources/README.md) |
| Homework questions | [`../../cohorts/2026/homework1.md`](../../cohorts/2026/homework1.md) |

## Notes

_(fill in during the session)_

## Homework

Worked in [`homework1.ipynb`](homework1.ipynb) — edit
[`../tools/build_homework1.py`](../tools/build_homework1.py) and regenerate rather than
hand-editing the JSON.

**Answered 2026-08-24; not yet submitted** — `cohorts/2026/homework1.md` still says
`Form for submitting: TO BE ADDED`.

| Q | Question | Answer |
|---|---|---|
| 1 | Year with most S&P 500 additions since 2020 | **2025** (18 additions) |
| 2 | Indexes beating the S&P 500 YTD as of 2026-08-21 | **2** — Nikkei 225 +27.4%, S&P/TSX +14.9% vs S&P 500 +11.9% |
| 3 | Median drawdown of >5% corrections | **7.99%** (74 corrections; median duration 40 days) |
| 4 | Correlation, 2-day return vs earnings surprise | **0.2191** Pearson, n=24 |

Every window is pinned to a constant in the setup cell. The lecture notebook derives its
window from `date.today()` minus 70 years, which is why its numbers change every run — a
homework answer cannot do that.

### Two ambiguities in the question sheet

Both are in the sheet itself, not in the working; the notebook prints both readings.

- **Q2 dates.** Title and hint say 2026-08-21; the prose says "1 January-1 August 2026".
  Two signals to one, so 08-21 is submitted → **2**. The 08-01 reading gives **4**.
- **Q4 wording.** The heading asks for the median 2-day change after positive surprises
  (**0.35%**, n=20); step 4 asks for the correlation (**0.2191**). The numbered step is
  taken as the question. Spearman is **0.2835** — a 657% surprise (2022-02-03) dominates
  the Pearson figure on 24 points.

### Self-checks

Q3 reproduces **all 10** corrections published in the question text — exact dates,
drawdowns and durations. Q1 and Q2 have no published key, so they are checked only
structurally (503 constituents, 100% of dates parsed; 11/11 indexes fetched), and the
notebook says so rather than implying more confidence than it has.

### Traps this material sets

- `pd.read_html` on Wikipedia is **403** without a browser `User-Agent` — the question's
  own hint says so.
- yfinance wants `%Y-%m-%d` date bounds. `"2026-08-22 00:00:00"` raises
  `ValueError: unconverted data remains: 00:00:00`, surfacing as an **empty frame for
  every ticker** rather than an error.
- `get_earnings_dates()` returns a **tz-aware** index (America/New_York, 16:00 — after the
  close) and only 25 quarters back to 2020-10.
- 2025's notebook read `^SPX` from Stooq, which returned rows **reversed** and so used
  negative shifts. Yahoo is chronological — do not copy that sign convention.

## Questions to follow up
