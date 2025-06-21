# 📦 INSTALLATION.md

## 🚀 Distributed K-Means with Apache Spark

This guide walks you through the full setup and execution of a distributed K-Means clustering pipeline using:

- Apache Spark (via Bitnami Docker images)
- Docker Compose (multi-container setup)
- The SUSY dataset (2.4 GB from UCI ML repository)

## 🛠️ Requirements

Before starting, ensure the following are installed:

| Tool           | Version        |
|----------------|----------------|
| Docker         | ≥ 20.10        |
| Docker Compose | ≥ v2.0         |
| Python         | ≥ 3.8 (for local runs) |
| wget / curl    | optional (for dataset download) |

---

## 📁 Project Structure

```

.
├── docker-compose.yml
├── Dockerfile
├── src/
│   ├── kmeans\_job.py         # Main KMeans runner
│   └── utils.py              # Dataset stat & logging tools
├── data/
│   └── SUSY.csv              # Dataset file (\~2.4 GB)
├── results/                  # Output logs + metrics
├── scripts/
│   ├── run\_once.sh           # Runs one cluster config
│   ├── run\_cluster.sh        # Runs all worker configs
│   ├── run\_local.sh          # Run KMeans locally (no Spark)
│   └── cleanup.sh            # Teardown & cleanup

````



## 🧾 Step-by-Step Installation

### 1. Clone or Prepare the Project

```bash
git clone <your-repo-url>
cd <project-dir>
````

---

### 2. Download the SUSY Dataset

You can either download manually or let the script fetch it:

```bash
wget https://archive.ics.uci.edu/ml/machine-learning-databases/00279/SUSY.csv.gz -P data/
gunzip data/SUSY.csv.gz
```

Ensure the resulting path is: `data/SUSY.csv`.

---

### 3. Build Docker Images

```bash
docker compose build
```

This compiles the Spark master and worker containers based on your Dockerfile.

---

### 4. Start Cluster (e.g., 2 Workers)

```bash
WORKERS=2 docker compose up -d --scale spark-worker=2
```

This starts the Spark master and 2 worker nodes in detached mode.

---

### 5. Run Distributed KMeans Job

```bash
docker compose exec spark-master spark-submit \
  --master spark://spark-master:7077 \
  --conf spark.jars.ivy=/tmp/.ivy2 \
  /workspace/src/kmeans_job.py \
  --k 8 --maxIter 20 --parts 16 --fraction 1.0 --tag run_2workers
```

This uses the full dataset and saves metrics to `results/`.

---

## 🧪 Benchmark: Run at 1/2/5 Workers

To benchmark all configs with a single script:

```bash
./scripts/run_cluster.sh
```

To run a single config:

```bash
./scripts/run_once.sh 5 --k 8 --maxIter 20 --parts 16 --fraction 0.5
```

---

## 🧼 Cleanup

```bash
./scripts/cleanup.sh
```

This stops and deletes all containers and volumes used in the test.

---

## 📊 Output

All job metrics are saved in structured JSON format in the `results/` directory:

```
results/
├── run_1w_20250621_2015.json
├── run_2w_20250621_2041.json
└── ...
```

Each file contains:

* Row count
* Feature count
* Elapsed time
* Clustering cost (WSSSE)
* Cluster size distribution

---

## 🖥️ Spark UI

Access the live Spark job dashboard via:

```
http://localhost:18081
```

Useful for debugging, executor tracking, and job visualization.


✅ Success Criteria

* Can run on 8 GB RAM machine (using `--fraction 0.5`)
* Full data = 5M rows, \~2.39 GB
* Each run logs performance + cluster metrics

