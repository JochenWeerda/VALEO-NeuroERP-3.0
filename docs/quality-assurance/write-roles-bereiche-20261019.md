# Schreibwege mit Bereichsrolle (WRITE-ROLES-AREAS-20261019)

Nutzerentscheid 19.10.2026: Schreibwege brauchen eine ausdrueckliche serverseitige Berechtigung aus dem bestehenden
Rollenmodell; Fachaktionen behalten Bereichsrollen und Freigaben; das Inventar ist Pruefliste. Nach den
Admin-Wegen (ADMIN-WRITE-ROLES) folgen die Fachbereiche, je Gruppe ein Commit.

## Modell (`app/auth/bereich_roles.py`)

Je Weg haengt `dependencies=SCHREIBEN["<GRUPPE>"]` am Decorator. Rollen aus `config/keycloak/fachrollen.json`
(`*_BEARBEITEN`/`*_ADMIN`) plus Leitung `admin`/`manager` wie in `beleg_roles`. Strengere eigene Pruefungen
(Finanzleitung, Vier-Augen, Freigaben) bleiben zusaetzlich bestehen.

| Gruppe | Rollen (Bereiche) | Wege unter `/api/v1/...` |
|---|---|---|
| VERKAUF | SALES | sales, verkauf, pos, kasse, webshop, Preise/Preislisten, kunden, dauerauftraege, report-print |
| CRM | CRM, SALES | crm, mail-workspace, marketing, collab, messages |
| EINKAUF | EINKAUF | einkauf, procurement, purchase-orders, edi |
| LAGER | LAGER | lager, inventory, warehouses, silo, waage(n), weighing-tickets, rohware, pick/preparation-lists, inventur, chargen, verladung, nve, gs1, etiketten, scan |
| STAMMDATEN | EINKAUF, SALES, LAGER | artikel, articles, master-data, stammdaten |
| LOGISTIK | LAGER, SALES, EINKAUF | logistik, tours, transporte, disposition, strecke, fuhrpark, schaeden, zoll, gelangensbestaetigung, supply-chain, tankstelle, mobile |
| AGRAR | AGRAR, HARVEST, KONTRAKT, FUTTERMITTEL | agrar, saatzucht, gap, eudr, labor, massebilanz, naehrstoffe, foerderung, sustainability, agribusiness, genossenschaft |
| ERNTE | HARVEST, AGRAR, LAGER | annahme, ernte-kampagnen |
| KONTRAKT | KONTRAKT, AGRAR | kontrakte, contracts, vertraege, Hedging, Kontraktklassen, contract-pricing |
| FUTTERMITTEL | FUTTERMITTEL, AGRAR | futtermittel, futter |
| PRODUKTION | LAGER, AGRAR, FUTTERMITTEL | produktion |
| FINANZ | FINANCE | banken, zinsabrechnung, erechnung, intrastat, gobd, versicherungen, meldewesen |
| CONTROLLING | FINANCE, controller | controlling, kontrolle |
| PERSONAL | PERSONAL | personal, training, hrm |
| BELEGE | FINANCE, SALES, EINKAUF, LAGER | docflow, belege, dokumente, dms, approvals |
| QUALITAET | LAGER, EINKAUF, SALES, AGRAR, FUTTERMITTEL | compliance, gdpr, qualitaet, reklamationen, zertifikate, Nachweise, audit |
| PLATTFORM | admin | tenants, users, identity, config, setup, governance, dev, uat, webhooks (Registrierung), ai-data-classes, whatsapp/dev |
| FACHLICH | irgendeine Bearbeitungsrolle | process, neuro, workflow, agent(s), studio, runtime, mcp, ki/ai, knowledge, jobs, commands, Berichte, export, planung, projekte, service, wartung u. a. |
| EIGENE_DATEN | gepruefte Person (eigene Daten) | ux, ux-telemetry, recent-documents, voice |
| GERAET | geprueft, auch technischer Zugang | Eingaenge/Webhooks/Rueckmeldungen (SPS, MDE, EPCIS, Kanalbruecken, Tour-/Fahrerereignisse, Tank-Eingang, Zoll-Callback) |

**Zur Entscheidung vorgelegt:** GERAET verlangt bewusst keine Fachrolle (technische Zugaenge haben keine); EIGENE_DATEN
ordnet ueber die Kennung zu. Beide sind ausdrueckliche Abhaengigkeiten und als solche im Inventar sichtbar.

## Fortschritt

- Gruppe VERKAUF: 99 Decorators in 30 Routern (u. a. alle Auftragswege `sales_orders`). Inventar 1521 -> 1417.
  Nachweis: 334 Suiten des Verkaufs 9212 gruen; 7 Mini-App-Tests mit Testidentitaet nachgezogen; ein Fehlschlag
  (`test_einkauf_bestellliste_beide_speicher`, Kategorie `tax`) ist vorbestehend und unabhaengig.
- Gruppen CRM, EINKAUF, STAMMDATEN: 339 Decorators. Inventar 1417 -> 1073. Nachweis: 583 Suiten 16706 gruen.
  Nachgezogen: `testgrenze.ersetze_bearer` liefert jetzt auch den Nutzer aus denselben Claims (Rollen-Abhaengigkeiten
  lesen ihn); Testidentitaeten fuer Bestellvorschlag (Einkauf) und Interessenten (Vertrieb); die Bestellmail
  versendet im Test der Einkauf statt des Lagers. Nebenbefund aus Rollout-Schritt 6: Mahnen fehlte in
  `agentContract.dangerousActions` der Maske `finance/ar-open-item` (Vertragstest war rot) — ergaenzt.
