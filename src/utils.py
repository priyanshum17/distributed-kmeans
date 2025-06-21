import os, json, pathlib, time
from pyspark.sql import DataFrame


def dataset_stats(path: pathlib.Path, df: DataFrame, parts: int) -> dict:
    size_bytes = path.stat().st_size
    n_rows = df.count()
    n_features = len(df.columns) - 1  # first col = label
    return {
        "file": str(path),
        "size_gb": round(size_bytes / 1e9, 3),
        "rows": n_rows,
        "features": n_features,
        "spark_partitions": parts,
    }


def write_metrics(out_dir: pathlib.Path, payload: dict):
    out_dir.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    fname = out_dir / f"{payload['tag']}_{ts}.json"
    with fname.open("w") as f:
        json.dump(payload, f, indent=2)
    print(f"→ metrics saved to {fname}")
