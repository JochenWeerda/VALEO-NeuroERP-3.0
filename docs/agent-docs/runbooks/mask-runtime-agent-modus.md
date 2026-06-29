---
title: Runbook — Mask Runtime Agent-Modus
type: reference
audience: [ki-agent, betrieb, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-06-29
version: 1.0.0
description: Operatives Runbook für Agenten auf der Universal Mask Runtime — lesen, propose, dryRun, humanApproval, Audit.
---

# Runbook: Mask Runtime Agent-Modus (UIX-036)

## Ziel

Agenten nutzen dieselbe `ScreenDefinition` wie die Human-UI, aber mit **expliziten Policies**:
lesen ohne Risiko, vorschlagen ohne Ausführung, ausführen nur mit Freigabe.

## Voraussetzungen

- Bearer-Token + `X-Tenant-ID` gesetzt
- Agent kennt `mask_id` (z. B. `crm/customer-360`, `einkauf/supplier`)
- Guardrails: [Guardrails](../guardrails.md)

## Schritt 1 — AgentMaskContract laden

```http
GET /api/v1/masks/{mask_id}/agent-contract
Authorization: Bearer …
X-Tenant-ID: …
```

Prüfen:

- `readableFields` / `editableFields` / `sensitiveFields`
- `availableActions[]` mit `dangerLevel`, `permission`, `humanApprovalRequired`
- `validationRules`, `auditRequirements`

## Schritt 2 — Readiness prüfen (optional)

```http
GET /api/v1/masks/{mask_id}/readiness
```

Nur Masken mit `generatorReady=true` für produktive Agent-Automation freigeben.

## Schritt 3 — Daten lesen (idempotent)

1. `screen-summary` oder Entity-Endpunkt
2. Tab-Daten mit `page`, `limit`, `q`, `sort`, `filter_plan`
3. **Keine** `execute`-Calls ohne explizite User-Freigabe

## Schritt 4 — Aktion vorschlagen (dryRun / propose)

Beispiel CRM Aktivität:

```http
POST /api/v1/crm/customers/{customer_id}/actions/create_activity
Content-Type: application/json

{
  "_mode": "dryRun",
  "_auditReason": "Agent-Vorschlag: Follow-up nach offenen Posten",
  "betreff": "Rückruf Kunde",
  "typ": "Anruf"
}
```

Erwartung: `success=true`, keine Persistenz, Validierungsfehler in `validationErrors`.

## Schritt 5 — Human Approval

Wenn `humanApprovalRequired=true`:

1. Vorschlag dem User anzeigen (UI oder Freigabe-Queue)
2. Erst nach Bestätigung `_mode` weglassen oder `execute` senden
3. `_auditReason` und `_idempotencyKey` mitschicken

## Schritt 6 — Audit

Jede vorbereitete oder ausgeführte Aktion muss `auditReason` tragen.
Backend schreibt Audit-Eintrag (z. B. `domain_shared.action_audit`).

## Abnahme-Szenario (UIX-036)

```text
„Analysiere Kunde X, prüfe offene Posten, schlage nächste Aktion vor,
 führe aber nichts ohne Freigabe aus.“
```

Checkliste:

- [ ] Agent liest `agent-contract`
- [ ] Agent nutzt `readableFields`, respektiert `sensitiveFields`
- [ ] Agent nutzt `dryRun` / `propose`
- [ ] Agent blockiert bei `humanApprovalRequired`
- [ ] Agent setzt `auditReason` bei vorbereiteten Aktionen

## Tests

```bash
pytest tests/test_uix035_action_runtime_crm.py
pytest tests/test_agent_mask_contract.py
```

## Eskalation

| Problem | Aktion |
|---------|--------|
| Readiness rot | Maske nicht für Agent-Automation freigeben |
| 422 filter_plan | FilterPlan gegen Whitelist prüfen |
| Permission denied | RBAC / Tenant prüfen |
| execute ohne Approval | Guardrail-Verstoß — Incident loggen |

## Verweise

- [Mask Runtime API (Entwickler)](../entwickler/mask-runtime-api.md)
- [Universal Mask Runtime Status](../../architecture/uix/universal-mask-runtime-status.md)
- [Benutzerhandbuch Masken-Plattform](../../benutzerhandbuch/masken-plattform.md)
