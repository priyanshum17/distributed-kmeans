#!/usr/bin/env bash
set -euo pipefail
for n in 1 2 5; do
  echo -e "\n=== Scaling to $n workers ==="
  docker compose up -d --scale spark-worker=$n
  ./scripts/run_cluster.sh --k 8 --maxIter 20 --parts 16
done
