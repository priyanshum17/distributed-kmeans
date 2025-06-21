#!/usr/bin/env bash
set -euo pipefail

# Usage: scripts/run_once.sh <num_workers> [spark & job args …]
# Example: scripts/run_once.sh 2 --k 10 --maxIter 30

W=$1; shift
export WORKER_COUNT="$W"

echo -e "\n▶ scaling cluster to $W worker(s)…"
docker compose up -d --scale spark-worker="$W"

# give them a heartbeat to register
sleep 5

echo -e "\n🚀  submitting Spark job…"
docker compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.jars.ivy=/tmp/.ivy2 \
  /workspace/src/kmeans_job.py --tag "run_${W}w" "$@"

# -----------------------------------------------------------------------------
# NEW: tear the workers right back down so their JVMs free the RAM
# -----------------------------------------------------------------------------
echo -e "\n🧹  stopping workers…"
docker compose rm -fsv spark-worker   # removes all spark-worker containers
