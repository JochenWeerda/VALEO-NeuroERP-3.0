---
title: AppSec S608 Review
type: reference
audience: [sicherheit, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-09
version: 2.0.0
description: SPEC-P1-05 — SQL-f-String-Inventar; Verdikt aus dem Bandit-Lauf.
---

# AppSec S608-Review (SPEC-P1-05)

Stand: **2026-09-09** — erzeugt von `scripts/generate_s608_review.py`.

Das Verdikt stammt aus einem echten `bandit -t B608`-Lauf, nicht aus dem
Wortlaut der Kommentare. Version 1.0 dieses Berichts hatte nach Prosa
klassifiziert und deshalb 132 Stellen als geprueft ausgewiesen, die Bandit
unveraendert meldete.

SQL-f-String-Aufrufe gesamt: **315**

| Verdikt | Anzahl | Bedeutung |
|---|---:|---|
| `suppressed` | 315 | Bandit meldet die Stelle nicht mehr — Suppression wirkt |
| `unsuppressed` | 0 | Kommentar vorhanden, aber wirkungslos platziert |
| `unreviewed` | 0 | SQL-f-String ohne jedes `nosec` — echtes Review offen |

## Platzierung

Bandit unterdrueckt nur, wenn `# nosec` auf einer Zeile **des gemeldeten
Ausdrucks** steht. Zwei Formen wirken nicht:

```python
# nosec B608  # Begruendung        <- Zeile DARUEBER: wirkungslos
rows = db.execute(text(f"SELECT ... {where}"), params)

rows = db.execute(text(f"""  -- nosec S608 ...   <- im SQL-String: wirkungslos
    SELECT ... {where}
"""), params)
```

Richtig ist die schliessende Klammerzeile:

```python
rows = db.execute(text(f"""
    SELECT ... {where}
"""), params)  # nosec B608  # reviewed-safe: <Begruendung>
```

## Gate

`scripts/check_sql_fstrings.py` bildet dieselbe Semantik ab und faellt bei
**neuen** ungeflaggten Stellen. Die bekannte Restschuld steht in
`config/sql_fstring_review_baseline.json` (0 Stellen) und
darf nur schrumpfen.

## Wirksam unterdrueckt (315)

| Datei | Zeilen | Begruendung |
|---|---:|---|
| `app/api/v1/endpoints/accruals_provisions.py` | 187 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/accruals_provisions.py` | 73-79 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/admin_devices.py` | 148-155 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/admin_devices.py` | 276-283 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/admin_devices.py` | 454-461 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/admin_devices.py` | 645-652 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/admin_mobile.py` | 172 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/admin_mobile.py` | 256-263 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/admin_mobile.py` | 706-714 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/admin_mobile.py` | 733-741 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/admin_reporting.py` | 69-76 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/ap_approval_workflow.py` | 204 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/ap_approval_workflow.py` | 202 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/articles.py` | 639-654 | `# nosec B608 - Fragment aus Modulkonstanten, Werte via Bind-Params` |
| `app/api/v1/endpoints/asset_accounting.py` | 155-162 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 262-264 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 305-310 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 240-242 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 293-295 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 413-417 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 429-431 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 388-391 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 123 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/asset_accounting.py` | 208-212 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 375-380 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 477-485 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 490-497 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_accounting.py` | 542-548 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/asset_ledger_connector.py` | 113-117 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/audit_evidence.py` | 66-72 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/auto_matching.py` | 117 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/auto_matching.py` | 115 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/auto_matching.py` | 794 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/auto_matching.py` | 811 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/auto_matching.py` | 825 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/auto_matching.py` | 839 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/auto_matching.py` | 474 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/bank_accounts.py` | 147-159 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/bank_accounts.py` | 289-291 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/bank_import.py` | 293-299 | `# nosec B608  # reviewed-safe: dynamische Fragmente aus festen Literalen, Werte gebunden` |
| `app/api/v1/endpoints/beleg_vordrucke.py` | 125 | `# nosec B608  # where aus Code-Konstanten` |
| `app/api/v1/endpoints/booking_templates.py` | 134 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/booking_templates.py` | 527-533 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/booking_templates.py` | 132 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/branches.py` | 169-173 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/budget_planning.py` | 114-117 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/budget_planning.py` | 356-360 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/budget_planning.py` | 418-420 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/budget_planning.py` | 145-149 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/budget_planning.py` | 275-281 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/central_contracts.py` | 332 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/central_contracts.py` | 207-210 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/central_contracts.py` | 410 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/closing_checklists.py` | 63 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/closing_checklists.py` | 800 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/closing_checklists.py` | 57 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/closing_checklists.py` | 61 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/closing_checklists.py` | 798 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/closing_checklists.py` | 848 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/closing_checklists.py` | 875 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/compat.py` | 2475-2484 | `# nosec B608 - Fragmente aus Modulkonstanten, Werte via Bind-Params` |
| `app/api/v1/endpoints/compat.py` | 2497-2508 | `# nosec B608 - Fragment aus Modulkonstanten, Werte via Bind-Params` |
| `app/api/v1/endpoints/compat.py` | 2662-2666 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/compliance.py` | 914-919 | `# nosec B608  # reviewed-safe: dynamische Fragmente aus festen Literalen, Werte gebunden` |
| `app/api/v1/endpoints/compliance_dsgvo.py` | 132 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/compliance_whistleblower_lksg.py` | 118-123 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/compliance_whistleblower_lksg.py` | 213-218 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/creditors.py` | 362-364 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/creditors.py` | 225 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/creditors.py` | 229-236 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/crm_reports.py` | 155-159 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/crm_reports.py` | 163-167 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/data_quality.py` | 122-130 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/api/v1/endpoints/data_quality.py` | 168-176 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/api/v1/endpoints/data_quality.py` | 198-208 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/api/v1/endpoints/debtors.py` | 229-231 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/debtors.py` | 235-242 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/debtors.py` | 389-395 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/dms_images.py` | 94 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/api/v1/endpoints/dms_images.py` | 99-109 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/api/v1/endpoints/dms_images.py` | 145-150 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/api/v1/endpoints/dunning.py` | 158 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/dunning.py` | 710 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/dunning.py` | 156 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/dunning.py` | 708 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/einkauf_lieferschein.py` | 327 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/einkauf_lieferschein.py` | 274 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/einkauf_lieferschein.py` | 393 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/einkauf_lieferschein.py` | 181 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/einkauf_lieferschein.py` | 250-252 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/ers_settlement.py` | 82 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/exchange_rates.py` | 126 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/exchange_rates.py` | 315-321 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/exchange_rates.py` | 124 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/fibu_connectors.py` | 173 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/finance_actions.py` | 570-587 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/finance_followup.py` | 160-168 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/finance_followup.py` | 302-309 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/finance_invoices.py` | 243-256 | `# nosec B608  # reviewed-safe: Tabellenname stammt aus einer festen Kandidatenliste, Werte sind gebunden` |
| `app/api/v1/endpoints/finance_invoices.py` | 268-276 | `# nosec B608  # reviewed-safe: Tabellenname stammt aus einer festen Kandidatenliste, Werte sind gebunden` |
| `app/api/v1/endpoints/finance_invoices.py` | 229-236 | `# nosec B608  # reviewed-safe: Tabellenname stammt aus einer festen Kandidatenliste, Werte sind gebunden` |
| `app/api/v1/endpoints/finance_invoices.py` | 575-581 | `# nosec B608  # reviewed-safe: Tabellenname stammt aus einer festen Kandidatenliste, Werte sind gebunden` |
| `app/api/v1/endpoints/financial_reports.py` | 698-729 | `# nosec B608  # reviewed-safe: dynamische Fragmente aus festen Literalen, Werte gebunden` |
| `app/api/v1/endpoints/fuhrpark.py` | 622 | `# nosec B608  # reviewed-safe: set_clause is built only from Pydantic model field names.` |
| `app/api/v1/endpoints/fuhrpark.py` | 725 | `# nosec B608  # reviewed-safe: set_clause is built only from Pydantic model field names.` |
| `app/api/v1/endpoints/futtermittel_rezepte.py` | 286-291 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/futtermittel_rohwaren.py` | 305-310 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/gelangensbestaetigung.py` | 116-123 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/genossenschaft.py` | 244-247 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/api/v1/endpoints/gobd_archiv.py` | 328-336 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/gobd_archiv.py` | 366-375 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/gobd_archiv.py` | 417-426 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/gobd_archiv.py` | 456-468 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/gobd_archiv.py` | 498-507 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/hofliste.py` | 167-171 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/individualpreise.py` | 190-199 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/intrastat.py` | 232-235 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/api/v1/endpoints/intrastat.py` | 140-147 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/api/v1/endpoints/inventory_operations.py` | 478 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/inventory_operations.py` | 466-473 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/inventory_operations.py` | 785-803 | `# nosec B608  # where_clause/having aus festen Literalen dieser Funktion, alle Werte via Bind-Params` |
| `app/api/v1/endpoints/kontrakt_mengenzeitraum.py` | 183-186 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/liquidity_planning.py` | 227 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/liquidity_planning.py` | 238-241 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/logistics_freight.py` | 164 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/logistics_freight.py` | 477-485 | `# nosec B608  # reviewed-safe: dynamische Fragmente aus festen Literalen, Werte gebunden` |
| `app/api/v1/endpoints/logistics_tours.py` | 433 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/logistics_tours.py` | 206 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/logistics_tours.py` | 882-896 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/logistics_tours.py` | 902-908 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/logistics_tours.py` | 215-218 | `# nosec B608` |
| `app/api/v1/endpoints/logistik_frachtbriefe.py` | 73-76 | `# nosec B608  # column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/payment_runs.py` | 360 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/payment_runs.py` | 548 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/payment_runs.py` | 358 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/payment_runs.py` | 545 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/personal.py` | 2807 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/personal.py` | 2988 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/personal.py` | 2733 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/personal.py` | 2760-2769 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/personal.py` | 3151 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/personal.py` | 1922-1932 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/price_lists.py` | 253 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/price_lists.py` | 161-168 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/pricing.py` | 290 | `# nosec B608  # where besteht nur aus festen Literalen dieser Funktion, alle Werte via Bind-Params` |
| `app/api/v1/endpoints/procurement_match.py` | 276 | `# nosec B608  # reviewed-safe: where fragments are code-controlled, values parameterized` |
| `app/api/v1/endpoints/purchase_invoice_verification.py` | 77 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/purchase_invoice_verification.py` | 96 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/purchase_invoice_verification.py` | 115 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/quadriga_connector.py` | 111-115 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/ruestliste.py` | 197 | `# noqa: S608  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/saatzucht.py` | 241 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/saatzucht.py` | 94 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/sales_blanket_orders.py` | 244 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/sales_blanket_orders.py` | 153-156 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/sales_credit_notes.py` | 183-190 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/sales_credit_notes.py` | 407-414 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/sales_delivery_notes.py` | 445-449 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/sales_offers.py` | 397-403 | `# nosec B608  # reviewed-safe: Spalten stammen aus deklarierten Pydantic-Feldnamen, Werte sind gebunden` |
| `app/api/v1/endpoints/sales_offers.py` | 212-220 | `# nosec B608  # reviewed-safe: Spalten stammen aus deklarierten Pydantic-Feldnamen, Werte sind gebunden` |
| `app/api/v1/endpoints/sales_offers.py` | 207 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/sales_orders.py` | 650-656 | `# nosec B608  # reviewed-safe: Spalten stammen aus deklarierten Pydantic-Feldnamen, Werte sind gebunden` |
| `app/api/v1/endpoints/sales_orders.py` | 217-225 | `# nosec B608  # reviewed-safe: Spalten stammen aus deklarierten Pydantic-Feldnamen, Werte sind gebunden` |
| `app/api/v1/endpoints/sales_orders.py` | 215 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/sanctions_compliance.py` | 296-302 | `# nosec B608  # fixed allow-listed clause` |
| `app/api/v1/endpoints/silo.py` | 690 | `# noqa: S608  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/stmd_duplikat.py` | 208-213 | `# nosec B608  # reviewed-safe: dynamische Fragmente aus festen Literalen, Werte gebunden` |
| `app/api/v1/endpoints/subsidiary_ledger_reconciliation.py` | 151-161 | `# nosec B608  # reviewed-safe: Tabellenname stammt aus einer festen Kandidatenliste, Werte sind gebunden` |
| `app/api/v1/endpoints/subsidiary_ledger_reconciliation.py` | 242-252 | `# nosec B608  # reviewed-safe: Tabellenname stammt aus einer festen Kandidatenliste, Werte sind gebunden` |
| `app/api/v1/endpoints/subsidiary_ledger_reconciliation.py` | 401-412 | `# nosec B608  # reviewed-safe: Tabellenname stammt aus einer festen Kandidatenliste, Werte sind gebunden` |
| `app/api/v1/endpoints/subsidiary_ledger_reconciliation.py` | 431-442 | `# nosec B608  # reviewed-safe: Tabellenname stammt aus einer festen Kandidatenliste, Werte sind gebunden` |
| `app/api/v1/endpoints/tapi.py` | 89 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/tapi.py` | 97 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/tapi.py` | 149 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/tapi.py` | 156-160 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/api/v1/endpoints/tax_keys.py` | 152-162 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/tax_keys.py` | 437-445 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/vat_return_export.py` | 654 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/vat_return_export.py` | 651 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/api/v1/endpoints/warehouse_wms.py` | 319 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/api/v1/endpoints/wf_trigger.py` | 66-73 | `# nosec B608  # reviewed-safe: dynamische Fragmente aus festen Literalen, Werte gebunden` |
| `app/crm/router.py` | 1037 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/crm/router.py` | 777-783 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/domains/inventory/api/charge_lineage.py` | 117-125 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/admin_core_service.py` | 295-302 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/admin_core_service.py` | 599-607 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/admin_core_service.py` | 633-640 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/agri_lot_link_booking_service.py` | 394-404 | `# nosec B608  # wid_clause is code-controlled and only adds a static  # noqa: S608` |
| `app/services/agri_silo_material_flow_service.py` | 77 | `# nosec B608  # reviewed-safe: where fragments are code-controlled, values parameterized` |
| `app/services/agri_silo_material_flow_service.py` | 128 | `# nosec B608  # reviewed-safe: where fragments are code-controlled, values parameterized` |
| `app/services/agri_silo_material_flow_service.py` | 220-225 | `# nosec B608  # reviewed-safe: set_parts are built only from explicit allowlisted payload keys.  # noqa: S608` |
| `app/services/agri_silo_material_flow_service.py` | 260 | `# nosec B608  # reviewed-safe: where fragments are code-controlled, values parameterized` |
| `app/services/agri_silo_material_flow_service.py` | 336-341 | `# nosec B608  # reviewed-safe: set_parts are built only from explicit allowlisted payload keys.  # noqa: S608` |
| `app/services/agri_silo_material_flow_service.py` | 419 | `# nosec B608  # reviewed-safe: where fragments are code-controlled, values parameterized` |
| `app/services/agri_silo_material_flow_service.py` | 501-506 | `# nosec B608  # reviewed-safe: set_parts are built only from explicit allowlisted payload keys.  # noqa: S608` |
| `app/services/audit_hardening.py` | 167-173 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/billing_batch_service.py` | 118-120 | `# nosec B608  # reviewed-safe: WHERE-Fragmente aus festen Literalen, Werte nur gebunden` |
| `app/services/billing_batch_service.py` | 126-131 | `# nosec B608  # reviewed-safe: WHERE-Fragmente aus festen Literalen, Werte nur gebunden` |
| `app/services/billing_batch_service.py` | 160-165 | `# nosec B608  # reviewed-safe: WHERE-Fragmente aus festen Literalen, Werte nur gebunden` |
| `app/services/business_partner_service.py` | 333-337 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/business_partner_service.py` | 348 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/business_partner_service.py` | 371 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/business_partner_service.py` | 382 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/calendar_projection_service.py` | 832-841 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/compliance_pcn_lifecycle_service.py` | 143 | `# nosec B608  # set_clauses is assembled only from fixed code-controlled fragments; values are parameterized.` |
| `app/services/controlling_budget_lifecycle_service.py` | 131 | `# nosec B608  # set_clauses is assembled only from fixed code-controlled fragments; values are parameterized.` |
| `app/services/controlling_kostenstellen_abschluss_service.py` | 66 | `# nosec B608  # set_clauses is assembled only from fixed code-controlled fragments; values are parameterized.` |
| `app/services/controlling_service.py` | 54 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/crm_capture_inbox_service.py` | 92 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_capture_inbox_service.py` | 99-103 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_capture_inbox_service.py` | 119 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_capture_inbox_service.py` | 56-59 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_gift_service.py` | 78 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_gift_service.py` | 108 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_kontakt_service.py` | 35 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_kontakt_service.py` | 70 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_kontakt_service.py` | 92 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_kontakt_service.py` | 97-102 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_lead_gen_service.py` | 52-70 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/crm_lead_gen_service.py` | 85-99 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/crm_lead_gen_service.py` | 145-150 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/crm_merge_service.py` | 92 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/services/crm_merge_service.py` | 54 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/services/crm_notification_service.py` | 69 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/crm_notification_service.py` | 138 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/customer_service.py` | 343 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/customer_service.py` | 348-354 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/customer_service.py` | 212-215 | `# nosec B608  # reviewed-safe: interpoliert werden nur generierte Parameternamen, Werte sind gebunden` |
| `app/services/doc_nachweisraum_lifecycle_service.py` | 108-112 | `# nosec B608  # extra is assembled only from fixed code-controlled fragments; values are parameterized.` |
| `app/services/doc_nachweisraum_lifecycle_service.py` | 206-210 | `# nosec B608  # extra is assembled only from fixed code-controlled fragments; values are parameterized.` |
| `app/services/docflow_return_service.py` | 106 | `# nosec B608  # field and timestamp are closed constants` |
| `app/services/docflow_return_service.py` | 148 | `# nosec B608` |
| `app/services/docflow_return_service.py` | 149-157 | `# nosec B608` |
| `app/services/docflow_service.py` | 592 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/docflow_service.py` | 111-115 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/document_control_service.py` | 178 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/document_control_service.py` | 184-191 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/feed_produktion_lifecycle_service.py` | 112-116 | `# nosec B608  # update_fields is assembled only from fixed code-controlled fragments; values are parameterized.` |
| `app/services/feeding_consulting_service.py` | 30-32 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/services/feeding_feed_analysis_service.py` | 38-44 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/feeding_feed_catalog_service.py` | 164-166 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)  # noqa: S608` |
| `app/services/feeding_feed_catalog_service.py` | 35-38 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/feeding_measure_lifecycle_service.py` | 38-47 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/finance_read_model_service.py` | 593-600 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/fiscalization/service.py` | 307-321 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/foreign_goods_worklist_service.py` | 51-53 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/foreign_goods_worklist_service.py` | 59-71 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/gap_pipeline_service.py` | 368-390 | `# noqa: S608 — Filter-Klauseln sind code-kontrolliert, alle Werte parametrisiert  # nosec B608  # reviewed-safe: SQL-Fra` |
| `app/services/geo_pipeline.py` | 194-202 | `# noqa: S608 — Bezeichner aus Config, Werte parametrisiert  # nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sin` |
| `app/services/geo_pipeline.py` | 288 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/geo_pipeline.py` | 382-390 | `# noqa: S608 — status_filter ist code-kontrolliert (kein User-Input)  # nosec B608  # reviewed-safe: angehaengte SQL-Fra` |
| `app/services/interaction_state_manager.py` | 137-142 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/inventory_auxiliary_service.py` | 96 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/inventory_auxiliary_service.py` | 98-103 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/inventory_balance_reconciliation.py` | 113-119 | `# nosec B608 - Fragmente aus Modulkonstanten, Werte via Bind-Params` |
| `app/services/inventory_balance_reconciliation.py` | 124-139 | `# nosec B608 - Fragmente aus Modulkonstanten, Werte via Bind-Params` |
| `app/services/inventory_balance_reconciliation.py` | 157-168 | `# nosec B608 - Fragmente aus Modulkonstanten, Werte via Bind-Params` |
| `app/services/inventory_lot_trace_service.py` | 103-106 | `# nosec B608  # reviewed-safe` |
| `app/services/inventory_stock_balance.py` | 33-41 | `# nosec B608 - Fragment aus Modulkonstanten, Werte via Bind-Params` |
| `app/services/ist_aggregation_service.py` | 227-241 | `# noqa: S608 — alle Identifier stammen aus code-kontrollierter Config  # nosec B608  # reviewed-safe: Bezeichner stammen` |
| `app/services/knowledge_store.py` | 178-181 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/kunden_backfill.py` | 85-90 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/kunden_backfill.py` | 101-106 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/kunden_backfill.py` | 115-120 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/services/kunden_backfill.py` | 148-152 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/kunden_backfill.py` | 134-138 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/services/kunden_merge.py` | 438 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/kunden_merge.py` | 444-448 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/kunden_merge.py` | 318-327 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/kunden_merge.py` | 455-461 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/l3_report_catalog_service.py` | 411-418 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/l3_report_catalog_service.py` | 459-461 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/services/l3_report_catalog_service.py` | 466-468 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus einer Allowlist im Code, Werte sind gebunden` |
| `app/services/l3_report_catalog_service.py` | 477-485 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/l3_report_catalog_service.py` | 520-527 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/legacy_interface_adapter_service.py` | 468-470 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/legacy_interface_adapter_service.py` | 476-478 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/mail_workspace_service.py` | 132-134 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/mail_workspace_service.py` | 140-148 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/mask_rollout_summary_service.py` | 347-353 | `# nosec B608  # reviewed-safe: Schemaname stammt aus dem information_schema-Katalog, Werte sind gebunden` |
| `app/services/mask_rollout_summary_service.py` | 394-401 | `# nosec B608  # reviewed-safe: Schemaname stammt aus dem information_schema-Katalog, Werte sind gebunden` |
| `app/services/meldewesen_lifecycle_service.py` | 113-117 | `# nosec B608  # extra is assembled only from fixed code-controlled fragments; values are parameterized.` |
| `app/services/mobile_sync_service.py` | 542 | `# nosec B608  # clauses and sort are allowlisted` |
| `app/services/mobile_sync_service.py` | 547-554 | `# nosec B608  # clauses and sort are allowlisted` |
| `app/services/neuro_decision_protocol.py` | 117-123 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/personal_service.py` | 423-427 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/personal_service.py` | 145-149 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/personal_service.py` | 238-241 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/personal_service.py` | 252-259 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/personal_service.py` | 280-286 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/personal_service.py` | 297-303 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/personal_service.py` | 324-332 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/personal_service.py` | 621-625 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/personal_service.py` | 698-702 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/personal_service.py` | 817-820 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/personal_service.py` | 900-902 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/personal_service.py` | 225-228 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/personal_service.py` | 372-376 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/personal_service.py` | 458-465 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/pos_tagesabschluss_service.py` | 115-119 | `# nosec B608  # extra_fields is assembled only from fixed code-controlled fragments; values are parameterized.` |
| `app/services/production_control_service.py` | 110 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/production_control_service.py` | 114-119 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/query_center_service.py` | 207-209 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/query_center_service.py` | 215-219 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/rations_lifecycle_service.py` | 222-228 | `# nosec B608  # reviewed-safe: angehaengte SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/recent_documents_service.py` | 166-168 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/recent_documents_service.py` | 138 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/recent_documents_service.py` | 144-149 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/sales_lieferschein_close_service.py` | 94 | `# nosec B608  # set_clauses is assembled only from fixed code-controlled fragments; values are parameterized.` |
| `app/services/supply_chain_event_service.py` | 105 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/supply_chain_event_service.py` | 143-148 | `# nosec B608  # reviewed-safe: Bezeichner stammen aus Modulkonstanten, Werte sind gebunden` |
| `app/services/tank_adapter_service.py` | 279 | `# nosec B608  # Identifier aus Allowlist/festen Literalen; Werte nur gebunden (:params)` |
| `app/services/tank_adapter_service.py` | 285-287 | `# nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden` |
| `app/services/warehouse_service.py` | 91 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |
| `app/services/warehouse_service.py` | 606-616 | `# nosec B608  # reviewed-safe: column names code-controlled, values parameterized` |

## Naechste Schritte

1. `unsuppressed` beheben — Kommentar auf die Aufrufzeile verschieben.
2. `unreviewed` fachlich pruefen: Identifier aus Allowlist? Werte
   gebunden? Danach `nosec` setzen und aus der Baseline austragen.
3. Erst wenn die Baseline leer ist, ist SPEC-P1-05 erledigt.
