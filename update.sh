#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
YEAR=${1:-2026}
MONTH=${2:-6}
python3 pipeline/fetch.py --year "$YEAR" --month "$MONTH"
python3 pipeline/aggregate.py
python3 pipeline/build.py
echo "done. site is in output/"
