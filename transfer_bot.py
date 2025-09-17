#!/usr/bin/env python3
"""transfer_bot.py
Perform an SPL Token transfer on devnet via SPL-Token CLI and log to CSV.
Logs errors to errors.csv.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
import csv
from decimal import Decimal
import re
from typing import List

from utils import load_config, ensure_csv, append_row, run_cmd, log_error

DEVNET_URL = "https://api.devnet.solana.com"

def extract_signature(stdout: str) -> str:
    # Try common patterns from spl-token output
    # e.g. "Signature: <base58>" or "Transaction signature: <base58>"
    patterns = [
        r"Signature:\s*([1-9A-HJ-NP-Za-km-z]+)",
        r"Transaction signature:\s*([1-9A-HJ-NP-Za-km-z]+)",
        r"signature:\s*([1-9A-HJ-NP-Za-km-z]+)",
    ]
    for pat in patterns:
        m = re.search(pat, stdout, flags=re.IGNORECASE)
        if m:
            return m.group(1)
    # Otherwise, first long base58-looking token
    m = re.search(r"([1-9A-HJ-NP-Za-km-z]{44,})", stdout)
    if m:
        return m.group(1)
    return ""

def main() -> int:
    parser = argparse.ArgumentParser(description="Transfer SPL Token (devnet) and log to CSV.")
    parser.add_argument("--config", default="config.json", help="Path to config.json")
    parser.add_argument("--amount", type=str, default=None, help="Amount to transfer (overrides config)")
    parser.add_argument("--transfers-csv", default="transfers.csv", help="Path to transfers CSV log")
    parser.add_argument("--errors-csv", default="errors.csv", help="Path to errors CSV log")
    args = parser.parse_args()

    config_path = Path(args.config)
    transfers_csv = Path(args.transfers_csv)
    errors_csv = Path(args.errors_csv)

    try:
        cfg = load_config(config_path)
        from_wallet = cfg.get("wallet_pubkey")  # for logging only
        mint = cfg.get("token_mint")
        to_wallet = cfg.get("recipient_wallet")
        amount_str = args.amount or str(cfg.get("transfer_amount", ""))

        if not from_wallet:
            raise KeyError("wallet_pubkey missing in config.json (used for logging)")
        if not mint:
            raise KeyError("token_mint missing in config.json")
        if not to_wallet:
            raise KeyError("recipient_wallet missing in config.json")
        if not amount_str:
            raise KeyError("transfer amount missing; pass --amount or set transfer_amount in config.json")

        # Validate amount format
        _ = Decimal(amount_str)  # raises if invalid

        ensure_csv(transfers_csv, ["from_wallet", "to_wallet", "amount", "signature", "timestamp"])

        cmd = [
            "spl-token", "transfer", mint, amount_str, to_wallet,
            "--fund-recipient", "--allow-unfunded-recipient",
            "--url", DEVNET_URL
        ]

        proc = run_cmd(cmd)

        if proc.returncode != 0:
            msg = f"CMD: {' '.join(cmd)}\nRC: {proc.returncode}\nSTDERR: {proc.stderr.strip()}"
            log_error(errors_csv, msg)
            print(f"[ERROR] transfer failed. See {errors_csv}", file=sys.stderr)
            return proc.returncode

        sig = extract_signature(proc.stdout)
        ts = datetime.now(timezone.utc).isoformat()
        append_row(transfers_csv, [from_wallet, to_wallet, amount_str, sig, ts])

        print("Transfer OK")
        if sig:
            print(f"Signature: {sig}")
        else:
            print("(Signature not found in output; logged anyway)")
        print(f"Time: {ts}")
        return 0

    except Exception as e:
        log_error(Path(args.errors_csv), f"Unhandled: {type(e).__name__}: {e}")
        print(f"[ERROR] {e} (logged)", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
