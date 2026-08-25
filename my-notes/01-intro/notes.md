# Stock Markets Analytics Zoomcamp 2025
**Course by Ivan (Business Intelligence Analyst at Google) and PythonInvest.com**

## Table of Contents
- [Course Resources](#course-resources)
- [Understanding Data-Driven Decisions](#understanding-data-driven-decisions)
- [Let's Start with Macroeconomics (FRED)](#lets-start-with-macroeconomics-and-the-first-data-source-fred)
- [Inflation - "Core CPI"](#do-i-save-faster-than-inflation-core-cpi-us-is-28-mar25)
- [Saving Options](#saving-money-with-cash-interest-may-bring-you-2-325-interest-in-2025)
- [Fed Funds Rate and Risk-Free Returns](#if-you-start-investing-in-the-us-the-most-important-rate-is-fed-funds-rate)
- [S&P 500 and Investment Benchmarks](#look-at-index-growth-for-a-benchmark-when-investing-in-stocks)
- [Rule of 72](#rule-of-72-concept-how-quickly-can-you-double-your-real-capital)
- [Long-term Success of a Profitable Strategy](#the-long-term-success-of-a-profitable-strategy-is--to-be-higher-than-a-benchmark)
- [Risk-Reward Curve by Asset Class](#concept-generic-risk-reward-curve-by-asset-class)
- [Select Your Risk](#select-your-risk-to-define-one-of-the-major-characteristics-of-future-strategy)
- [Google Colab Setup](#google-colab-is-the-main-environment-for-the-course)
- [Data Sources For Stocks](#data-sources-for-stocks)
- [Stock Screeners](#feel-the-data-start-from-stocks-screener-tradingview-example)
- [OHLCV Data from Yahoo Finance](#main-data-source-ohlcv-data-from-yahoo-finance)
- [Paid Data Sources](#paid-data-polygonio-alpha-vantage-etc)
- [Macroeconomic Stats](#macroeconomics-stats)
- [Financial Reporting for Public Companies](#financial-reporting-for-public-companies)
- [Web Scraping](#web-scraping)
- [Alternative Data Sources](#other-related-data-sources-and-alternative-data)


## Course Resources
- [YouTube Recording](https://youtu.be/2zlv2nU7g58)
- [GitHub Repository](https://github.com/DataTalksClub/stock-markets-analytics-zoomcamp)
- [Presentation Slides](https://docs.google.com/presentation/d/e/2PACX-1vR_vfIYCpGhgsR_jef9uo5YdKbg68LGO6pZR5kRSrxDTHNRujKgPb7r9K1U1SM9yOFJlC7OoDAAjKHG/pub?start=false&loop=false&delayms=10000&slide=id.g2c7aa6c5021_0_22)


## Understanding Data-Driven Decisions

### Intro: Understanding Data-Driven Decisions

Making informed choices for personal savings and investments

## Let's Start with Macroeconomics and the First Data Source (FRED)

**Real potential GDP** is the CBO's estimate of the output the economy could produce if its capital and labor resources were used at a high rate. This data is adjusted to remove the effects of inflation. The prediction is stable: +2-2.3% YoY last 5 years

Resources:
- [FRED GDP Documentation](https://data.nasdaq.com/data/FRED-federal-reserve-economic-data/documentation)
- [FRED GDP Series](https://fred.stlouisfed.org/series/GDPPOT)
- [Global Markets Tariff Impact](https://simplywall.st/article/beyond-the-us-global-markets-after-yet-another-tariff-update)
- [PythonInvest Dashboard](https://pythoninvest.com/long-read/2024-year-wrap-and-automatic-dashboard)

## Do I Save Faster than Inflation? "Core CPI" (US) is 2.8% (Mar'25)

The "**Consumer Price Index for All Urban Consumers: All Items Less Food & Energy**" is an aggregate of prices paid by urban consumers for a typical basket of goods, excluding food and energy. This measurement, known as "**Core CPI**", is widely used by economists because food and energy have very volatile prices. "**Core CPI**" declined from 3.7% on Feb'24 to 2.8% on Mar'25

Resources:
- [FRED CPI Series](https://fred.stlouisfed.org/series/CPILFESL)
- [10-Year Inflation Expectations](https://fred.stlouisfed.org/series/T10YIE)
- [Constructing Real Interest Rates](https://fredblog.stlouisfed.org/2022/05/constructing-ex-ante-real-interest-rates-on-fred/)

## Saving Money with Cash Interest May Bring You 2–3.25% Interest in 2025, Slightly Higher than Inflation (2.2%–2.8%)

- Currency: USD or EUR (harder when income vs. investments in different currencies)
- Inflation in Ireland is 2.2% and in the US is 2.8% (Mar'25)
- Strategy 1: Do nothing (0% interest, full liquidity)
- Strategy 2: Bank Savings Accounts: For example, the traditional bank interest rate in Ireland is 2–3% in EUR (comparison). It has a money protection scheme.
- Strategy 3: Money Service Businesses (MSBs) offer in April 2025: 2.24% (Wise, down from 3.67% last year) in EUR and 4.08% in USD (Wise, down from 5.05% last year)
- Strategy 4: Broker Accounts:
  - (NL) DEGIRO pays 0% interest on uninvested cash, regardless of currency
  - (DE) Trade Republic bank/broker offers 3-3.25% interest on uninvested EUR cash (down from 4% last year). Trade Republic is a licensed German bank with deposit protection up to €100,000
  - (US) Interactive Brokers offers up to 4.1% in USD (down from 4.83% last year), and up to 2.7% (down from 3.45%) in EUR (for cash balances above $10,000/€10,000; 0% for the first $10,000/€10,000)

Resources:
- [Irish Inflation Calculator](https://visual.cso.ie/?body=entity/cpicalculator)
- [Irish Savings Accounts Comparison](https://www.bonkers.ie/compare-savings-accounts/your-results/)
- [Wise Interest Rates](https://wise.com/gb/interest/)
- [Interactive Brokers Interest Rates](https://www.interactivebrokers.com/en/accounts/fees/pricing-interest-rates.php)

## If You Start Investing (in the US), the Most Important Rate is Fed Funds Rate. Generally You Can Get Slightly Higher Rates of Return on Debt Instruments (4-5% in USD in Apr'25)

The federal funds rate is the interest rate at which depository institutions trade federal funds (balances held at Federal Reserve Banks) with each other overnight. The latest value is 4.33%, down from 5.33% one year ago.

- Fed Funds Rate is 4.33% (Mar'25), which is higher than cash rate (2-3%)
- There is ongoing debate about future Fed rate changes, with markets expecting two rate cuts in 2025
- U.S. Treasury securities are considered the lowest risk ("risk-free rate" - typically it is a 3 month t-bill (4.21%) for short-term and 10Y treasury yield for long-term (4.29% in Apr'2025)). The Treasury yield curve (1 month to 30 years) is available daily. It can be reconstructed from FRED time series, like DGS1 (1MO) to DGS30 (30Y). Longer-term bonds usually offer higher yields, but sometimes the yield curve inverts (long-term yields < short-term)
- Bond yield = "(risk-free rate)" + premium for risk (e.g., default). Corporate debt and riskier bonds can yield 5–7% or more in 2025, but with higher risk. Data: Moody's Corporate Bond Yield Averages series on FRED (AAA is 5.3%, BAA is 5.9%)

Resources:
- [FRED Fed Funds Rate](https://fred.stlouisfed.org/series/FEDFUNDS)
- [Fed Dot Plot](https://www.bondsavvy.com/fixed-income-investments-blog/fed-dot-plot)
- [Treasury Yield Curve](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2025)
- [1-Year Treasury Constant Maturity Rate](https://fred.stlouisfed.org/series/DGS1) — `DGS1` is the **1-Year** rate; the 1-month series is [`DGS1MO`](https://fred.stlouisfed.org/series/DGS1MO)
- [30-Year Treasury Constant Maturity Rate](https://fred.stlouisfed.org/series/DGS30)
- [Inverted Yield Curve Explanation](https://www.investopedia.com/terms/i/invertedyieldcurve.asp)
- [Moody's Seasoned Aaa Corporate Bond Yield](https://fred.stlouisfed.org/series/AAA)
- [Moody's Seasoned Baa Corporate Bond Yield](https://fred.stlouisfed.org/series/BAA)

## Look at Index Growth for a Benchmark When Investing in Stocks

The S&P 500 Index tracks 500 leading U.S. companies, offering a snapshot of the country's stock market health. It is a go-to benchmark for investors and reflects a diverse range of sectors.

- Individual stocks can deliver a much wider range of returns-both positive and negative-due to higher risk - check the heatmap
- The S&P 500 is the most widely recognized benchmark for U.S. stock performance.
  - From 1990 to 2025, the average annual return (with dividends reinvested) was 10.31%; inflation-adjusted, the real return was 7.54% per year
  - The index's performance can vary widely from year to year. For example, in 2024 the S&P 500 gained 23.31%, but in 2025 it is down -6.06% (as of April 26, 2025)

Resources:
- [TradingView Stock Heatmap](https://www.tradingview.com/heatmap/stock/)

## The Long-term Success of a Profitable Strategy is ... to be Higher than a Benchmark

- Positive return: Ideally, any strategy should have a rolling positive return over any selected period of 6–12 months.
- 60/40 portfolio (equity/bonds): Historically, a global 60/40 portfolio has offered a lower yield, with recent baseline forecasts around 7.1% nominal (about 5% inflation-adjusted)
- S&P 500 (Equity): Over 30 years (1995–2024), the average annual return was 10.5% (about 6.3% inflation-adjusted). There are years with declines of ~20% to ~40% in a single year (link)
- Sweet spot: The "sweet spot" for long-term returns is typically in the range of 6–10% per year, net of inflation
- Warren Buffett (Berkshire Hathaway): Achieved a compound annual growth rate (CAGR) of ~20% over several decades (LINK)
- Renaissance Technologies (Medallion Fund): Achieved a reported CAGR of 66% (gross, before fees) over three decades, using highly leveraged quantitative strategies : LINK, LINK2

Resources:
- [Warren Buffett Returns](https://www.thestreet.com/investing/warren-buffett-berkshire-stock-investor)
- [Renaissance Technologies Returns](https://finance.yahoo.com/news/renaissance-technologies-returns-aum-ceo-145524029.html)
- [Medallion Fund Performance](https://www.cornell-capital.com/blog/2020/02/medallion-fund-the-ultimate-counterexample.html)
- [Risk-Return by Asset Class](https://www.ngpf.org/blog/investing/chart-explaining-investing-concept-risk-return/)
- [ARK Invest Big Ideas 2024](https://europe.ark-funds.com/wp-content/uploads/2024/02/ARK-Invest-Big-Ideas-2024.pdf)
- [Portfolio Optimization Articles](https://pythoninvest.com/long-read/practical-portfolio-optimisation)

## Select Your Risk to Define One of the Major "Characteristics" of Future Strategy

- Risk tolerance varies by investor: Each investor has a unique risk-return profile, shaped by their financial goals, investment horizon, and personal comfort with potential losses
- General guidance: It is often recommended to take more risk earlier in your investment journey (when you have less capital and a longer time horizon), and shift to more conservative strategies (such as bonds or diversified ETFs) as your capital grows or your goals near
- Defining success: Success is easier to measure relative to a benchmark-such as the risk-free rate or a passive investment portfolio. Common metrics include the Sharpe ratio, Sortino ratio, and maximum drawdown
- Data perspective: Because all markets are interconnected, you will likely need data on various asset classes and macroeconomic factors-even if your strategy focuses on a single asset type (for example, US large-cap stocks)

Google Colab is the recommended environment for the course due to:
- **Low barriers to start**: No installation required, runs in browser
- **Pre-installed libraries**: Python, data science, and ML libraries ready to use
- **Free GPU access**: Useful for training complex models
- **Easy sharing and saving**: Cloud-based with automatic saving
- **Dynamic visualizations**: Interactive graphs in the notebook

Alternatives include local Jupyter Notebooks with Anaconda or IDEs like VS Code.

Resources:
- [Google Colab](https://colab.research.google.com/)
- [Python Environment Setup](https://pythoninvest.com/long-read/python-environment)
- [Colab Pricing](https://colab.research.google.com/signup)

## Data Sources For Stocks

An extensive list of data sources for equities and more

→ OHLCV Data (Yahoo Finance, Polygon.io, Alpha Vantage)
→ Technical Indicators (covered in Module 2; available via Yahoo Finance, TA-Lib, or built-in libraries)
→ Macroeconomic Data (FRED, Pandas DataReader, Eurostat, etc.)
→ Financial Reporting (SEC EDGAR: 10-K, 10-Q, 8-K filings)
→ News (Polygon.io, NewsAPI)
→ Fundamental Data (Yahoo Finance, paid data providers, or web scraping)
→ Alternative Data (e.g., web traffic, YouTube revenue, satellite imagery, social media sentiment from X/Twitter, Reddit, Glassdoor, app usage, credit card data)
→ Events (Earnings calendars, ETF flows, activist investor actions, mergers & acquisitions, conference calls)

Resources:
- [Yahoo Finance Library](https://pypi.org/project/yfinance/)
- [Yahoo Finance Definitive Guide](https://www.qmr.ai/yfinance-library-the-definitive-guide/)
- [Yale Finance Lectures](https://zoo.cs.yale.edu/classes/cs458/lectures/yfinance.html)
- [Paid Data Services](https://polygon.io/pricing)
- [Financial News Summarization](https://pythoninvest.com/long-read/chatgpt-api-for-financial-news-summarization)

## Feel the Data: Start from Stocks Screener (TradingView Example)

- Many data providers offer free stock screeners; for example: https://www.tradingview.com/screener/
- Use "hand" rules to quickly filter stocks, such as: select all stocks in the S&P 500 with a dividend yield > 2%, revenue growth > 0% YoY, and a price-to-earnings growth (PEG) ratio < 0.5 and Upcoming earnings date =Next Week
- Here is the recent article on PythonInvest: https://pythoninvest.com/long-read/stock-screening-using-paid-data

## Macroeconomics Stats

Macro data provides big-picture insights into economic trends, guides policy decisions, influences market sentiment, evaluates sector performance, and offers global perspectives. Traders and investors rely on it to make informed decisions, anticipate market movements, and manage risks effectively.

- [US] FRED: Federal Reserve Economic Data
  - Many useful charts with explanations about time series.
  - Can be Daily, Weekly, Monthly, Quarterly, sometimes you need to transform the data (e.g. calculate growth period-over-period)
  - For other countries: usually freely available from statistical/government agencies in other countries
  - Can be downloaded via Pandas Data Reader (PDR), or Nasdaq's Quandl, or directly from the website (CSV)

- There are many other data sites with (global) macro stats, for example:
  - [US indicators - latest dates] https://tradingeconomics.com/united-states/indicators
  - [Global interest rates] https://tradingeconomics.com/country-list/interest-rate
  - [DE stock market and related] https://tradingeconomics.com/germany/stock-market

- Example macro stats
  - Financial markets benchmarks, consumer/investor behaviour, and economic cycle indicators
  - Other examples: unemployment, inflation, central bank interest rates (Fed, ECB, BoE, etc.), savings rate, debt rate
  - Asset benchmarks: gold/silver, commodities, crude oil, real estate indices, etc.
  - See the article on PythonInvest for 60+ macro indicators: https://pythoninvest.com/long-read/macro-indicators-affecting-stock-market

## RECAP

What we have learned?
- Financial rate of return
- Developing an investment idea
- Macroeconomic data and indicators
- Stock datasets and data sources
- Cheat sheet for starting a project

The instructor provides a step-by-step guide for developing a project:
1. Select a market or country (or go global)
2. Choose benchmarks for comparison
3. Select relevant macroeconomic indicators
4. Decide on dataset size (recommended: 25 years of data, >1 million rows)
5. Determine if fundamental data is needed
6. Consider including alternative data

IMPORTANT: Never "leak" data by including information that wasn't available at the prediction date.