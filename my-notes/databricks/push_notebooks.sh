#!/usr/bin/env bash
# Push coursework .ipynb notebooks to the Databricks workspace so they can be
# opened and run interactively in the UI.
#
# Why this exists alongside the Asset Bundle: the bundle syncs its own root
# (bundle/) and nothing else, which is correct — that directory is
# infrastructure, and `bundle deploy` owns its lifecycle. Coursework notebooks
# live in my-notes/<module>/ and have a different lifecycle: they change every
# week, they are not deployed as jobs, and they should not be destroyed by a
# bundle operation. So they are pushed here instead.
#
#   ./push_notebooks.sh                     # every my-notes/**/*.ipynb
#   ./push_notebooks.sh ../01-intro/homework1.ipynb
#
# Lands them in /Users/<you>/sma-zoomcamp/ — the same folder run_notebook.sh
# uses for ad hoc runs.
set -euo pipefail

: "${DATABRICKS_CONFIG_PROFILE:=free-edition}"
export DATABRICKS_CONFIG_PROFILE

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolve the calling identity rather than hardcoding a service-principal id —
# this repo is public.
ME="$(databricks current-user me --output json \
      | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d.get("userName") or d["emails"][0]["value"])')"
DEST="/Users/$ME/sma-zoomcamp"

if [ "$#" -gt 0 ]; then
  FILES=("$@")
else
  # Default: every notebook under my-notes/, excluding the gitignored archive.
  IFS=$'\n' read -r -d '' -a FILES < <(
    find "$HERE/.." -name '*.ipynb' -not -path '*/archive/*' \
                    -not -path '*/.ipynb_checkpoints/*' | sort && printf '\0'
  )
fi

if [ "${#FILES[@]}" -eq 0 ]; then
  echo "no notebooks found"; exit 0
fi

echo "==> pushing ${#FILES[@]} notebook(s) to $DEST"
databricks workspace mkdirs "$DEST" 2>/dev/null || true

for f in "${FILES[@]}"; do
  [ -f "$f" ] || { echo "    skip (missing): $f"; continue; }
  name="$(basename "${f%.*}")"
  # --format JUPYTER, and NO --language: for a .ipynb the language comes from
  # the notebook's own metadata.language_info. Passing --language here is what
  # makes the import fail.
  databricks workspace import "$DEST/$name" --file "$f" \
    --format JUPYTER --overwrite
  echo "    $(basename "$f")  ->  $DEST/$name"
done

HOST="$(databricks auth describe 2>/dev/null | sed -n 's/^Host: *//p' | head -1)"
echo
echo "==> open in the UI: ${HOST}/#workspace${DEST}"
databricks workspace list "$DEST" --output json \
  | python3 -c 'import sys,json; [print("    "+o["path"]) for o in json.load(sys.stdin)]'
