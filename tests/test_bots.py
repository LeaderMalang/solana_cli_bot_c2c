import csv, json
from pathlib import Path
# from datetime import datetime, timezone
# import builtins

import types

def fake_completed(stdout="", stderr="", rc=0):
    C = types.SimpleNamespace()
    C.stdout, C.stderr, C.returncode = stdout, stderr, rc
    return C

def write_cfg(tmp, wallet="W", mint="M", to="T", amt=1):
    cfg = {"wallet_pubkey": wallet, "token_mint": mint, "recipient_wallet": to, "transfer_amount": amt}
    (tmp/"config.json").write_text(json.dumps(cfg))

def test_balance_ok(tmp_path, monkeypatch):
    from utils import ensure_csv
    write_cfg(tmp_path)
    ensure_csv(tmp_path/"balance.csv", ["wallet","timestamp","balance"])
    ensure_csv(tmp_path/"errors.csv", ["timestamp","error"])

    def fake_run(cmd, capture_output, text, encoding):
        return fake_completed(stdout="1.23 SOL\n")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("subprocess.run", fake_run)

    import balance_bot
    assert balance_bot.main() == 0
    rows = list(csv.reader((tmp_path/"balance.csv").open()))
    assert rows[-1][0] == "W"
    assert rows[-1][2] == "1.23"

def test_transfer_error_logs(tmp_path, monkeypatch):
    from utils import ensure_csv
    write_cfg(tmp_path)
    ensure_csv(tmp_path/"transfers.csv", ["from_wallet","to_wallet","amount","signature","timestamp"])
    ensure_csv(tmp_path/"errors.csv", ["timestamp","error"])

    def fake_run(cmd, capture_output, text, encoding):
        return fake_completed(stdout="", stderr="boom", rc=1)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("subprocess.run", fake_run)

    import transfer_bot
    rc = transfer_bot.main()
    assert rc != 0
    rows = list(csv.reader((tmp_path/"errors.csv").open()))
    assert "boom" in rows[-1][1]
