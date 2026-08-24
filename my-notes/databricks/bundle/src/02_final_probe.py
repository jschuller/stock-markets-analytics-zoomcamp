# Databricks notebook source
import json, sys, subprocess, importlib, traceback, os
R = {"gdown": {}, "pandas_upgrade": {}, "tensorflow": {}, "storage": {}}

def pip(*p, timeout=1800):
    r = subprocess.run([sys.executable,"-m","pip","install","-q",*p],
                       capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stderr or r.stdout or "")[-400:]

# ---- 1. gdown with the REAL file IDs the course uses (Modules 3/4/5)
pip("gdown"); importlib.invalidate_caches()
import gdown
for fid in ["1kNWWPi49td0EZhmi6LzNCa2ssC5IUxHP", "1mb0ae2M5AouSDlqcUnIwaHq7avwGNrmB"]:
    try:
        out = gdown.download(f"https://drive.google.com/file/d/{fid}/view?usp=sharing",
                             output=f"/tmp/{fid}.bin", fuzzy=True, quiet=True)
        R["gdown"][fid] = f"OK {os.path.getsize(out):,} bytes" if out else "returned None"
    except Exception as e:
        R["gdown"][fid] = f"FAILED {type(e).__name__}: {str(e)[:100]}"

# ---- 2. can we get pandas 2.x on top of the 1.5.3 base?
import pandas as _pd
R["pandas_upgrade"]["before"] = _pd.__version__
rc, msg = pip("pandas>=2.2,<3")
R["pandas_upgrade"]["pip_rc"] = rc
if rc != 0:
    R["pandas_upgrade"]["pip_msg"] = msg[-250:]

# ---- 3. tensorflow: capture the real import error (Module 3 DNN section)
rc, msg = pip("tensorflow")
R["tensorflow"]["pip_rc"] = rc
try:
    import tensorflow as tf
    R["tensorflow"]["import"] = tf.__version__
except Exception:
    R["tensorflow"]["import"] = traceback.format_exc()[-700:]

# ---- 4. where can this service principal actually write?
# Resolve the current identity rather than hardcoding it — this notebook is
# committed to a public fork.
_me = spark.sql("SELECT current_user()").collect()[0][0]
for label, path in [("tmp", "/tmp/probe.txt"),
                    ("workspace_files", f"/Workspace/Users/{_me}/probe.txt"),
                    ("uc_volume", "/Volumes/workspace/default/probe.txt")]:
    try:
        with open(path, "w") as f: f.write("ok")
        R["storage"][label] = "WRITABLE"
        os.remove(path)
    except Exception as e:
        R["storage"][label] = f"NO: {type(e).__name__}: {str(e)[:70]}"
try:
    R["storage"]["catalogs"] = [r[0] for r in spark.sql("SHOW CATALOGS").collect()]
    R["storage"]["schemas_workspace"] = [r[0] for r in spark.sql("SHOW SCHEMAS IN workspace").collect()]
except Exception as e:
    R["storage"]["catalogs"] = f"FAILED {type(e).__name__}"

dbutils.notebook.exit(json.dumps(R))
