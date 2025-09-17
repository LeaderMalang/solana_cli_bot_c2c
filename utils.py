# utils.py
from __future__ import annotations
import json
import csv
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import List

def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def ensure_csv(path: Path, headers: List[str]) -> None:
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)

def append_row(path: Path, row: List[str]) -> None:
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

def run_cmd(cmd: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

def log_error(errors_csv: Path, error_msg: str) -> None:
    """Append ISO-8601 UTC timestamp + error message to errors.csv, creating headers if needed."""
    ensure_csv(errors_csv, ["timestamp", "error"])
    ts = datetime.now(timezone.utc).isoformat()
    append_row(errors_csv, [ts, error_msg])
