# SEC-001 - Hardcoded Secrets Remediation

**Lane:** Security
**Prioritaet:** P0
**Status:** umgesetzt

## Umsetzung

- LinkUp-Repo-Key aus Scripts entfernt
- MCP-Antworten leaken keine Teil-Secrets mehr
- Alembic-/Backend-DB-Defaults enthalten keine realen Credentials mehr
- Compose-Dateien nutzen fuer sensible Werte env-pflichtige Variablen statt schwacher Defaults
