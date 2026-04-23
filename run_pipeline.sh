#!/usr/bin/env bash
set -e

export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}."

if [ "$#" -ge 1 ]; then
  CATEGORY="$1"
else
  CATEGORY="lua_gao"
fi

python -m sources.scraper.scraper "$CATEGORY"
python -m sources.dlt.dlt_ingestion
python -m sources.utils.transform_to_silver
python -m sources.utils.analysis
