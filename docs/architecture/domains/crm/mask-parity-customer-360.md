---
title: CRM Customer 360 — Mask Parity Matrix
type: reference
audience: [agent, entwickler, fachlich]
owner: Cursor
status: aktiv
last_reviewed: 2026-08-19
version: 1.2.0
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
| System (`system`) | `system` | Partnerstatus, Liefer- und Rechnungssperre | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Steuern (`tax`) | `tax` | USt-IdNr., Steuernummer, Steuerart | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Qualitaet / Compliance (`quality_compliance`) | `quality_compliance` | Betriebsnummer, QS, Bio | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Finanzen (`finance`) | `finance` | Offene Posten; Kreditlimit auf Stammdaten | Summary + `GET .../tabs/dokumente` | lazy table | ok |
| Bank (`bank`) | `bank` | Kontoinhaber, Bank, IBAN, BIC | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Marketing (`marketing`) | `marketing` | Segment, Newsletter, E-Mail-Einwilligung | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Genossenschaft (`cooperative`) | `cooperative` | Mitgliedsnummer, Pflichtanteile, Beendet | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Ausgabe (`output`) | `output` | Rechnungs- und Mahnversand | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Schnittstellen (`interfaces`) | `interfaces` | EDIFACT INVOIC, ORDERS, DESADV | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Potenzial (`potential`) | `potential` | Juengster Satz aus `public.customer_potential_snapshot` | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Ansprechpartner (`contacts`) | `contacts` | `domain_crm.business_partner_contacts` und `public.kunden_ansprechpartner` | `GET .../tabs/contacts` | lazy table | ok |
| CRM 360 Auftraege | `auftraege` (Belege) | Auftragsliste | `GET .../tabs/auftraege` | ok |
| CRM 360 Aktivitaeten | `aktivitaeten` | Aktivitaetenliste | `GET .../tabs/aktivitaeten` | ok |
| CRM 360 Dokumente | `dokumente` / `finance` | Offene Posten ueber `kunde_id` | `GET .../tabs/dokumente` | ok |
| KIM Belege | `auftraege` | Auftragsliste | `GET .../tabs/auftraege` | ok |
| KIM Finanzen | `finance` | Offene Posten | `GET .../tabs/dokumente` | ok |
| KIM Aufgaben | `aufgaben` | Titel, Art, Faelligkeit, Status | `GET .../tabs/aufgaben` | ok |
| KIM Kontrakte | `kontrakte` | Kontraktliste ueber `party_id` | `GET .../tabs/kontrakte` | ok |
| CRM 360 Angebote | `angebote` | Verkaufschancen | `GET .../tabs/angebote` | lazy table | ok |
| CRM 360 Historie | `historie` | Aktivitaetenhistorie | `GET .../tabs/historie` | lazy table | ok |
| KIM Chef/Präsente/Postfach/Geo | `masterdata` / `praesente` / `postfach` / `address` | Chefanweisung, Präsenteliste, Postfachfelder, Koordinaten | `GET .../customers/{id}` + `GET .../tabs/praesente` | compiled | ok |
| Pflege Tab 21 Chef-Anweisung | `chefanweisungen` | `domain_crm.business_partner_instructions` | `GET .../tabs/chefanweisungen` | lazy table | ok |
| Pflege Tab 23 Anschriften | `anschriften` | `domain_crm.business_partner_addresses` | `GET .../tabs/anschriften` | lazy table | ok |
| Pflege Tab 24 Kontoauszug | `kontoauszug` | `domain_crm.business_partner_billing_configs` | `GET /api/v1/crm/customers/{id}` | compiled | ok |
| Pflege Tab 25 CPD-Konto | `cpd` | `domain_crm.business_partner_cpd_accounts` | `GET .../tabs/cpd` | lazy table | ok |
| Rabatte | `rabatte` | `domain_crm.business_partner_discount_items` | `GET .../tabs/rabatte` | lazy table | ok |
| Preise | `preise` | `domain_crm.business_partner_price_agreements` | `GET .../tabs/preise` | lazy table | ok |

## Summary vs. Mask-Tab-Keys

| screen-summary `available_tabs` | Generator `tab.key` | Anmerkung |
|---|---|---|
| `stammdaten` | `masterdata` | Alias in `tab_endpoints` |
| `kontakte` | `contacts` | Alias in `tab_endpoints` |
| `auftraege` | `auftraege` | Supplemental Tab im Pilot |
| `aktivitaeten` | `aktivitaeten` | Supplemental Tab im Pilot |
| `dokumente` | `dokumente` | Supplemental Tab; `finance` nutzt gleiche API |
| `aufgaben` | `aufgaben` | KIM-Aufgaben, leer wenn keine Quelle |
| `kontrakte` | `kontrakte` | `domain_ops.kon_contract` nach `party_id` |

## Lazy-Load Vertrag (Wave 27)

- `GET /api/v1/crm/customers/{id}/screen-summary` liefert `tab_endpoints`.
- Aktiver Tab loest `GET /api/v1/crm/customers/{id}/tabs/{tab_key}` aus (read-only, max. 25 Zeilen).
- Stammdaten-Tabs laden weiterhin den Kunden-Stammdatensatz; Listentabs laden separat.

## Abnahme Kern-Stammdaten

Felder in `masterdata`, `address`, `contacts` und Summary-KPIs: **>= 90 % read-only abgedeckt**. Mutationen (Speichern, Anlegen) bleiben Legacy/naechste Waves.

## Offene Luecken

- Mutationen (Anlegen, Aendern, Loeschen) bleiben unter `/verkauf/kunden-stamm/:id?pflege=1`.
- Die Pflege-Register Chef-Anweisung, Anschriften, Kontoauszug und CPD-Konto
  sind in der Akte lesbar. Ohne Partnersatz bleiben sie leer.
- Potenzial ist der juengste GAP-Snapshot (`customer_potential_snapshot`);
  ohne Pipeline-Lauf bleibt das Register leer.
- Chef, Präsente, Postfach und Geo sitzen in der nativen Object Page
  (`masterdata`/`praesente`/`postfach`/`address`); Mini-Apps bleiben weg.
- Listen-IDs (`kunden_nr`, Partnernummer) oeffnen dieselbe Akte wie die UUID.
- Jahresumsatz zaehlt Auftraege mit Status `completed`, `geliefert` oder `invoiced`.
- Der letzte Wareneingang kommt vom Annahmeschein; fehlt der, von der
  Lagerbewegung ueber `owner_partner_id`.
- Laufende Agrarkontrakte haengen an der Partner-ID oder der Partnernummer.
- Postfach kommt aus `public.kunden`, Koordinaten aus `public.kunden_geo`.
- `/verkauf/kunden-stamm/:id` und `/crm/kunden-cockpit?id=` leiten auf dieselbe Akte;
  Mutationen der Tabs 21–25 bleiben unter `?pflege=1`.

## Desktop-Gewohnheitsbruecke 2026-08-19

Die native Maske nutzt den zentralen Meridian-Vertrag: stabiler Header und
Footer, `create_activity` links als Fachaktion, `edit` rechts als
Commit-Aktion sowie Enter-Feldfluss. Das Muster ist herstellerneutral; die
redigierte L3-Ableitung steht in
[`l3-to-meridian-habit-parity.md`](../../../design/l3-to-meridian-habit-parity.md).
