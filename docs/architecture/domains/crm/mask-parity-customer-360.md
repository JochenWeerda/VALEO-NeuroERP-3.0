---
title: CRM Customer 360 — Mask Parity Matrix
type: reference
audience: [agent, entwickler, fachlich]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-29
version: 1.1.0
description: Paritaetsmatrix Legacy-Kundenmaske vs. Universal Mask Generator (CRM 360 Pilot); Native-Runtime siehe UIX-034.
---

# CRM Customer 360 — Paritaetsmatrix

Referenz fuer Wave 27 (`UIX-CRM-PARITY-003`). Spalten: Legacy-Tab, Generator-Tab, Felder/Liste, API, Status.

> **Native Runtime (UIX-028/034):** Detaillierte Legacy-vs.-Native-Matrix mit Readiness-Gates:
> [`uix-034-crm360-native-parity-matrix.md`](../../../adr/uix-034-crm360-native-parity-matrix.md)

**Legende:** `ok` = funktional abgedeckt | `partial` = read-only Teilmenge | `gap` = noch nicht im Generator

| Legacy-Tab (mask-builder-customer.json) | Generator-Tab | Felder / Liste | API | RenderPlan | Status |
|---|---|---|---|---|---|
| Stammdaten (`masterdata`) | `masterdata` | Stammdaten-Felder | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Adresse & Kommunikation (`address`) | `address` | Adress-/Kommunikationsfelder | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| System (`system`) | `system` | Metadaten, Sperren, Notizen | `GET /api/v1/crm/customers/{id}` | compiled | partial |
| Steuern (`tax`) | `tax` | Steuerkennzeichen | `GET /api/v1/crm/customers/{id}` | compiled | partial |
| Qualitaet / Compliance (`quality_compliance`) | `quality_compliance` | Farm-IDs, DSGVO | `GET /api/v1/crm/customers/{id}` | compiled | partial |
| Finanzen (`finance`) | `finance` | Felder + Offene Posten (Liste) | Summary + `GET .../tabs/dokumente` | lazy table | partial |
| Bank (`bank`) | `bank` | Bankverbindungen | `GET /api/v1/crm/customers/{id}` | partial |
| Marketing (`marketing`) | `marketing` | Profile, Verteiler | `GET /api/v1/crm/customers/{id}` | partial |
| Genossenschaft (`cooperative`) | `cooperative` | Anteile, Betriebsgruppen | `GET /api/v1/crm/customers/{id}` | partial |
| Ausgabe (`output`) | `output` | Belegversand | `GET /api/v1/crm/customers/{id}` | partial |
| Schnittstellen (`interfaces`) | `interfaces` | Integrationen | `GET /api/v1/crm/customers/{id}` | partial |
| Potenzial (`potential`) | `potential` | GAP/Potenzial (Feature-Flag) | `GET /api/v1/crm/customers/{id}` | partial |
| Ansprechpartner (`contacts`) | `contacts` | Felder + Kontaktliste | `GET .../tabs/contacts` | partial |
| CRM 360 Auftraege | `auftraege` (supplemental) | Auftragsliste | `GET .../tabs/auftraege` | partial |
| CRM 360 Aktivitaeten | `aktivitaeten` (supplemental) | Aktivitaetenliste | `GET .../tabs/aktivitaeten` | partial |
| CRM 360 Dokumente | `dokumente` (supplemental) | Offene Posten als Belege | `GET .../tabs/dokumente` | partial |
| CRM 360 Angebote | `angebote` (Summary only) | — | `GET .../tabs/angebote` | gap |
| CRM 360 Historie | `historie` (Summary only) | — | `GET .../tabs/historie` | gap |

## Summary vs. Mask-Tab-Keys

| screen-summary `available_tabs` | Generator `tab.key` | Anmerkung |
|---|---|---|
| `stammdaten` | `masterdata` | Alias in `tab_endpoints` |
| `kontakte` | `contacts` | Alias in `tab_endpoints` |
| `auftraege` | `auftraege` | Supplemental Tab im Pilot |
| `aktivitaeten` | `aktivitaeten` | Supplemental Tab im Pilot |
| `dokumente` | `dokumente` | Supplemental Tab; `finance` nutzt gleiche API |

## Lazy-Load Vertrag (Wave 27)

- `GET /api/v1/crm/customers/{id}/screen-summary` liefert `tab_endpoints`.
- Aktiver Tab loest `GET /api/v1/crm/customers/{id}/tabs/{tab_key}` aus (read-only, max. 25 Zeilen).
- Stammdaten-Tabs laden weiterhin den Kunden-Stammdatensatz; Listentabs laden separat.

## Abnahme Kern-Stammdaten

Felder in `masterdata`, `address`, `contacts` und Summary-KPIs: **>= 90 % read-only abgedeckt**. Mutationen (Speichern, Anlegen) bleiben Legacy/naechste Waves.

## Offene Luecken

- Angebote und Historie: Endpunkt vorhanden, liefert leere Liste bis fachliche Quelle angebunden ist.
- Vollstaendige Feld-Paritaet aller Legacy-Sections: bewusst ausserhalb Wave 27 (Adapter-Pilot).
