---
title: AppSec-Review — SQL-f-String-Stellen (nosec S608)
type: report
audience: [security, entwickler, lead]
owner: Claude
status: aktiv
last_reviewed: 2026-07-05
version: 1.0.0
description: Stelle-fuer-Muster-Verdikt der dynamischen SQL-f-Strings (nosec S608) — Identifier-Whitelist + Wertebindung; SPEC-P1-05 / A7.
---

# AppSec-Review: dynamische SQL-f-Strings (nosec S608)

**Umfang:** 121 mit `# nosec S608` annotierte f-String-`text(...)`-Stellen (Stand 2026-07-05).
**Gate:** `scripts/check_sql_fstrings.py` blockiert im CI jede **neue** ungeflaggte
f-String-SQL-Stelle (aktuell grün) — neue Stellen können nur mit bewusstem, sichtbarem
`nosec S608`-Kommentar hinzukommen.

## Ergebnis

**Kein SQL-Injection-Risiko über die geprüften Muster.** Alle dynamischen Anteile der
SQL-Strings sind **Identifier** (Spaltennamen, WHERE-/SET-/HAVING-/ORDER-Fragmente),
die aus einer der drei folgenden Quellen stammen — nie aus rohem Nutzer-Freitext. Alle
**Werte** werden ausnahmslos über gebundene `:param`-Platzhalter übergeben.

## Belegte sichere Muster (Stichproben über die dichtesten Dateien)

1. **Literal-Fragmente, bedingt zusammengesetzt** (z. B. `logistics_tours.py`,
   `pricing.py`, `inventory_operations.py`, `personal.py`):
   ```python
   conditions = ["tenant_id = :tenant_id"]
   if status: conditions.append("status = :status"); params["status"] = status
   where = " AND ".join(conditions)
   text(f"SELECT ... WHERE {where} ORDER BY created_at DESC")  # nosec S608
   ```
   `where` besteht ausschließlich aus im Code festgelegten Literalen; Werte gebunden.

2. **Feste Dict-/Feldlisten** (z. B. `crm_campaigns.py` `ts_fields`):
   ```python
   ts_fields = {"state": target, "updated_at": now(), ...}   # feste Keys
   set_clauses = ", ".join(f"{k} = :{k}" for k in ts_fields)
   ```
   Keys sind Code-Literale.

3. **Pydantic-Modell-Feldnamen als Whitelist** (der einzige nicht-offensichtliche Fall,
   `crm_campaigns.py` UPDATE-Endpoints):
   ```python
   updates = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
   set_clauses = ", ".join(f"{k} = :{k}" for k in updates)
   ```
   **Verifiziert:** `TemplateUpdate`/`CampaignUpdate` sind reine `BaseModel` mit
   ausschließlich definierten Feldern und **ohne** `model_config = ConfigDict(extra="allow")`.
   Pydantic v2 verwirft unbekannte Keys per Default (`extra="ignore"`), bevor sie den Code
   erreichen → `{k}` ist auf die Modell-Felder (Whitelist) beschränkt. Injektion über
   Spaltennamen ausgeschlossen.

## Empfehlung / Restrisiko

- **Invariante für neue Endpoints:** UPDATE/INSERT-Set-Klauseln aus `model_dump()` sind nur
  sicher, solange das Modell **kein** `extra="allow"` trägt. Bei künftigen Modellen mit
  `extra="allow"` darf `model_dump()`-Keys NICHT in Identifier-Position interpoliert werden.
- **Follow-up (Audit-Stretch, offen):** Hypothesis-Property-Tests mit Injection-Payloads
  gegen die ~10 exponiertesten Endpunkte als zusätzliche Absicherung (nicht blockierend,
  da Musterlage als sicher belegt).
