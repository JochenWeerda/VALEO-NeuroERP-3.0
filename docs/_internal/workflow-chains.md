---
title: Workflow-Ketten-Registry (intern)
type: reference
audience: [entwickler, product, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Workflow-Ketten-Registry (intern)

Kanonische Zuordnung von **Flow-Spine / Lane → Cards in Prozessreihenfolge**.
Cards sind intern (`docs/cards/`, MkDocs-ausgeschlossen); diese Datei ist die
**Source of Truth** für Kettenlogik. Detail-Analysen liegen in `docs/workflows/`.

**Maschinelle Pflege:** `scripts/cards-inventory-audit.py` (Registry + Frontmatter).
**Offene Fix-Slices:** `docs/agent-ops/active-workboard.md` (CARD-AUDIT-Follow-up).

---

## Benennungsregeln

| Präfix | Bedeutung | Nummerierung |
|--------|-----------|--------------|
| `OTC`, `P2P`, `FIN`, `INV`, `CTS`, `REK`, `CMP`, `SVC`, `CRM` | End-to-End-Lane | `010` Overview/Kern, `011+` Folgeschritte |
| `VK` | Harvest-to-Settlement (historisch „Verkauf", faktisch Annahme) | sequenziell entlang Kette |
| `SEC`, `NC`, `INT-SG` | Querschnitt (keine Prozesskette) | unabhängig |
| `DOM-*` | Domänen-Vertiefung | Bezug zur Domäne |

**Card-Frontmatter** (optional, empfohlen):

```yaml
---
card_id: VK-011
chain: harvest-to-settlement
chain_step: 2
card_type: process-step          # overview | process-step | cross-cutting | hardening
parent_card: VK-010
related_cards: [VK-018, VK-012]
flow_spine: flow-spine-harvest-to-settlement
workflow_doc: docs/workflows/vk-011-qp-handover-und-lkw-validierung.md
overlaps: [SEC-029]
---
```

---

## 1. Harvest-to-Settlement (`harvest-to-settlement`)

| Step | Card | Rolle | Vor | Nach |
|------|------|-------|-----|------|
| 0 | VK-010-ernte-annahme | Overview / Gesamtkette | — | VK-011 |
| 1 | VK-010-ernte-annahme-standardmaske | Spezialmaske (Detail) | VK-010 | VK-011 |
| 2 | VK-011-qp-handover-und-lkw-validierung | LKW-Wizard + QP-Handover | VK-010 | VK-012 |
| 3 | VK-016-queue-cta-und-artikel-api | Queue-CTA + Artikel-API | VK-011 | VK-012 |
| 4 | VK-017-queue-article-id | QR-Artikel-Auflösung | VK-016 | VK-012 |
| 5 | VK-019-queue-repair-article-id | Repair article_id | VK-017 | VK-012 |
| 6 | VK-018-klaerungsprozess-gesperrt | Klärung gesperrte Ware | VK-011 | — |
| 7 | VK-012-annahme-abrechnung | Abrechnung / Settlement | VK-011 | VK-013 |
| 8 | VK-013-kampagnenabschluss | Kampagnenabschluss | VK-012 | VK-014 |
| 9 | VK-014-settlement-kampagnenreferenz | Kampagnenreferenz | VK-013 | VK-015 |
| 10 | VK-015-settlement-kampagnen-backfill | Backfill Bestand | VK-014 | — |
| 11 | VK-020-rohware-wizard-schrittvalidierung | Rohware-Wizard | VK-011 | VK-012 |

- **Workflow:** [vk-010-ernte-annahme.md](../workflows/vk-010-ernte-annahme.md)
- **Flow-Spine:** `Harvest-to-Settlement`
- **Querschnitt:** SEC-029 (Agrar Contracts)
- **Offen (Workboard):** Barcode-Scanner-Platzhalter (VK-010 Follow-up, P3)

---

## 2. Order-to-Cash (`order-to-cash`)

| Step | Card | Rolle | Vor | Nach |
|------|------|-------|-----|------|
| 0 | OTC-010-order-to-cash | Overview + Kernkette | — | OTC-011 |
| 1 | OTC-011-zahlungseingang-und-abstimmung | Zahlung / OP-Abstimmung | OTC-010 | — |

- **Workflow:** [otc-010-order-to-cash.md](../workflows/otc-010-order-to-cash.md), [otc-011-zahlungseingang-und-abstimmung.md](../workflows/otc-011-zahlungseingang-und-abstimmung.md)
- **Flow-Spine:** `flow-spine-order-to-cash`
- **Querschnitt:** SEC-031, SEC-032, SEC-023–025
- **Offen (Workboard):** OTC-010-P1 Positionen Auftrag→LS, OTC-010-P2 source_order_id, OTC-010-P3 Rechnungsroute

---

## 3. Procure-to-Pay (`procure-to-pay`)

| Step | Card | Rolle | Vor | Nach |
|------|------|-------|-----|------|
| 0 | *(fehlt: P2P-010 Overview)* | — | — | P2P-020 |
| 1 | P2P-020-direktbestellung-standardmaske | Direktbestellung | Flow-Spine | P2P-040 |
| 2 | P2P-040-vorbelegung-standardmaske | Vorbelegung Standard | P2P-020 | P2P-041 |
| 3 | P2P-041-vorbelegung-aus-anfrage-und-vertrag | Vorbelegung Anfrage/Vertrag | P2P-040 | — |
| — | P2P-050-wizard-schrittvalidierung | Querschnitt Wizard | alle P2P | — |

- **Workflow:** [p2p-001-procure-to-pay-direktbestellung.md](../workflows/p2p-001-procure-to-pay-direktbestellung.md)
- **Flow-Spine:** `flow-spine-procure-to-pay`
- **Querschnitt:** SEC-008, INT-SG-057
- **Offen (Workboard):** P2P-010 Overview-Card anlegen; Inline-Fehler Wizard (P2P-020 Follow-up)

---

## 4. Finance-to-Close / Reporting (`finance-to-close`)

| Step | Card | Rolle | Vor | Nach |
|------|------|-------|-----|------|
| 0 | FIN-001-finance-to-close | Overview Abschluss | — | — |
| 0b | FIN-001-finance-to-reporting | Overview Reporting | — | — |

- **Workflow:** [fin-001-finance-to-close.md](../workflows/fin-001-finance-to-close.md)
- **Flow-Spine:** `flow-spine-finance-to-close`
- **Querschnitt:** SEC-006, SEC-020, SEC-021, SEC-022
- **Offen (Workboard):** Abschluss-Stubs calculate/lock/run (P1); Journal-Pfad reports.tsx

---

## 5. Inventory-to-Settlement (`inventory-to-settlement`)

| Step | Card | Rolle |
|------|------|-------|
| 0 | INV-001-inventory-to-settlement | Overview Lager-Kette |

- **Workflow:** [inv-001-inventory-to-settlement.md](../workflows/inv-001-inventory-to-settlement.md)
- **Querschnitt:** SEC-027, WM-* Slices

---

## 6. Contract-to-Settlement (`contract-to-settlement`)

| Step | Card | Rolle |
|------|------|-------|
| 0 | CTS-001-contract-to-settlement | Overview |
| 1 | CTS-009-rohwaren-positionsmonitor | Positionsmonitor |

- **Flow-Spine:** `flow-spine-contract-to-settlement`
- **Querschnitt:** SEC-029, DOM-CON-003

---

## 7. Complaint-to-Resolution (`complaint-to-resolution`)

| Step | Card | Rolle |
|------|------|-------|
| 0 | REK-001-complaint-to-resolution | Overview Reklamation |

- **Workflow:** [rek-001-complaint-to-resolution.md](../workflows/rek-001-complaint-to-resolution.md)
- **Flow-Spine:** `flow-spine-complaint-to-resolution`

---

## 8. Compliance-to-Report / Audit

| Step | Card | Rolle |
|------|------|-------|
| 0 | CMP-001-compliance-to-report | Meldewesen → Report |
| 0b | COM-001-compliance-to-audit | Audit-Spine |

- **Flow-Spine:** `flow-spine-compliance-to-report`
- **Offen (Workboard):** CMP ustva Client; COM CamelCase Register; Flow-Spine workflowInstanceId

---

## 9. Service-to-Customer (`service-to-customer`)

| Step | Card | Rolle |
|------|------|-------|
| 0 | SVC-001-service-to-customer | Overview Service |

---

## 10. CRM-to-Revenue (ohne eigener Spine)

| Step | Card | Rolle | related_chain |
|------|------|-------|---------------|
| 0 | CRM-001-crm-to-revenue | CRM → Umsatz | order-to-cash |

- **Offen (Workboard):** Legacy `/api/crm/` → `/api/v1/crm/`

---

## Querschnitt-Familien (keine Kette)

| Familie | Anzahl | Bezug |
|---------|--------|-------|
| SEC-* | 33 | Security-Hardening; `applies_to` in Card oder Roadmap |
| NC-* / INT-SG-* | 52+ | Neuro-Core / Superglue Plattform |
| DOM-*-003 | 6 | Domänen-Deepening |

---

## Überschneidungs-Matrix (Auszug)

| Card A | Card B | Art |
|--------|--------|-----|
| VK-010 | VK-011 | Parent/Child + sequenziell |
| VK-011 | VK-018 | Verzweigung (gesperrt) |
| OTC-010 | OTC-011 | Folgeprozess |
| OTC-010 | SEC-031 | Querschnitt ∩ Domäne |
| CRM-001 | OTC-010 | Einstieg ohne eigenen Spine |
| P2P-050 | P2P-020 | Querschnitt innerhalb Lane |

---

## Pflege

1. Neue Prozess-Card: Frontmatter `chain` + `chain_step` setzen; Zeile in dieser Datei.
2. `python scripts/cards-inventory-audit.py` — prüft unzugeordnete Cards.
3. Abgeschlossene Gaps → Workboard-Slice schließen + Card-Status aktualisieren.
