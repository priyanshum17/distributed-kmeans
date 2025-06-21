#!/usr/bin/env bash
set -euo pipefail
echo "🧹  Stopping containers & removing volumes…"
docker compose down -v
