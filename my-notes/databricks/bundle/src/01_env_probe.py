# Databricks notebook source
import json, sys, subprocess, importlib, platform
R = {"python": platform.python_version(), "base": {}, "installs": {}, "data": {}}

for m in ["pandas","numpy","sklearn","scipy","matplotlib","plotly","seaborn","pyspark"]:
    try: R["base"][m] = getattr(importlib.import_module(m), "__version__", "present")
    except Exception: R["base"][m] = "MISSING"

def pip(*p):
    r = subprocess.run([sys.executable,"-m","pip","install","-q",*p],
                       capture_output=True, text=True, timeout=1800)
    return r.returncode

# The heavy Module 3 deps, plus the small missing ones
for pkgs in (["tensorflow"], ["keras"], ["beautifulsoup4"], ["tqdm"], ["lxml"], ["html5lib"]):
    try: R["installs"]["+".join(pkgs)] = pip(*pkgs)
    except Exception as e: R["installs"]["+".join(pkgs)] = f"EXC {type(e).__name__}"

importlib.invalidate_caches()
for m in ["tensorflow","keras","bs4","tqdm"]:
    try: R["installs"][f"import_{m}"] = getattr(importlib.import_module(m), "__version__", "present")
    except Exception as e: R["installs"][f"import_{m}"] = f"FAILED {type(e).__name__}"

# Does the Stooq CSV endpoint work from here? It is JS-challenged from a home IP.
try:
    import requests
    t = requests.get("https://stooq.com/q/d/l/?s=aapl.us&i=d", timeout=30).text
    R["data"]["stooq_csv"] = ("OK csv" if t.startswith("Date,Open") else
                              "JS_CHALLENGE" if "requires JavaScript" in t else f"other: {t[:60]}")
except Exception as e:
    R["data"]["stooq_csv"] = f"FAILED {type(e).__name__}"

# pandas_datareader's Stooq reader (what data_repo.py actually calls)
try:
    subprocess.run([sys.executable,"-m","pip","install","-q","pandas-datareader==0.10.0"], timeout=600)
    importlib.invalidate_caches()
    import pandas_datareader as pdr
    R["data"]["pdr_get_data_stooq"] = f"{len(pdr.get_data_stooq('AAPL.US'))} rows"
except Exception as e:
    R["data"]["pdr_get_data_stooq"] = f"FAILED {type(e).__name__}: {str(e)[:90]}"

# gdown is how Modules 3-5 load their prebuilt datasets
try:
    subprocess.run([sys.executable,"-m","pip","install","-q","gdown"], timeout=600)
    importlib.invalidate_caches()
    import gdown, os
    out = gdown.download(id="1IqZpTiG1eBftYeOKZbP7VmYyHkNqUZTC",
                         output="/tmp/gdown_probe.bin", quiet=True)
    R["data"]["gdown"] = f"OK {os.path.getsize(out)} bytes" if out else "returned None"
except Exception as e:
    R["data"]["gdown"] = f"FAILED {type(e).__name__}: {str(e)[:90]}"

# Unity Catalog volume write — the plan-B path for pre-staged data
try:
    spark.sql("CREATE SCHEMA IF NOT EXISTS workspace.sma")
    spark.sql("CREATE VOLUME IF NOT EXISTS workspace.sma.data")
    with open("/Volumes/workspace/sma/data/_probe.txt","w") as f: f.write("ok")
    R["data"]["uc_volume_write"] = "OK /Volumes/workspace/sma/data"
except Exception as e:
    R["data"]["uc_volume_write"] = f"FAILED {type(e).__name__}: {str(e)[:90]}"

dbutils.notebook.exit(json.dumps(R))
