# Databricks notebook source
# MAGIC %md
# MAGIC # 00 — Egress & Library Probe (Databricks Free Edition)
# MAGIC
# MAGIC Answers in one run whether this workspace can run the SMA Zoomcamp notebooks:
# MAGIC DNS/HTTPS reachability per domain, which deps are preinstalled, which install,
# MAGIC and whether real course calls work.
# MAGIC
# MAGIC Results come back via `dbutils.notebook.exit(json)` so they are readable from
# MAGIC the Jobs API — `print()` output is not. Every step is guarded so one failure
# MAGIC (notably TA-Lib, which wraps a C library) cannot abort the run.

# COMMAND ----------

import json, socket, ssl, sys, subprocess, importlib, platform

R = {"python": platform.python_version(), "egress": {}, "preinstalled": {},
     "pip_install": {}, "post_install": {}, "course_calls": {}}

# ---------------------------------------------------------------- 1. egress
# Free Edition blocks at DNS ("Temporary failure in name resolution"),
# so separating DNS from connect distinguishes "blocked" from "slow".
TARGETS = [
    ("pypi",        "pypi.org",                 "/simple/"),
    ("pypi_files",  "files.pythonhosted.org",   "/"),
    ("yahoo1",      "query1.finance.yahoo.com", "/v8/finance/chart/AAPL"),
    ("yahoo2",      "query2.finance.yahoo.com", "/v8/finance/chart/AAPL"),
    ("fred",        "fred.stlouisfed.org",      "/"),
    ("stooq",       "stooq.com",                "/"),
    ("gdrive",      "drive.google.com",         "/"),
    ("wikipedia",   "en.wikipedia.org",         "/wiki/Main_Page"),
    ("cmarketcap",  "companiesmarketcap.com",   "/"),
    ("control",     "example.com",              "/"),
]

for key, host, path in TARGETS:
    try:
        ip = socket.gethostbyname(host)
    except Exception as e:
        R["egress"][key] = f"DNS_BLOCKED: {type(e).__name__}"
        continue
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=15) as sk:
            with ctx.wrap_socket(sk, server_hostname=host) as s:
                s.send(f"HEAD {path} HTTP/1.1\r\nHost: {host}\r\n"
                       f"User-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n".encode())
                line = s.recv(200).decode(errors="replace").split("\r\n")[0]
        R["egress"][key] = f"OK: {line.strip()}"
    except Exception as e:
        R["egress"][key] = f"NET_BLOCKED: {type(e).__name__}"

# --------------------------------------------------------- 2. preinstalled
DEPS = ["pandas", "numpy", "matplotlib", "seaborn", "plotly", "sklearn", "scipy",
        "requests", "bs4", "statsmodels", "joblib", "tqdm", "pyspark",
        "yfinance", "pandas_datareader", "gdown", "eurostat",
        "talib", "tensorflow", "keras", "pmdarima"]
for m in DEPS:
    try:
        R["preinstalled"][m] = getattr(importlib.import_module(m), "__version__", "present")
    except Exception as e:
        R["preinstalled"][m] = f"MISSING ({type(e).__name__})"

# ------------------------------------------------------------ 3. pip installs
# subprocess, not %pip: the magic raises CalledProcessError and kills the run.
# TA-Lib is expected to fail — no apt-get on serverless for the C library.
def pip(*pkgs):
    p = subprocess.run([sys.executable, "-m", "pip", "install", "-q", *pkgs],
                       capture_output=True, text=True, timeout=900)
    tail = (p.stderr or p.stdout or "").strip().splitlines()
    return {"rc": p.returncode, "msg": (tail[-1][:200] if tail else "ok")}

for pkgs in (["yfinance"], ["pandas-datareader==0.10.0"], ["gdown"],
             ["ta-lib-binary"], ["TA-Lib"], ["pmdarima"], ["eurostat"]):
    try:
        R["pip_install"]["+".join(pkgs)] = pip(*pkgs)
    except Exception as e:
        R["pip_install"]["+".join(pkgs)] = {"rc": -1, "msg": f"{type(e).__name__}: {e}"[:200]}

importlib.invalidate_caches()
for m in ["yfinance", "pandas_datareader", "gdown", "talib", "pmdarima", "eurostat"]:
    try:
        R["post_install"][m] = getattr(importlib.import_module(m), "__version__", "present")
    except Exception as e:
        R["post_install"][m] = f"FAILED ({type(e).__name__})"

# ------------------------------------------------------- 4. real course calls
try:
    import yfinance as yf
    df = yf.download("AAPL", period="5d", progress=False, auto_adjust=True)
    R["course_calls"]["yfinance_AAPL"] = f"{len(df)} rows"
except Exception as e:
    R["course_calls"]["yfinance_AAPL"] = f"FAILED {type(e).__name__}: {str(e)[:120]}"

try:
    import pandas_datareader as pdr
    d = pdr.DataReader("CPILFESL", "fred", start="2024-01-01")
    R["course_calls"]["fred_CPILFESL"] = f"{len(d)} rows"
except Exception as e:
    R["course_calls"]["fred_CPILFESL"] = f"FAILED {type(e).__name__}: {str(e)[:120]}"

try:
    import pandas as pd, requests, io
    h = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
    rr = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies",
                      headers=h, timeout=30)
    R["course_calls"]["wikipedia_read_html"] = f"{len(pd.read_html(io.StringIO(rr.text))[0])} rows"
except Exception as e:
    R["course_calls"]["wikipedia_read_html"] = f"FAILED {type(e).__name__}: {str(e)[:120]}"

dbutils.notebook.exit(json.dumps(R))
