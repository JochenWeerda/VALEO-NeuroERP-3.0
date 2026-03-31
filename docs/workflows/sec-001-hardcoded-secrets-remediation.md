# SEC-001 - Hardcoded Secrets Remediation

## Ziel

Echte Secrets und unsichere Default-Credentials aus dem Repo entfernen, ohne den Scope vorzeitig auf Auth-, Tenant- oder SAST-Folgeprobleme auszuweiten.

## Umsetzung

- `scripts/mcp_server.py`, `scripts/genxais_prompt_generator_simple.py` und `scripts/test_mcp_api.py` nutzen keinen hardcodierten LinkUp-API-Key mehr
- der MCP-Server leakt keinen Teil-Key mehr in Responses
- `alembic.ini` enthaelt keine konkrete DB-Credential-URL mehr
- `app/core/config.py` nutzt fuer `DATABASE_URL` keinen echten Repo-Credential-String mehr
- Domain-Compose-Dateien fuer Procurement, Inventory, Finance und ERP ziehen Datenbank-/Admin-/JWT-/Supplier-Secrets jetzt auf env-pflichtige Variablen

## Ergebnis

- die bestaetigten P0/P1-Secret-Funde aus dem aktuellen Security-Befund sind aus den betroffenen Dateien entfernt
- lokale Starts ohne gesetzte Variablen schlagen fuer die betroffenen Compose-Stacks jetzt frueh fehl statt mit bekannten Default-Credentials hochzukommen
- die offenen Security-Restthemen liegen jetzt klar in Auth-, Tenant- und Query-Hardening
