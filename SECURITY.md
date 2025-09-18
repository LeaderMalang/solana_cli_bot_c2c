# Security Policy

## Supported
- `main` (active)
- Other branches are best-effort.

## Reporting a Vulnerability
- Email: **admin@codetocapital.us**
- PGP (optional): publish your key/fingerprint here.
- Please include: repro steps, impact, logs (no secrets).

**Disclosure timeline**
- Acknowledge: within **72 hours**
- Status update: within **5 days**
- Target fix window: **7–14 days** for high/critical (best-effort)

## Incident Response (IR) Playbook
1. **Triage**: confirm issue, assign severity (Low/Med/High/Crit).
2. **Contain**: revoke/rotate keys, disable affected CI jobs, lock releases.
3. **Eradicate**: patch code/deps, add tests/checks.
4. **Recover**: release fixed version, re-enable CI.
5. **Notify**: stakeholders and reporters (with CVE if applicable).
6. **Post-mortem**: timeline, root cause, fixes, learnings.

## Secrets & Key Handling
- **Never commit secrets** (keys, mnemonics, tokens).  
- Use environment vars / secret stores (e.g., GitHub Actions Secrets).  
- `.env*` must stay in `.gitignore`.  
- Enable **secret scanning** (e.g., GitHub Secret Scanning / gitleaks).

## Dependencies
- Pin versions; update regularly.
- Run SCA on PRs (e.g., `pip-audit`, `npm audit` where relevant).
- No auto-merge for security-related bumps without review.

## CI/CD Hardening
- Principle of least privilege on tokens.
- Protected branches, required reviews, signed commits/tags (if feasible).
- Run **lint + static checks + secret scan** on every PR.

## Logging
- Logs must not contain secrets or private keys.
- Redact on capture and before publishing artifacts.

## Contact
- Security team: **admin@codetocapital.us**
