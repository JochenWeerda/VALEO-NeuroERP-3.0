---
title: Prozessketten (Flow Spine)
type: reference
audience: [ki-agent, entwickler, integrator]
owner: Cursor
status: aktiv
last_reviewed: 2026-07-10
version: 3.0.0
description: End-to-End-Prozessräume mit Knoten, Masken-Deep-Links und Instanz-Lifecycle-API.
---

# Prozessketten (Flow Spine)

> Generiert aus `app/core/flow_spine_registry.py` und `docs/workflows/`.

Jeder **Flow Spine** ist ein agentenfähiger Steuerraum für eine E2E-Kette. Agenten arbeiten **instanzbasiert**: zuerst Instanz anlegen/laden, dann Knoten und verlinkte Masken bedienen.

## Instanz-Lifecycle (gemeinsam für alle 9 Prozesse)

| Aktion | Methode | Pfad |
|---|---|---|
| Instanz anlegen | POST | `/api/v1/process/flow-spines/{process_key}/instances` |
| Instanzen listen | GET | `/api/v1/process/flow-spines/{process_key}/instances` |
| Instanz laden | GET | `/api/v1/process/flow-spines/{process_key}/instances/{instance_id}` |
| Speichern | POST | `.../instances/{instance_id}/save` |
| Fortsetzen | POST | `.../instances/{instance_id}/resume` |
| Pausieren | POST | `.../instances/{instance_id}/hold` |
| Abschließen | POST | `.../instances/{instance_id}/complete` |
| Abbrechen | POST | `.../instances/{instance_id}/cancel` |
| Fehlschlagen | POST | `.../instances/{instance_id}/fail` |
| Timeline | GET | `.../instances/{instance_id}/timeline` |
| Knotenwechsel | POST | `.../instances/{instance_id}/transitions` |
| Agent-Aktion | POST | `/api/v1/process/flow-spines/{process_key}/agent-action` |

---

## Order-to-Cash (`order-to-cash`)

**Route:** `/workflow/flow-spine-order-to-cash`
**Domäne:** `sales`
**Zusammenfassung:** Vertrieb, Lieferung, Faktura und Zahlung in einem agentenfaehigen Steuerraum.

**Catalog:** `GET /api/v1/process/flow-spines/catalog`
**Workspace:** `GET /api/v1/process/flow-spines/order-to-cash`
**Workspace (Instanz):** `GET /api/v1/process/flow-spines/order-to-cash?instance_id={id}`

**Fachliche Workflow-Specs:**

- [CRM-001 — CRM-to-Revenue (Kundenmanagement bis Umsatz)](../workflows/crm-001-crm-to-revenue.md)
- [OTC-010 - Order-to-Cash End-to-End Workflow](../workflows/otc-010-order-to-cash.md) (Order-to-Cash | **Status:** abgeschlossen | **Owner:** Codex)
- [OTC-011 — Zahlungseingang und Abstimmung](../workflows/otc-011-zahlungseingang-und-abstimmung.md) (Order-to-Cash (Folge) | **Status:** abgeschlossen | **Owner:** Claude Sonnet 4.6)

### Prozessknoten → Masken → APIs

| Knoten | Status | Deep-Link | API (Primäraktion) |
|---|---|---|---|
| Auftrag | active | `/sales/orders/new` | `/api/v1/sales/orders` |
| Pruefung | ok | `/workflows/approval` | `/api/v1/process/approval-density/overview` |
| Lieferung | warning | `/sales/lieferungen` | `/api/v1/sales-shipping/delivery-notes` |
| Rechnung | warning | `/sales/invoices/new` | `/api/v1/finance/invoices` |
| Zahlung | warning | `/finance/reconciliation` | `/api/v1/finance/reconciliation` |
| Abschluss | critical | `/finance/abschluss` | `/api/v1/process/settlement/completion/evaluate` |

### Alle Knotenaktionen

#### Knoten: Auftrag

_Im Vertriebsinnendienst werden Kunde, Positionen, Mengen, Preise und Konditionen gepflegt._

- **Auftrag erfassen** → `/sales/orders/new` (API: `/api/v1/sales/orders`, Variante: primary)
- **Neukunde (Stammdaten)** → `/verkauf/kunde/neu` (API: `/api/v1/crm/customers`, Variante: secondary)
- **Kundenliste** → `/crm/kunden` (API: `/api/v1/crm/customers`, Variante: secondary)
- *Agent-Hinweis:* Mengen, Preise, Rabatte und Zusatzpositionen gehoeren in die Auftragsmaske, nicht in den Flow selbst.

#### Knoten: Pruefung

_Bonitaet, Preisregeln und Lieferfaehigkeit werden nach der Auftragserfassung bewertet._

- **Freigaben anzeigen** → `/workflows/approval` (API: `/api/v1/process/approval-density/overview`, Variante: primary)
- **Preisabweichungen pruefen** → `/sales/order` (API: `/api/v1/sales/orders`, Variante: secondary)
- *Agent-Hinweis:* Freigabe wurde policy-konform und auditierbar abgeschlossen.

#### Knoten: Lieferung

_Nach dem Auftrag werden Mengen disponiert, Lieferscheine erzeugt und die Auslieferung gesteuert._

- **Lieferschein anlegen** → `/sales/lieferungen` (API: `/api/v1/sales-shipping/delivery-notes`, Variante: primary)
- **Disposition oeffnen** → `/verladung` (API: `/api/v1/tours`, Variante: secondary)
- **Positionen pruefen** → `/sales/order` (API: `/api/v1/sales/orders`, Variante: secondary)
- *Agent-Hinweis:* Teillieferungen, Ersatzartikel und Mengenaenderungen passieren spaetestens in Disposition und Lieferschein.

#### Knoten: Rechnung

_Die Faktura zieht belastbare Liefermengen aus Lieferschein und Versandstatus._

- **Rechnung erzeugen** → `/sales/invoices/new` (API: `/api/v1/finance/invoices`, Variante: primary)
- **Lieferschein pruefen** → `/sales/lieferungen` (API: `/api/v1/sales-shipping/delivery-notes`, Variante: secondary)
- *Agent-Hinweis:* Rechnungsmenge kommt aus der gelieferten Menge, nicht aus einem separaten Workflow-Feld.

#### Knoten: Zahlung

_Nach der Faktura steuern Zahlungsziel, Skonto und Mahnstatus den Debitorenprozess._

- **Offene Posten** → `/finance/reconciliation` (API: `/api/v1/finance/reconciliation`, Variante: primary)
- **Zahlungslauf** → `/finance/zahlungslauf-kreditoren` (API: `/api/v1/finance/payment-runs`, Variante: secondary)
- *Agent-Hinweis:* Zahlung frueh terminieren, sobald Rechnung freigegeben ist.

#### Knoten: Abschluss

_Korrekturen, Gutschriften und Abschlusspruefungen folgen erst, wenn Lieferung, Faktura und Zahlung konsistent sind._

- **Abschlusspruefung** → `/finance/abschluss` (API: `/api/v1/process/settlement/completion/evaluate`, Variante: primary)
- **Gutschrift/Belastung** → `/einkauf/gutschriften-belastungen` (API: `/api/v1/credit-debit-memos`, Variante: secondary)
- *Agent-Hinweis:* Bitte Lieferabweichung und Faktura zuerst bereinigen.

### Registrierte Masken (ScreenDefinition)

- `crm/customer-360` — Kundenstamm · Contract: `GET /api/v1/masks/crm/customer-360/agent-contract` · Rollout: `/mask-rollout/crm__customer-360/:entityId`
- `crm/opportunity` — Opportunity · Contract: `GET /api/v1/masks/crm/opportunity/agent-contract` · Rollout: `/mask-rollout/crm__opportunity/:entityId`
- `finance/ar-open-item` — Offener Posten · Contract: `GET /api/v1/masks/finance/ar-open-item/agent-contract` · Rollout: `/mask-rollout/finance__ar-open-item/:entityId`
- `finance/payment-run` — Zahlungslauf · Contract: `GET /api/v1/masks/finance/payment-run/agent-contract` · Rollout: `/mask-rollout/finance__payment-run/:entityId`
- `sales/delivery-note` — Lieferschein · Contract: `GET /api/v1/masks/sales/delivery-note/agent-contract` · Rollout: `/mask-rollout/sales__delivery-note/:entityId`
- `sales/sales-order` — Verkaufsauftrag · Contract: `GET /api/v1/masks/sales/sales-order/agent-contract` · Rollout: `/mask-rollout/sales__sales-order/:entityId`

---

## Procure-to-Pay (`procure-to-pay`)

**Route:** `/workflow/flow-spine-procure-to-pay`
**Domäne:** `procurement`
**Zusammenfassung:** Bedarf, Bestellung, Wareneingang, Rechnung und Zahlung mit ETA- und Match-Fokus.

**Catalog:** `GET /api/v1/process/flow-spines/catalog`
**Workspace:** `GET /api/v1/process/flow-spines/procure-to-pay`
**Workspace (Instanz):** `GET /api/v1/process/flow-spines/procure-to-pay?instance_id={id}`

**Fachliche Workflow-Specs:**

- [P2P-001 - Procure-to-Pay Direktbestellung](../workflows/p2p-001-procure-to-pay-direktbestellung.md)
- [P2P-040 - Procure-to-Pay Vorbelegung aus Bedarfsmeldung, RFQ und Vertrag](../workflows/p2p-040-procure-to-pay-vorbelegung.md)
- [P2P-040 - Procure-to-Pay Vorbelegung aus Bedarfsmeldung, Vertrag oder RFQ](../workflows/p2p-040-vorbelegung-requisition-vertrag-rfq.md)
- [P2P-050 - Procure-to-Pay Wizard-Schrittvalidierung](../workflows/p2p-050-wizard-schrittvalidierung.md)

### Prozessknoten → Masken → APIs

| Knoten | Status | Deep-Link | API (Primäraktion) |
|---|---|---|---|
| Bedarf | ok | `/einkauf/anfragen` | `/api/v1/einkauf/anfragen` |
| Freigabe | ok | `/workflows/approval` | `/api/v1/finance/ap/approval-rules` |
| Bestellung | active | `/einkauf/bestellungen` | `/api/v1/einkauf-bestellvorschlag` |
| Wareneingang | warning | `/einkauf/wareneingang` | `/api/v1/einkauf/wareneingang` |
| Rechnung | warning | `/einkauf/rechnung-abgleich` | `/api/v1/finance/ap/invoices` |
| Zahlung | critical | `/finance/zahlungslauf-kreditoren` | `/api/v1/finance/payment-runs` |

### Alle Knotenaktionen

#### Knoten: Bedarf

_Anforderung vollstaendig mit Budgetbezug und Warengruppe._

- **Bedarf oeffnen** → `/einkauf/anfragen` (API: `/api/v1/einkauf/anfragen`, Variante: primary)
- *Agent-Hinweis:* Budget und Warengruppe sind freigabefaehig.

#### Knoten: Freigabe

_Freigabekette innerhalb der Policy abgeschlossen._

- **Freigaben** → `/workflows/approval` (API: `/api/v1/finance/ap/approval-rules`, Variante: primary)
- *Agent-Hinweis:* Freigabepfad ist policy-konform.

#### Knoten: Bestellung

_Bestellung laeuft, Liefertermin und Incoterm werden aktiv ueberwacht._

- **Bestellung oeffnen** → `/einkauf/bestellungen` (API: `/api/v1/einkauf-bestellvorschlag`, Variante: primary)
- **Lieferantenanfrage** → `/einkauf/anfragen` (API: `/api/v1/messages`, Variante: secondary)
- *Agent-Hinweis:* Expressoption oder Zweitlieferant empfohlen.

#### Knoten: Wareneingang

_Lieferfenster kippt, Expressoption und Zweitquelle verfuegbar._

- **Wareneingang** → `/einkauf/wareneingang` (API: `/api/v1/einkauf/wareneingang`, Variante: primary)
- *Agent-Hinweis:* Wareneingang und Folgeprozesse neu terminieren.

#### Knoten: Rechnung

_Preisabweichung von 1,8% erwartet, Vorpruefung empfohlen._

- **Rechnungsabgleich** → `/einkauf/rechnung-abgleich` (API: `/api/v1/finance/ap/invoices`, Variante: primary)
- *Agent-Hinweis:* Vor Freigabe die Preisabweichung pruefen.

#### Knoten: Zahlung

_Skontofenster gefaehrdet, wenn Wareneingang weiter rutscht._

- **Zahlungslauf** → `/finance/zahlungslauf-kreditoren` (API: `/api/v1/finance/payment-runs`, Variante: primary)
- *Agent-Hinweis:* Wareneingang und AP-Freigabe priorisieren.

### Registrierte Masken (ScreenDefinition)

- `einkauf/purchase-order` — Bestellung · Contract: `GET /api/v1/masks/einkauf/purchase-order/agent-contract` · Rollout: `/mask-rollout/einkauf__purchase-order/:entityId`
- `einkauf/supplier` — Lieferant · Contract: `GET /api/v1/masks/einkauf/supplier/agent-contract` · Rollout: `/mask-rollout/einkauf__supplier/:entityId`
- `finance/ap-invoice` — Eingangsrechnung · Contract: `GET /api/v1/masks/finance/ap-invoice/agent-contract` · Rollout: `/mask-rollout/finance__ap-invoice/:entityId`
- `finance/payment-run` — Zahlungslauf · Contract: `GET /api/v1/masks/finance/payment-run/agent-contract` · Rollout: `/mask-rollout/finance__payment-run/:entityId`

---

## Inventory-to-Settlement (`inventory-to-settlement`)

**Route:** `/workflow/flow-spine-inventory-to-settlement`
**Domäne:** `inventory`
**Zusammenfassung:** Lager, Versand und Settlement als gemeinsamer Operations-Flow.

**Catalog:** `GET /api/v1/process/flow-spines/catalog`
**Workspace:** `GET /api/v1/process/flow-spines/inventory-to-settlement`
**Workspace (Instanz):** `GET /api/v1/process/flow-spines/inventory-to-settlement?instance_id={id}`

**Fachliche Workflow-Specs:**

- [INV-001 — Inventory-to-Settlement End-to-End Workflow-Analyse](../workflows/inv-001-inventory-to-settlement.md) (Inventory-to-Settlement | **Status:** abgeschlossen | **Owner:** Claude Opus 4.6)

### Prozessknoten → Masken → APIs

| Knoten | Status | Deep-Link | API (Primäraktion) |
|---|---|---|---|
| Bestandsaufnahme | ok | `/lager/bestandsuebersicht` | `/api/v1/inventory` |
| Umlagerung | ok | `/lager/auslagerung` | `/api/v1/warehouses/transfers` |
| Kommissionierung | active | `/lager/terminal` | `/api/v1/pick-lists` |
| Versand | warning | `/verladung` | `/api/v1/tours` |
| Faktura | warning | `/sales/rechnungen` | `/api/v1/finance/invoices` |
| Settlement | critical | `/annahme/abrechnung` | `/api/v1/process/settlement/completion/evaluate` |

### Alle Knotenaktionen

#### Knoten: Bestandsaufnahme

_Bestand und Chargenstatus wurden ohne Differenz abgeglichen._

- **Lagerbestand** → `/lager/bestandsuebersicht` (API: `/api/v1/inventory`, Variante: primary)
- *Agent-Hinweis:* Keine Differenz im laufenden Abgleich.

#### Knoten: Umlagerung

_Umlagerung abgeschlossen, Kommissionierzone ist aufgefuellt._

- **Umlagerung** → `/lager/auslagerung` (API: `/api/v1/warehouses/transfers`, Variante: primary)
- *Agent-Hinweis:* Kommissionierzone ist bereit.

#### Knoten: Kommissionierung

_Kommissionierung laeuft, Prioritaetswelle 2 benoetigt Engpasssteuerung._

- **Kommissionierung** → `/lager/terminal` (API: `/api/v1/pick-lists`, Variante: primary)
- *Agent-Hinweis:* Engpasssteuerung oder Rampenwechsel empfohlen.

#### Knoten: Versand

_Rampenkonflikt erkannt, Umlenkung oder Zeitslot-Verschiebung empfohlen._

- **Verladung** → `/verladung` (API: `/api/v1/tours`, Variante: primary)
- *Agent-Hinweis:* Dock 4 ueberbucht, Slotwechsel fuer Welle 3 empfohlen.

#### Knoten: Faktura

_Faktura wartet auf Versandbestaetigung aus Welle 3._

- **Rechnungen** → `/sales/rechnungen` (API: `/api/v1/finance/invoices`, Variante: primary)
- *Agent-Hinweis:* Versandbestaetigung zuerst stabilisieren.

#### Knoten: Settlement

_Settlement kippt, wenn Versandfenster und Faktura nicht stabilisiert werden._

- **Settlement pruefen** → `/annahme/abrechnung` (API: `/api/v1/process/settlement/completion/evaluate`, Variante: primary)
- *Agent-Hinweis:* Versand und Faktura muessen vor T+1 stabilisiert werden.

### Registrierte Masken (ScreenDefinition)

- `lager/article-stock` — Artikelbestand · Contract: `GET /api/v1/masks/lager/article-stock/agent-contract` · Rollout: `/mask-rollout/lager__article-stock/:entityId`
- `lager/stock-movement` — Lagerbewegung · Contract: `GET /api/v1/masks/lager/stock-movement/agent-contract` · Rollout: `/mask-rollout/lager__stock-movement/:entityId`

---

## Harvest-to-Settlement (`harvest-to-settlement`)

**Route:** `/workflow/flow-spine-harvest-to-settlement`
**Domäne:** `agrar`
**Zusammenfassung:** Ernteannahme, Trocknung, Einlagerung und Abrechnung als Kampagnenfluss.

**Catalog:** `GET /api/v1/process/flow-spines/catalog`
**Workspace:** `GET /api/v1/process/flow-spines/harvest-to-settlement`
**Workspace (Instanz):** `GET /api/v1/process/flow-spines/harvest-to-settlement?instance_id={id}`

**Fachliche Workflow-Specs:**

- [VK-010 - Harvest-to-Settlement Ernte-Annahme Handover](../workflows/vk-010-ernte-annahme.md)
- [VK-011 - Qualitaets-Check Handover und LKW-Wizard-Schrittvalidierung](../workflows/vk-011-qp-handover-und-lkw-validierung.md)
- [VK-012 — Annahme-Abrechnung: Settlement-Flow-Analyse](../workflows/vk-012-annahme-abrechnung.md)
- [VK-013 - Ernte-Kampagnenabschluss](../workflows/vk-013-kampagnenabschluss.md)
- [VK-014 - Settlement-Kampagnenreferenz](../workflows/vk-014-settlement-kampagnenreferenz.md)
- [VK-015 - Settlement-Kampagnen-Backfill](../workflows/vk-015-settlement-kampagnen-backfill.md)
- [VK-016 - Queue-CTA und kanonische Artikel-API](../workflows/vk-016-queue-cta-und-artikel-api.md)
- [VK-017 - Queue-Contract mit echter article_id](../workflows/vk-017-queue-article-id.md)
- … und 3 weitere

### Prozessknoten → Masken → APIs

| Knoten | Status | Deep-Link | API (Primäraktion) |
|---|---|---|---|
| Annahme | ok | `/agrar/ernte-annahme-erfassung` | `/api/v1/agrar/harvest-acceptance` |
| Trocknung | active | `/workflow/workflow-monitoring` | `/api/v1/background-jobs/queues` |
| Einlagerung | warning | `/silo/kapazitaeten` | `/api/v1/inventory` |
| Kontrakt | warning | `/kontrakte` | `/api/v1/agrar/contracts` |
| Abrechnung | critical | `/annahme/abrechnung` | `/api/v1/agrar/settlements` |
| Zahlung | critical | `/finance/zahlungslauf-kreditoren` | `/api/v1/finance/payment-runs` |

### Alle Knotenaktionen

#### Knoten: Annahme

_Rohware angenommen, Qualitaetspruefung ohne Beanstandungen._

- **Annahme oeffnen** → `/agrar/ernte-annahme-erfassung` (API: `/api/v1/agrar/harvest-acceptance`, Variante: primary)
- *Agent-Hinweis:* Rohware und Ticket sind verknuepft.

#### Knoten: Trocknung

_Trocknung aktiv, Zielfeuchte 14% wird in 4h erreicht._

- **Trockner planen** → `/workflow/workflow-monitoring` (API: `/api/v1/background-jobs/queues`, Variante: primary)
- **Silokapazitaet pruefen** → `/silo/kapazitaeten` (API: `/api/v1/inventory`, Variante: secondary)
- *Agent-Hinweis:* Umlagerung oder Dritttrockner empfohlen.

#### Knoten: Einlagerung

_Silo 3 fast voll, Umlagerung in Silo 5 empfohlen._

- **Siloansicht** → `/silo/kapazitaeten` (API: `/api/v1/inventory`, Variante: primary)
- *Agent-Hinweis:* Einlagerung muss vor Abrechnung stabil sein.

#### Knoten: Kontrakt

_Qualitaetsabweichung erkannt, Kontraktruecksprache erforderlich._

- **Kontrakt pruefen** → `/kontrakte` (API: `/api/v1/agrar/contracts`, Variante: primary)
- *Agent-Hinweis:* Qualitaetsabweichung muss dokumentiert werden.

#### Knoten: Abrechnung

_Abrechnung kippt, wenn Trocknungsgrad nicht stabil bleibt._

- **Abrechnung pruefen** → `/annahme/abrechnung` (API: `/api/v1/agrar/settlements`, Variante: primary)
- *Agent-Hinweis:* Vor Settlement Trocknung und Kontrakt klaeren.

#### Knoten: Zahlung

_Skontofenster gefaehrdet, wenn Abrechnung weiter rutscht._

- **Zahlungslauf** → `/finance/zahlungslauf-kreditoren` (API: `/api/v1/finance/payment-runs`, Variante: primary)
- *Agent-Hinweis:* Abrechnung stabilisieren und Zahlung terminieren.

### Registrierte Masken (ScreenDefinition)

- `agrar/harvest-settlement` — Ernte-Abrechnung · Contract: `GET /api/v1/masks/agrar/harvest-settlement/agent-contract` · Rollout: `/mask-rollout/agrar__harvest-settlement/:entityId`
- `agrar/kontrakte` — Kontrakt · Contract: `GET /api/v1/masks/agrar/kontrakte/agent-contract` · Rollout: `/mask-rollout/agrar__kontrakte/:entityId`

---

## Contract-to-Settlement (`contract-to-settlement`)

**Route:** `/workflow/flow-spine-contract-to-settlement`
**Domäne:** `agrar`
**Zusammenfassung:** Kontrakt, Annahme, Qualitaet und Settlement ohne Medienbruch.

**Catalog:** `GET /api/v1/process/flow-spines/catalog`
**Workspace:** `GET /api/v1/process/flow-spines/contract-to-settlement`
**Workspace (Instanz):** `GET /api/v1/process/flow-spines/contract-to-settlement?instance_id={id}`

**Fachliche Workflow-Specs:**

- [CTS-001 — Contract-to-Settlement (Kontrakt bis Abrechnung)](../workflows/cts-001-contract-to-settlement.md)
- [CTS-009 — Rohwaren-Positionsmonitor (Long/Short)](../workflows/cts-009-rohwaren-positionsmonitor.md)

### Prozessknoten → Masken → APIs

| Knoten | Status | Deep-Link | API (Primäraktion) |
|---|---|---|---|
| Kontrakt | ok | `/kontrakte` | `/api/v1/agrar/contracts` |
| Annahme | active | `/agrar/ernte-annahme-erfassung` | `/api/v1/agrar/harvest-acceptance` |
| Qualitaet | ok | `/annahme/qualitaets-check` | `/api/v1/agrar/quality-protocols` |
| Settlement | warning | `/annahme/abrechnung` | `/api/v1/agrar/settlements` |

### Alle Knotenaktionen

#### Knoten: Kontrakt

_Lieferkontrakt ist vollstaendig digital verknuepft._

- **Kontrakt oeffnen** → `/kontrakte` (API: `/api/v1/agrar/contracts`, Variante: primary)
- *Agent-Hinweis:* Preis, Menge und Lieferfenster stimmen.

#### Knoten: Annahme

_Ernteannahme ist erfasst und referenziert den Kontrakt ohne Medienbruch._

- **Annahme bearbeiten** → `/agrar/ernte-annahme-erfassung` (API: `/api/v1/agrar/harvest-acceptance`, Variante: primary)
- *Agent-Hinweis:* Kontrakt- und Ticketbezug sind vollstaendig.

#### Knoten: Qualitaet

_Qualitaetsprotokoll liegt vor und ist der Annahme zugeordnet._

- **Qualitaet oeffnen** → `/annahme/qualitaets-check` (API: `/api/v1/agrar/quality-protocols`, Variante: primary)
- *Agent-Hinweis:* Keine Abweichung zum Kontraktprofil.

#### Knoten: Settlement

_Settlement ist vorbereitet, wartet aber auf finale Freigabe und Journal-Posting._

- **Abrechnung** → `/annahme/abrechnung` (API: `/api/v1/agrar/settlements`, Variante: primary)
- **Abschlusspruefung** → `/finance/abschluss` (API: `/api/v1/process/settlement/completion/evaluate`, Variante: secondary)
- *Agent-Hinweis:* Settlement-Journal und Abschlussvertrag zuerst pruefen.

### Registrierte Masken (ScreenDefinition)

- `agrar/harvest-settlement` — Ernte-Abrechnung · Contract: `GET /api/v1/masks/agrar/harvest-settlement/agent-contract` · Rollout: `/mask-rollout/agrar__harvest-settlement/:entityId`
- `agrar/kontrakte` — Kontrakt · Contract: `GET /api/v1/masks/agrar/kontrakte/agent-contract` · Rollout: `/mask-rollout/agrar__kontrakte/:entityId`

---

## Complaint-to-Resolution (`complaint-to-resolution`)

**Route:** `/workflow/flow-spine-complaint-to-resolution`
**Domäne:** `quality`
**Zusammenfassung:** Reklamationen End-to-End ueber CRM, DMS und Freigaben.

**Catalog:** `GET /api/v1/process/flow-spines/catalog`
**Workspace:** `GET /api/v1/process/flow-spines/complaint-to-resolution`
**Workspace (Instanz):** `GET /api/v1/process/flow-spines/complaint-to-resolution?instance_id={id}`

**Fachliche Workflow-Specs:**

- [REK-001 — Complaint-to-Resolution End-to-End Workflow-Analyse](../workflows/rek-001-complaint-to-resolution.md) (Complaint-to-Resolution | **Status:** umgesetzt | **Owner:** Claude Opus 4.6)

### Prozessknoten → Masken → APIs

| Knoten | Status | Deep-Link | API (Primäraktion) |
|---|---|---|---|
| Erfassung | ok | `/qualitaet/reklamationen` | `/api/v1/reklamationen` |
| Triage | active | `/qualitaet/reklamationen` | `/api/v1/reklamationen/REK-2026-044/transition` |
| Analyse | warning | `/dokumente/ablage` | `/api/v1/docflow` |
| Loesung | warning | `/workflows/approval` | `/api/v1/reklamationen/REK-2026-044/transition` |
| Abschluss | critical | `/admin/audit-log` | `/api/v1/reklamationen/REK-2026-044/audit` |

### Alle Knotenaktionen

#### Knoten: Erfassung

_Reklamation wurde mit CRM- und DMS-Bezug erfasst._

- **Reklamation oeffnen** → `/qualitaet/reklamationen` (API: `/api/v1/reklamationen`, Variante: primary)
- *Agent-Hinweis:* Erfassung ist vollstaendig angelegt.

#### Knoten: Triage

_Triage bewertet SLA, Ursache und Eskalationspfad._

- **Case aktualisieren** → `/qualitaet/reklamationen` (API: `/api/v1/reklamationen/REK-2026-044/transition`, Variante: primary)
- *Agent-Hinweis:* Risiko fuer Kundenabwanderung ist erhoeht.

#### Knoten: Analyse

_Dokumente, Fotos und CRM-Historie werden zusammengefuehrt._

- **DMS ansehen** → `/dokumente/ablage` (API: `/api/v1/docflow`, Variante: primary)
- *Agent-Hinweis:* Vergleich mit aehnlichen Faellen vorgeschlagen.

#### Knoten: Loesung

_Loesungsweg ist vorbereitet, Freigabe fuer Kulanz steht noch aus._

- **Freigabe senden** → `/workflows/approval` (API: `/api/v1/reklamationen/REK-2026-044/transition`, Variante: primary)
- *Agent-Hinweis:* Freigabe durch Vertrieb oder Qualitaet noetig.

#### Knoten: Abschluss

_Abschluss erfordert finalen Audit-Trail und Rueckmeldung an den Kunden._

- **Audit oeffnen** → `/admin/audit-log` (API: `/api/v1/reklamationen/REK-2026-044/audit`, Variante: primary)
- *Agent-Hinweis:* Rueckmeldung an Kunde und Abschlussbuchung fehlen.

### Registrierte Masken (ScreenDefinition)

- `qualitaet/reklamation` — Reklamation · Contract: `GET /api/v1/masks/qualitaet/reklamation/agent-contract` · Rollout: `/mask-rollout/qualitaet__reklamation/:entityId`

---

## Service-to-Customer (`service-to-customer`)

**Route:** `/workflow/flow-spine-service-to-customer`
**Domäne:** `service`
**Zusammenfassung:** Serviceanfragen, Einsatzsteuerung und Rueckmeldung in einem Arbeitsraum.

**Catalog:** `GET /api/v1/process/flow-spines/catalog`
**Workspace:** `GET /api/v1/process/flow-spines/service-to-customer`
**Workspace (Instanz):** `GET /api/v1/process/flow-spines/service-to-customer?instance_id={id}`

**Fachliche Workflow-Specs:**

- [SVC-001 — Service-to-Customer End-to-End Workflow-Analyse](../workflows/svc-001-service-to-customer.md) (Service-to-Customer | **Status:** umgesetzt | **Owner:** Claude Opus 4.6)

### Prozessknoten → Masken → APIs

| Knoten | Status | Deep-Link | API (Primäraktion) |
|---|---|---|---|
| Anfrage | ok | `/service/anfragen` | `/api/v1/crm/cases` |
| Disposition | ok | `/agribusiness/field-service-tasks` | `/api/v1/crm/cases` |
| Einsatz | active | `/agribusiness/field-service-tasks` | `/api/v1/crm/cases` |
| Rueckmeldung | warning | `/crm/aktivitaeten` | `/api/v1/crm/activities` |
| Kundenabschluss | warning | `/service/anfragen` | `/api/v1/crm/cases` |

### Alle Knotenaktionen

#### Knoten: Anfrage

_Serviceanfrage ist aufgenommen und dem Kunden zugeordnet._

- **Anfrage oeffnen** → `/service/anfragen` (API: `/api/v1/crm/cases`, Variante: primary)
- *Agent-Hinweis:* Kundendaten und Dringlichkeit sind vorhanden.

#### Knoten: Disposition

_Einsatz und Techniker wurden disponiert._

- **Disposition** → `/agribusiness/field-service-tasks` (API: `/api/v1/crm/cases`, Variante: primary)
- *Agent-Hinweis:* Termin und Fahrzeit sind innerhalb SLA.

#### Knoten: Einsatz

_Techniker ist unterwegs, Live-Rueckmeldung und ETA laufen._

- **Field Task** → `/agribusiness/field-service-tasks` (API: `/api/v1/crm/cases`, Variante: primary)
- *Agent-Hinweis:* ETA stabil, Vorbereitung auf Rueckmeldung.

#### Knoten: Rueckmeldung

_Technikerbericht ist begonnen, Materialverbrauch muss noch erfasst werden._

- **Aktivitaet buchen** → `/crm/aktivitaeten` (API: `/api/v1/crm/activities`, Variante: primary)
- *Agent-Hinweis:* Rueckmeldung vor Kundenabschluss vervollstaendigen.

#### Knoten: Kundenabschluss

_Kundenrueckmeldung und Abschlussbewertung fehlen noch._

- **Abschluss senden** → `/service/anfragen` (API: `/api/v1/crm/cases`, Variante: primary)
- *Agent-Hinweis:* Finale Rueckmeldung fuer sauberen Abschluss einholen.

### Registrierte Masken (ScreenDefinition)

- `crm/customer-360` — Kundenstamm · Contract: `GET /api/v1/masks/crm/customer-360/agent-contract` · Rollout: `/mask-rollout/crm__customer-360/:entityId`

---

## Finance-to-Close (`finance-to-close`)

**Route:** `/workflow/flow-spine-finance-to-close`
**Domäne:** `finance`
**Zusammenfassung:** Buchung, Abstimmung, Meldewesen und Abschluss als periodischer Steuerraum.

**Catalog:** `GET /api/v1/process/flow-spines/catalog`
**Workspace:** `GET /api/v1/process/flow-spines/finance-to-close`
**Workspace (Instanz):** `GET /api/v1/process/flow-spines/finance-to-close?instance_id={id}`

**Fachliche Workflow-Specs:**

- [FIN-001 — Finance-to-Close End-to-End Workflow-Analyse](../workflows/fin-001-finance-to-close.md) (Finance-to-Close | **Status:** abgeschlossen | **Owner:** Claude Sonnet 4.6)
- [FIN-001 — Finance-to-Reporting (Finanzbuchhaltung bis Abschluss)](../workflows/fin-001-finance-to-reporting.md)

### Prozessknoten → Masken → APIs

| Knoten | Status | Deep-Link | API (Primäraktion) |
|---|---|---|---|
| Buchung | ok | `/finance/bookings/new` | `/api/v1/journal-entries` |
| Abstimmung | active | `/finance/nebenbuch-abstimmung` | `/api/v1/finance/reconciliation` |
| Meldewesen | warning | `/finance/ustva` | `/api/v1/compliance/ustva` |
| Abschluss-Check | warning | `/finance/abschluss` | `/api/v1/process/settlement/completion/evaluate` |
| Genehmigung | critical | `/workflows/approval` | `/api/v1/channels/slack/process-actions/execute` |
| Abschluss | critical | `/fibu/abschluss-cockpit` | `/api/v1/finance/close-readiness` |

### Alle Knotenaktionen

#### Knoten: Buchung

_Alle Buchungen fuer Maerz sind erfasst und validiert._

- **Buchungen oeffnen** → `/finance/bookings/new` (API: `/api/v1/journal-entries`, Variante: primary)
- *Agent-Hinweis:* Periodenstart fuer den Abschluss ist sauber vorbereitet.

#### Knoten: Abstimmung

_Abstimmung laeuft, 3 Sachkonten zeigen kleine Abweichungen._

- **Nebenbuch-Abstimmung** → `/finance/nebenbuch-abstimmung` (API: `/api/v1/finance/reconciliation`, Variante: primary)
- *Agent-Hinweis:* Klaerung vor USTVA und Sign-off noetig.

#### Knoten: Meldewesen

_USTVA-Frist in 3 Tagen, Vorbereitungsgrad bei 82%._

- **USTVA oeffnen** → `/finance/ustva` (API: `/api/v1/compliance/ustva`, Variante: primary)
- *Agent-Hinweis:* Abstimmung abschliessen und Meldung vorbereiten.

#### Knoten: Abschluss-Check

_Zwei Hinweise aus Plausibilitaetspruefung, Klaerung erforderlich._

- **Abschluss pruefen** → `/finance/abschluss` (API: `/api/v1/process/settlement/completion/evaluate`, Variante: primary)
- *Agent-Hinweis:* Vor Sign-off Abschluss-Check bereinigen.

#### Knoten: Genehmigung

_Genehmigungsfrist kippt, wenn Abstimmung nicht abgeschlossen wird._

- **Sign-off anfordern** → `/workflows/approval` (API: `/api/v1/channels/slack/process-actions/execute`, Variante: primary)
- *Agent-Hinweis:* Abstimmung und Meldung zuerst stabilisieren.

#### Knoten: Abschluss

_Abschluss gefaehrdet, wenn Genehmigung und USTVA nicht rechtzeitig vorliegen._

- **Abschluss cockpit** → `/fibu/abschluss-cockpit` (API: `/api/v1/finance/close-readiness`, Variante: primary)
- *Agent-Hinweis:* Offene Vorstufen blockieren den finalen Close.

### Registrierte Masken (ScreenDefinition)

- `finance/payment-run` — Zahlungslauf · Contract: `GET /api/v1/masks/finance/payment-run/agent-contract` · Rollout: `/mask-rollout/finance__payment-run/:entityId`

---

## Compliance-to-Report (`compliance-to-report`)

**Route:** `/workflow/flow-spine-compliance-to-report`
**Domäne:** `compliance`
**Zusammenfassung:** Nachhaltigkeit, Compliance, Freigabe und Reporting als auditierbarer End-to-End-Prozess.

**Catalog:** `GET /api/v1/process/flow-spines/catalog`
**Workspace:** `GET /api/v1/process/flow-spines/compliance-to-report`
**Workspace (Instanz):** `GET /api/v1/process/flow-spines/compliance-to-report?instance_id={id}`

**Fachliche Workflow-Specs:**

- [CMP-001 — Compliance-to-Report End-to-End Workflow-Analyse](../workflows/cmp-001-compliance-to-report.md) (Compliance-to-Report | **Status:** abgeschlossen | **Owner:** Claude Opus 4.6)
- [COM-001 — Compliance-to-Audit (Meldewesen bis Pruefung)](../workflows/com-001-compliance-to-audit.md)

### Prozessknoten → Masken → APIs

| Knoten | Status | Deep-Link | API (Primäraktion) |
|---|---|---|---|
| Datensammlung | ok | `/admin/data-quality` | `/api/v1/data-quality/rules` |
| Aggregation | active | `/nachhaltigkeit/co2-bilanz` | `/api/v1/sustainability/read-model` |
| Validierung | warning | `/nachhaltigkeit/eudr-compliance` | `/api/v1/compliance/eudr` |
| Freigabe | warning | `/workflows/approval` | `/api/v1/channels/slack/process-actions/execute` |
| Reporting | critical | `/nachhaltigkeit/esg-report` | `/api/v1/sustainability/read-model` |

### Alle Knotenaktionen

#### Knoten: Datensammlung

_Datenquellen fuer Compliance und Nachhaltigkeit sind konsolidiert._

- **Datenqualitaet** → `/admin/data-quality` (API: `/api/v1/data-quality/rules`, Variante: primary)
- *Agent-Hinweis:* Keine kritischen Luecken in den Quelldaten.

#### Knoten: Aggregation

_CO2- und Compliance-Metriken werden fuer das Quartal berechnet._

- **CO2 Bilanz** → `/nachhaltigkeit/co2-bilanz` (API: `/api/v1/sustainability/read-model`, Variante: primary)
- *Agent-Hinweis:* Eine Management-Freigabe steht noch aus.

#### Knoten: Validierung

_Ein Herkunftsnachweis benoetigt manuelle Freigabe._

- **EUDR pruefen** → `/nachhaltigkeit/eudr-compliance` (API: `/api/v1/compliance/eudr`, Variante: primary)
- *Agent-Hinweis:* Vor Report-Freigabe die Ausnahme bereinigen.

#### Knoten: Freigabe

_Management-Freigabe fuer das Quartalsreporting fehlt noch._

- **Freigabe senden** → `/workflows/approval` (API: `/api/v1/channels/slack/process-actions/execute`, Variante: primary)
- *Agent-Hinweis:* Report kann nach Ausnahme-Klaerung direkt in Freigabe gehen.

#### Knoten: Reporting

_ESG- und Compliance-Report sind vorbereitet, aber noch nicht publiziert._

- **ESG Report** → `/nachhaltigkeit/esg-report` (API: `/api/v1/sustainability/read-model`, Variante: primary)
- *Agent-Hinweis:* Publikation erst nach finalem Sign-off.

---
