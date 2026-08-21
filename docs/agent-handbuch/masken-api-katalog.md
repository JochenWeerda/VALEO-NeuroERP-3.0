---
title: Masken-API-Katalog
type: reference
audience: [ki-agent, entwickler, integrator]
owner: Cursor
status: aktiv
last_reviewed: 2026-08-21
version: 3.0.0
description: ScreenDefinitions mit AgentMaskContract, REST-Endpoints und Actions.
---

# Masken-API-Katalog

> Generiert aus `app/core/screen_definitions.py` (55 Masken).

## Übersicht

| mask_id | Titel | Domäne | Risiko | Prozessketten | Agent-Contract |
|---|---|---|---|---|---|
| `agrar/duenger` | Duenger | agrar | niedrig | — | `GET /api/v1/masks/agrar/duenger/agent-contract` |
| `agrar/feed-advice` | Fuetterungsberatung | agrar | niedrig | — | `GET /api/v1/masks/agrar/feed-advice/agent-contract` |
| `agrar/feed-controlling` | Fuetterungscontrolling | agrar | niedrig | — | `GET /api/v1/masks/agrar/feed-controlling/agent-contract` |
| `agrar/feed-readiness` | Futterversorgung | agrar | niedrig | — | `GET /api/v1/masks/agrar/feed-readiness/agent-contract` |
| `agrar/feeding-actuals` | Komponentenbezogene Ist-Fuetterung | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-actuals/agent-contract` |
| `agrar/feeding-business` | Fuetterungsbetrieb | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-business/agent-contract` |
| `agrar/feeding-businesses` | Fuetterungsbetriebe | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-businesses/agent-contract` |
| `agrar/feeding-group` | Tiergruppe | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-group/agent-contract` |
| `agrar/feeding-plan` | Fuetterungsplan | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-plan/agent-contract` |
| `agrar/feeding-reference-data` | Naehrstoffe und Einheiten | agrar | niedrig | — | `GET /api/v1/masks/agrar/feeding-reference-data/agent-contract` |
| `agrar/harvest-settlement` | Ernte-Abrechnung | agrar | niedrig | `harvest-to-settlement`, `contract-to-settlement` | `GET /api/v1/masks/agrar/harvest-settlement/agent-contract` |
| `agrar/kontrakte` | Kontrakt | agrar | niedrig | `contract-to-settlement`, `harvest-to-settlement` | `GET /api/v1/masks/agrar/kontrakte/agent-contract` |
| `agrar/ration` | Rationsfreigabe | agrar | hoch | — | `GET /api/v1/masks/agrar/ration/agent-contract` |
| `agrar/rations-lifecycle` | Rationen und Freigaben | agrar | niedrig | — | `GET /api/v1/masks/agrar/rations-lifecycle/agent-contract` |
| `agrar/saatgut` | Saatgut | agrar | niedrig | — | `GET /api/v1/masks/agrar/saatgut/agent-contract` |
| `auswertungen/abfrage-center` | Abfrage-Center | reporting | mittel | — | `GET /api/v1/masks/auswertungen/abfrage-center/agent-contract` |
| `auswertungen/beleg-kontrolle` | Beleg-Kontrolle | finance | niedrig | — | `GET /api/v1/masks/auswertungen/beleg-kontrolle/agent-contract` |
| `crm/customer-360` | Kundenstamm | crm | niedrig | `order-to-cash`, `service-to-customer` | `GET /api/v1/masks/crm/customer-360/agent-contract` |
| `crm/lead` | Lead | crm | niedrig | — | `GET /api/v1/masks/crm/lead/agent-contract` |
| `crm/mail-arbeitsplatz` | Mail-Arbeitsplatz | crm | niedrig | — | `GET /api/v1/masks/crm/mail-arbeitsplatz/agent-contract` |
| `crm/opportunity` | Opportunity | crm | niedrig | `order-to-cash` | `GET /api/v1/masks/crm/opportunity/agent-contract` |
| `docflow/dokumenten-ruecklauf` | Dokumentenruecklauf | dms-compliance | niedrig | — | `GET /api/v1/masks/docflow/dokumenten-ruecklauf/agent-contract` |
| `einkauf/anfrage` | Einkaufsanfrage | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/anfrage/agent-contract` |
| `einkauf/angebot` | Lieferantenangebot | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/angebot/agent-contract` |
| `einkauf/anlieferavis` | Anlieferavis | einkauf | mittel | — | `GET /api/v1/masks/einkauf/anlieferavis/agent-contract` |
| `einkauf/auftragsbestaetigung` | Auftragsbestaetigung | einkauf | niedrig | — | `GET /api/v1/masks/einkauf/auftragsbestaetigung/agent-contract` |
| `einkauf/purchase-order` | Bestellung | einkauf | niedrig | `procure-to-pay` | `GET /api/v1/masks/einkauf/purchase-order/agent-contract` |
| `einkauf/supplier` | Lieferant | einkauf | niedrig | `procure-to-pay` | `GET /api/v1/masks/einkauf/supplier/agent-contract` |
| `finance/ap-invoice` | Eingangsrechnung | finance | mittel | `procure-to-pay` | `GET /api/v1/masks/finance/ap-invoice/agent-contract` |
| `finance/ar-open-item` | Offener Posten | finance | mittel | `order-to-cash` | `GET /api/v1/masks/finance/ar-open-item/agent-contract` |
| `finance/bankkonto` | Bankkonto | finance | niedrig | — | `GET /api/v1/masks/finance/bankkonto/agent-contract` |
| `finance/debitor` | Debitor | finance | niedrig | — | `GET /api/v1/masks/finance/debitor/agent-contract` |
| `finance/kreditor` | Kreditor | finance | niedrig | — | `GET /api/v1/masks/finance/kreditor/agent-contract` |
| `finance/payment-run` | Zahlungslauf | finance | niedrig | `procure-to-pay`, `order-to-cash`, `finance-to-close` | `GET /api/v1/masks/finance/payment-run/agent-contract` |
| `finance/rechnungstapel` | Rechnungstapel | finance | niedrig | — | `GET /api/v1/masks/finance/rechnungstapel/agent-contract` |
| `futtermittel/analyse` | Futteranalyse | futtermittel | hoch | — | `GET /api/v1/masks/futtermittel/analyse/agent-contract` |
| `futtermittel/analysen` | Futteranalysen | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/analysen/agent-contract` |
| `futtermittel/einzelfuttermittel` | Einzelfuttermittel | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/einzelfuttermittel/agent-contract` |
| `futtermittel/mischfuttermittel` | Mischfuttermittel | futtermittel | niedrig | — | `GET /api/v1/masks/futtermittel/mischfuttermittel/agent-contract` |
| `lager/article-stock` | Artikelbestand | lager | niedrig | `inventory-to-settlement` | `GET /api/v1/masks/lager/article-stock/agent-contract` |
| `lager/fremdware` | Fremdware und Fremdbestand | inventory | niedrig | — | `GET /api/v1/masks/lager/fremdware/agent-contract` |
| `lager/inventur-nebenlaeufe` | Inventur-Nebenlaeufe | inventory | hoch | — | `GET /api/v1/masks/lager/inventur-nebenlaeufe/agent-contract` |
| `lager/leitstand` | Lager-Leitstand | lager | niedrig | — | `GET /api/v1/masks/lager/leitstand/agent-contract` |
| `lager/stock-movement` | Lagerbewegung | lager | hoch | `inventory-to-settlement` | `GET /api/v1/masks/lager/stock-movement/agent-contract` |
| `planung/kalender` | Planungskalender | platform | mittel | — | `GET /api/v1/masks/planung/kalender/agent-contract` |
| `produktion/produktionsleitstand` | Produktionsleitstand | agrar | mittel | — | `GET /api/v1/masks/produktion/produktionsleitstand/agent-contract` |
| `qualitaet/reklamation` | Reklamation | qualitaet | mittel | `complaint-to-resolution` | `GET /api/v1/masks/qualitaet/reklamation/agent-contract` |
| `sales/delivery-note` | Lieferschein | sales | niedrig | `order-to-cash` | `GET /api/v1/masks/sales/delivery-note/agent-contract` |
| `sales/sales-order` | Verkaufsauftrag | sales | niedrig | `order-to-cash` | `GET /api/v1/masks/sales/sales-order/agent-contract` |
| `schnittstelle/mde-inbox` | MDE-Eingangskorb | platform | mittel | — | `GET /api/v1/masks/schnittstelle/mde-inbox/agent-contract` |
| `workspace/einkauf` | Einkauf-Cockpit | einkauf | niedrig | — | `GET /api/v1/masks/workspace/einkauf/agent-contract` |
| `workspace/fibu` | FIBU-Cockpit | finance | niedrig | — | `GET /api/v1/masks/workspace/fibu/agent-contract` |
| `workspace/lager` | Lager-Cockpit | lager | niedrig | — | `GET /api/v1/masks/workspace/lager/agent-contract` |
| `workspace/leitung` | Leitungs-Cockpit | management | niedrig | — | `GET /api/v1/masks/workspace/leitung/agent-contract` |
| `workspace/verkauf` | Verkauf-Cockpit | sales | niedrig | — | `GET /api/v1/masks/workspace/verkauf/agent-contract` |

---

## Domäne: agrar

### `agrar/duenger` — Duenger

**Zweck:** Duenger-Stammdaten: Naehrstoffgehalte, Verwendungshistorie und Preise fuer Duengungsplanung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/duenger/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/duenger/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/duenger/readiness` |
| Rollout-Route | `/mask-rollout/agrar__duenger/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/agrar/duenger/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/agrar/duenger/entity/{entity_id}`
- `verwendung` → `/api/v1/masks/agrar/duenger/entity/{entity_id}/tabs/verwendung`
- `preise` → `/api/v1/masks/agrar/duenger/entity/{entity_id}/tabs/preise`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Naehrstoffgehalte hat Duenger {entity_id}?
- Zeige die Preisentwicklung von Duenger {entity_id}.

**Sensible Felder:** `preis`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `agrar/feed-advice` — Fuetterungsberatung

**Zweck:** Aufgabenorientierter Einstieg in Planung, Freigabe, Stallausfuehrung und Controlling der Fuetterung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feed-advice/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feed-advice/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feed-advice/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feed-advice/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Ration braucht heute Aufmerksamkeit?
- Wo fehlen aktuelle Analysen oder ausreichend Bestand?
- Zeige mir den schnellsten Weg zur heutigen Fuetterung.

**Sensible Felder:** `futterkosten, milchleistung`

---

### `agrar/feed-controlling` — Fuetterungscontrolling

**Zweck:** Aufnahme, Kosten, Milch/ECM, Stickstoff und Methan je Tiergruppe im Zeitverlauf vergleichen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feed-controlling/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feed-controlling/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feed-controlling/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feed-controlling/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `series` → `/api/v1/agrar/rations-optimization/controlling/series`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Gruppe weicht bei der Aufnahme ab?
- Wie entwickeln sich ECM und Futterkosten?

**Sensible Felder:** `actual_cost_eur_cow`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `record_observation` | Tageswerte erfassen | safe | nein | `—` |

---

### `agrar/feed-readiness` — Futterversorgung

**Zweck:** Planbedarf, Sicherheitsreserve und Bestandsreichweite erklaerbar vergleichen und Unterdeckungen kontrolliert an den Einkauf geben.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feed-readiness/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feed-readiness/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feed-readiness/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feed-readiness/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `materials` → `/api/v1/agrar/rations-optimization/feeding/supply`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Futtermittel reichen weniger als 14 Tage?
- Welche Unterdeckungen sind wegen unbekannter Handelseinheiten noch nicht uebergabefaehig?

**Sensible Felder:** `stock_kg`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `create_handoff` | An Einkauf uebergeben | confirm | nein | `—` |
| `open_inventory` | Bestaende pflegen | safe | nein | `—` |

---

### `agrar/feeding-actuals` — Komponentenbezogene Ist-Fuetterung

**Zweck:** Komponentenabweichungen und ihre Kosten-/Naehrstofffolgen planversionsgebunden erklaeren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-actuals/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-actuals/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-actuals/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-actuals/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `actuals` → `/api/v1/agrar/rations-optimization/feeding/actuals/components`
- `findings` → `/api/v1/agrar/rations-optimization/feeding/actuals/findings`
- `measures` → `/api/v1/agrar/rations-optimization/feeding/actuals/measures`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Komponenten wurden heute ueberdosiert?
- Bei welchen Ist-Fuetterungen fehlen Preise oder Naehrstoffwerte?

**Sensible Felder:** `comment, value_consequences`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `export_csv` | CSV exportieren | safe | nein | `—` |
| `create_measure` | Massnahme aus Abweichung | confirm | nein | `—` |
| `configure_threshold` | Schwellen konfigurieren | confirm | nein | `—` |
| `open_mobile` | Ist-Fuetterung erfassen | safe | nein | `—` |

---

### `agrar/feeding-business` — Fuetterungsbetrieb

**Zweck:** Die naechste fachliche Fuetterungsentscheidung aus belastbarer Datenlage ableiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-business/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-business/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-business/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-business/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}/overview`
- `groups` → `/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}/groups`
- `rations` → `/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}/rations`
- `findings` → `/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}/findings`
- `templates` → `/api/v1/agrar/rations-optimization/feeding/businesses/{entity_id}/ration-templates`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Ration ist blockiert?
- Wo fehlt eine belastbare Analyse?
- Welche Befunde sind kritisch?

**Sensible Felder:** `business_partner_id, preferences, snapshot_checksum`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `create_template` | Vorlage anlegen | safe | nein | `—` |
| `apply_template` | Vorlage anwenden | safe | nein | `—` |

---

### `agrar/feeding-businesses` — Fuetterungsbetriebe

**Zweck:** Autorisierte Fuetterungsbetriebe und ihre Beratungsreife steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-businesses/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-businesses/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-businesses/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-businesses/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `businesses` → `/api/v1/agrar/rations-optimization/feeding/businesses`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Betriebe betreue ich?
- Wo fehlen Herden oder Tiergruppen?

**Sensible Felder:** `business_partner_id, preferences`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `create_business` | Betrieb anlegen | safe | nein | `—` |

---

### `agrar/feeding-group` — Tiergruppe

**Zweck:** Tiergruppenparameter und ihre zeitliche Herkunft sicher pflegen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-group/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-group/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-group/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-group/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/lifecycle/groups/{entity_id}`
- `history` → `/api/v1/agrar/rations-optimization/lifecycle/groups/{entity_id}/history`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige die aktuelle Leistung der Tiergruppe.
- Welche Parameter wurden zuletzt geaendert?

**Sensible Felder:** `business_id, herd_id, external_ref`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit_group` | Tiergruppe bearbeiten | safe | nein | `—` |

---

### `agrar/feeding-plan` — Fuetterungsplan

**Zweck:** Eine publizierte Mischanweisung sicher ausfuehren und ihre Herkunft nachweisen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-plan/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-plan/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-plan/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-plan/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/feeding/plans/{entity_id}`
- `instructions` → `/api/v1/agrar/rations-optimization/feeding/plans/{entity_id}/instructions`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Menge kommt als Naechstes?
- Ist dieser Plan noch aktuell?
- Warum wurde gerundet?

**Sensible Felder:** `source_ration_version_id, published_by`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `print_plan` | Drucken / als PDF speichern | safe | nein | `—` |
| `open_mobile` | Mobile Stallansicht | safe | nein | `—` |

---

### `agrar/feeding-reference-data` — Naehrstoffe und Einheiten

**Zweck:** Einheiten, Bezugsbasen und Naehrstoffherkunft fuer Berechnung und Beratung erklaerbar machen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/feeding-reference-data/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/feeding-reference-data/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/feeding-reference-data/readiness` |
| Rollout-Route | `/mask-rollout/agrar__feeding-reference-data/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `nutrients` → `/api/v1/agrar/rations-optimization/reference-data/nutrients`
- `units` → `/api/v1/agrar/rations-optimization/reference-data/units`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- In welcher Einheit wird Rohprotein bewertet?
- Welche Naehrstoffe sind auf TM bezogen?

---

### `agrar/harvest-settlement` — Ernte-Abrechnung

**Zweck:** Ernte-Abrechnung: Erzeuger-Abrechnung mit Lieferschein-Positionen, Qualitaets-Abzuegen und Gesamtbetrag fuer Agrar-Buchhalter.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/harvest-settlement/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/harvest-settlement/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/harvest-settlement/readiness` |
| Rollout-Route | `/mask-rollout/agrar__harvest-settlement/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/agrar/settlements/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/agrar/settlements/{entity_id}`
- `positionen` → `/api/v1/mask-rollouts/agrar/harvest-settlement/{entity_id}/tabs/positionen`
- `abzuege` → `/api/v1/mask-rollouts/agrar/harvest-settlement/{entity_id}/tabs/abzuege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der Gesamtbetrag und Status der Ernte-Abrechnung {entity_id}?
- Zeige alle Lieferschein-Positionen und Qualitaets-Abzuege von Abrechnung {entity_id}.

**Sensible Felder:** `gesamtbetrag`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `drucken` | Abrechnung drucken | safe | nein | `/api/v1/agrar/harvest-settlements/{entity_id}/actions/drucken` |

---

### `agrar/kontrakte` — Kontrakt

**Zweck:** Agrar-Kontrakt-Cockpit: Positionen (Sorte, Menge, Preis) und Umsaetze fuer Erzeuger-Vertragsmanagement.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/kontrakte/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/kontrakte/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/kontrakte/readiness` |
| Rollout-Route | `/mask-rollout/agrar__kontrakte/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/kontrakte/{contract_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/kontrakte/{entity_id}`
- `positionen` → `/api/v1/kontrakte/{entity_id}/tabs/positionen`
- `umsaetze` → `/api/v1/kontrakte/{entity_id}/tabs/umsaetze`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der Erfuellungsstand von Kontrakt {entity_id}?
- Zeige alle Lieferschein-Umsaetze fuer Kontrakt {entity_id}.
- Welche Sorten und Mengen sind in Kontrakt {entity_id} vereinbart?

**Sensible Felder:** `preis`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `agrar/ration` — Rationsfreigabe

**Zweck:** Eine Rationsversion pruefen, freigeben, terminieren, aktivieren oder revisionssicher beenden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/ration/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/ration/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/ration/readiness` |
| Rollout-Route | `/mask-rollout/agrar__ration/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}`
- `versions` → `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/versions`
- `audit` → `/api/v1/agrar/rations-optimization/lifecycle/rations/{entity_id}/audit`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Warum wurde diese Ration freigegeben?
- Wann beginnt die Fuetterung dieser Version?

**Sensible Felder:** `snapshot, snapshot_checksum`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `submit_review` | Zur Pruefung | safe | nein | `—` |
| `approve` | Freigeben | moderate | ja | `—` |
| `schedule` | Fuetterungsbeginn planen | moderate | nein | `—` |
| `activate` | Jetzt aktivieren | moderate | ja | `—` |
| `retire` | Fuetterung beenden | high | nein | `—` |
| `archive` | Archivieren | high | nein | `—` |

---

### `agrar/rations-lifecycle` — Rationen und Freigaben

**Zweck:** Rationsversionen nach Tiergruppe, Status und Fuetterungsbeginn steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/rations-lifecycle/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/rations-lifecycle/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/rations-lifecycle/readiness` |
| Rollout-Route | `/mask-rollout/agrar__rations-lifecycle/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `rations` → `/api/v1/agrar/rations-optimization/lifecycle/rations`
- `groups` → `/api/v1/agrar/rations-optimization/lifecycle/groups`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Rationen warten auf Freigabe?
- Welche Ration ist je Tiergruppe aktiv?

**Sensible Felder:** `snapshot_checksum`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `plan_ration` | Neue Ration planen | safe | nein | `—` |
| `create_group` | Tiergruppe anlegen | safe | nein | `—` |

---

### `agrar/saatgut` — Saatgut

**Zweck:** Saatgut-Stammdaten: Sorteninfo, Lagerbestaende und Anbauvertraege fuer Saatgutplanung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/agrar/saatgut/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/agrar/saatgut/agent-contract` |
| Readiness | `GET /api/v1/masks/agrar/saatgut/readiness` |
| Rollout-Route | `/mask-rollout/agrar__saatgut/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/agrar/saatgut/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/agrar/saatgut/entity/{entity_id}`
- `lagerbestaende` → `/api/v1/masks/agrar/saatgut/entity/{entity_id}/tabs/lagerbestaende`
- `vertraege` → `/api/v1/masks/agrar/saatgut/entity/{entity_id}/tabs/vertraege`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Lagerbestaende hat Saatgut {entity_id}?
- Zeige alle Anbauvertraege fuer Saatgut {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `produktion/produktionsleitstand` — Produktionsleitstand

**Zweck:** Produktionsvorgaenge aus kanonischen Auftraegen und Bewegungen steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/produktion/produktionsleitstand/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/produktion/produktionsleitstand/agent-contract` |
| Readiness | `GET /api/v1/masks/produktion/produktionsleitstand/readiness` |
| Rollout-Route | `/mask-rollout/produktion__produktionsleitstand/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/production-control/summary`
- `operations` → `/api/v1/production-control/operations`

**MCP-Tools (Domäne):**

- `agrar.contract.get` — scope `agrar:read`, Risiko niedrig
- `agrar.weighing_ticket.list` — scope `agrar:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige laufende Muehlenauftraege.
- Welche Vorgaenge brauchen Nachbearbeitung?

**Sensible Felder:** `assigned_user, notes`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `sync` | Auftraege synchronisieren | moderate | nein | `/api/v1/production-control/sync` |

---

## Domäne: crm

### `crm/customer-360` — Kundenstamm

**Zweck:** 360-Grad-Kundenstamm-Cockpit fuer Vertrieb und CRM — Stammdaten, Aktivitaeten, offene Auftraege und Dokumente in einer Ansicht.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/customer-360/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/customer-360/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/customer-360/readiness` |
| Rollout-Route | `/mask-rollout/crm__customer-360/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/crm/customers/{customer_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/crm/customers/{entity_id}`
- `contacts` → `/api/v1/crm/customers/{entity_id}/tabs/contacts`
- `auftraege` → `/api/v1/crm/customers/{entity_id}/tabs/auftraege`
- `aktivitaeten` → `/api/v1/crm/customers/{entity_id}/tabs/aktivitaeten`
- `dokumente` → `/api/v1/crm/customers/{entity_id}/tabs/dokumente`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Analysiere Kunde {entity_id}: offene Posten, letzte Aktivitaeten, Umsatz 12M.
- Lege eine Aktivitaet fuer Kunde {entity_id} an — Betreff: {betreff}, Typ: Anruf.
- Zeige alle offenen Auftraege von Kunde {entity_id} mit Status 'offen'.

**Sensible Felder:** `kreditlimit, zahlungsbedingungen, notizen`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |
| `create_activity` | Aktivitaet anlegen | safe | nein | `/api/v1/crm/customers/{entity_id}/actions/create_activity` |

---

### `crm/lead` — Lead

**Zweck:** Lead-Cockpit: Kundenpotenzial mit Aktivitaeten und Aufgaben fuer Vertriebssteuerung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/lead/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/lead/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/lead/readiness` |
| Rollout-Route | `/mask-rollout/crm__lead/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/crm/leads/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/crm/lead/entity/{entity_id}`
- `aktivitaeten` → `/api/v1/masks/crm/leads/entity/{entity_id}/tabs/aktivitaeten`
- `aufgaben` → `/api/v1/masks/crm/leads/entity/{entity_id}/tabs/aufgaben`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Was ist der Status von Lead {entity_id}?
- Zeige alle offenen Aufgaben fuer Lead {entity_id}.
- Welche Aktivitaeten wurden fuer Lead {entity_id} erfasst?

**Sensible Felder:** `wert`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |
| `qualifizieren` | Als Opportunity qualifizieren | safe | nein | `/api/v1/crm/leads/{entity_id}/actions/qualifizieren` |

---

### `crm/mail-arbeitsplatz` — Mail-Arbeitsplatz

**Zweck:** Rollenpostfaecher revisionssicher mit Kontakten und Belegen verbinden.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/mail-arbeitsplatz/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/mail-arbeitsplatz/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/mail-arbeitsplatz/readiness` |
| Rollout-Route | `/mask-rollout/crm__mail-arbeitsplatz/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `messages` → `/api/v1/mail-workspace`
- `attachments` → `/api/v1/mail-workspace/attachments`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Zeige unzugeordnete CRM-Mails.
- Welche Anlagen warten auf DMS-Uebernahme?

**Sensible Felder:** `from_address, to_addresses, subject, body_text, contact_id`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `draft` | Neue Mail | low | nein | `—` |

---

### `crm/opportunity` — Opportunity

**Zweck:** CRM-Verkaufschance: Phase, Wert, Wahrscheinlichkeit, Aktivitaeten und Angebote in einer Ansicht fuer Vertriebssteuerung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/crm/opportunity/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/crm/opportunity/agent-contract` |
| Readiness | `GET /api/v1/masks/crm/opportunity/readiness` |
| Rollout-Route | `/mask-rollout/crm__opportunity/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/crm/opportunities/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/crm/opportunities/{entity_id}`
- `aktivitaeten` → `/api/v1/mask-rollouts/crm/opportunity/{entity_id}/tabs/aktivitaeten`
- `angebote` → `/api/v1/mask-rollouts/crm/opportunity/{entity_id}/tabs/angebote`

**MCP-Tools (Domäne):**

- `crm.customer.search` — scope `crm:read`, Risiko niedrig
- `crm.customer.summary360` — scope `crm:read`, Risiko niedrig
- `crm.contact.log` — scope `crm:write`, Risiko mittel

**Beispiel-Prompts:**

- Was ist der aktuelle Status und die Wahrscheinlichkeit von Opportunity {entity_id}?
- Zeige alle Aktivitaeten der letzten 30 Tage fuer Opportunity {entity_id}.
- Welche Angebote sind mit Opportunity {entity_id} verknuepft?

**Sensible Felder:** `wert, wahrscheinlichkeit`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |
| `create_activity` | Aktivitaet anlegen | safe | nein | `/api/v1/crm/opportunities/{entity_id}/actions/create_activity` |

---

## Domäne: dms-compliance

### `docflow/dokumenten-ruecklauf` — Dokumentenruecklauf

**Zweck:** Dokumentenversand und erwartete Ruecklaeufe mandantensicher bearbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/docflow/dokumenten-ruecklauf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/docflow/dokumenten-ruecklauf/agent-contract` |
| Readiness | `GET /api/v1/masks/docflow/dokumenten-ruecklauf/readiness` |
| Rollout-Route | `/mask-rollout/docflow__dokumenten-ruecklauf/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/docflow/returns/summary`
- `returns` → `/api/v1/docflow/returns`

**Beispiel-Prompts:**

- Zeige ueberfaellige Ruecklaeufe.
- Welche Dokumente wurden noch nicht versendet?

**Sensible Felder:** `contact_ref, subject_ref, storage_key`

---

## Domäne: einkauf

### `einkauf/anfrage` — Einkaufsanfrage

**Zweck:** Einkaufsanfrage: Kopfdaten und Positionen fuer Beschaffungsanfragen an Lieferanten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/anfrage/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/anfrage/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/anfrage/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__anfrage/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/einkauf/anfragen/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/einkauf/anfrage/entity/{entity_id}`
- `positionen` → `/api/v1/masks/einkauf/anfragen/entity/{entity_id}/tabs/positionen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der Status von Anfrage {entity_id}?
- Zeige alle Positionen von Anfrage {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `einkauf/angebot` — Lieferantenangebot

**Zweck:** Lieferantenangebot: Preise und Positionen fuer Angebotsvergleich und Bestellentscheidung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/angebot/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/angebot/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/angebot/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__angebot/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/einkauf/angebote/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/einkauf/angebot/entity/{entity_id}`
- `positionen` → `/api/v1/masks/einkauf/angebote/entity/{entity_id}/tabs/positionen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig

**Beispiel-Prompts:**

- Wie lange ist Angebot {entity_id} gueltig?
- Zeige alle Positionen und Preise von Angebot {entity_id}.

**Sensible Felder:** `gesamtbetrag, einzelpreis`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `bestellen` | Bestellung erstellen | safe | nein | `/api/v1/einkauf/bestellungen/{entity_id}/actions/bestellen` |

---

### `einkauf/anlieferavis` — Anlieferavis

**Zweck:** Anlieferavis: Ankuendigung eines Wareneingangs mit Positionen und Lieferdatum.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/anlieferavis/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/anlieferavis/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/anlieferavis/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__anlieferavis/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/einkauf/anlieferavise/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/einkauf/anlieferavis/entity/{entity_id}`
- `positionen` → `/api/v1/masks/einkauf/anlieferavise/entity/{entity_id}/tabs/positionen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig

**Beispiel-Prompts:**

- Wann ist Avis {entity_id} angekuendigt?
- Zeige alle Positionen von Avis {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `wareneingang` | Wareneingang buchen | moderate | nein | `/api/v1/lager/artikel/{entity_id}/actions/wareneingang` |

---

### `einkauf/auftragsbestaetigung` — Auftragsbestaetigung

**Zweck:** Auftragsbestaetigung: Lieferanten-Rueckmeldung auf Bestellung mit zugesagtem Liefertermin.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/auftragsbestaetigung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/auftragsbestaetigung/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/auftragsbestaetigung/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__auftragsbestaetigung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/einkauf/auftragsbestaetigungen/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/einkauf/auftragsbestaetigung/entity/{entity_id}`
- `positionen` → `/api/v1/masks/einkauf/auftragsbestaetigungen/entity/{entity_id}/tabs/positionen`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig

**Beispiel-Prompts:**

- Wann hat Lieferant den Liefertermin fuer AB {entity_id} zugesagt?
- Zeige alle Positionen von AB {entity_id}.

**Sensible Felder:** `einzelpreis`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `einkauf/purchase-order` — Bestellung

**Zweck:** Einkaufs-Bestellung: Kopfdaten, Positionen und Kommunikation fuer Beschaffungssteuerung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/purchase-order/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/purchase-order/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/purchase-order/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__purchase-order/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/einkauf/bestellungen/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/einkauf/bestellungen/{entity_id}`
- `positionen` → `/api/v1/mask-rollouts/einkauf/purchase-order/{entity_id}/tabs/positionen`
- `kommunikation` → `/api/v1/mask-rollouts/einkauf/purchase-order/{entity_id}/tabs/kommunikation`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der Status von Bestellung {entity_id} und wann ist der Liefertermin?
- Zeige alle Positionen und bestellten Mengen von Bestellung {entity_id}.

**Sensible Felder:** `zahlungsbedingungen, betrag`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `einkauf/supplier` — Lieferant

**Zweck:** Lieferantenstamm-Cockpit fuer Einkauf — Stammdaten, offene Bestellungen und Ansprechpartner in einer Ansicht.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/einkauf/supplier/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/einkauf/supplier/agent-contract` |
| Readiness | `GET /api/v1/masks/einkauf/supplier/readiness` |
| Rollout-Route | `/mask-rollout/einkauf__supplier/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/einkauf/lieferanten/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/einkauf/lieferanten/{entity_id}`
- `bestellungen` → `/api/v1/mask-rollouts/einkauf/supplier/{entity_id}/tabs/bestellungen`
- `kontakte` → `/api/v1/mask-rollouts/einkauf/supplier/{entity_id}/tabs/kontakte`

**MCP-Tools (Domäne):**

- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige alle offenen Bestellungen von Lieferant {entity_id} mit Status 'offen'.
- Welche Ansprechpartner gibt es bei Lieferant {entity_id}?
- Wie sind die Zahlungsbedingungen und Lieferzeiten von Lieferant {entity_id}?

**Sensible Felder:** `zahlungsbedingungen, lieferzeit_tage`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |
| `neue_bestellung` | Bestellung anlegen | safe | nein | `/api/v1/einkauf/lieferanten/{entity_id}/actions/neue_bestellung` |

---

### `workspace/einkauf` — Einkauf-Cockpit

**Zweck:** Rollen-Startseite Einkauf — offene Bestellungen, Avis und Preisabweichungen mit direktem Sprung in die Prozessmasken.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/einkauf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/einkauf/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/einkauf/readiness` |
| Rollout-Route | `/mask-rollout/workspace__einkauf/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `einkauf.bestellung.list` — scope `einkauf:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was steht heute in Einkauf-Cockpit an?
- Zeige die dringendsten Worklists fuer meine Rolle.

---

## Domäne: finance

### `auswertungen/beleg-kontrolle` — Beleg-Kontrolle

**Zweck:** Belegausnahmen mandantensicher priorisieren und zum Ursprungsbeleg springen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/beleg-kontrolle/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/beleg-kontrolle/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/beleg-kontrolle/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__beleg-kontrolle/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/document-control/summary`
- `exceptions` → `/api/v1/document-control/exceptions`

**MCP-Tools (Domäne):**

- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige nicht fakturierte Lieferscheine.
- Welche Bestellungen sind unerledigt?
- Welche Belegausnahmen sind ueberfaellig?

**Sensible Felder:** `partner_name, partner_ref, notes`

---

### `finance/ap-invoice` — Eingangsrechnung

**Zweck:** Eingangsrechnung: Kopfdaten, Positionen und Freigabe-Historie fuer AP-Buchhalter und Audit.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/ap-invoice/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/ap-invoice/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/ap-invoice/readiness` |
| Rollout-Route | `/mask-rollout/finance__ap-invoice/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/finance/ap/invoices/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/finance/ap/invoices/{entity_id}`
- `positionen` → `/api/v1/mask-rollouts/finance/ap-invoice/{entity_id}/tabs/positionen`
- `freigabe` → `/api/v1/mask-rollouts/finance/ap-invoice/{entity_id}/tabs/freigabe`

**MCP-Tools (Domäne):**

- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der Freigabe-Status von Eingangsrechnung {entity_id}?
- Wann ist Eingangsrechnung {entity_id} faellig und wie hoch ist der Bruttobetrag?

**Sensible Felder:** `brutto, mwst, faellig_am`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `freigeben` | Freigeben | moderate | nein | `/api/v1/finance/ap/invoices/{entity_id}/actions/freigeben` |

---

### `finance/ar-open-item` — Offener Posten

**Zweck:** Offener Posten: Forderungs-Cockpit fuer Debitorenbuchhaltung mit Faelligkeiten, Skonto und Ausgleichshistorie.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/ar-open-item/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/ar-open-item/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/ar-open-item/readiness` |
| Rollout-Route | `/mask-rollout/finance__ar-open-item/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/finance/open-items/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/finance/open-items/{entity_id}`
- `ausgleich` → `/api/v1/mask-rollouts/finance/ar-open-item/{entity_id}/tabs/ausgleich`

**MCP-Tools (Domäne):**

- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Wann ist OP {entity_id} faellig und wie hoch ist der offene Betrag?
- Zeige alle bisherigen Zahlungseingaenge fuer OP {entity_id}.

**Sensible Felder:** `brutto, offen, skonto, faellig_am`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `mahnen` | Mahnung erstellen | moderate | nein | `/api/v1/finance/open-items/{entity_id}/actions/mahnen` |

---

### `finance/bankkonto` — Bankkonto

**Zweck:** Bankkonto-Stamm: Kontodaten und Buchungshistorie fuer Finanzbuchhaltung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/bankkonto/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/bankkonto/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/bankkonto/readiness` |
| Rollout-Route | `/mask-rollout/finance__bankkonto/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/finance/bankkonten/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/finance/bankkonto/entity/{entity_id}`
- `buchungen` → `/api/v1/masks/finance/bankkonten/entity/{entity_id}/tabs/buchungen`

**MCP-Tools (Domäne):**

- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der aktuelle Saldo von Bankkonto {entity_id}?
- Zeige die letzten Buchungen auf Bankkonto {entity_id}.

**Sensible Felder:** `konto_nr, iban, bic, saldo`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `finance/debitor` — Debitor

**Zweck:** Debitoren-Stammdaten: Kreditlimit, offene Posten und Umsatzhistorie fuer Debitorenbuchhaltung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/debitor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/debitor/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/debitor/readiness` |
| Rollout-Route | `/mask-rollout/finance__debitor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/finance/debitoren/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/finance/debitor/entity/{entity_id}`
- `offene_posten` → `/api/v1/masks/finance/debitoren/entity/{entity_id}/tabs/offene-posten`
- `umsaetze` → `/api/v1/masks/finance/debitoren/entity/{entity_id}/tabs/umsaetze`

**MCP-Tools (Domäne):**

- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist das Kreditlimit von Debitor {entity_id}?
- Zeige alle offenen Posten von Debitor {entity_id}.

**Sensible Felder:** `kreditlimit, steuernummer, ust_id`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `finance/kreditor` — Kreditor

**Zweck:** Kreditoren-Stammdaten: Zahlungsbedingungen, offene Posten und Bestellhistorie fuer Kreditorenbuchhaltung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/kreditor/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/kreditor/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/kreditor/readiness` |
| Rollout-Route | `/mask-rollout/finance__kreditor/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/finance/kreditoren/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/finance/kreditor/entity/{entity_id}`
- `offene_posten` → `/api/v1/masks/finance/kreditoren/entity/{entity_id}/tabs/offene-posten`
- `bestellungen` → `/api/v1/masks/finance/kreditoren/entity/{entity_id}/tabs/bestellungen`

**MCP-Tools (Domäne):**

- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche offenen Posten hat Kreditor {entity_id}?
- Zeige alle Bestellungen bei Kreditor {entity_id}.

**Sensible Felder:** `iban, steuernummer, ust_id`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `finance/payment-run` — Zahlungslauf

**Zweck:** Zahlungslauf-Cockpit (read-only fuer Agenten): Laufdetails und Einzelzahlungen fuer Audit und Reconciliation. Freigabe ist Agent-gesperrt.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/payment-run/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/payment-run/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/payment-run/readiness` |
| Rollout-Route | `/mask-rollout/finance__payment-run/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/finance/payment-runs/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/finance/payment-runs/{entity_id}`
- `zahlungen` → `/api/v1/mask-rollouts/finance/payment-run/{entity_id}/tabs/zahlungen`

**MCP-Tools (Domäne):**

- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der Status von Zahlungslauf {entity_id} und wie hoch ist der Gesamtbetrag?
- Zeige alle Einzelzahlungen von Zahlungslauf {entity_id} mit Status 'fehler'.

**Sensible Felder:** `gesamtbetrag, bank`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `freigeben` | Zahlungslauf freigeben | critical | ja | `/api/v1/finance/payment-runs/{entity_id}/actions/freigeben` |

---

### `finance/rechnungstapel` — Rechnungstapel

**Zweck:** Rechnungs- und Selbstabrechnungsstapel nachvollziehbar abarbeiten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/finance/rechnungstapel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/finance/rechnungstapel/agent-contract` |
| Readiness | `GET /api/v1/masks/finance/rechnungstapel/readiness` |
| Rollout-Route | `/mask-rollout/finance__rechnungstapel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/billing-batches/summary`
- `batches` → `/api/v1/billing-batches`
- `errors` → `/api/v1/billing-batches/lines?status=failed`

**MCP-Tools (Domäne):**

- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Fehlerzeilen im Rechnungstapel.
- Welche Selbstabrechner warten auf Freigabe?

**Sensible Felder:** `validation_error, source_ref, maker, checker`

---

### `workspace/fibu` — FIBU-Cockpit

**Zweck:** Rollen-Startseite FIBU — offene Posten, faellige Zahlungen und Mahnstufen mit Sprung in Zahlungslauf und OP-Masken.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/fibu/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/fibu/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/fibu/readiness` |
| Rollout-Route | `/mask-rollout/workspace__fibu/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `fibu.open_items.list` — scope `finance:read`, Risiko niedrig
- `fibu.dunning.status` — scope `finance:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was steht heute in FIBU-Cockpit an?
- Zeige die dringendsten Worklists fuer meine Rolle.

---

## Domäne: futtermittel

### `futtermittel/analyse` — Futteranalyse

**Zweck:** Laborbefund nachvollziehbar pruefen und genau eine Analyseversion bewusst aktivieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/analyse/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/analyse/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/analyse/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__analyse/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}`
- `values` → `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/values`
- `findings` → `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/findings`
- `history` → `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/history`

**Beispiel-Prompts:**

- Welche Blocker verhindern die Freigabe?
- Zeige Original- und Rechenwerte dieser Analyse.

**Sensible Felder:** `original_document_id, original_sha256`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `validate` | Plausibilitaet pruefen | safe | nein | `—` |
| `release` | Analyse freigeben | high | ja | `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/actions/release` |
| `reject` | Zurueckweisen | moderate | nein | `/api/v1/agrar/rations-optimization/feed-analyses/{entity_id}/actions/reject` |

---

### `futtermittel/analysen` — Futteranalysen

**Zweck:** Futteranalysen nach Plausibilitaet, Freigabe und Aktualitaet priorisieren.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/analysen/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/analysen/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/analysen/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__analysen/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `list` → `/api/v1/agrar/rations-optimization/feed-analyses`

**Beispiel-Prompts:**

- Welche Analysen warten auf Pruefung?
- Welche aktiven Analysen sind veraltet?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `import_analysis` | Analyse erfassen | safe | nein | `—` |

---

### `futtermittel/einzelfuttermittel` — Einzelfuttermittel

**Zweck:** Einzelfuttermittel-Stamm: Naehrstoffgehalte und Preise fuer Rationsoptimierung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/einzelfuttermittel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/einzelfuttermittel/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/einzelfuttermittel/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__einzelfuttermittel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}`
- `naehrstoffe` → `/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}/reference-values`
- `preise` → `/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}/products`
- `history` → `/api/v1/agrar/rations-optimization/feed-catalog/feeds/{entity_id}/history`

**Beispiel-Prompts:**

- Welche NEL und Rohprotein-Gehalte hat Futtermittel {entity_id}?
- Zeige die aktuellen Preise fuer Futtermittel {entity_id}.

**Sensible Felder:** `preis`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `futtermittel/mischfuttermittel` — Mischfuttermittel

**Zweck:** Mischfuttermittel: Rezeptur-Komponenten und berechnete Naehrstoffgehalte fuer Rationsoptimierung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/futtermittel/mischfuttermittel/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/futtermittel/mischfuttermittel/agent-contract` |
| Readiness | `GET /api/v1/masks/futtermittel/mischfuttermittel/readiness` |
| Rollout-Route | `/mask-rollout/futtermittel__mischfuttermittel/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/futtermittel/mischfuttermittel/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/futtermittel/mischfuttermittel/entity/{entity_id}`
- `rezeptur` → `/api/v1/masks/futtermittel/mischfuttermittel/entity/{entity_id}/tabs/rezeptur`
- `naehrstoffe` → `/api/v1/masks/futtermittel/mischfuttermittel/entity/{entity_id}/tabs/naehrstoffe`

**Beispiel-Prompts:**

- Welche Komponenten hat Mischfutter {entity_id}?
- Zeige die berechneten Naehrstoffgehalte von Mischfutter {entity_id}.

**Sensible Felder:** `preis_je_t`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

## Domäne: inventory

### `lager/fremdware` — Fremdware und Fremdbestand

**Zweck:** Fremde Ware eigentuemer- und mandantensicher im Lager steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/fremdware/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/fremdware/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/fremdware/readiness` |
| Rollout-Route | `/mask-rollout/lager__fremdware/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/foreign-goods/summary`
- `items` → `/api/v1/foreign-goods`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Zeige Fremdbestand nach Eigentuemer.
- Welche Einlagerungen sind ueberfaellig?

**Sensible Felder:** `tenant_id, eigentuemer_id, eigentuemer_name, lagerort, notiz`

---

### `lager/inventur-nebenlaeufe` — Inventur-Nebenlaeufe

**Zweck:** Inventur-Nebenlaeufe hashgebunden und im Vier-Augen-Prinzip steuern.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/inventur-nebenlaeufe/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/inventur-nebenlaeufe/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/inventur-nebenlaeufe/readiness` |
| Rollout-Route | `/mask-rollout/lager__inventur-nebenlaeufe/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/inventory/auxiliary/summary`
- `batches` → `/api/v1/inventory/auxiliary/batches`

**MCP-Tools (Domäne):**

- `wms.lot.trace` — scope `inventory:read`, Risiko niedrig
- `wms.cell.status` — scope `inventory:read`, Risiko niedrig

**Beispiel-Prompts:**

- Erzeuge einen Kontrolllauf.
- Welche Bestandsvortraege warten auf Freigabe?

**Sensible Felder:** `maker, checker, source_hash`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `create_count_sheet` | Zaehlliste | low | nein | `—` |
| `create_control` | Kontrolllauf | low | nein | `—` |
| `create_valuation` | Vorlaeufig bewerten | low | nein | `—` |
| `create_opening` | Bestandsvortrag | high | nein | `—` |

---

## Domäne: lager

### `lager/article-stock` — Artikelbestand

**Zweck:** Artikelbestand-Cockpit: Stammdaten, Bestand je Lagerort und Bewegungshistorie fuer Disposition und Einkauf.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/article-stock/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/article-stock/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/article-stock/readiness` |
| Rollout-Route | `/mask-rollout/lager__article-stock/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/articles/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/articles/{entity_id}`
- `bestand` → `/api/v1/mask-rollouts/lager/article-stock/{entity_id}/tabs/bestand`
- `bewegungen` → `/api/v1/mask-rollouts/lager/article-stock/{entity_id}/tabs/bewegungen`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig

**Beispiel-Prompts:**

- Wie hoch ist der aktuelle Bestand von Artikel {entity_id} je Lagerort?
- Zeige alle Lagerbewegungen von Artikel {entity_id} der letzten 30 Tage.
- Welche Lagerorte haben Bestand unter Mindestbestand fuer Artikel {entity_id}?

**Sensible Felder:** `mindestbestand, meldebestand`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `lager/leitstand` — Lager-Leitstand

**Zweck:** Physische Silozellen-Belegung, Fuellstand und QS-Sperren als klickbares Werkzeug im Lager-Leitstand anzeigen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/leitstand/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/leitstand/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/leitstand/readiness` |
| Rollout-Route | `/mask-rollout/lager__leitstand/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig

**Beispiel-Prompts:**

- Welche Silozellen sind gesperrt?
- Zeige den Fuellstand im Lager-Leitstand.
- Welche Zelle ist ueber 90 Prozent belegt?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `refresh` | Aktualisieren | safe | nein | `—` |

---

### `lager/stock-movement` — Lagerbewegung

**Zweck:** Lagerbewegung: Einzelne Warenbewegung mit Belegpositionen fuer Lager-Audit und Traceability.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/lager/stock-movement/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/lager/stock-movement/agent-contract` |
| Readiness | `GET /api/v1/masks/lager/stock-movement/readiness` |
| Rollout-Route | `/mask-rollout/lager__stock-movement/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/inventory/stock-movements/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/inventory/stock-movements/{entity_id}`
- `details` → `/api/v1/mask-rollouts/lager/stock-movement/{entity_id}/tabs/details`

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was ist der Status und Typ von Lagerbewegung {entity_id}?
- Zeige alle Positionen und betroffenen Lagerorte von Bewegung {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `stornieren` | Stornieren | high | ja | `/api/v1/lager/stock-movements/{entity_id}/actions/stornieren` |

---

### `workspace/lager` — Lager-Cockpit

**Zweck:** Rollen-Startseite Lager — Annahmen, Wartezeiten und Trocknerauslastung mit Sprung in Bestands- und Qualitaetsmasken.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/lager/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/lager/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/lager/readiness` |
| Rollout-Route | `/mask-rollout/workspace__lager/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `lager.bestand.get` — scope `lager:read`, Risiko niedrig
- `lager.inventur.status` — scope `lager:read`, Risiko niedrig

**Beispiel-Prompts:**

- Was steht heute in Lager-Cockpit an?
- Zeige die dringendsten Worklists fuer meine Rolle.

---

## Domäne: management

### `workspace/leitung` — Leitungs-Cockpit

**Zweck:** Rollen-Startseite Leitung — Umsatz, Rohertrag und Top-Ausnahmen mit Sprung in Eskalations- und Audit-Ansichten.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/leitung/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/leitung/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/leitung/readiness` |
| Rollout-Route | `/mask-rollout/workspace__leitung/:entityId` |
| Adapter | `native` (temporary=nein) |

**Beispiel-Prompts:**

- Was steht heute in Leitungs-Cockpit an?
- Zeige die dringendsten Worklists fuer meine Rolle.

---

## Domäne: platform

### `planung/kalender` — Planungskalender

**Zweck:** Zeitbezogene Fristen, Wiedervorlagen und Laeufe ohne Doppelpflege als Planungscockpit sichtbar machen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/planung/kalender/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/planung/kalender/agent-contract` |
| Readiness | `GET /api/v1/masks/planung/kalender/readiness` |
| Rollout-Route | `/mask-rollout/planung__kalender/:entityId` |
| Adapter | `native` (temporary=nein) |

**Beispiel-Prompts:**

- Was steht naechste Woche an?
- Zeige Fristen der naechsten 14 Tage.
- Welche OP-Faelligkeiten kommen diese Woche?
- Zeige die Frei/Belegt-Sicht meines Teams.
- Blende abgelehnte Termine ein.

**Sensible Felder:** `owner_id, team_id, title, payload, object_route`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `reproject` | Neu projizieren | moderate | nein | `/api/v1/planung/kalender/reproject` |

---

### `schnittstelle/mde-inbox` — MDE-Eingangskorb

**Zweck:** MDE-Ereignisse mandantenbezogen ueberwachen und fehlgeschlagene Verarbeitung nachvollziehbar behandeln.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/schnittstelle/mde-inbox/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/schnittstelle/mde-inbox/agent-contract` |
| Readiness | `GET /api/v1/masks/schnittstelle/mde-inbox/readiness` |
| Rollout-Route | `/mask-rollout/schnittstelle__mde-inbox/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/mobile/sync-summary`
- `queue` → `/api/v1/mobile/sync-queue`

**Beispiel-Prompts:**

- Zeige MDE-Ereignisse in Quarantaene.
- Welche Inventurzaehlungen sind fehlgeschlagen?
- Welche Geraete liefern aktuell Fehler?

**Sensible Felder:** `error_message, idempotency_key`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `process_pending` | Ausstehende verarbeiten | moderate | nein | `/api/v1/mobile/sync-process` |

---

## Domäne: qualitaet

### `qualitaet/reklamation` — Reklamation

**Zweck:** Reklamation: Qualitaetsmaengel mit Massnahmen und Dokumenten fuer Reklamationsbearbeitung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/qualitaet/reklamation/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/qualitaet/reklamation/agent-contract` |
| Readiness | `GET /api/v1/masks/qualitaet/reklamation/readiness` |
| Rollout-Route | `/mask-rollout/qualitaet__reklamation/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/masks/qualitaet/reklamationen/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/masks/qualitaet/reklamation/entity/{entity_id}`
- `massnahmen` → `/api/v1/masks/qualitaet/reklamationen/entity/{entity_id}/tabs/massnahmen`
- `dokumente` → `/api/v1/masks/qualitaet/reklamationen/entity/{entity_id}/tabs/dokumente`

**Beispiel-Prompts:**

- Was ist der Status von Reklamation {entity_id}?
- Zeige alle offenen Massnahmen von Reklamation {entity_id}.

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |
| `abschliessen` | Abschliessen | moderate | nein | `/api/v1/reklamationen/{entity_id}/actions/abschliessen` |

---

## Domäne: reporting

### `auswertungen/abfrage-center` — Abfrage-Center

**Zweck:** Freigegebene Read Models ohne beliebiges SQL anwendergerecht abfragen.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/auswertungen/abfrage-center/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/auswertungen/abfrage-center/agent-contract` |
| Readiness | `GET /api/v1/masks/auswertungen/abfrage-center/readiness` |
| Rollout-Route | `/mask-rollout/auswertungen__abfrage-center/:entityId` |
| Adapter | `native` (temporary=nein) |

**Data Sources:**

- `entity` → `/api/v1/query-center/catalog`
- `definitions` → `/api/v1/query-center`

**Beispiel-Prompts:**

- Zeige meine favorisierten Abfragen.
- Erstelle eine begrenzte Vorschau offener Rechnungen.

**Sensible Felder:** `filter_spec, selected_fields`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `create` | Neue Abfrage | low | nein | `—` |
| `import` | Signiert importieren | moderate | nein | `—` |

---

## Domäne: sales

### `sales/delivery-note` — Lieferschein

**Zweck:** Lieferschein-Cockpit: Kopfdaten, Positionen und Dokumente fuer Warenausgang und Lieferverfolgung.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/delivery-note/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/delivery-note/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/delivery-note/readiness` |
| Rollout-Route | `/mask-rollout/sales__delivery-note/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/sales/delivery-notes/{entity_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/sales/delivery-notes/{entity_id}`
- `positionen` → `/api/v1/mask-rollouts/sales/delivery-note/{entity_id}/tabs/positionen`
- `dokumente` → `/api/v1/mask-rollouts/sales/delivery-note/{entity_id}/tabs/dokumente`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Zeige alle Positionen und Chargen von Lieferschein {entity_id}.
- Welche Dokumente sind mit Lieferschein {entity_id} verknuepft?
- Was ist der aktuelle Status von Lieferschein {entity_id}?

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `drucken` | Lieferschein drucken | safe | nein | `/api/v1/sales/delivery-notes/{entity_id}/actions/drucken` |

---

### `sales/sales-order` — Verkaufsauftrag

**Zweck:** Verkaufsauftrag-Cockpit: Kopfdaten, Positionen, Lieferscheine und Dokumente fuer Auftragsabwicklung und Kundenkommunikation.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/sales/sales-order/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/sales/sales-order/agent-contract` |
| Readiness | `GET /api/v1/masks/sales/sales-order/readiness` |
| Rollout-Route | `/mask-rollout/sales__sales-order/:entityId` |
| Adapter | `native` (temporary=nein) |

**Summary:** `/api/v1/sales/orders/{order_id}/screen-summary`

**Data Sources:**

- `entity` → `/api/v1/sales/orders/{entity_id}`
- `positionen` → `/api/v1/sales/orders/{entity_id}/tabs/positionen`
- `lieferung` → `/api/v1/sales/orders/{entity_id}/tabs/lieferung`
- `dokumente` → `/api/v1/sales/orders/{entity_id}/tabs/dokumente`

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Was ist der Status von Auftrag {entity_id} und welche Positionen sind noch offen?
- Welche Lieferscheine wurden fuer Auftrag {entity_id} erstellt?
- Zeige alle Dokumente von Auftrag {entity_id}.

**Sensible Felder:** `einzelpreis, betrag`

**Actions:**

| key | label | danger | Human-Approval | commandEndpoint |
|---|---|---|---|---|
| `edit` | Bearbeiten | safe | nein | `—` |

---

### `workspace/verkauf` — Verkauf-Cockpit

**Zweck:** Rollen-Startseite Verkauf — Auftragsbestand, Ueberfaellige und Kreditlimit-Warnungen mit Sprung in Auftrags- und CRM-Masken.

| | |
|---|---|
| ScreenDefinition | `GET /api/v1/masks/workspace/verkauf/screen-definition` |
| Agent-Contract | `GET /api/v1/masks/workspace/verkauf/agent-contract` |
| Readiness | `GET /api/v1/masks/workspace/verkauf/readiness` |
| Rollout-Route | `/mask-rollout/workspace__verkauf/:entityId` |
| Adapter | `native` (temporary=nein) |

**MCP-Tools (Domäne):**

- `sales.order.status` — scope `sales:read`, Risiko niedrig
- `sales.invoice.propose` — scope `sales:write`, Risiko hoch

**Beispiel-Prompts:**

- Was steht heute in Verkauf-Cockpit an?
- Zeige die dringendsten Worklists fuer meine Rolle.

---
