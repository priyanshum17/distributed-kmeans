#!/usr/bin/env python
import os
import argparse, time, pathlib, socket, json
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.clustering import KMeans
from utils import dataset_stats, write_metrics

def load_susy(spark, path, parts, fraction):
    df = spark.read.option("inferSchema", "true").csv(str(path)).repartition(parts)
    if 0 < fraction < 1.0:
        df = df.sample(withReplacement=False, fraction=fraction, seed=42)
    vec = VectorAssembler(inputCols=df.columns[1:], outputCol="features")
    return vec.transform(df).select("features")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--k", type=int, default=8)
    p.add_argument("--maxIter", type=int, default=20)
    p.add_argument("--parts", type=int, default=16)
    p.add_argument("--fraction", type=float, default=1.0, help="Fraction of dataset to use (0.0–1.0)")
    p.add_argument("--tag", default="run")
    args = p.parse_args()

    spark = SparkSession.builder.appName("Distributed-KMeans-SUSY").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    path = pathlib.Path("/workspace/data/SUSY.csv")
    if not path.exists():
        raise FileNotFoundError(f"SUSY.csv missing at {path}")

    data = load_susy(spark, path, args.parts, args.fraction)
    row_count = data.count()
    feature_count = len(data.schema["features"].metadata["ml_attr"]["attrs"]["numeric"])
    approx_size_gb = row_count * feature_count * 8 / 1e9  # 8 bytes per float

    print(
        f"### Loaded {row_count:,} rows, {feature_count} features "
        f"({approx_size_gb:.2f} GB) in {args.parts} partitions"
    )

    t0 = time.time()
    model = KMeans(k=args.k, maxIter=args.maxIter, seed=42).fit(data)
    dt = round(time.time() - t0, 2)
    cost = model.summary.trainingCost
    sizes = list(model.summary.clusterSizes)

    print(f"### Completed in {dt}s | WSSSE={cost:,.0f} | clusterSizes={sizes}")

    payload = {
        "tag": args.tag,
        "hostname": socket.gethostname(),
        "workers": int(os.getenv("WORKER_COUNT", "1")),
        "k": args.k,
        "maxIter": args.maxIter,
        "parts": args.parts,
        "rows": row_count,
        "features": feature_count,
        "size_gb": round(approx_size_gb, 2),
        "fraction": args.fraction,
        "train_sec": dt,
        "wssse": cost,
        "cluster_sizes": sizes,
    }
    write_metrics(pathlib.Path("/workspace/results"), payload)
    spark.stop()

if __name__ == "__main__":
    main()
