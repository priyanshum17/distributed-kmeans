#!/usr/bin/env bash
set -euo pipefail

echo "Running Spark job on cluster..."

docker compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.jars.ivy=/tmp/.ivy2 \
  /workspace/src/kmeans_job.py "$@"
