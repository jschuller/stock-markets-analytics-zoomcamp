#!/usr/bin/env bash
# Upload a local notebook, run it on serverless, wait, and print its JSON result.
#
# Collapses the four-step CLI cycle (import -> jobs submit -> poll -> get-run-output)
# into one command. The notebook must end with dbutils.notebook.exit(json.dumps(...)) —
# print() output does not come back through the Jobs API.
#
#   ./run_notebook.sh 00_egress_probe.py [client_version]
#
set -euo pipefail

: "${DATABRICKS_CONFIG_PROFILE:=free-edition}"
export DATABRICKS_CONFIG_PROFILE

FILE="${1:?usage: run_notebook.sh <local.py> [client_version]}"
CLIENT="${2:-}"
NAME="$(basename "$FILE" .py)"

# Resolve the calling identity instead of hardcoding a service-principal id.
ME="$(databricks current-user me --output json | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("userName") or d["emails"][0]["value"])')"
REMOTE="/Users/$ME/sma-zoomcamp/$NAME"

echo "==> importing $FILE -> $REMOTE"
databricks workspace mkdirs "/Users/$ME/sma-zoomcamp" 2>/dev/null || true
databricks workspace import "$REMOTE" --file "$FILE" \
  --format SOURCE --language PYTHON --overwrite

if [ -n "$CLIENT" ]; then
  SPEC=",\"environments\":[{\"environment_key\":\"default\",\"spec\":{\"client\":\"$CLIENT\"}}]"
  ENVKEY=",\"environment_key\":\"default\""
else
  SPEC=""; ENVKEY=""
fi

echo "==> submitting serverless run${CLIENT:+ (client $CLIENT)}"
RUN_ID="$(databricks jobs submit --no-wait --json \
  "{\"run_name\":\"$NAME\",\"tasks\":[{\"task_key\":\"t\",\"notebook_task\":{\"notebook_path\":\"$REMOTE\"}$ENVKEY}]$SPEC}" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["run_id"])')"
echo "    run_id=$RUN_ID"

echo "==> waiting"
for _ in $(seq 1 90); do
  STATE="$(databricks jobs get-run "$RUN_ID" --output json \
    | python3 -c 'import sys,json; print((json.load(sys.stdin).get("status") or {}).get("state","?"))')"
  printf '\r    %s   ' "$STATE"
  case "$STATE" in TERMINATED|INTERNAL_ERROR) break ;; esac
  sleep 15
done
echo

TASK_ID="$(databricks jobs get-run "$RUN_ID" --output json \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["tasks"][0]["run_id"])')"

echo "==> result"
databricks jobs get-run-output "$TASK_ID" --output json | python3 -c '
import sys, json
d = json.loads(sys.stdin.read())
if d.get("error"):
    print("ERROR:", d["error"][:600])
out = (d.get("notebook_output") or {}).get("result")
if out:
    try:    print(json.dumps(json.loads(out), indent=2))
    except Exception: print(out)
elif not d.get("error"):
    print("(no notebook_output — did the notebook call dbutils.notebook.exit?)")
'
