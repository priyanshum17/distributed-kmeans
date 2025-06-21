#!/usr/bin/env bash
set -euo pipefail
for W in 1 2 5; do
  scripts/run_once.sh "$W" --k 8 --maxIter 20 --parts 16
done
