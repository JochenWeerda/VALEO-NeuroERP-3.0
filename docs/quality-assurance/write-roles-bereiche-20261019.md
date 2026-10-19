# Schreibwege mit Bereichsrolle (WRITE-ROLES-AREAS-20261019)

Nutzerentscheid 19.10.2026: Schreibwege brauchen eine ausdrueckliche serverseitige Berechtigung aus dem bestehenden
Rollenmodell; Fachaktionen behalten Bereichsrollen und Freigaben; das Inventar ist Pruefliste. Nach den
Admin-Wegen (ADMIN-WRITE-ROLES) folgen die Fachbereiche, je Gruppe ein Commit.

## Modell (`app/auth/bereich_roles.py`)

Je Weg haengt `dependencies=SCHREIBEN["<GRUPPE>"]` am Decorator. Rollen aus `config/keycloak/fachrollen.json`
(`*_BEARBEITEN`/`*_ADMIN`) plus `admin` wie in `beleg_roles`; die historische Rolle `manager` erteilt seit
MANAGER-ROLE-ENFORCEMENT-20261019 keine Rechte und ist aus den Bereichslisten entfernt. Strengere eigene Pruefungen
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
- Gruppen LAGER, LOGISTIK, ERNTE, PRODUKTION: 284 Decorators. Inventar 1073 -> 790. Nachweis: Suiten des Blocks
  10717 gruen; 69 Mini-App-Tests ohne Testidentitaet nachgezogen (`ersetze_nutzer`; beim Fuhrpark in der Fixture,
  die nach jedem Test alle Overrides leert). Der Fuhrpark prueft keine Scopes selbst; die Tests ersetzten nur den
  Nutzer des Mandantenwegs.
- `manager` aus `bereich_roles`/`betrieb_roles`, der Kassenrolle und dem Auftragsstorno entfernt: abgeloest seit
  MANAGER-ROLE-ENFORCEMENT-20261019 (die zentrale Pruefung wertet sie schon nicht mehr aus).
- Gruppen AGRAR, KONTRAKT, FUTTERMITTEL, FINANZ, CONTROLLING, PERSONAL: 347 Decorators. Inventar 790 -> 441.
  Nachweis: Suiten des Blocks 6309 gruen; Mini-App-Tests mit Testidentitaet nachgezogen.
- **Godfile-Ratsche:** Die bisherigen Commits liessen fuenf Godfiles wachsen (u. a. `sales_orders.py` +43 durch den
  Storno-Kommandoweg). Behoben durch echte Verkleinerung: Storno nach `sales_order_commands.py`, Preiskalkulation
  nach `preis_kalkulation_bridge.py` (Pfade unveraendert), doppelter `require_roles`-Import in `admin_suite.py`,
  ungenutzte Importe entfernt. Baseline gesenkt, Integritaet OK.
- Nebenbefunde (nicht aus diesem Slice, belegt und behoben): Testgrenze von `test_freigabe_zweitwege` legt die
  geprueften Claims in den Request (seit AUDIT-IDENTITY-INTEGRITY liest das FiBu-Audit sie dort). Hinweis:
  `test_process_kernel_wave74_rations_optimization` verdeckt per `sys.path` das `app`-Paket fuer spaetere Tests
  derselben Sitzung (vorbestehend, nur bei abweichender Reihenfolge sichtbar).
- Gruppen BELEGE, QUALITAET, PLATTFORM (+ Agrar-/CRM-Reste): 125 Decorators. Inventar 441 -> 318. Neue Gruppe
  FREIGABE (Belegbereiche, Buchhaltung, Controlling) fuer `approvals` und die Beleg-Freigabeentscheidung, wie
  `beleg_roles.rollen_fuer("freigeben")`; vorher haette die Bereichsliste den Controller ausgesperrt.
- **Bearbeiter aus dem Body (Sicherheitsbefund):** Compliance-Lebenszyklus (PCN, VVVO, Artikelsperre) sowie sieben
  Router (u. a. Mahnstufen-Eskalation, Wareneingangs-QS, Budgetstatus, AB-/Lieferscheinstatus, Preisabweichung)
  nahmen den Urheber aus `operator`/`actor`/`created_by` im Anfragekoerper. Jetzt aus dem Token; der
  Identitaetsvertrag verbietet das Muster. Eine nie erreichbare doppelte Route `POST /compliance/pcn-meldungen`
  entfernt. Mandanten-Kopfzeilen sind dagegen kein Befund: `bind_headers` setzt `X-Tenant-ID` nach der
  Tokenpruefung auf den Tokenmandanten und weist Abweichungen ab.
- **Nachdruck ueber Maske/CLI/MCP:** Die Maskenaktion „Lieferschein drucken“ rief den Druckweg mit `request=None`
  auf; seit AUDIT-IDENTITY-INTEGRITY scheiterte jeder Nachdruck an der fehlenden Nutzerzuordnung. Request wird
  durchgereicht. Bewusst offen gelassen (Claim AUDIT-IDENTITY-INTEGRITY): FiBu-Audit mit `request=None` in
  Connector-, Journal- und Lagergeldwegen.
- Godfiles: AB-/Lieferschein-/Preisabweichungsblock nach `sales_order_commands.py`; `compliance.py` schrumpft.
- Testgrenze: `ersetze_nutzer` legt dieselbe Identitaet als gepruefte Claims in den Request.
- Nachweis: gezielte Suiten gruen (Compliance 159, Finanz/Freigabe/Mahnstufe/Vertraege 103, Maskenaktionen 23,
  Identitaetsvertrag, Rollen-Ratsche). Der Gesamtlauf der Block-Suiten wurde vom System wegen Speichermangels
  abgebrochen und steht aus.
- **Abschluss FACHLICH, FACHLICH_LESEN, EIGENE_DATEN, GERAET und Produktions-App:** 392 Decorators in 88 Dateien
  (FACHLICH 241, FACHLICH_LESEN 46, GERAET 23, EIGENE_DATEN 7; dazu FINANZ 29, CRM 20, EINKAUF 13 u. a. in den
  Routern, die nur `main:app` montiert: `app/finance`, `app/crm`, `app/einkauf`, FiBu, Vertraege, Workflow, DMS,
  GoBD, Uebersetzungen, VIES). **Inventar 318 -> 0**, jetzt ueber `app.main` **und** `main:app` (die Anwendung des
  Containers haengt weitere Router an; vorher sah die Ratsche sie nicht).
- FACHLICH_LESEN (neu): Berechnungen ohne Schreibwirkung (Policy aufloesen/testen, pruefen, erklaeren, simulieren,
  validieren) verlangen eine Lese- oder Bearbeitungsrolle irgendeines Bereichs. Die Zuordnung ist eine Heuristik
  (Pfad nach Pruefen/Berechnen **und** kein Commit/DML im Handler) und wurde nachgesehen: Abfrage-Import und
  signierter Export sowie die Superglue-Quarantaene (Aufloesen/Wiederholen) schreiben und tragen FACHLICH.
- **Delegiert geprueft** (Nutzerentscheid: delegierte Commands pruefen tiefer): `POST /api/v1/mcp/tools/call` ist in
  der Ratsche als `DELEGIERT` mit Begruendung gefuehrt — `execute_mcp_tool` prueft Werkzeug-Scope, Mandanten-Claim
  und Mensch-Sperre, der Zielweg laeuft mit dem Token des Aufrufers. Eine Fachrolle davor saehe Agenten (Scopes
  statt Fachrollen) aus.
- **Sicherheitsbefunde (behoben):** Superglue-Quarantaene nahm den Bearbeiter aus den Query-Parametern `resolved_by`
  und `retried_by` — jetzt aus dem Token. Der Demo-Anmelderouter (`/auth/...`, feste Demo-Konten) war in `main:app`
  in jeder Umgebung montiert — jetzt nur bei `APP_ENV == "development"`.
- `POST /api/mcp/policy/test` verlangt jetzt FACHLICH_LESEN; der Vertragstest, der „ohne Rollenpruefung“ festhielt,
  haelt die neue Entscheidung fest. Die drei leeren MCP-Stubs in `main.py` (KPIs, Trends, Prognose) ebenso; das
  Frontend behandelt eine Ablehnung der Prognose als „keine Prognose“.
- Nachweis: alle Testdateien, die einen geaenderten Router importieren (76 Dateien, 1600 Tests), gruen gegen die
  frische Pruefstand-DB `valeo_probe_writeroles`; 13 Mini-App-Testdateien mit Testidentitaet nachgezogen (MCP,
  Prozesskern-Wellen, Neuro-Zustandsgraph, Nebenbuch, Reporting). Vertragstests (Identitaet, Rollen-Ratsche,
  Policy-Routen, Personal-Zerlegung, OpenAPI/Architektur) 72 gruen; Gates (Projektionen, Masken-Studio-Ratsche,
  Kommando-Inventar, MCP-Bindungen, Architektur-Drift, Godfile, Baseline-Integritaet) gruen.
- **Offen:** Gesamtlauf der Backend-Suite (zweimal wegen Speichermangels vom System abgebrochen; CI ist
  Schiedsrichter). Zur Entscheidung: GERAET/EIGENE_DATEN (siehe oben).
- **Nachtrag (STAMMDATEN-BEARBEITEN, Sicherheitsbefund):** Der Body-Vertrag in `tests/test_keine_client_identitaet.py`
  war wirkungslos — sein Suchmuster enthielt zwei Backspace-Zeichen (`\x08`) statt `\b` und traf nie. Repariert und
  um `req.` sowie `aktor_id` und `.get("...")` erweitert; ein Mustertest haelt die Formen fest. Er fand 23 weitere
  Stellen, alle behoben: Nachweisraum, Futtermittelproduktion, Personal-Lebenszyklus, Meldewesen und
  POS-Tagesabschluss (`operator`), GoBD-Artefakte/E-Rechnungs-XML und Kommissionierlisten (`created_by`),
  Kontraktnachtrag (Rueckfall auf `payload.created_by`), Wareneingang aus dem Avis (`payload.get("operator")`), dazu
  die fuenf Reklamationswege und „Reklamation abschliessen“ (`aktor_id`). Der Statuswechsel der Reklamation ist eine
  Arbeitsfunktion `wechsle_status(..., aktor=...)`, die REST, Maske und MCP mit dem Token-Akteur aufrufen.
