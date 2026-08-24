# 2026 Cohort — Prep Brief

Operational detail for the 2026 Stock Markets Analytics Zoomcamp. Sourced from the
[Pre-Course Live Q&A](https://www.youtube.com/watch?v=Qph4w_WYECc) (Ivan Brigida +
Alexey Grigorev, 2026-08-18) and the course platform. Most of this is **not** in the
repo README.

---

## Module 1 is live now

| | |
|---|---|
| **When** | Mon **2026-08-24, 11:00 EDT** — 16:00 Dublin / 15:00 UTC |
| **What** | Module 1, "Introduction and Data Sources" |
| **Stream** | <https://www.youtube.com/watch?v=66T0fbf5rdc> (`66T0fbf5rdc`) |
| **Playlist** | [2026 SMA Zoomcamp](https://www.youtube.com/playlist?list=PLAlZmugkCNtk) |

Ivan moved the start ~1–1.5 h earlier than the pre-launch stream slot. Attending live
is optional — everything is recorded, and homework windows are two weeks wide.

## Schedule

Five homeworks this year; 2025 had four. Deadlines from
[courses.datatalks.club/sma-zoomcamp-2026](https://courses.datatalks.club/sma-zoomcamp-2026/),
shown in your local timezone on the platform itself.

| # | Module | Homework due |
|---|---|---|
| 1 | Data Sources | 2026-09-02 |
| 2 | One Dataframe | 2026-09-16 |
| 3 | The Model | 2026-09-30 |
| 4 | Trading System | 2026-10-14 |
| 5 | Automation | 2026-10-28 |
| — | **Project attempt 1** | **2026-11-02** |
| — | **Project attempt 2** | **2026-11-30** |

Homeworks open as each module airs. Lessons stream live on Mondays; Ivan keeps them
live rather than pre-recorded so the market data is fresh.

## Certification — read this once

**Only the capstone project is required for a certificate.** Homeworks are optional;
they feed the leaderboard and are how Ivan tests new ideas, but you can skip every one
and still graduate by submitting a project.

- Two attempts, each: **2 weeks build + 1 week peer review**, reviewing **3 peers**.
- Rubric lives in [`projects/README.md`](../projects/README.md). Max observed score
  **36**; you need **6** to pass. The bar is low — finishing is the hard part.
- Historic completion: 36% after Module 1 → **8%** at the end. ~22 projects submitted
  in 2025. Getting to the finish line puts you in a small group.

What made 2025's top projects stand out, per Ivan and Alexey: a **well-written README**
with screenshots, a live link, and the rubric self-scored as checkboxes. A hiring manager
reads the README, not the code.

## Time budget

Underestimating this is the single most common failure mode — Ivan called it out directly.

- **7–10 h per week**, per module (~5–6 h homework + 2–4 h lecture, per 2-week module)
- **15–50 h** for the capstone, depending on ambition

## Links

| What | Where |
|---|---|
| Course platform (submissions, deadlines, leaderboard) | <https://courses.datatalks.club/sma-zoomcamp-2026/> |
| Official course docs | <https://datatalks.club/docs/courses/stock-markets-analytics-zoomcamp/> |
| FAQ | <https://datatalks.club/faq/stock-markets-analytics-zoomcamp.html> |
| Slack `#course-stocks-analytics-zoomcamp` | <https://datatalks-club.slack.com/archives/C06L1RTF10F> |
| Telegram announcements | <https://t.me/stockanalyticszoomcamp> |
| YouTube (PythonInvest) | <https://www.youtube.com/@pythoninvest> |
| Q&A tool for live sessions | <https://qna.dtcdev.click/r/sma> |
| Pre-launch slide deck | [Google Slides](https://docs.google.com/presentation/d/e/2PACX-1vSnjdqFhJQFTUG3SVi2fNVNZUAhPrYOZXbfpGqQPMSZFkW5VwNRWG940kBLkbFpmkiJc23VHcN6F5j8/pub) |
| Registration | <https://pythoninvest.com/course> |

Slack and Telegram are the fast channels — Ivan's email announcements lag 1–2 days.
Roughly 730 registrations across 58 countries this year; ~1,800 people in the Slack channel.

## Technical gotchas

**yfinance is an unofficial API and it goes down.** Ivan's explicit warning. Upstream
handles it in [`05-deployment-and-automation/scripts/data_repo.py`](../05-deployment-and-automation/scripts/data_repo.py)
with a triple fallback: **yfinance → Stooq → FRED**.

**That Stooq middle tier is currently broken — verified 2026-08-23.** Stooq now serves a
JavaScript proof-of-work bot challenge instead of CSV on `https://stooq.com/q/d/l/`, for
every symbol format tried (`aapl.us`, `AAPL.US`, `aapl`, `^spx`, `spy.us`). This is a
server-side change at Stooq, not a client problem — `curl` with a browser User-Agent gets
the same challenge page. So `pdr.get_data_stooq(...)` raises `RemoteDataError` regardless
of client version. Practical effect:

- **Indexes** still have a working fallback — FRED tier 3 is fine (`SP500`, `NASDAQ100`,
  `DJIA`, `VIXCLS` all verified returning data).
- **Individual tickers** effectively have **no fallback**, since FRED carries no per-stock
  OHLCV. If Yahoo is down mid-homework, cache what you have and wait, or substitute
  another provider (Alpha Vantage / Tiingo free tiers).

Worth raising in Slack — it affects everyone running Module 5 as written.

**Pin `pandas-datareader==0.10.0`.** Version 0.11 **removed Stooq support entirely**, so
`pdr.get_data_stooq(...)` raises `AttributeError` rather than even attempting the call.
Already pinned in [`environment.yml`](environment.yml).

**Keep pandas below 3.0.** The notebooks are written for pandas 2.x and Colab ships 2.x.
pandas 3.0 changes copy-on-write semantics and drops APIs the lectures use. A bare
`conda env create` resolves to pandas 3.0.5 if you let it, so the pin matters.

**`pd.read_html` on Wikipedia returns HTTP 403** without a browser User-Agent. Fetch with
`requests` and a UA header, then hand the HTML to `read_html`:

```python
import requests, io, pandas as pd
h = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
r = requests.get(url, headers=h, timeout=30); r.raise_for_status()
df = pd.read_html(io.StringIO(r.text))[0]
```

**Financial-statement data arrives 1–2 months after quarter close.** Ivan flagged this as
the subtle trap: joining it naively on report date leaks future information into the
training set. Watch for lookahead bias.

## What's new in 2026

- All homeworks and materials refreshed with current market numbers — 2025's answers
  will not carry over.
- Heavier AI emphasis, beyond coding assistance: data generation and agentic workflows.
  Ivan asked participants to share what works.
- Most-requested project theme this year was an **AI agent / investment recommendation
  system** — a shift from prior cohorts.
- Streamlined content, aimed at raising that 8% completion rate.

## Prerequisites, honestly

No finance or trading background needed — Ivan builds it up from scratch, and Alexey
confirmed he followed it without one.

You do need: comfort in **Python** (loops, functions, Pandas — no OOP, no exotic
features; the reference project is under 1,000 lines), and enough **ML** to train and
run one scikit-learn model. If you want the ML grounding first,
[ML Zoomcamp](http://mlzoomcamp.com) covers it.

Fastest self-assessment: open a previous year's notebook, run it, and see whether it
makes sense. All 2024/2025 materials are in this repo.

Budget **$10–20/month** for an AI coding assistant. Not required — the free tiers work
since most files are self-contained.

---

## Local setup

```bash
conda env create -f my-notes/environment.yml
conda activate stock-markets-analytics
python -m ipykernel install --user --name stock-markets-analytics
```

Colab stays primary for live sessions — see [`01-intro/COLAB_SETUP.md`](01-intro/COLAB_SETUP.md).

Pull each week's new material:

```bash
git fetch upstream && git merge --ff-only upstream/main
```
