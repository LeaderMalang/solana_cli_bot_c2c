#!/usr/bin/env python3
"""balance_bot.py
Fetch a wallet's SOL balance on devnet via Solana CLI and log to CSV.
Logs errors to errors.csv.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
import csv
from typing import List

from utils import load_config, ensure_csv, append_row, run_cmd, log_error

DEVNET_URL = "https://api.devnet.solana.com"

def parse_balance(stdout: str) -> str:
    # Expecting output like: "1.2345 SOL"
    # Fallback: first number in the output
    for line in stdout.splitlines():
        line = line.strip()
        if line.endswith("SOL"):
            parts = line.split()
            if parts and parts[0].replace(".", "", 1).isdigit():
                return parts[0]
    # Generic regex for a float number
    import re
    m = re.search(r"(\d+\.\d+|\d+)", stdout)
    if m:
        return m.group(1)
    raise ValueError("Could not parse balance from output:\n" + stdout)

def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch SOL balance (devnet) and log to CSV.")
    parser.add_argument("--config", default="config.json", help="Path to config.json")
    parser.add_argument("--wallet", default=None, help="Override wallet pubkey")
    parser.add_argument("--balance-csv", default="balance.csv", help="Path to balance CSV log")
    parser.add_argument("--errors-csv", default="errors.csv", help="Path to errors CSV log")
    args = parser.parse_args()

    config_path = Path(args.config)
    balance_csv = Path(args.balance_csv)
    errors_csv = Path(args.errors_csv)

    try:
        cfg = load_config(config_path)
        wallet = args.wallet or cfg.get("wallet_pubkey")
        if not wallet:
            raise KeyError("wallet_pubkey not provided via --wallet or config.json")

        ensure_csv(balance_csv, ["wallet", "timestamp", "balance"])

        cmd = ["solana", "balance", wallet, "--url", DEVNET_URL]
        proc = run_cmd(cmd)

        if proc.returncode != 0:
            msg = f"CMD: {' '.join(cmd)}\nRC: {proc.returncode}\nSTDERR: {proc.stderr.strip()}"
            log_error(errors_csv, msg)
            print(f"[ERROR] balance failed. See {errors_csv}", file=sys.stderr)
            return proc.returncode

        try:
            bal = parse_balance(proc.stdout)
        except Exception as e:
            log_error(errors_csv, f"ParseError: {e}\nRAW: {proc.stdout}")
            print(f"[ERROR] failed to parse balance. See {errors_csv}", file=sys.stderr)
            return 2

        ts = datetime.now(timezone.utc).isoformat()
        append_row(balance_csv, [wallet, ts, bal])
        print(f"Wallet: {wallet} | Balance: {bal} SOL | Time: {ts}")
        return 0

    except Exception as e:
        log_error(Path(args.errors_csv), f"Unhandled: {type(e).__name__}: {e}")
        print(f"[ERROR] {e} (logged)", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
