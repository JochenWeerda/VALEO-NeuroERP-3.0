---
title: UIX-037 Rollout-Kandidaten Readiness-Report
description: Bewertung der 10 Wave-42-51-Rollout-Kandidaten gegen verschaerfte Readiness-Gates nach UIX-033
type: reference
audience: [entwicklung, architektur, agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-29
version: 1.0.0
---

# UIX-037 — Rollout-Kandidaten Readiness-Report

> Stand: 2026-06-29 nach UIX-033 (12 Gates) und UIX-037-Fixes

## Methodik

Jeder Rollout-Kandidat (Wave 42-51) wird gegen alle 12 Readiness-Gates geprueft:
- 6 Mandatory Gates (blockieren `generatorReady`)
- 6 Advisory Gates (Score 0-100%, kein Block)

`non_temporary = true` ist bei allen Kandidaten der einzige Mandatory-Blocker — das ist der bewusste Rollout-Modus. Die Kandidaten werden per Domain-Parity-Review (analog UIX-034) einzeln auf `temporary=False` promoviert.

## Ergebnis nach UIX-037-Fixes

| Kandidat | non_temporary | adv-Score | Struktur | Bereit fuer Parity-Review |
|---|---|---|---|---|
| lager/stock-movement | FAIL (absichtlich) | 50% | OK | nach einkauf/supplier |
| lager/article-stock | FAIL (absichtlich) | 50% | OK | nach lager/stock-movement |
| finance/ap-invoice | FAIL (absichtlich) | 50% | OK | nach crm/opportunity |
| finance/ar-open-item | FAIL (absichtlich) | 50% | OK | nach finance/ap-invoice |
| einkauf/purchase-order | FAIL (absichtlich) | 50% | OK | nach einkauf/supplier |
| einkauf/supplier | FAIL (absichtlich) | 50% | OK | **Naechster: Parity-Review starten** |
| crm/opportunity | FAIL (absichtlich) | 50% | OK | nach einkauf/supplier |
| sales/delivery-note | FAIL (absichtlich) | 50% | OK | nach crm/opportunity |
| agrar/harvest-settlement | FAIL (absichtlich) | 50% | 50% | spaeter (Domain-Spezifika) |
| finance/payment-run | FAIL (absichtlich) | 50% | OK | zuletzt (Zahlungs-Risiko) |

## Was UIX-037 behoben hat

Vor diesem Fix hatten alle 10 Kandidaten **3 Mandatory Gate-Failures**:

```
FAIL non_temporary    (absichtlich — Rollout-Status)
FAIL table_data_source_bound  (kopf-Tab ohne dataSourceKey)
FAIL table_columns_complete   (kopf-Tab mit trivialcm Spalten id/bezeichnung)
```

Ursache: `kopf`-Tab wurde als `tables[]`-Tab gebaut ohne Entity-DataSource.

Behoben durch:
1. Entity-DataSource immer anlegen: `{"key": "entity", "endpoint": "{api_prefix}/{entity_id}"}`
2. `kopf`-Tab als `fields[]`-Tab (Detail-View, nicht Listenview)
3. Domain-spezifische `_ROLLOUT_KOPF_FIELDS` fuer crm/lager/finance/einkauf/sales/agrar
4. `noWorkflowReason` in allen Generator-SDs
5. `einkauf/supplier`: kontakte-Tab `sortable`+`filterable` ergaenzt

## Verbleibende Advisory-Gaps (3 pro Kandidat)

Jeder Kandidat hat noch 3 Advisory-Warnings:
- `agent_contract` — kein explizites `agentContract.businessPurpose`
- `stable_test_selectors` — kein `testSelectors.screenRoot`
- `sort_whitelist` oder `filter_columns` — je nach Tab-Konfiguration

Diese werden im Parity-Review-Prozess je Kandidat individuell behoben.

## Promotions-Prozess: Rollout → Nativ

Ein Kandidat wird von `temporary=True` auf `temporary=False` promoviert wenn:

1. Eigene `build_*_screen_definition()` Funktion (wie CRM-360/Sales/Kontrakt)
2. Alle 6 Mandatory Gates gruen (inkl. `non_temporary`)
3. `agent_contract` explizit gesetzt (Advisory → gruen)
4. `testSelectors.screenRoot` gesetzt (Advisory → gruen)
5. Parity-Matrix vs. Legacy-Maske dokumentiert
6. Backend-Tests gruen

## Promotions-Reihenfolge

```
1. einkauf/supplier        — Lieferantenstamm (Standard-Detail-Maske, kein Zahlungsrisiko)
2. crm/opportunity         — Opportunity-Cockpit (CRM-Kontext bereits bekannt)
3. lager/article-stock     — Artikelstamm (read-heavy, sicher)
4. sales/delivery-note     — Lieferschein (nach Verkaufsauftrag-Parity)
5. einkauf/purchase-order  — Bestellvorgang (nach Lieferant)
6. finance/ap-invoice      — Eingangsrechnung (nach Lieferant + Bestellung)
7. finance/ar-open-item    — Offener Posten (nach AP)
8. lager/stock-movement    — Lagerbewegung (read-only, spaeter)
9. agrar/harvest-settlement — Ernte-Abrechnung (Domain-Spezifika, vorsichtig)
10. finance/payment-run    — Zahlungslauf (hoechstes Risiko, zuletzt)
```

## Naechster Schritt: UIX-038 einkauf/supplier Parity-Review

Analog UIX-034 (CRM 360):
- Eigene `build_supplier_screen_definition()` erstellen
- Parity-Matrix vs. Legacy-Lieferantenmaske
- `temporary=False` setzen
- All Mandatory Gates gruen
- Advisory-Score > 0.5 anstreben
