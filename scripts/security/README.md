# VALEO NeuroERP — Security Agent

Multi-Scanner Security Pipeline mit LLM-Triage.

## Architektur

```
Stufe 1: Gitleaks        → Secrets in Repo + Git-History
Stufe 2: Semgrep+Bandit  → SAST (Code-Patterns, OWASP Top 10)
Stufe 3: Trivy           → Dependencies, Dockerfiles, Container-Images
Stufe 4: Triage          → Deduplizierung, Priorisierung, Unified Report
Stufe 5: LLM-Triage      → Claude/GPT bewertet Exploitability + liefert Fixes
```

## Lokaler Scan

```bash
# Voraussetzungen installieren
# macOS:   brew install gitleaks semgrep trivy jq
# Windows: choco install gitleaks jq; pip install semgrep bandit

# Repo scannen
chmod +x scripts/security/run_security_scan.sh
./scripts/security/run_security_scan.sh

# Mit Docker-Image
docker build -t valeo-erp:test .
IMAGE_NAME=valeo-erp:test ./scripts/security/run_security_scan.sh
```

## LLM-Triage (nach Scan)

```bash
# Option A: Claude Code CLI
./scripts/security/run_claude_triage.sh security-reports/<timestamp>/

# Option B: Manuell
# 1. unified_findings.json oeffnen
# 2. Inhalt + llm_triage_prompt.txt in ChatGPT/Claude geben
# 3. Nur bestaetigte Critical/High Findings beheben
```

## Lokale Secret-Pflege

Fuer lokale Entwicklung koennen Secrets zentral ueber den bestehenden Vault-Service
und optional ueber das OS-Keyring gepflegt werden.

```bash
# optional: Python-Keyring installieren
pip install keyring

# Secret ins lokale OS-Keyring schreiben
python scripts/security/secret_store.py set LINKUP_API_KEY <wert> --provider keyring --type api_key

# Secret lesen
python scripts/security/secret_store.py get LINKUP_API_KEY

# Metadaten listen
python scripts/security/secret_store.py list
```

Ohne `keyring` kann bewusst `--provider memory` genutzt werden; das ist dann nur
prozesslokal und nicht fuer dauerhafte Pflege gedacht.

## Produktiver Vault-Pfad

Seit `SEC-014` kann der Vault-Service auch HashiCorp Vault KV-v2 als externen
Provider nutzen. Fuer Produktion ist der erwartete Grundpfad:

```bash
SECRET_PROVIDER=hashicorp_vault
REQUIRE_EXTERNAL_SECRETS_IN_PRODUCTION=true
HASHICORP_VAULT_ADDR=https://vault.example.local
HASHICORP_VAULT_TOKEN=<token>
HASHICORP_VAULT_MOUNT=secret
HASHICORP_VAULT_PATH_PREFIX=valeo-neuroerp
```

Pflicht-Secrets fuer den Startup-Guard:

```bash
python scripts/security/secret_store.py set SECRET_KEY <wert> --provider hashicorp_vault --type encryption_key
python scripts/security/secret_store.py set ENCRYPTION_KEY <wert> --provider hashicorp_vault --type encryption_key
python scripts/security/secret_store.py config
python scripts/security/secret_store.py health
```

In `APP_ENV=production` blockiert der App-Start jetzt, wenn
- `API_DEV_TOKEN` gesetzt ist
- kein externer Secret-Provider aktiv ist
- `SECRET_KEY` oder `ENCRYPTION_KEY` nicht aus Provider/Environment geladen werden koennen

## CI/CD (GitHub Actions)

Workflow: `.github/workflows/security-agent.yml`

- Laueft automatisch: Montag 03:00 UTC + Push auf main
- Manuell: Actions > Security Agent > Run workflow
- Ergebnisse: Artifacts > security-agent-unified

## Feste Regression-Lane

Seit `SEC-017` enthaelt derselbe Workflow zusaetzlich eine feste Security-Regression-Lane.
Sie ist kein Scanner-Ersatz, sondern prueft die bereits behobenen P0/P1-Pfade direkt gegen
Regressionen im Code.

Backend:

```bash
pytest tests/test_security_*.py tests/test_secrets_vault.py tests/test_neuro_tool_execution.py -q --no-cov
```

Frontend:

```bash
pnpm --dir packages/frontend-web exec vitest run src/__tests__/lib/export-utils.test.ts
```

Dokumentation:

```bash
node scripts/docs-governance-check.cjs
```

## Custom Semgrep Rules

`semgrep-rules.yml` enthaelt projektspezifische Regeln:

- `valeo-tenant-bypass`: Endpoint ohne Tenant-Isolation
- `valeo-sqli-fstring`: SQL via f-string
- `valeo-pickle-usage`: Unsichere Deserialisierung
- `valeo-hardcoded-secret`: Hardcoded Credentials
- `valeo-ssrf-requests`: SSRF via dynamische URL
- `valeo-path-traversal`: Path Traversal
- `valeo-xss-dangerously`: dangerouslySetInnerHTML
- `valeo-eval-usage`: eval()/new Function()

## Dateien

```
scripts/security/
  run_security_scan.sh    # Lokaler Orchestrator (Bash)
  triage_findings.py      # Ergebnis-Vereinheitlichung + Summary
  llm_triage_prompt.txt   # 4-Stufen LLM-Prompt (Analyse/RedTeam/BlueTeam/Fixer)
  semgrep-rules.yml       # Projektspezifische SAST-Regeln
  run_claude_triage.sh    # Claude Code CLI Integration
  secret_store.py         # Lokales Set/Get/List/Delete fuer Vault/Keyring
  README.md               # Diese Datei
```
