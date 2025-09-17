# C2C Solana CLI Bots (Devnet)

Two small Python CLIs that wrap **Solana** / **SPL-Token** commands and log to CSV.

* `balance_bot.py` — fetch SOL balance
* `transfer_bot.py` — transfer SPL tokens
* `utils.py` — shared helpers (`load_config`, `ensure_csv`, `append_row`, `run_cmd`, `log_error`)
* Logs: `balance.csv`, `transfers.csv`, `errors.csv` (auto-created)

---

## 1) Requirements

* Python **3.10+**
* **Solana CLI** and **SPL-Token** CLI in PATH

  ```bash
  solana --version
  spl-token --version
  ```
* Use **devnet**:

  ```bash
  solana config set --url https://api.devnet.solana.com
  ```

> Scripts never read private keys directly, but `spl-token transfer` uses your default Solana keypair if present. Use **devnet only**.

---

## 2) Configure

Edit `config.json`:

```json
{
  "wallet_pubkey": "EnterYourDevnetPublicKeyHere",
  "token_mint": "EnterTokenMintPubkeyHere",
  "recipient_wallet": "EnterRecipientPubkeyHere",
  "transfer_amount": 0.01
}
```

(Optional on macOS/Linux):

```bash
chmod +x balance_bot.py transfer_bot.py
```

---

## 3) Usage

### A) Check SOL balance

```bash
python balance_bot.py
# override wallet:
python balance_bot.py --wallet <PUBKEY>
```

**Appends to `balance.csv`:**

```
wallet,timestamp,balance
```

Timestamps are ISO-8601 (UTC).

### B) Transfer SPL tokens

```bash
python transfer_bot.py
# override amount:
python transfer_bot.py --amount 0.02
```

Runs:

```
spl-token transfer <MINT> <AMOUNT> <RECIPIENT> --fund-recipient --allow-unfunded-recipient --url https://api.devnet.solana.com
```

**Appends to `transfers.csv`:**

```
from_wallet,to_wallet,amount,signature,timestamp
```

---

## 4) Errors & Logs

* On failure (non-zero exit, parse error, etc.), one row is added to **`errors.csv`**:

  ```
  timestamp,error
  ```
* CSVs are auto-created with headers if missing.

---

## 5) Troubleshooting

* **CLI not found** → Install Solana/SPL-Token and ensure PATH.
* **Need funds** (devnet) →

  ```bash
  solana airdrop 2 <PUBKEY> --url https://api.devnet.solana.com
  ```
* **No keypair / insufficient SOL for fees** →

  ```bash
  solana-keygen new
  solana config set --keypair <PATH_TO_KEYPAIR>
  ```
* **Balance parse error** → See `errors.csv` (script also falls back to first number in output).
* **Missing signature** → Output formats vary; script tries multiple patterns and still logs the row.

---

## 6) Command Cheat-Sheet

```bash
# Balance (use config)
python balance_bot.py

# Balance (override)
python balance_bot.py --wallet <PUBKEY>

# Transfer (use config amount)
python transfer_bot.py

# Transfer (override amount)
python transfer_bot.py --amount 1.5
```

---

## 7) Notes

* Network is hard-coded to **devnet** in both scripts.
* CSVs are UTF-8, comma-separated.
* Keep secrets out of `config.json`.
