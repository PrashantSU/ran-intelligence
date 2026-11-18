#!/usr/bin/env bash
set -euo pipefail

echo "Downloading private RAN runtime assets..."

python - <<'PY'
import os
import zipfile
from pathlib import Path
from huggingface_hub import hf_hub_download

token = os.environ.get("HF_TOKEN")
if not token:
    raise RuntimeError("HF_TOKEN environment variable is missing.")

archive = hf_hub_download(
    repo_id="PrashantSU/ran-intelligence-assets",
    repo_type="dataset",
    filename="ran_runtime_assets.zip",
    token=token,
)

with zipfile.ZipFile(archive, "r") as zf:
    zf.extractall(Path.cwd())

print("Runtime assets extracted successfully.")
PY

echo "Starting RAN Intelligence API..."
exec uvicorn ran_intelligence.api.app:app --host 0.0.0.0 --port "${PORT:-10000}"
