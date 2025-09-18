# Threat Model

## Scope
Small Python CLIs that call Solana/SPL-Token CLIs and write CSV logs on **devnet**.

## Assets
- Local machine environment
- **Keypair** used by Solana CLI (fee-payer)
- `config.json` (public addresses only; must not contain secrets)
- CSV logs (`balance.csv`, `transfers.csv`, `errors.csv`)

## Trust Boundaries
- Local host ↔ Solana/SPL binaries (via PATH)
- Local host ↔ Remote RPC (`https://api.devnet.solana.com`)
- Local filesystem (read `config.json`, write logs)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---:|---:|---|
| **Secret leakage** (keys in repo/logs) | Med | High | `.gitignore` for `.env*`/keys; secret scanning in CI; redact logs; doc in SECURITY.md |
| **Poisoned PATH / tampered CLI** | Low | High | Pin install source; verify `solana`/`spl-token` versions; optionally hash check |
| **Command injection via args** | Low | Med | Use `subprocess.run` with list args (no shell); validate numeric inputs |
| **Malicious/invalid `config.json`** | Med | Med | Validate schema/types; reject non-pubkey fields; strict error paths |
| **Log poisoning / CSV injection** | Med | Med | Sanitize leading `= + - @` in CSV cells; quote fields |
| **Insecure key storage on host** | Med | High | Rely on Solana CLI’s key management; advise disk encryption/permissions |
| **MITM to RPC** | Low | Med | Use HTTPS endpoints; allow user to override only to `https://` |
| **DoS via huge output** | Low | Low | Cap stdout/stderr captured; fail gracefully, log error |
| **Stale/vulnerable deps** | Low | Med | Pin Python version; periodic `pip-audit` (if deps added later) |

## Assumptions
- Users run on their own dev machines.
- No private keys in repo or `config.json`.
- Network: **devnet** (not mainnet).

## Non-Goals
- Hardware wallet support
- Full key management
