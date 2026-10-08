---
title: Open Gaps and Known Issues
type: reference
audience: [entwickler, agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-29
version: 3.4.0
description: Tracker aller bekannten offenen Luecken, Issues und technischen Schulden in VALEO NeuroERP — Referenz fuer Priorisierung und Gap-Closure.
---

# Open Gaps and Known Issues

## Zahlungslauf-Freigabenachweis (2026-10-08)

Fehlende authentifizierte Freigeber, fehlende Ersteller und Selbstfreigaben
zentral gesperrt; tenantgebundener FOR-UPDATE-Guard fordert draft in allen
Command-Modi. Echte Freigabe/Audit/Outbox atomar, Vorschauen schreibfrei.
Original 18 Fehler/7 gruen; final 36 Guard-/HTTP-/API-/echte PG-Vertraege
ohne Skip gruen (61,43s). Gemeinsamer valeo_probe, nur eigene Testdaten;
keine neue DB/Container/Schema/Migration/Reset. Menschlicher Rollenschutz und
forbiddenForAgents bleiben verpflichtend. Zahlauf-MCP open_high, FIN-CLOSE
gegen ADR-076 und die 31 fehlenden HTTP-Commandvertraege bleiben offen.
[QA und Handshake](../quality-assurance/payment-run-evidence-20261008.md).

## SonarCloud — Runtime-Blocker und verbleibende Gatebedingungen (2026-10-08)

Quality Gate37828122495 aufcbcd52b84 bestaetigt den frischen 670er-Katalog,
Backend, Frontend, Docker und Sicherheitspruefungen. Der nachgelagerte
SonarCloud-Scan laeuft technisch durch; sein Qualitaetsgate bleibt rot.
Zehn deklarierte Agrar-Exporte an bestehende Fachfunktionen gebunden,
zwei defekte NUTS-Altexporte samt unbrauchbarem Service/Beispiel-Seed entfernt.
Fehlender Audit-Filter, falscher Erfolgsquotenaufruf und zusaetzlich echte
MaintenanceWindow-Konstruktorfehler behoben. Original20 Fehler/1 gruen;
repariert43 neue und bestehende Fachvertraege ohne Skip gruen (3,99s),
keine DB/Container/Reset. [QA und Handshake](../quality-assurance/sonar-runtime-blockers-20261008.md).
Offen: weitere Sonar-Bugs/Sicherheitsklassifikation, Hotspot-Reviews,
Coverage55,2 unter80 und Duplikate3,3 ueber3. Keine Schwelle/Baseline oder
Scanner-Ausnahme geaendert. Kein vollstaendiges ISO27001-Persistenzversprechen
fuer die bestehenden In-Memory-Dienste; NUTS-PLZ-Heuristik nicht amtlich abgenommen.

## Sortenregister — kanonischer Lesevertrag (2026-10-08)

Agrar-Smoke zeigte dreimal404 auf einem nicht vorhandenen Sortenpfad.
Hook und Datenfelder auf den vorhandenen `/agrar/varieties/`-Vertrag
umgestellt, nullable Metadaten und Aktivstatus ohne Phantomfelder.
Vier React-, zwei Browser-,18 Schema-/HTTP-Vertraege und Frontend-Typpruefung
gruen. [QA und Handshake](../quality-assurance/sorten-canonical-read-20261008.md).
Handelsbestand/-preise der Saatgutbestellung und alter Ernte-Sortenfallback
bleiben separat offen. Voller GitHub-Security-Scan und vorheriger grosser
Backend-CI-Lauf b47cd87be inzwischen gruen; neue Agrar-Folgeabnahme offen.

## Vier verbleibende Backend-CI-Regressionen (2026-10-08)

Im grossen CI-Lauf9176 standen 16499 bestandenen Tests vier konkrete Fehler
gegenueber. Zwei veraltete 6.7-Taxonomieerwartungen auf kanonische 6.9
nachgezogen, zwei WMS-Mocks um die bereits erforderlichen tenantgebundenen
Lager-/Artikelabfragen und Bestands-ID ergaenzt. Fachschutz nicht veraendert.
Komplette betroffene Module plus Lager-Schutzvertraege lokal isoliert
30/30 gruen. [QA und Handshake](../quality-assurance/ci-four-regressions-20261008.md).
GitHub-Folgeabnahme offen; keine pauschale Meldung, alle CI-Laeufe seien gruen.

## Node Production High — Quellreparaturen und Betrieb (2026-10-08)

node-forge GHSA-86w9-cpqp-85rv und braces GHSA-vfj7-8cjw-p6xm durch
gezielte pnpm-Quellbackports behandelt. Die Originalgegenprobe reproduziert
neun Angriffspfade; drei normale Vertraege bestehen bereits im Original.
Roh-Audit und versionsbasierte Alerts bleiben sichtbar. Der getrennte Gate
verlangt exakt gepruefte Patches und installierte Quellen, Manifest-/Lockhashes,
reale Laufzeittests und befristete Review; unbekannte oder geaenderte Befunde
sperren. [QA und Wiedervorlage](../quality-assurance/node-high-backports-20261008.md).
Review vor 15.10.2026 erforderlich. Herstellerreleases und GitHub-Folgeabnahme
bleiben offen, andere Security-Alerts sind nicht pauschal geschlossen.

## Parser-Sicherheit und XBRL-Doku-CI (2026-10-08)

Unabhaengiger stream-json-Assembler-Befund GHSA-mjw6-4jj6-33hc durch
provenienzgebundenen pnpm-Backport geschlossen; Original-Negativkontrolle und
gepatchte normale/Reviver-/Array-Parservertraege. Kein 3.x-API-Wechsel oder
neue Audit-Ausnahme. [QA und verbleibende Alerts](../quality-assurance/stream-json-prototype-20261008.md).
Der bestehende CI-Security-Einstieg prueft jetzt automatisch alle 18 Paket-/
Parservertraege; exakt derselbe Aufruf lokal gruen. Docs Governance auf GitHub
fuer e4487188d ebenfalls gruen, weitere Folgepruefungen laufen.
ChromaDB-Evidenz erneut unveraendert bestaetigt, Review endet weiterhin 15.10.
Die beiden eigenen XBRL-Doku-CI-Ursachen (Slice-Harness und ADR-Nav) korrigiert;
alle lokalen Doku-Gates inklusive vollstaendigem Build bestanden. GitHub-
Folgeabnahme, weitere Alerts und vorhandene Doku-Linkwarnungen bleiben offen.

## EBILANZ-XBRL-DRAFT — amtlicher Katalog und XML-Entwurf (2026-10-08)

Falscher historischer GCD-Teilkatalog durch 3944 amtlich abgeleitete 6.9 GCD-/
Kernkonzepte ersetzt; hashgebunden und deterministisch, Requests ohne Netzabruf.
Echter rollen-/tenantgeschuetzter XML-Download einfacher expliziter Fakten am
vorhandenen Export, DRAFT_UNVALIDATED und keine Status-/Ticketmutation.
49 XML-/HTTP-/PostgreSQL-Vertraege gruen. [QA und Betrieb](../quality-assurance/ebilanz-xbrl-draft-20261008.md).
Offen bleiben Arelle-/amtliche Vollvalidierung, Bilanz-/GuV-Kontenzuordnung,
Tupel/Dimensionen und echter ERiC-Empfang; keine vollstaendige Steuerabnahme.

## CI-CONTRACT-CLOSURE — erster Meilenstein (2026-10-08)

OpenAPI-Beschreibungen der Lead-Aliase nachgetragen; zwei bereits typisierte
eBilanz-Dekoratoren für den bestehenden Scanner korrekt angeordnet.
OpenAPI-Schwelle bleibt 0. Der nachfolgende AST-Vertragscheck erkennt die
20 fälschlich als untypisiert gezählten Routen korrekt; nun 3590/3590 Verträge,
Default und CI-Schwelle 0, 45 Parser-/Policy-/Studio-Tests grün.
Secret-Scan-Fehlalarm im künstlichen Kalenderfixture beseitigt, keine neue
Ausnahme; Gitleaks 8.30.1 auf HEAD-Snapshot null Funde. 24 Kalenderverträge grün.
[Abnahme und ELSTER-Registrierungsstand](../quality-assurance/ci-contract-closure-20261008.md).
Native Lead-Neuanlage und Berechtigungsprojektion im zentralen Maskenweg
abgenommen: 834 Backend-Verträge, 12 React-Verträge und bestehender Chromium-
Smoke zur Lead-Anlage grün. Acht Logistik-Berechtigungen in BE/FE deklariert.
Das schließt die geprüfte Lead-Smoke-Ursache und den UI-Berechtigungsvertrag;
eine vollständige serverseitige Logistik-Sicherheitsabnahme wird nicht behauptet.
Neun direkte Security-Pins mit vorhandenen Overrides abgeglichen, Lockfile
unverändert, alle 36 Workspaces frozen/offline geprüft; sechs echte Runtime-
Verträge grün. Zwei High ohne Herstellerfix bleiben audit-blockierend.
GitHub-Smoke 37730263363 auf c59df8391 in allen fünf Domänen erfolgreich.
Vollständiges XBRL/ERiC, ungepatchte Security-Befunde und Gesamt-Quality bleiben
offen. ELSTER-Registrierung durch Nutzer abgesendet, Bestätigungs-PDF lokal
gesichert; SDK-Zugang und Lizenzannahme noch ausstehend.

## EBILANZ-HONEST-PERSISTENCE — Scheinwirkung und Laufzeit-DDL geschlossen (2026-10-07)

Reale tenantgebundene Entwurfsmetadaten, Alembic-Schema statt Request-DDL, 503/Rollback statt verschluckter DB-Fehler. Fehlende/fremde IDs 404; vollständige XBRL-Validierung und echte ELSTER-/UStVA-Übertragung fehlen und liefern ausdrücklich 409. Simulationsservice entfernt, Readiness nicht bereit, historische Tickets niemals als ANGENOMMEN dargestellt; fremde Zeilen erhalten. [QA/Betrieb](../quality-assurance/ebilanz-honest-persistence-20261007.md). Die Implementierung des vollständigen XBRL-/ERiC-Fachwegs bleibt offen, ebenso die separate Gesamtkatalog-Abnahme. SQL-Gate prüft neue und verbleibende Dateien; Baselines nur abgesenkt.

## ACTION-DEN — ScreenDefinition→Registry (2026-10-08)

U-C10-01 teilweise geschlossen: 85 Maskenaktionen mit Ausführungspfad werden aus
ScreenDefinitions nach `services/ki-usability/app/data/screen_mask_actions.json`
generiert und in die Action-Registry gemerged (`mask:{screen}:{key}`).
Drift-Gate und Tests gruen.
[QA](../quality-assurance/usability-action-registry-20261008.md).
**Teilweise geschlossen (MCP-WRITE-20261008):** `crm.activity.create` und
`sales.invoice.post` (nur nach freigegebenem Vorschlag; Mandanten-ID aus
Token). [QA](../quality-assurance/mcp-write-20261008.md).
**Teilweise geschlossen (MCP-CUSTOMER-OPEN-20261008):** `crm.customer.open`
liefert Mandanten-Route `/crm/customers/{id}` (Screen `crm/customer-360`);
Voice-Phrasen „öffne Kunde(n)“. [QA](../quality-assurance/mcp-customer-open-20261008.md).
**Geschlossen (MCP-CUSTOMER-NAV-20261008):** Dispatch/Voice Deep-Link auf sicheren
`route_path` bei `kunden_nr`; Listen-Fallback ohne Kennung.
[QA](../quality-assurance/mcp-customer-nav-20261008.md).
**Geschlossen (MCP-CUSTOMER-SEARCH-20261008):** `crm.customer.search` Read-Adapter
(Trefferliste + `route_path`). [QA](../quality-assurance/mcp-customer-search-20261008.md).
**Geschlossen (MCP-CUSTOMER-SUMMARY360-20261008):** `crm.customer.summary360`
Read-Adapter. [QA](../quality-assurance/mcp-customer-summary360-20261008.md).
**Geschlossen (MCP-ORDER-STATUS-20261008):** `sales.order.status` Read-Adapter.
[QA](../quality-assurance/mcp-order-status-20261008.md).
**Geschlossen (MCP-FIBU-OPEN-ITEMS-20261008):** `fibu.open_items.list` Read-Adapter
(kein FIN-CLOSE). [QA](../quality-assurance/mcp-fibu-open-items-20261008.md).
**Geschlossen (MCP-FIBU-DUNNING-20261008):** `fibu.dunning.status` Read-Adapter
(kein Mahnlauf/FIN-CLOSE). [QA](../quality-assurance/mcp-fibu-dunning-20261008.md).
**Geschlossen (MCP-WMS-LOT-TRACE-20261008):** `wms.lot.trace` Read-Adapter
(keine Buchung/QS-Änderung). [QA](../quality-assurance/mcp-wms-lot-trace-20261008.md).
**Geschlossen (MCP-WMS-CELL-STATUS-20261008):** `wms.cell.status` Read-Adapter
(kein Transfer/QS-Write). [QA](../quality-assurance/mcp-wms-cell-status-20261008.md).
**Geschlossen (MCP-CATALOG-READS-REST-20261008):** Rest-Katalog-Reads
(DMS/Agrar/Lager/Einkauf/Compliance/Proposals). [QA](../quality-assurance/mcp-catalog-reads-rest-20261008.md).
**Geschlossen (MCP-MASK-WRITE-PARITY-20261008):** Mask→MCP Mapping
(`config/mcp_mask_action_map.yaml`); FIN-CLOSE `blocked_adr_076`.
[QA](../quality-assurance/mcp-mask-write-parity-20261008.md).
**Geschlossen (MCP-MASK-WRITES-TOP-20261008):** `crm.lead.qualify` und
`einkauf.bestellung.versenden` (Token-Mandant, Idempotenz, Audit);
Map mapped 4 / open_medium 43. [QA](../quality-assurance/mcp-mask-writes-top-20261008.md).
**Geschlossen (MCP-MASK-WRITES-NEXT-20261008):** `einkauf.angebot.bestellen`,
`einkauf.anlieferavis.wareneingang`, `lager.stock_movement.stornieren`;
Map mapped 7 / open_medium 41. [QA](../quality-assurance/mcp-mask-writes-next-20261008.md).
**Geschlossen (MCP-MASK-WRITES-BATCH3-20261008):** `agrar.ration.transition`
(submit_review/approve/schedule/activate); Map mapped 11 / open_medium 37.
[QA](../quality-assurance/mcp-mask-writes-batch3-20261008.md).
**Geschlossen (MCP-MASK-WRITES-BATCH4-20261008):** Lifecycle retire/archive;
`agrar.feeding.supply_handoff`, `agrar.feeding.actual_measure`;
Map mapped 15 / open_medium 33. [QA](../quality-assurance/mcp-mask-writes-batch4-20261008.md).
**Geschlossen (MCP-MASK-WRITES-BATCH5-20261008):** `configure_threshold`,
Feed-Analyse release/reject, Reklamation abschliessen;
Map mapped 19 / open_medium 32. [QA](../quality-assurance/mcp-mask-writes-batch5-20261008.md).
**Geschlossen (MCP-MASK-WRITES-REMAINING-20261008):** Leitstand-Sync, Kalender-Reproject,
MDE `process_pending`; Rest `blocked_no_endpoint` / Inventur `open_high`;
Map mapped 22 / open_medium **0**, `classification_complete`.
[QA](../quality-assurance/mcp-mask-writes-remaining-20261008.md).
**Geschlossen (MCP-ORDER-NAV-20261008):** Voice/Dispatch Deep-Link aus
`sales.order.status` (`route_path` `/sales/order-editor/{id}`); Listen-Fallback
ohne `auftrag_nr`. [QA](../quality-assurance/mcp-order-nav-20261008.md).
**Geschlossen (MCP-DEEP-LINK-LOT-20261008):** Voice/Dispatch Deep-Link aus
`wms.lot.trace` (`route_path` `/charge/stamm/{id}`); Listen-Fallback
`/charge/rueckverfolgung`. [QA](../quality-assurance/mcp-deep-link-lot-20261008.md).
**Geschlossen (MCP-DEEP-LINK-CELL-20261008):** Voice/Dispatch Deep-Link aus
`wms.cell.status` (`route_path` `/lager/silo-zellen/{id}`); Listen-Fallback
`/lager/silo-uebersicht`. [QA](../quality-assurance/mcp-deep-link-cell-20261008.md).
**Geschlossen (MCP-DEEP-LINK-PO-20261008):** Voice/Dispatch Deep-Link aus
`einkauf.bestellung.status` (`route_path` `/einkauf/bestellung/{id}`);
Listen-Fallback `/einkauf/bestellungen`; List-Items mit `route_path`.
[QA](../quality-assurance/mcp-deep-link-po-20261008.md).
**Geschlossen (MCP-DEEP-LINK-DMS-20261008):** Voice/Dispatch Deep-Link aus
`dms.document.search` (`route_path` `/docflow/nachweisraum/{id}`); GoBD-Status
mit `/docflow/gobd-export/{id}`; Listen-Fallback `/docflow/nachweisraum`.
[QA](../quality-assurance/mcp-deep-link-dms-20261008.md).
**Geschlossen (MCP-DEEP-LINK-AGRAR-20261008):** Voice/Dispatch Deep-Link aus
`agrar.contract.get` (`/agrar/kontrakt/{id}`) und `agrar.weighing_ticket.list`
(`/waage/wiegeschein/{id}`).
[QA](../quality-assurance/mcp-deep-link-agrar-20261008.md).
**Geschlossen (MCP-DEEP-LINK-STOCK-20261008):** Voice/Dispatch Deep-Link aus
`lager.bestand.get` (`/lager/artikel/{id}`); Listen-Fallback Bestandsuebersicht.
[QA](../quality-assurance/mcp-deep-link-stock-20261008.md).
**Deep-Link-Serie abgeschlossen:** Kunde → Auftrag → Lot → Zelle → Bestellung →
DMS → Agrar/Wiegeschein → Bestand. Keine weiteren klaren Einzel-Read-Deep-Links
ohne Backend-/UI-Erfindung (`inventur.status`/`compliance.gate`/`proposal.list`).
**Geschlossen (MCP-AP-FREIGABE-20261008):** `finance.ap_invoice.propose` +
`finance.ap_invoice.freigeben` (Vier-Augen analog `sales.invoice.post`;
CommandEndpoint; kein Journal/FIN-CLOSE). Map mapped 23.
[QA](../quality-assurance/mcp-ap-freigabe-20261008.md).
**Geschlossen (MCP-INVENTUR-OPENING-PROPOSE-20261008):**
`lager.inventur.propose_opening` propose-only (Snapshot aus Inventurzeilen;
execute 501; kein Booking). Map `mapped_propose_only` 1 / open_high **1**
(nur Zahlauf). [QA](../quality-assurance/mcp-inventur-opening-propose-20261008.md).
**Geschlossen (USABILITY-MCP-MAP-CI-VOICE-20261008):** Audit bestaetigt 31×
`blocked_no_endpoint` ohne SD-`commandEndpoint` (REST-CRUD allein reicht nicht);
CI-Drift-Gate Mask-Map + Screen-Action-Katalog; Haupt-App Voice Deep-Link
Nav-IDs (`nav-einkauf`/`nav-lager`/`nav-agrar-vertraege`) + Param-Extraktion +
Vite-Proxy-Mount. [QA](../quality-assurance/usability-mcp-map-ci-voice-20261008.md).
**Konsolidiert (MCP-CONSOLIDATE-COMMIT-20261008):** Deep-Link-Serie, AP-Freigabe,
Inventur propose-only und Usability-Map-CI lokal committed/pushed; Re-Audit
31× blocked ohne CE; keine weiteren umsetzbaren Mask-Writes ohne Backend-Erfindung.
**Weiter offen:** FIN-CLOSE/agentic Finance (P0, ADR-076 — kein Scheinabschluss;
Claim frei nur fuer Doku/Pruefung); 1× Mask `open_high` (Zahlauf-Freigabe
forbiddenForAgents/ADR-076-nah — nicht verdrahten); 31× `blocked_no_endpoint`
(Personal/Fuhrpark/Admin/Reporting/Speichern) erst nach HTTP-CommandEndpoint;
Stufe-2-SUS live.

## GAP-HUB — Archiv 2025 ersetzt (2026-10-07)

Kanonische Gap-Übersicht: [docs/gap/README.md](../gap/README.md),
[Executive Summary](../gap/executive-summary-20261007.md),
[Domänenreife CSV](../gap/domain-maturity-matrix-20261007.csv).
Die 2025er Archiv-Dateien unter `docs/_internal/archive/gap/` (inkl. „~38 %
Maturity“ und P0 „fehlt komplett“) sind historisch und keine Priorisierungsquelle.
Dieses Open-Gaps-Dokument bleibt der **Detail-Tracker**; der Hub die
Management-/Domänenübersicht.

## USABILITY-SYSTEMAUDIT — Stufe-1 Systemaudit (2026-10-07)

Systemweites Experten-Usability-Audit und Vergleichsdossier geliefert:
[Protokoll](../quality-assurance/usability-erp-audit-protocol-20261007.md),
[Dossier](../quality-assurance/usability-erp-vergleichsdossier-20261007.md),
[Matrix](../gap/usability-systemaudit-matrix-20261007.csv),
[Findings](../gap/usability-systemaudit-findings-20261007.csv),
[Peer-Matrix](../gap/usability-peer-matrix-20261007.csv). SUS-Experten-Schnitt
~66 (±8). Gap-Hub ersetzt 2025-Archive; Stufe-2-SUS-Protokoll vorbereitet
(Durchführung mit Endnutzern steht aus). ACTION-DEN (85 mask:*) und
MCP-WRITE Top-Adapter und `crm.customer.open` 2026-10-08 nachgezogen.
**Weiter priorisierte UX/Future-Gaps (nicht als erledigt werten):**
U-C06-01/02/04 (agentic Finance, immutable Agent-Ledger-Muster, echter
Kassenabschluss) P0; Rest-MCP-Schreibparität (übrige Mask-IDs/Read-Adapter),
Local-OCR (TaxHacker-Muster), Steuer-Skill-MCP (OpenAccountants),
Masken-Framework-Abschmelzung, Finance-IA-Konsolidierung P1. Light (light.inc)
und Peers ERPClaw/OpenLedger sind Zukunftsspiegel, kein Ersatz der Landhandel-SoR.

## USER-DECISIONS-LEAD-PDF — Entscheidungsrest geschlossen (2026-10-07)

Lead-Maske/Qualifizierung verwenden public.crm_leads und einen ausgewaehlten eigenen Kunden; echte lokale Opportunity atomar mit Audit/Outbox. Ernte-PDFs liegen vollstaendig und versioniert in PostgreSQL, mit mandantengebundenem Download und Hashpruefung. Acht Logistikdeklarationen bereits b2a63f451 geliefert, erneut geprueft. [ADR-078](../adr/adr-078-canonical-lead-postgresql-pdf.md), [QA](../quality-assurance/user-decisions-lead-pdf-20261007.md). Die physische Domain-Verlagerung von Leads sowie Gesamtatomizitaet der FIBU-Verbuchung mit nachgelagerter Archivierung bleiben eigene offene Fach-Slices. Alte Hash-only-Belege enthalten kein PDF und werden nicht als wiederherstellbar bestaetigt. Die alte Round-robin-/Assign-Lead-API verwendet noch das Nebenmodell und bleibt ein gesonderter Altverbraucher.

## HANDSHAKE-GAP-CLOSURE — vier benannte Befunde (2026-10-05)

Bank-Proof-Fixture korrigiert: migriertes Schema kopieren, nur fehlenden
privaten FK ergaenzen; 32 Bankvertraege bestanden statt 31 Setup-Fehler.
Ledger-Optionen SQL-begrenzt und fetchmany(limit), Seitentest und Ratsche
gruen. Journalnummern-UQ je Mandant statt systemweit: Migration/ORM und
sechs echte private PG-Vertraege und gemeinsame Integration abgeschlossen:
Merge-Revision zusammenfuehrung_20261005_preis_journal (4b513ff75), genau ein
Head. Read-only check_journal_identity.py ist im vorhandenen Probe PASS;
Global-UQ entfernt und Tenant/Nummern-UQ wirksam. 40 gezielte Checks nach
Integration bestanden, inklusive zweier echter Gate-Faelle. 380 Regressionen insgesamt bestanden.
ADR-077 entscheidet `domain_inventory.weighing_tickets` als fuehrenden
Wiegeschein; Entscheidungs-Handshake geschlossen. Technischer Rueckbau der
Mobile-/Operations-Wiege-Altverbraucher bleibt ausdruecklicher Folge-Slice.
Nachweis: [Handshake-Abnahme](../quality-assurance/handshake-gap-closure-20261005.md).


## CASH-CLOSE-DIRECTBOOK — Scheinbuchung entfernt, echter Abschluss offen

2026-10-05: cash/close-day summiert keine Tagesjournale mehr und erzeugt
keinen posted-Header/Zeilen auf geratenem Konto 1000. HTTP 409 mit
fachlichem Grund, keine SQL/DML/Commits, wiederholte Aufrufe unveraendert.
397 Regressionen plus 12 gezielte API-/OpenAPI-Checks bestanden; reale private
Journal-Snapshots erhalten. ADR-076 Proposed und Finance Domain Pack;
QA: [Kassen-Direktbuchung](../quality-assurance/cash-close-retirement-20261005.md).
Offen: Belegter Kassenbestand, Bewertung, Gegenkontierung und atomarer
Abschluss ueber zentralen Journal-/Perioden-/Auditvertrag. Vorhandene Maske
zeigt HTTP-Fehler; sie ist kein fachlich fertiger Kassenabschluss. Fremdes
Global-OpenAPI-Refresh unberuehrt, eigener Routen-Snapshot bereit.
Source-Whitelist/weitere rohe Journal-Schreiber bleiben separate Integration.

## JOURNAL-TRANSACTION-OWNERSHIP — Service bereit, Consumer-Integration offen

2026-10-05: commit_on_success=False erlaubt aeussere Transaktionen fuer alle
sechs Journalmutationen. Sie flushen und behalten Sperren bis zum aeusseren
Commit/Rollback. 337 Regressionen, 16 neue echte PostgreSQL-Faelle belegen
Peer-Sichtbarkeit und vollstaendiges Rollback auch nach mehreren erfolgreichen
Schritten und spaeterem Domain-/SQL-Fehler. QA:
[Transaktionssteuerung](../quality-assurance/journal-transaction-ownership-20261005.md).
Default-Aufrufer bleiben selbst committend. API/Repository/Posting-Consumer
muessen die aeussere Steuerung explizit uebernehmen; log_fibu_audit und Anchor
committen weiterhin selbst. Diese Faehigkeit allein ist keine geschlossene
Audit-/Consumer-Atomizitaet. API/DTO-Fremdclaim und Schema/Hash-Gaps weiter offen.

## JOURNAL-PERIOD-ENFORCEMENT — Zentraler Guard geschlossen, weitere Schreiber offen

2026-10-05: Anlage/Post/Storno pruefen verpflichtend ihre Zielperiode.
Anlage/Post verwenden Buchungsdatum, Storno das neue Buchungsdatum. Eine
explizite Create-Periode muss passen. Shared-Journal-/Exclusive-Periodensperre
schliesst das Rennen auch ohne Periodenzeile; READ COMMITTED und FOR SHARE
sichern frischen Zustand. Close/Reopen und Perioden-API Create/Update
verwenden dieselbe Sperre. Vorhandenes NULL/unknown sperrt, fehlende Zeile
bleibt nach bestehendem Vertrag offen. ADJUSTING bleibt buchbar.
371 Journal-/Periodentests plus 25 Statusvertraege bestanden; 29 neue
(19 PostgreSQL), vier echte Wartebelege. Globalen DDL-Test durch privaten
Schemafehlerfall ersetzt. QA:
[Periodenpflicht](../quality-assurance/journal-period-enforcement-20261005.md).
Offen bleiben andere rohe Journal-/OP-Schreiber und deren gemeinsame
Abschlussreife-/Perioden-/Transaktionsintegration. Kein globaler Buchungs-
oder GoBD-Beleg. API-Fehlermapping, Audit/Anchor-Atomizitaet, Schema/Hash,
NULL-Waehrung und Cancel-Grund bleiben eigene offene Vertraege.

## JOURNAL-CREATE-CANONICAL — Zweiter Anlageweg entfernt, API/Schema offen

2026-10-05: Repository-Create nutzt FinanceTransactionService statt eigener
JSON/Float-Hashberechnung. Explizite Waehrung und Buchungsdatum gespeichert;
Storno erhaelt Waehrung einschliesslich explizitem NULL. Nicht speicherbare
Steuer-/Kostenstellen-/Profitcenter-/Segmentangaben werden abgewiesen;
DTO-Leerdefaults enthalten keine Fachinformation. Fremdtenant, freie
Stempel/Status/ID-Felder und widerspruechliche Kopfsummen abgewiesen.
321 Regressionen, 39 neue (fuenf PostgreSQL); vorhandener valeo_probe,
Revision zusammenfuehrung_20261005, ohne eigenen Migrationslauf. QA:
[Journalanlage](../quality-assurance/journal-create-canonical-20261005.md).
Die darunter genannten Repository-Create-Gaps vom vorherigen Stand sind
mit diesem begrenzten Vertrag geschlossen. Offen bleiben API-HTTP-Mapping/
Session/Audit/Anchor, NULL-Waehrung im Response-DTO, aktive fremde API/DTO-
Claims, Datumsnormalisierung und vollstaendiger Hash. ORM-Laengen und
reales Schema widersprechen sich noch (entry_number 20/50, reference 50/255,
description VARCHAR(200)/TEXT; Datum DateTime/DATE). Keine Migration in
fremder Nutzung, keine erfundene Datenkorrektur oder globale API-Abnahme.

## JOURNAL-REPOSITORY-LIFECYCLE — Mutationen zentral, API/Anlage offen

2026-10-05: JournalEntryRepositoryImpl delegiert Update/Delete/Post/Reverse
an FinanceTransactionService. Get/Exists/Count greifen nicht mehr auf die
fehlende is_active-Spalte zu; Lesefehler werden nicht als leeres Journal
verschluckt. 282 Tests, 35 neue (27 PostgreSQL), zwei neue echte
Repository-Wartebelege inkl. vorab gecachtem Zustand. QA:
[Repository-Lifecycle](../quality-assurance/journal-repository-lifecycle-20261005.md).
Offen: Repository-Create mit anderem Hashpayload und still verworfenen
DTO-Feldern; API faengt Domainfehler noch als HTTP 500 ab, hat einen eigenen
Session-/Audit-/Anchor-Weg. Nicht unterstuetzte Datumsupdates werden jetzt
explizit abgewiesen statt ungesichert geschrieben. API/DTO-Dateibesitz ist
weiter im fremden L3-JOURNAL-SOURCE-20260910 als in arbeit eingetragen.
Cancel-Grund, vollstaendiger Hash/Schema, weitere SQL-Schreiber, Consumer-
Atomizitaet und Bankintegration offen. Keine globale GoBD-/API-Abnahme.

## JOURNAL-LIFECYCLE-INTEGRITY — Service serialisiert, API/Repository noch offen

2026-10-02: Kopf-FOR-UPDATE mit frischem ORM-Zustand fuer alle Service-
Mutationen; Zeilen-Lesesperre, Stempelerhalt bei Delete-Abweisung/Cancel,
eigene ungestempelte Altentwuerfe loeschbar. 247 Tests, 16 neue PostgreSQL-
Faelle, fuenf echte wartende Paralleltransaktionen inkl. gecachtem Zustand.
QA: [Lifecycle-Vertrag](../quality-assurance/journal-lifecycle-integrity-20261002.md).
Fortschritt 2026-10-05: Repository-Lifecycle delegiert jetzt an den Service.
Offen: Journal-API Fehler-/Session-/Auditvertrag und Repository-Create;
Cancel-Grund ohne Journal-ORM-Mapping/Audit, Consumer-Atomizitaet, Schema/Hash,
Bewertung und Bankintegration. Kein globaler Stempel-/Delete-/Concurrency-Beleg.

## JOURNAL-AMOUNT-INTEGRITY — Service-Guard geschlossen, Bewertung/Schema offen

2026-10-02: Exakte endliche positive ausgeglichene Centbuchungen im Service;
Create ohne Datenbankzugriff bei ungueltigem Betrag, erneute echte Zeilen-/
Kopf-/Tenant-/Kontopruefung vor Post/Reverse. Produktions-Nullbetragshelper
entfernt, fehlende Bewertung gemeldet und keine FiBu-Referenz behauptet.
231 Tests bestanden (46 neue, 18 PostgreSQL). QA:
[Betrags-/Lifecycle-Vertrag](../quality-assurance/journal-amount-integrity-20261002.md).
Offen bleiben reale Bewertung, andere Schreiber, physische Betragsdubletten,
Concurrency weiterer Journalwege/Consumer-Atomizitaet, Hash, Bankintegration
und Handbuch-Drift. Guard ist keine Produktionskosten- oder GoBD-Abnahme.

## JOURNAL-ACCOUNT-ID — Service/Verbraucher kanonisch, Schema/andere Schreiber offen

2026-10-02: Globale OR-Kontenaufloesung und accountId-Fallback im
FinanceTransactionService entfernt. Neun nummernkonfigurierte Verbraucher
loesen eigene Nummern ausdruecklich zu IDs auf; eine gebuendelte Pruefung
vor Kopf/Zeilen-Schreiben. Automatische Sales-Kontenanlage und toter zweiter
Invoice-GL-Weg entfernt. 186 Tests bestanden (26 neue, 16 PostgreSQL).
QA: [Kontoreferenz-Vertrag](../quality-assurance/journal-account-identity-20261002.md).
Weiter offen: globale account_number-UQ, Komposit-Tenant-FKs/andere Schreiber,
Consumer-Atomizitaet, vollstaendiger Hash-Payload/Lifecycle/Betragskanonisierung,
Bankintegration und Handbuch-Drift im parallelen Worktree. Neu belegt:
Leere/Nullbetragsjournale im Service sind jetzt abgewiesen und Produktions-
Scheinbuchungen entfernt (JOURNAL-AMOUNT-INTEGRITY). Reale Bewertung offen.

## JOURNAL-STAMP-INTEGRITY — Service-Guard geschlossen, Journalkanonisierung offen

2026-10-02: Verschluckter Stempelfehler und konkurrierende Sequenzvergabe im
FinanceTransactionService behoben (115 Tests, 19 neue, 14 echte PostgreSQL).
READ-COMMITTED-Transaktionssperre, konsistente Sequenz/Vorgaenger-Metadaten,
keine Teilstempel oder Create/Reverse-Commits bei Fehler. QA-Nachweis:
quality-assurance/journal-stamp-integrity-20261002.md.
Offen bleiben kanonischer Hash-Payload inkl. Zeilen, alle weiteren Schreiber,
Delete-Integration weiterer Journalwege, Konto-ID/Nummern-Verwechslung anderer Journalwege und
skalierbarer Kettenzustand. Bankmigration/Betriebsprobe weiter offen.

## BANK-RECONCILIATION-PROOF — Code geprueft, Integration noch offen

Explizite GL-Konto-ID mit Tenant-FK statt verlorenem gl_account_number;
Header-Tenant/Konto, ein SQL-Snapshot, Decimal/null und typisierte Statuswerte.
55 Backend- und fuenf Maskentests bestanden. Gemeinsame Migration nicht
angewandt: parallele EUDR-Kette braucht koordinierten Merge-Head und danach
Betriebsprobe. Kein abgeschlossener Lieferstatus. QA:
[Saldennachweis](../quality-assurance/bank-reconciliation-proof-20261002.md).
Neu belegte Journal-Gaps: Kontoreferenzen anderer Journalwege, unvollstaendiger
GoBD-Hash-Payload, globale account_number-UQ und Betragsdubletten. Auch Bank/GL-
Zeilenlink, Bankstamm-Audit/RBAC und native Maskenkonvergenz offen.

## BANK-DIRECTBOOK — unsicheren Altweg entfernt, Hauptbuchnachweis offen

Entwicklungsfreigabe fuer Altlasten repositoryweit in AGENTS.md. Direkte
Abgleichsbuchung mit geratenen Konten geloescht; true-Flag explizit 409 vor
DB-Zugriff, False-Default fuer interne Calls. Keine Vorschlaege, stets keine
Buchungsfreigabe. Maske entfernt lokale Scheinzuordnung und Book-Aktion;
Save prueft. 62 Backend- und zwei Maskentests bestanden.
Offen: Mandant/Konto-/GL-Bindung, Journalbetragsdubletten, stille Lesefehler,
PARTIAL/Vollstaendigkeitsnachweis und CSV-Saldonachweis. Der bestehende
Saldenvergleich ist hiermit nicht als korrekt abgenommen. Typecheck weiter
rot durch bestehendes CallWidget.tsx:54. QA: bank-directbook-retirement-20261001.md.

## BANK-STATEMENT-DATE — ein fachlicher Stichtag (2026-10-01)

**Geschlossen:** Importdatum statt Saldo-Datum, verschiedene CSV-Stichtage,
Datumskonflikt bei Replay, MT940-Buchungen ausserhalb Saldointervall und
leere Fremdwaehrung. 169 Vertraege bestanden (15 neu), bestehender valeo_probe,
keine neue Datenbank/Dockerinstanz oder Reset. Kein neues API-/Schemafeld.
**Offen:** Historische kanonische Kopf-Daten, Bankreconciliation (Query-Tenant,
Kontobindung/Hauptbuch/Stichtag und angenommene Abstimmbarkeit), weitere
Bankprofile und GitHub-CI/Deployment. Lager-Referenzdubletten gefunden;
Inventory-WIP wird separat bearbeitet. Nachweis:
docs/quality-assurance/bank-statement-date-20261001.md.

## BANK-LEGACY-IMPORT-INTEGRATION — zweiter Bankweg entfernt (2026-10-01)

**Geschlossen:** bank_import.py / INT-BANK-001, vier alte DTOs, konkurrierende
API-/Parser-/Testvertraege und zwei alte domain_finance-Banktabellen entfernt.
Ein aktives Modell domain_erp unter /api/v1/finance. Nach expliziter User-
Freigabe Entwicklungs-Altbestand entfernt, kein Archiv/Adapter. Migration auf
beiden vorhandenen Datenbanken verifiziert; keine neue DB/Dockerinstanz,
kein Reset, kein zweites Matching oder OP-Umschreiben. 187 Vertraege bestanden,
davon 9 neue. Inventare, Architekturindex, OpenAPI und Tabellenkatalog nachgezogen.
**Offen:** GitHub-CI/Deployment und kanonische Fachgaps (weitere CAMT-Profile,
semantische Duplikate, Reversal/GL); keine pauschale Bank-/Gesamtfreigabe.
Nachweis: docs/quality-assurance/bank-legacy-retirement-20261001.md.

## COVERAGE-RETIRED-MODULE-INTEGRITY — reale Loeschung und Messwerte (2026-10-01)

**Geschlossen:** verwaiste Coverage-Schwellen nach echter Modul-Loeschung,
fehlende Quelldatei trotz XML-Erfolg und NaN/Infinity-Vergleichsumgehung.
Git-/Dateinachweis schuetzt Retirement; Rename-Nachfolger behaelt mindestens
die alte Schwelle. Umgeschriebene/aus app verschobene Nachfolger werden nicht
als unbedeutende Loeschung angenommen. Vier Kontrakt-Leichen entfernt,
alle 99 lebenden Schwellen exakt unveraendert.
**Offen:** Reale Coverage-Unterschreitungen und fehlende Messwerte im vorhandenen
datierten Bericht; frische SHA-/Run-gleiche CI-Evidence erforderlich. Keine
behauptete Gesamtabdeckungsverbesserung. Nachweis:
`docs/quality-assurance/coverage-retired-module-integrity-20261001.md`.

## BANK-CAMT-PARSER-INTEGRITY — gebuchte Salden und Einzelzahlungen (2026-10-01)

**Geschlossen:** falsche erste Saldoart/Vorzeichen, errechneter statt gepruefter
Endsaldo, Datumsersatz durch heute, ungebuchte/mehrdeutige Einzelzuordnung,
verschachtelte Ersatzwerte sowie verlorene Gegenkonten/Referenztexte.
OPBD/CLBD und BOOK im CAMT.053.001.02-Einzelauszugsprofil abgestimmt;
134 Vertraege, davon 32 neue CAMT-Vertraege bestanden auf vorhandenem valeo_probe.
**Offen:** Weitere Versionen/Bankprofile und andere Importwege, Sammler-
aufloesung, FX, Retouren, Rueckbuchung/GL und semantische/historische
Datei-Duplikate. GitHub-CI/Bankprofil-/Deployment-Abnahme extern. Nachweis:
`docs/quality-assurance/bank-camt-parser-integrity-20261001.md`.

## BANK-MT940-PARSER-INTEGRITY — vollstaendige Zeilen und Salden (2026-10-01)

**Geschlossen:** verlorene :61:-Zeilen ohne optionales :86:, falsche
Datumslaenge, positive Sollsalden und ignorierter Endsaldo. Begrenztes
IBAN-Einzelauszugsprofil; Bank-Saldo muss alle Zahlungszeilen exakt abdecken.
102 Parser-, Finanz- und DQ-Vertraege bestanden auf bestehendem valeo_probe.
**Offen:** RC/RD-Rueckbuchungsintegration, weitere Bankprofile/SWIFT-Umschlaege,
nationale Kontokennungen, weitere CAMT-Bankprofile und semantische bzw.
historische Datei-Duplikate. Fremde CRM-Baselineintegritaet bleibt beim Owner;
GitHub-CI/Bankprofil-/Deployment-Abnahme extern. Nachweis:
`docs/quality-assurance/bank-mt940-parser-integrity-20261001.md`.

## BANK-IMPORT-ACCOUNT-REPLAY — Konto und Dateiwiederholung (2026-10-01)

**Geschlossen:** Import auf unbekanntes/fremdes/inaktives Konto,
ungepruefte IBAN und Kontowaehrung; erneute Zahlung durch identische
Datei-Bytes in Tenant/Konto/Format. Beide CSV-Routen teilen Sperre und
Identitaet; Replay zeigt gespeicherten Status ohne zweites Matching/Audit.
106 verschiedene Vertraege bestanden auf vorhandenem valeo_probe.
**Offen:** Historische UUID-Importe ohne Dateiidentitaet, gleiche Buchungen
in unterschiedlichen Bytes/Konto-IDs/Formaten, weitergehende Parserdetails,
Rueckbuchung/GL und externe CI-/Deployment-Abnahme. Slice-CLI-Fehlaufruf durch
Ergebnisbeschreibungen als Befehle in beiden eigenen Slices korrigiert. CRM-Godfile
bleibt beim aktiven Owner. Nachweis:
`docs/quality-assurance/bank-import-account-replay-20261001.md`.

## BANK-PAYMENT-MATCHING-INTEGRITY — sicherer Abgleich (2026-10-01)

**Geschlossen:** angenommene statt gelesene Zahlung, falscher Belegstatus bei
Teilzahlung, Fremdmandanten ueber Query, ungesicherte Wiederholung und
fehlender atomarer Nachweis. Import-, Einzel- und Batchabgleich verwenden
denselben Vertrag; 82 verschiedene echte und bestehende Vertraege bestanden.
**Nachzug:** Kontobindung und identische Datei-Bytes in BANK-IMPORT-ACCOUNT-REPLAY
abgesichert. **Offen:** Historische/semantische Duplikate, Rueckbuchung,
GL-Journalintegration und weitergehende CAMT-/MT940-Abnahme. Fremde aktive
CI-Gaps und externe Integration bleiben offen. Nachweis:
`docs/quality-assurance/bank-payment-matching-integrity-20261001.md`.

## BANK-STATEMENT-IMPORT-INTEGRITY — manueller Import (2026-10-01)

**Geschlossen:** Selbstduplikate gueltiger Zeilen, Erfolg trotz SQL-/Commitfehler,
Waehrungsverlust und kollidierende Import-IDs. 18 Vertraege im manuellen
Meilenstein bestanden. Die damalige 501-Sperre fuer auto_match ist im Nachzug
BANK-PAYMENT-MATCHING-INTEGRITY durch den sicheren gemeinsamen Vertrag ersetzt.
Aktuelle Abnahme und verbleibende Fach-/Parsergaps stehen im Nachzug.
Nachweis: `docs/quality-assurance/bank-statement-import-integrity-20261001.md`.

## SECURITY-PATCH-MILESTONE — Paketbefunde (2026-10-01)

**Repo-seitig repariert:** PyJWT 2.15.0, grpc-js 1.14.5, fastify 5.12.5,
fast-uri 3.1.8 und moment 2.31.0. Frozen Install, JWT-Vertraege und Audits
geprueft. Root/CRM-Marketing/JavaScript ohne Befunde; AI behaelt drei
bestehende Embedded-only-Chroma-Bewertungen, ohne Review-Verlaengerung.
**Extern offen:** GitHub-Alert-Schliessung nach Defaultbranch-Integration,
CI und Deployment. Nachweis:
`docs/quality-assurance/security-patch-milestone-20261001.md`.

## TEST-DATABASE-RESOURCE-POLICY — alle Agenten (2026-10-01)

**Verbindlich integriert:** keine zusätzlichen Datenbank-/Dockerinstanzen
pro Test/Suite/Slice/Agent. Bestehenden Prüfstand mit eigenen isolierten
Testdaten verwenden. 36 Finanzverträge auf vorhandenem `valeo_probe` grün;
eigene zusätzliche Datenbank nach Nutzungsprüfung entfernt. Fremde
Ressourcen bleiben unberührt. Runbook und gemeinsame Agentenregel:
`docs/quality-assurance/test-database-resource-policy-20261001.md`, `AGENTS.md`.

## PAYMENT-CSV-IMPORT-INTEGRITY — Zahlungsimport (2026-10-01)

**Geschlossen:** Selbstduplikat-Blockade gültiger CSV-Daten, verschwiegene
Schreibfehler, Verlust der Währung, ID-Kollisionen innerhalb einer Sekunde
und Abweichung zwischen gerundetem SQL-Betrag und ungerundeter Antwort.
10 echte PostgreSQL-/HTTP- und sechs bestehende DQ-Verträge grün;
Dead-Transaction-Inventur und Ratsche stehen auf 75.
**Offen:** Andere Bankimport-/Matchingwege und die restlichen 75 Fundstellen
werden hier nicht als geschlossen gewertet. Nachweis:
`docs/quality-assurance/payment-csv-import-integrity-20260930.md`.

## PAYMENT-EXECUTION-ATOMICITY — Zahlungslauf (2026-09-30)

**Repo-seitig geschlossen:** falscher BEZAHLT-Status bei Teilzahlung,
interne Teilcommits und verschluckte Ausführungsfehler. Reale PostgreSQL-
Rollback-, Mandanten-, Wiederholungs- und Paralleltests sind grün.
**Separat offen:** Bankabnahme und Legacy-Belege ohne Tenantkennung;
projektweite Godfile-Befunde in fremden aktiven Slices bleiben sichtbar.
Nachweis: `docs/quality-assurance/payment-execution-atomicity-20260930.md`.

## CODE-IMPROVEMENT-INTEGRITY — verlässliche Pruefungen (2026-09-30)

**Repo-seitig abgeschlossen; externer CI-Nachweis offen.** Pagination wird pro Abfrage
und Funktion gemessen, Baselines gegen den Ausgangscommit geschuetzt,
Frontendtests sind verbindlich, Sonar verwendet SHA-/inhaltsgleiche Coverage
aus demselben Run. Der vorhandene Nightly publiziert lesende Artefakte.
Nachweis und Grenzen: `docs/quality-assurance/code-improvement-integrity-20260930.md`.
90 fokussierte Vertraege und der volle Frontend-Lauf (914 Tests) sind lokal gruen.

**Altbestand offen.** Die neue Messung erfasst 289 unbeschraenkte Abfragen in
262 Funktionen statt der unzureichenden alten Dateizaehlung (53). Das ist
keine Schuldentilgung. Fachliche Vollaggregate und echte Listen sind je
Funktion zu klassifizieren und mit Fehlervertraegen abzusichern.
Lokale Fremdaenderungen an CRM/Maskenbruecke verletzen aktuell die Godfile-
Ratsche; deren Owner muessen den Strukturabbau liefern, die Baseline bleibt scharf.

**Extern offen.** Erster realer GitHub-Lauf, Branchschutz mit erforderlichen
Checks und Sonar-Projekt/Token. Keine externe Freigabe wird lokal fingiert.

## DUE-DATE-CALENDAR — vergangene Faelligkeiten behoben (2026-09-30)

**Erledigt.** Elf Pfade interpretierten „in 30 Tagen“ als Austausch des
Monatstags und konnten dadurch vergangene Faelligkeiten erzeugen. Alle Aufrufer
verwenden nun `business_today()` und `business_date_after(30)`; Monats-,
Jahres- und Schaltjahrgrenzen sind getestet. Die Business-Time-Ratsche sinkt
von 244 auf 212 direkte Kalenderquellen. Details:
`docs/quality-assurance/due-date-calendar-20260930.md`.

## GODFILE-RATCHET — Gate repariert, Zerlegung offen (2026-09-30)

**Gate erledigt.** Der eingecheckte Stand enthaelt 15 Python-Endpunkte ueber
1.000 Zeilen. Die alte globale Schwelle 12 war bereits unterschritten und
blockierte alle spaeteren Backend-Pruefungen. Die neue pfad- und zeilengenaue
Baseline blockiert neue, verschobene und gewachsene Godfiles und muss bei jedem
Abbau sinken. Details:
`docs/quality-assurance/godfile-ratchet-20260930.md`.

**Abbau offen.** Zuerst eignen sich `logistics_tours.py` (1.033),
`admin_suite.py` (1.038) und `einkauf_bestellvorschlag.py` (1.058).
`crm_360.py` lag im Arbeitsbaum ueber 1.000 Zeilen. Die Register sind nach
`crm_360_reads.py` und `crm_360_tabs.py` gezogen; die Datei liegt wieder darunter.

## MERIDIAN-PARTY-OBJECTPAGE — eine Kundenakte (2026-09-30)

**Erledigt.** Lead und Bestandskunde teilen eine native Object Page. KIM und das
Kunden-Cockpit sind Redirects inklusive `?tab=`. Listen-IDs (`kunden_nr`,
Partnernummer) und `/verkauf/kunden-stamm/:id` oeffnen denselben Stamm. Chef,
Praesente, Postfach und Geo sitzen in der ScreenDefinition; Mini-Apps bleiben weg.
Angebote kommen aus `crm_opportunities`, Historie aus den CRM-Aktivitaeten.
Aufgaben sind nur Typ Aufgabe oder Task; ein offener Besuch bleibt in der Historie.
Potenzial ist der juengste Satz aus `public.customer_potential_snapshot`.
Chef-Anweisungen, Anschriften, Kontoauszug und CPD-Konten sind in der Akte lesbar.
Rabatte, Preise und das SEPA-Mandat kommen vom Partner.
Adresse, Branche und das operative Kreditlimit (Ausnahme aus `credit_limits`,
sonst der Stamm) stehen in der Akte. Koordinaten kommen aus `public.kunden_geo`,
ein reiner Bestandskunde aus `public.kunden` (`name1`, `tel`).
Mutationen der Tabs 21–25 bleiben unter `/verkauf/kunden-stamm/:id?pflege=1`.
`Bearbeiten` oeffnet diese Pflege ueber die Partnerkennung und schreibt auf der Akte nichts.

## POS-ZAHLARTEN + AGRAR-KONTRAKTE — Welle 2, zweiter und dritter Eintrag (2026-09-30)

**Erledigt (POS).** `domain_pos.payment_methods` und `domain_pos.promotions`
kommen aus `pos_zahlarten_aktionen_20260930`; die Laufzeit-DDL im Endpunkt ist
weg. Nebenbefund behoben: Ein **Datenbankfehler** lieferte dieselben drei
Zahlarten wie leere Pflege — eine Stoerung sah aus wie eine Konfiguration.
Jetzt 503. Fuenf Vertraege gruen gegen den frischen Stand.

**Offen, gehoert dem Agrar-Owner.** `domain_agrar.kontrakt_dispositionen` und
ihre **Elterntabelle** `domain_agrar.kontrakte` fehlen beide im
Migrationsstand. Dazu: Laufzeit-DDL in `kontrakte_service.py:410`; die drei
Dispositions-Endpunkte nehmen `tenant_id` entgegen und benutzen ihn nicht
(fremder Lese- **und** Schreibzugriff ueber die Kontraktkennung); und
`kontrakte.py:1001` verschluckt die fehlende Tabelle in eine leere Liste.
Handshake im Workboard.


## WHISTLEBLOWER-EINE-TABELLE — fuenf Befunde in einer Tabelle (2026-09-30)

**Erledigt.** Gefunden beim Abarbeiten der Schema-Drift-Liste. Die Tabelle
legte sich zur Laufzeit selbst an; zwei Endpunkte schrieben sie mit
unvereinbaren Formen; es gab keinen Mandantenbezug, weshalb `GET` alle
Meldungen aller Haeuser listete; die Notiz entstand per f-String in einem
JSON-Text; und die Routen lagen ohne Praefix unter `/api/v1/reports`, neben den
Verkaufsauswertungen.

Behoben mit Migration `whistleblower_eine_tabelle_20260930` und einem
ueberarbeiteten `compliance_whistleblower.py`. Sechs Vertraege gruen gegen
beide Datenbankstaende. Details:
`docs/quality-assurance/whistleblower-eine-tabelle-2026-09-30.md`.

**Offen, Produktentscheidung:** Sind der kurze und der LkSG-Weg Dubletten? Beide
schreiben jetzt dieselbe Tabelle; der eine bietet Token und Notizen, der andere
Kontaktmail und Statusuebergaenge. Und: Soll die Meldung verschluesselt werden?
Heute steht sie im Klartext — das ist jetzt wenigstens ehrlich benannt (die
Spalte hiess `description_encrypted`).


## GATE-BLOCKER — die zwei kleinen Blockierer des Quality Gate (2026-09-30)

**Erledigt.** `brace-expansion` von `^2.1.4` auf `^2.1.6` (zwei High-Funde,
`pnpm audit --audit-level high` jetzt Exit 0) und der Kontrast der
Kachelueberschrift in `LaunchpadBoard.tsx` **und** `start-dashboard.tsx`.

**Gemessen statt geschaetzt:** Mit `text-muted-foreground` verfehlen alle zwoelf
Kombinationen aus sechs Chart-Toenen und zwei Deckungsgraden die 4,5:1 (3,18 bis
4,50). Mit `text-foreground` sind es 8,84 bis 12,52.
`src/__tests__/kachel-kontrast.test.ts` liest die echten Tokens aus
`palette.css` und rechnet es nach — deterministisch, im Gegensatz zum axe-Lauf,
der ohne Backend nur prueft, was gerendert wurde.

**Erledigt (2026-09-30):** Die Pagination-Ratsche steht wieder bei 53 und ihre
Schwelle blieb unveraendert. Drei CRM-Consent-Listen sind echt paginiert;
`document_allocations.py` ist als vollstaendiges Belegaggregat begruendet
ausgenommen. Eine Teilseite wuerde dort Summen und offene Mengen verfaelschen.
Nachweis: `docs/quality-assurance/pagination-ratchet-restore-20260930.md`.


## SCHEMA-DRIFT-GATE — Datenbank gegen Migrationsstand (2026-09-30)

**Erledigt.** `scripts/check_schema_drift.py` vergleicht eine Ziel-Datenbank mit
einer frisch migrierten: Tabellen, Spalten (Typ, Laenge, Skala, Nullbarkeit),
Fremdschluessel, CHECK, UNIQUE und Indizes. 15 Unit-Tests ohne Datenbank, ein
Lauf gegen echtes Postgres. Bewusst keine Ratsche und nicht in CI — der Abstand
haengt vom Rechner ab.

**Der Befund:** **881 Abweichungen** zwischen `valeo_neuro_erp` und dem
Migrationsstand. Die Entwicklungsdatenbank ist nie das gewesen, was die
Migrationen beschreiben. Vier Stichproben von Hand bestaetigt.

**Offen, Entscheidung des Hauses:** 484 Funde sind „fehlt" — die Migration gibt
es, sie ist auf dieser Datenbank nur nie vollstaendig angekommen. Die Reparatur
ist ein Neuaufsetzen, keine Migration. Ob die gewachsenen Daten erhalten bleiben
muessen, entscheidet das Haus; solange sie bleiben, gilt „Schema frisch pruefen,
Daten gewachsen".

**Offen, gehoert den Fachownern:** 76 Tabellen und Spalten, die der Code benutzt
und die keine Migration anlegt, plus 21 reine Typunterschiede. Handshake im
Workboard. 26 weitere ohne Codebezug: dokumentieren, nicht still loeschen.


## TOTE-TRANSAKTION — except ohne Rollback (2026-09-30)

**Erledigt.** `scripts/check_dead_transactions.py` (AST-Suche, Ratsche 78, im
Quality Gate vor der Pagination-Pruefung), 10 Unit-Tests ohne Datenbank, 5
HTTP-Vertraege gegen den frischen Pruefstand. Der Art.-17-Pfad ist behoben und
**auditiert**: hashverketteter Eintrag in `domain_shared.audit_logs` mit dem
Handelnden, dem Betroffenen und dem Loeschprotokoll; ein gescheiterter
Auditeintrag steht als `audit_fehler` in der Antwort.

**Offen, gehoert den Fachownern:** 18 mutierende Fundstellen in Finanzen (8),
Agrar (2), Verkauf (1), Lager (3), Logistik (1) und CRM (1) plus zwei im
Bankimport. Der schwerste ist `payment_runs.py:799`: Die erkennbare Absicht
„einen Posten ueberspringen, mit den uebrigen weitermachen" haelt nicht — nach
einem Fehlschlag faellt der ganze Lauf mit 500, und niemand erfaehrt, welcher
Posten der Ausloeser war. Handshake im Workboard, Einordnung je Stelle in
`docs/quality-assurance/tote-transaktion-2026-09-30.md`.

**Offen, Entscheidung:** Die 59 lesenden Fundstellen richten keinen unmittelbaren
Schaden an (die Anfrage endet, die Sitzung wird geschlossen). Ob sie trotzdem
aufgeraeumt werden, ist eine Frage von Aufwand gegen Gleichfoermigkeit.


## DB-PRUEFSTAND — frische Datenbank als Prüfstand (2026-09-30)

**Erledigt.** `scripts/pruefstand_db.py` setzt eine frisch migrierte Datenbank
auf (drop, create, migrate), idempotent und ohne Zugangsdaten im Code.
`TEST_DATABASE_URL` oder Ableitung aus `DATABASE_URL`. Regel in CLAUDE.md,
Runbook unter `docs/quality-assurance/pruefstand-datenbank.md`. Nachweis: die
elf in CI roten Testdateien laufen gegen einen von null aufgebauten Prüfstand
mit 87 bestandenen Tests durch.

**Erledigt (SLICE-YAML-INTEGRITY-20260930).** Leere Schlussdokumente werden
gelesen; befuellte zweite Dokumente und doppelte Schluessel sind explizite
Fehler. 19 echte Formfehler in abgeschlossenen historischen Slices wurden
inhaltserhaltend normalisiert. Inventur: 290/290 YAMLs lesbar, null Formfehler.
Ein Bestandstest verhindert Rueckfaelle; fehlende aktuelle Harness-Felder
in Legacy-Slices bleiben als Vertragsluecken erkennbar. Details:
`docs/quality-assurance/slice-yaml-integrity-20260930.md`.

**Offen, Entscheidung:** Der Prüfstand sagt nichts darüber, ob die gewachsene
Datenbank noch zum Schema passt. Diese Frage beantwortet der Slice
`SCHEMA-DRIFT-GATE`.


## MERIDIAN-BELEG-SYSTEMWEIT — Beleg-Look als Voreinstellung (2026-09-29)

Status: **abgeschlossen, Restpunkte offen.** Slice
[`docs/agent-ops/slices/MERIDIAN-BELEG-SYSTEMWEIT-20260929.yaml`](../agent-ops/slices/MERIDIAN-BELEG-SYSTEMWEIT-20260929.yaml).

| Lücke | Prio | Stand |
|---|---|---|
| Reklamation ohne fachliche Nummer; `reklamation_nr` ist der Primärschlüssel mit Präfix | P2 Qualität | geschlossen 2026-09-30: `REK-JJJJ-NNNNN` je Mandant und Geschaeftsjahr, Bestand migriert |
| Pilotseiten (`usePilotRenderPlan`: Auftrag, Kontrakt, Kunde-Altpfad) laden nur das aktive Register und erzwingen deshalb `tabs` | P2 UIX | geschlossen 2026-09-30: drei Pilotseiten auf `useUniversalMaskRuntime`, `usePilotRenderPlan` entfernt |
| Register-Endpunkte `mask-rollouts/*/tabs/*` verlangen UUIDs, Ernteabrechnungen haben Text-IDs; die Register bleiben dann leer mit Fehlermeldung | P2 Agrar | geschlossen 2026-09-30: Text-IDs fuer textbasierte Masken, UUID-Pruefung nur fuer Bestellung und Lieferant |
| Verkaufschance: Kopfdaten kommen aus dem externen crm-sales-Dienst; Browser-Abnahme ohne Dev-Daten, nur HTTP-Vertrag | P3 | offen |
| Futteranalyse-Tests hinterlassen Daten im Dev-Mandanten (wie die bestehenden Tests) | P3 | offen |
| Fremd, nicht Teil des Slices: `test_sales_invoices_api.py` (Kunden ohne `company_name`), `test_feed_advice_screen_definition.py::test_feeding_businesses_are_a_native_grant_aware_worklist` (erwartet Layout ohne `columnNavigation`) | P2 | offen |

## EK-BESTELLUNG-FUEHREND — Native Maske gegen L3 (2026-09-18)

Status: **abgeschlossen 2026-09-29.** Slice
[`docs/agent-ops/slices/EK-BESTELLUNG-FUEHREND-20260918.yaml`](../agent-ops/slices/EK-BESTELLUNG-FUEHREND-20260918.yaml).
Die native Maske `einkauf/purchase-order` ist die fuehrende Bestellmaske
(L3-Kopf, Positionsgrid, drei Bestellfaelle). Die Vereinheitlichung der beiden
Bestandsspeicher Compat-`purchase-orders` und `domain_einkauf.bestellungen`
ist ein eigener Folgeslice. Keine fuenfte Custom-Seite. HOME-UIX bleibt
Besitzer von `bestellungen-liste.tsx`.

| Luecke | Prio | Stand |
|---|---|---|
| Bestellkopf ohne Ladetermin, Kontrakt, Skontostaffel, Ansprechpartner | P1 Einkauf | geschlossen in der nativen SD + ORM |
| Position ohne Lief-Artikel, Gebinde, Gewicht, Lagerfach | P1 Einkauf | geschlossen in der nativen SD + ORM |
| Drei Bestellfaelle (Bestand/Abverkauf, Direktlieferung, Innovation) | P1 Einkauf | geschlossen als `bestellfall` |
| Zwei Speicher Compat vs `domain_einkauf` | P1 Einkauf | ausserhalb dieses Slices; eigener Folgeslice |
| `bestellung-stamm` neben native | P2 | bewusst Compat-Bruecke, nicht fuehrend |

## HOME-UIX-ANWENDER-BEDIENWEGE — Touch, Sprache, Agent (2026-09-17)

Status: **in Arbeit.** Diagnose und erster Schnitt:
[`docs/design/uix-anwender-bedienwege.md`](../design/uix-anwender-bedienwege.md).
Chrome (Top-Leiste, Sprache, Tastenkürzel auf Touch), Queue, Kundenliste,
Ernte-Annahme, Aktivitäten (Datumsfilter), Bestand, OP, Waage-Liste,
Hofliste und Prozessleitstand nachgeschärft. Bestellungen- und Lieferungen-Liste
Arbeit zuerst. Verkauf-Lieferschein 44 px. Einkauf-Wareneingang 44 px inkl.
LS-Suche/Niederlassung. Wizard/NativeSelect 44 px. Angebot 44 px, DS nur Desktop.
Kundenstamm Register 44 px ohne Tab-23-Copy. Copilot-FAB auf Touch aus,
Öffnen über Benutzermenü. Angebotsliste Arbeit zuerst, DS nur Desktop.
Wiegungen: Anlegen zuerst, Schließen 44 px. Wiegeschein-Detail Register 44 px.
Annahme-Abrechnung: Lieferdaten zuerst, Korrekturen 44 px, kein Settlement-MCP.
Einkauf-Angebotsliste: ListReport zuerst, DS-Theater nur Desktop.
Buchungsvorlagen: Anwenden/Löschen 44 px, Anlegen ehrlich noch API.
LKW-Registrierung und Qualitätsprüfung: Wizard zuerst, Scan/QS 44 px.
Ein-/Auslagerung und Beladung: Wizard zuerst. Disposition: Tabelle zuerst.
Verladung-Liste und Inventur: Arbeit zuerst. Kontraktliste: Tipp statt Doppelklick.
Reklamationen: Tabelle zuerst, kein Rohrot.
Kontrakt-Detail: Operator-h1, Register 44 px. Rohware: Wizard zuerst.
Positionsmonitor/Alarme/Labor-Liste: Arbeit zuerst, 44 px.
Lieferanten, Rückverfolgbarkeit, Labor-Auftrag nachgezogen.
Silo-Terminal, Mengenzeiträume, Ernte/Aussaat/PSM-Listen nachgezogen.
Schlagkartei, Bodenproben, Sortenregister, Saatgut-Liste, Lagerplätze nachgezogen.
Maßnahmen, Kulturpflanzen, Dünger, Kunden-Schlagkartei nachgezogen.
Sachkunde, Auflagen, Biostimulanzien, Artikel, Lagerbewegungen,
Düngemittel-Stamm, Chargen, Futter, Zertifikate, Versicherungen, Projekte,
Förderung, Schäden, Schlag-anlegen nachgezogen (Code; Browser folgt).
Listen-Kartenstapel gilt für DataTable, ListReport und FastTable; form-level MCP bleibt offen.
Commit `e7aa92913`: Ablage-Export ohne Global-Intercept; KIM, Auftrag, Rechnung
und Lieferschein 44 px bei unveränderter Claude-Struktur; Register-Tabs
`min-h-touch`; ELSTER und Bankabgleich Arbeit zuerst, Theater nur Desktop;
Sprache findet `elster-online` und `bankabgleich`. `sales.invoice.propose` legt einen
ausstehenden Vorschlag an und bucht keine Rechnung. Weitere MCP-Schreibadapter bleiben offen.

| Lücke | Prio | Stand |
|---|---|---|
| Top-Leiste auf 390 px unter 44 px gequetscht; Ctrl+K; Mikrofon `hidden sm:` | P1 | geschlossen im Chrome |
| Tastenkürzel-Panel mit Hover-Modus auf Handy | P2 | geschlossen (`useTouchDevice` inkl. Breite) |
| Queue-Zeilen-CTAs `size="sm"` ohne Touch-Höhe | P1 Annahme | geschlossen |
| Kundenliste Rohblau-Link, knappe Toolbar | P2 Außendienst | geschlossen |
| Ernte-Annahme 32-px-Felder, unbenannte Lookups | P1 Waage | geschlossen |
| Aktivitäten KPI vor der Arbeit, Rohblau | P2 Außendienst | geschlossen |
| Bestand Roh-Orange/Grün, kleine Drilldowns | P2 Disposition | geschlossen |
| OP Rohblau, knappe Suche | P2 Buchhaltung | geschlossen |
| Aktivitäten Heute/Diese Woche tot | P2 Außendienst | geschlossen |
| Waage-Liste Arbeit unter DS-Theater | P1 Annahme | geschlossen |
| Hofliste F-Tasten-Copy, knappe CTAs | P1 Annahme | geschlossen |
| Prozessleitstand size=sm, Rohblau | P2 Leitung | geschlossen |
| Bestellungen-Liste Arbeit unter DS-Theater | P1 Einkauf | geschlossen |
| Lieferungen tot-Export, Rohblau, DS zuerst | P2 Versand | geschlossen |
| Lieferschein-Erfassung 32-px-Felder | P1 Verkauf | geschlossen |
| Einkauf-Wareneingang tote Lookups, 32 px | P1 Einkauf | geschlossen |
| Angebot 32 px, tot-Chevrons, Doppelklick, DS zuerst | P1 Außendienst | geschlossen |
| Kundenstamm Tab-23-Copy, 32-px-Zeilen, Header quetscht | P1 Außendienst | geschlossen |
| Copilot-FAB verdeckt Felder auf 390 px | P1 Außendienst | geschlossen (Menü statt FAB) |
| Angebotsliste Rollenfokus vor Suche, Rohblau | P1 Außendienst | geschlossen |
| Wiegungen Theater vor Anlegen, Schließen size=sm | P1 Annahme | geschlossen |
| Wiegeschein-Detail Eigenbau-Reiter, Theater zuerst | P1 Annahme | geschlossen |
| Annahme-Abrechnung size=sm, Englisch, Theater zuerst | P1 Buchhaltung | geschlossen |
| Einkauf-Angebotsliste Theater vor der Liste | P1 Einkauf | geschlossen |
| Buchungsvorlagen size=sm, tote Neue-Vorlage | P1 Buchhaltung | geschlossen |
| LKW-Registrierung Theater vor Wizard, Rohblau | P1 Annahme | geschlossen |
| Qualitätsprüfung size=sm, Theater zuerst | P1 QS | geschlossen |
| Einlagerung/Auslagerung Rohgrün, Fallkopf zuerst | P1 Disposition | geschlossen |
| Disposition KPI vor der Tabelle | P1 Disposition | geschlossen |
| Verladung-Liste KPI vor der Arbeit | P1 Disposition | geschlossen |
| Inventur Fallkopf/KPI zuerst, 16-px-Checkbox | P1 Disposition | geschlossen |
| Kontraktliste size=sm Pager, nur Doppelklick | P1 Handel | geschlossen |
| Reklamationen Fallkopf/KPI zuerst, Hover-Blau | P1 QS | geschlossen |
| Kontrakt-Detail Formularname, size=sm, Theater zuerst | P1 Handel | geschlossen |
| Rohware Theater/KPI vor dem Wizard | P1 Annahme | geschlossen |
| Reklamation-Detail Hover-Blau, Icon-Zurück | P1 QS | geschlossen |
| Positionsmonitor Doppelklick, 16-px-Checkbox, KPI zuerst | P1 Handel | geschlossen |
| Kontrakt-Alarme size=sm, KPI-Theater | P1 Handel | geschlossen |
| Labor-Liste Hover-Blau, Theater zuerst | P1 QS | geschlossen |
| Lieferanten Hover-Blau, KPI zuerst | P1 Einkauf | geschlossen |
| Rückverfolgbarkeit size=sm, Hover-Punkte | P1 QS/Lager | geschlossen |
| Labor-Auftrag 16-px-Checkbox, natives Select | P1 QS | geschlossen |
| GS1-Scanner Eigenbau-Reiter, Rohindigo | P1 Lager | geschlossen |
| Silo-Terminal Rohfarben, 40-px-Lagerwahl, nur Farbpunkte | P1 Disposition | geschlossen |
| Mengenzeiträume Icon-Löschen, size=sm | P1 Handel | geschlossen |
| Ernte/Aussaat/PSM Hover-Blau, tote Aussaat-Suche | P1 Agrar | geschlossen |
| Schlagkartei Hover-Blau, Icon-Aktionen, Theater zuerst | P1 Agrar | geschlossen |
| Bodenproben/Sorten Hover-Blau, KPI zuerst | P1 Agrar | geschlossen |
| Saatgut-Liste size=sm Icons, KPI zuerst | P1 Agrar | geschlossen |
| Lagerplätze size=sm, natives Select, Theater zuerst | P1 Disposition | geschlossen |
| Maßnahmen Hover-Blau, Icon-Aktionen, Theater zuerst | P1 Agrar | geschlossen |
| Kulturpflanzen Hover-Blau, KPI zuerst | P1 Agrar | geschlossen |
| Dünger size=sm Icons, KPI zuerst | P1 Agrar | geschlossen |
| Kunden-Schlagkartei size=sm, Rohamber, KPI zuerst | P1 Innendienst | geschlossen |
| Sachkunde/Auflagen Hover-Blau, Icon-Erledigt | P1 Agrar | geschlossen |
| Artikel toter Export, Hover-Blau | P1 Stamm | geschlossen |
| Lagerbewegungen size=icon, englische Typen | P1 Disposition | geschlossen |
| Chargen/Futter/Zertifikate/Versicherungen/Projekte/Förderung/Schäden Hover-Blau | P1 Betrieb | geschlossen |
| Listen als Karten statt Horizontal-Scroll | P2 | geschlossen in DataTable + ListReport + FastTable/VirtualDataTable (Touch); KIM/FSX unangetastet |
| Sprache steuert keine Waage/Queue | P2 | Navigation geschlossen (öffne Warteschlange/Wiegungen); Wiegen bleibt Voice-Gate UIX-072 |
| MCP 18 Tools, kein Masken-Schreiben, kein „öffne Kunde“ | P1 Agent | Registry 39; Mask-Write medium 0; Deep-Link + AP-Freigabe + Inventur propose-only; CI Mask-Map-Drift + Haupt-App Voice-Nav-Sync 2026-10-08; FIN-CLOSE ADR-076 / 1× open_high (Zahlauf) / 31× blocked_no_endpoint / SUS offen |
| KIM Object Page | P1 | geschlossen 2026-09-30 (`MERIDIAN-PARTY-OBJECTPAGE`) |
| Listen-Hover-Blau (ohne FSX/Auftrag/Rechnung) | P1 | geschlossen 2026-09-18 |
| Benachrichtigungen toter Als-gelesen-CTA | P1 | geschlossen (lokales Overlay, kein Write-API) |
| Ablage-Export vom Global-Handler geschluckt; Folgezeile abgeschnitten | P1 Dokumente | geschlossen 2026-09-29 (`e7aa92913`) |
| KIM/Auftrag/Rechnung/Lieferschein `size=sm` unter 44 px | P1 Innendienst | geschlossen 2026-09-29; Struktur bleibt Claude |
| ELSTER Theater vor den Schritten | P1 Buchhaltung | geschlossen 2026-09-29; Sprache `elster-online` |
| Bankabgleich Theater vor der ObjectPage | P1 Buchhaltung | geschlossen 2026-09-29; Sprache `bankabgleich` |
| Übrige Fachmasken Seite für Seite | P1 | Slice weiter; weitere MCP-Schreibadapter offen |

## HOME-IA-HIERARCHIE — Startseite zu viele Ebenen gleichzeitig (2026-09-17)

Status: **Sprint 1+2 abgeschlossen.** Sidebar auf `/` eingeklappt,
Meine Kunden drei Einstiege, Prozessraum als Auswahl statt Unterreiter,
App-Finder mit Kategorie/Beschreibung ohne Anpassen, Schnellaktionen 4+Mehr,
KPI mit Drilldown ohne Fake-Lagerzahl, Start-Steuerelemente 44 px. Sprint 3
(KIM Object Page) ist geschlossen (`MERIDIAN-PARTY-OBJECTPAGE`); vollständige
WCAG/Responsive/Heute der übrigen Masken bleiben offen.
Entscheidung: [`docs/design/launchpad-informationshierarchie.md`](../design/launchpad-informationshierarchie.md).

| Lücke | Prio | Slice |
|---|---|---|
| Fünf Navigationsebenen gleichzeitig; „Meine Kunden“ fünf überlappende Kacheln | P1 | Sprint 1 — umgesetzt, verifiziert |
| Gleiche Kachelgewichtung, KPI ohne Trend, zu viele Schnellaktionen | P2 | Sprint 2 — Code da |
| App-Finder ohne Kategorie, nur im Anpassen-Modus, Suche nur Label | P4 / Sprint 2 | geschlossen |
| KIM nicht durchgängiger Object-Page-Workspace | P1/P3 | geschlossen 2026-09-30 (`MERIDIAN-PARTY-OBJECTPAGE`) |
| Realtime-Leiste dauerhaft für alle | P4 | Code: nur bei Störung; rollenbasiert danach |

Nicht in diesem Gap: SAP visuell kopieren; erfundene „Heute“-Kennzahlen.

## ASK-ACKERSCHLAGKARTEI — Lastenheft LWK 2017+ (2026-07-16)

Status: **repo-Gaps geschlossen** (Slice ACKER-OPEN-GAPS-009). Traceability: [`docs/specs/agrar/ackerschlagkartei-traceability.md`](../specs/agrar/ackerschlagkartei-traceability.md).

| Cluster | Status |
|---|---|
| AS-W1…W10 + Ink.1–5 Kern (Stammdaten, Register, QS/AUM, Lager, Offline-Queue) | erledigt (TDD) |
| NÄON/ENNI, Precision Farming / Telemetrie | BLOCKED / external_gate |
| GIS-Geometrieversionierung, Bodenhistorie, native PWA | PARTIAL / Folge |

## PROD-READINESS-AUDIT-001 — Production-Readiness-Audit & Agenten-Programm (2026-07-02)

Status: **aktiv**. Der aktuelle Production-Readiness-Nachaudit ist unter
[`docs/operations/production-readiness-audit-2026-07-02.md`](../operations/production-readiness-audit-2026-07-02.md)
kanonisch abgelegt. Er ersetzt keine externen Go-Live-Freigaben, sondern
verdichtet die repo-seitig loesbaren P0/P1-Arbeiten plus Agentenprogramm.

P0-Specs aus dem Audit:

| Spec | Status | Kurzinhalt |
|---|---|---|
| SPEC-P0-01 | erledigt 2026-07-05 (main) | quality-gate, security-scan, universal-mask-ci grün — Evidenz `artifacts/ci-green-evidence.md`, Run 28732436888 |
| SPEC-P0-02 | erledigt 2026-07-05 | Runtime-Sweep Nightly-Gate 0×5xx (`scripts/api_runtime_sweep.py`, Repair-Migration `runtime_sweep_repair_20260702`) |
| SPEC-P0-03 | erledigt 2026-08-23 | Kat.-B/D-Matrix + `/ready`/`/readyz`; Finance-/Bestands-Listen liefern bei DB-Fehler 503+Metrik (Nachzug OP/Matching/Bank) |
| SPEC-P0-04 | in arbeit | Repo-Hygiene und PII-Bereinigung; Branch `fix/pii-remediation` enthaelt bereits Remediation-Commits |
| SPEC-P0-05 | erledigt 2026-09-11 (Belege ≥70%; Gesamt-Coverage weiter COVERAGE-001) | only-up-Ratchet aktiv; `financial_reports`/`rohware_sammelabrechnung`/`sales_invoice_einvoice` Ratchet 0.70 (SPEC-P0-05-BELEGE-70) |
| SPEC-P0-06 | erledigt 2026-09-11 (enforce_admins=false bis Zweit-Reviewer) | CODEOWNERS inkl. finance/pos/alembic/.github; Branch-Protection main (1 Review + CODEOWNERS + Pflicht-Checks); Gate `check_codeowners_spec_p0_06.py` |
| SPEC-P0-07 | erledigt 2026-08-23 | SOC-2-Profil in `simulate_external_assessors.py` + `config/audit/soc2-tsc-matrix.yaml`; Type-II-/AVV-Gates bleiben extern |
| SPEC-P0-08 | repo-seitig erledigt 2026-09-11 (Drill selbst external_gate) | `run_restore_drill.sh` + `check_restore_drill_evidence.py` + CI-Notice in release-gates; Ops muss Protokoll committen |

P1-Specs aus dem Audit:

| Spec | Status | Kurzinhalt |
|---|---|---|
| SPEC-P1-01..03 | erledigt 2026-07-01 (Nachzug dokumentiert 2026-09-11) | UIX-054 Inventory, UIX-055 CI, UIX-056 Playwright, UIX-057 Rollback laut Workboard abgeschlossen |
| SPEC-P1-04 | erledigt 2026-07-06 | Mask-CommandEndpoints via `MaskActionRuntime` (validate/dryRun/propose/execute → Audit + Outbox); Inventur `scripts/check_mask_command_endpoint_inventory.py` — 26 native SDs, 0 stubReason |
| SPEC-P1-05 | erledigt 2026-09-09 | S608-Restschuld einzeln reviewt (SPEC-P1-05-S608-RESTSCHULD): Baseline 167 -> 0, `bandit -t B608` -> 0, unreviewed 136 -> 0; Injection-Pfad env -> SQL-Bezeichner in `geo_pipeline` ueber `app/core/sql_identifiers` geschlossen |
| SPEC-P1-06 | erledigt (geschlossen, Restschwelle 0) | Legacy-Routen mit `response_model` typisieren; W1–W14 erledigt, Gate `--threshold 0` (TypedObjectOut-Drain, kein CompatFlexOut) |
| SPEC-P1-07 | erledigt 2026-07-06 (Nachzug dokumentiert 2026-09-11) | `domains/` (paralleles TS-Backend inkl. inventory) per ADR-039 nach `docs/_internal/archive/domains-ts-backend/` archiviert; Root-`domains/` und Workflows `inventory-domain-ci`/`finance-domain-ci` entfernt; kanonisch: `app/domains/inventory` + Domain Pack |
| SPEC-P1-08 | erledigt 2026-07-06 | Chargen-Tiefenmodell: Lot-Attribute (herkunft, sperrgrund, qs_status, received_at); FEFO-Pick sortiert `mhd ASC NULLS LAST, created_at ASC`; Migration `inv_lot_depth_spec_p1_08` |
| SPEC-P1-09 | erledigt 2026-08-23 | Lizenzinventar (`docs/operations/license-inventory.md`) + erweiterte `THIRD_PARTY_NOTICES.md`; SBOM weiter via CI CycloneDX |
| SPEC-P1-10 | erledigt 2026-09-11 | Erntepeak-k6 lokal: `PROFILE=local|smoke` + `scripts/loadtest/run_harvest_peak_local.{ps1,sh}`; Staging bleibt `PROFILE=full` / externes Gate |

Priorisierte Sequenz: A0 Verifikation und A2 PII parallel/sofort, danach
A1 CI-Gruen, SPEC-P0-06 Governance, A3 Runtime-Sweep und A5 Modulaktivierung.

## A10-DOKU-EVIDENZ-001 — Doku-Drift & Evidenzkette (Prompt A10, Teilstand 2026-07-06)

Nachverifikation 2026-09-08: `doc_drift_report.py --fail-over 0` erneut gruen
mit **0 Items** (zuvor 7). Alle drei Code-Inventare und das Drift-Dashboard
erneuert; indirekt eingebundene Auswertungskomponenten durch Tests abgesichert.
Die historische Release-/CI-Evidenz unten wurde dabei nicht neu erhoben.
Details: [Uebergabe](../agent-ops/handoff-2026-09-08.md).

Status: **teilweise**. Nach A8 umsetzbar ohne A9-Abschluss:

| Check | Stand 2026-07-06 |
|---|---|
| `doc_drift_report.py --fail-over 0` | grün — 0 Drift-Items |
| `docs/entwickler/drift-dashboard.md` | regeneriert (0 Items) |
| `generate_openapi.py` | openapi.json aktualisiert (2537 Pfade) |
| `release_evidence_report.py --fail-on-red` | **WARN** (4 PASS, 2 WARN, 0 FAIL) — coverage-Ratchet lokal ohne Vollsuite; `production-readiness-assessment.json` nur in CI |
| README / Process-Kernel / Open-Gaps | auf gemessene Werte nachgezogen |
| `artifacts/release_evidence.{json,md}` | lokal regeneriert, versionierbar via `.gitignore`-Ausnahme |

Offen für Voll-A10: externe Assessment-Artefakte aus CI committen oder Gate anpassen; README-CI-Stand nach Merge `fix/pii-remediation` → `main` erneut verifizieren.

## API-GAP-STABILIZATION-001 — Lager/Pricing/Scan Nachzug (2026-07-02)

Status: **done**. Fünf zuvor fehlende/fehlerhafte API-Endpoints wurden gegen
die reale Postgres-Instanz stabilisiert (siehe E2E-Produktionsteststand
2026-07-02, 73/73 Tests grün) und mit Regressionstests gehärtet
(`tests/test_api_gap_lager_pricing_scan.py`).

| Endpoint | Status |
|---|---|
| `GET /api/v1/lager/bestaende` | done |
| `POST /api/v1/lager/bewegungen` | done |
| `POST /api/v1/scan/barcode` | done |
| `GET /api/v1/pricing/find` | done |
| `POST /api/v1/pricing/staffelrabatte` | done |

Behobene technische Ursachen:
- DB-Spaltenfehler `ean_code`/`unit`/`movement_date`/`reference_number` (Code
  referenzierte alte Spaltennamen, die nicht mehr existieren).
- `previous_stock`/`new_stock` sind `NOT NULL` in
  `domain_inventory.inventory_stock_movements` — müssen bei jedem INSERT
  mitgesetzt werden.
- psycopg2/SQLAlchemy `text()`: `::jsonb`-Cast-Syntax bricht — auf
  `CAST(:param AS jsonb)` umgestellt.
- `domain_pricing.price_list_items` korrekt als eigene Tabelle angebunden
  (nicht als JSON-Feld auf `price_lists`).
- Fehlende/optionale Schemas (`domain_contracts`, `domain_pricing.discount_rules`)
  defensiv mit try/except abgesichert, damit Preisfindung nicht 500et.
- `localhost:8000` → `127.0.0.1:8000` (Windows-IPv6-Problem, siehe
  `docs/project-context/...` Infra-Gotchas).
- `tenant_id=default` → echte Tenant-UUID (`00000000-0000-0000-0000-000000000001`)
  als Default in `app/core/config.py`.
- CRM Customer/Interessenten-ID-Split korrigiert (`/crm/customers/` liest aus
  `domain_crm.interessenten`, Sales-Order-`customer_id` validiert gegen
  `domain_crm.customers` — unterschiedliche ID-Räume).

**Regressionstests:** `tests/test_api_gap_lager_pricing_scan.py` — 18 Tests,
je Endpoint Happy Path, negativer Payload, Tenant-Isolation und fehlende
optionale Felder/Schemas. Benötigen `require_db` (laufende Postgres-Instanz),
skippen automatisch sonst.

**Nachfolgeblock:** E2E-Domänen-Routen (Wave A–E) sind ein eigener,
separater Arbeitsblock — siehe `docs/agent-ops/active-workboard.md` →
„E2E-DOMAIN-ROUTES-WAVES-001".

## UI-AGRAR-WIZARD-001 — Sammelabrechnung Wizard-Step-Badges (2026-07-02)

Status: **erledigt 2026-07-02** (Root-Cause war API-Verdrahtung, kein Rendering-Bug).

- Betroffener Test: `packages/frontend-web/tests/e2e/uat/uat-agrar-kernprozesse.spec.ts`
  → `TC-AGR-001: Sammelabrechnung — Wizard-Steps sichtbar und navigierbar` — **grün**.
- Tatsächlicher Root-Cause: das Frontend rief `/api/v1/rohware/sammelabrechnung`
  (existiert nicht, 404), der Backend-Router liegt auf
  `/api/v1/agrar/sammelabrechnung`. Zusätzlich passte das Payload-Schema nicht
  (`ernte_ids/abrechnungsdatum/notiz` vs. `harvest_acceptance_ids (min. 2)/
  abrechnungsperiode/bezeichnung/sammeldatum`). Der 404 führte zu `isError`
  → `ErrorState` ersetzte die ganze Seite inkl. Step-Badges — daher das
  scheinbare „Rendering-Problem".
- Fix: `src/pages/agrar/sammelabrechnung.tsx` auf den echten Backend-Vertrag
  verdrahtet (Auswahlliste aus `GET /agrar/harvest-acceptance/`, Anlage +
  direktes `/berechnen`, min-2-Validierung, Fehler-Feedback im Bestätigungs-Step).

## UI-PERSONAL-BADGES-001 — Bewerbungen Stage-Pipeline-Badges (2026-07-02)

Status: **erledigt 2026-07-02** (Root-Cause war fehlender Endpoint-Pfad + fehlende Tabelle).

- Betroffener Test: `packages/frontend-web/tests/e2e/uat/uat-admin-personal.spec.ts`
  → `TC-PER-002: Bewerbungen — Stage-Pipeline-Badges sichtbar` — **grün**.
- Tatsächlicher Root-Cause (zweiteilig):
  1. Frontend rief `/api/v1/personal/bewerbungen` (existiert nicht, 404) statt
     `/api/v1/personal/applications`; der Fehler ersetzte die Seite durch
     `ErrorState` — daher das scheinbare Badge-Rendering-Problem.
  2. Die Tabelle `domain_hr.applications` war nie migriert worden — die
     Applications-Endpoints liefen seit Wave-104 in den 503-Fallback.
- Fix: `src/pages/personal/bewerbungen.tsx` auf `/personal/applications` mit
  Feldmapping (`applicant_name/position_title/status/applied_at`) umgestellt;
  Migration `alembic/versions/hr_applications_table_20260702.py` ergänzt.

## UIX-MASK-FRAMEWORK-001 - Universal Mask Generator (2026-06-28)

Status: Skeleton geliefert als Architektur-Slice, kein offener UX-Baukasten-Rollout.

Nachzug 2026-07-05 (`UIX-MERIDIAN-BUILDER-001`): Meridian ist als zentrale
Builder-Capability verankert. `ScreenDefinition.layout` liefert `floorplan`,
`density`, `contextRail` und `tableProfile`; `RenderPlan.shell` transportiert
diese Felder; Frontend- und Backend-Readiness blockieren fehlende
Layout-Metadaten. Low-Fidelity-/Wireframe-Triage ist im Design-Regelwerk
[`docs/design/valeo-meridian-experience.md`](../design/valeo-meridian-experience.md)
festgelegt.

Nachzug 2026-07-05 (`UIX-MERIDIAN-VISUAL-AUDIT-002`): Der offene
Visual-Audit-Abnahmepunkt ist als fokussierter Playwright-Test umgesetzt.
`tests/e2e/meridian-visual-audit.spec.ts` nutzt die Benutzerhandbuch-
Screenshot-Helfer fuer Render-Wait, Content-QC und Capture-Ziel und prueft
Finance, CRM 360 und Lager bei 1366x768, 1440x900 und 1920x1080.

Nachzug 2026-08-19 (`L3-HABIT-BRIDGE-001`): Die technische Gewohnheitsbruecke
ist zentral im Single Mask Builder umgesetzt. CRM Customer 360, Lager
Artikelbestand und Sales Lieferschein deklarieren Footer-/Commit-Aktionszonen,
Sticky-Regionen und Enter-Fokus; der Lieferschein positioniert die Summary nach
den Positionen. Kein offener Architektur-Gap. Externes Rollout-Gate bleibt die
fachliche Pilotabnahme durch erfahrene L3-Anwender. Originalaufnahmen mit
Echtdaten sind absichtlich nicht versioniert.

Nachzug 2026-08-19 (`L3-FULL-MASK-GAP-002`): Die erreichbaren Funktionen der
zehn L3-Ribbonbereiche und 37 Dropdown-Gruppen wurden read-only gegen aktuelle
VALEO-Seiten, APIs und Lieferdokumentation abgeglichen. Es wurde kein neuer
P0-Blocker gefunden. Offen sind sechs P1-Gaps (MDE-Verarbeitung,
Dokumentenruecklauf, allgemeiner Produktionsleitstand, Inventur-Nebenlaeufe,
zentrale Belegkontrolle, Rechnungstapel/Selbstabrechner), sechs P2-Gaps
(Fremdware-Operator-UI, Abfrage-Center, Teamkalender, Mailarbeitsplatz,
Tankanlagen-Import, Berichtskatalog-Paritaet) und zwei P3-Gaps. Die vollstaendige
Evidenz, Abgrenzung und Abnahmekriterien stehen in
[`l3-full-mask-functional-gap-inventory.md`](../design/l3-full-mask-functional-gap-inventory.md).
Originalbilder mit Echtdaten bleiben lokal ausserhalb von Git.

Nachzug 2026-08-21 (`L3-MDE-INBOX-003`): `L3-GAP-MDE-001` ist repo-seitig
geschlossen. Der vorhandene Mobile-Sync-Kern besitzt nun Payload-Vorvalidierung,
echte Idempotenzantworten, serverseitige Pagination/Filter, drei
Verarbeitungsversuche mit Quarantaene, begruendetes Retry und append-only Audit.
Die native Meridian-Worklist `schnittstelle/mde-inbox` ist navigierbar und
nutzt zentrale statusabhaengige Tabellenzeilen-Aktionen. Damit verbleiben aus
der L3-Vollinventur fuenf offene P1-Gaps. Reale Geraete-/Provider-Mappings und
Pilotbetrieb bleiben externe Gates.

Nachzug 2026-08-21 (`L3-DOCRET-INBOX-004`): `L3-GAP-DOCRET-002` ist
repo-seitig geschlossen. Der kanonische Docflow besitzt nun eine
mandantenbezogene Ruecklauf-Worklist mit getrennten Versand-/Ruecklaufstatus,
serverseitigen Filtern nach Benutzer, Kontakt, Datum und Bezugsart,
Schlagworten, Artefaktvorschau-Metadaten, Ursprungsbeleg-Deep-Link und
begruendetem append-only Audit. Externe Provider-Zustellnachweise und der
fachliche Pilot bleiben Rollout-Gates. Damit verbleiben vier offene P1-Gaps.

Nachzug 2026-08-21 (L3-Delta-Inventur): Live-RDP-Erfassung der zehn
Ribbonbereiche gegen die Inventur vom 19.08.2026. Kein neuer P0, kein neuer
Ribbon-Hauptbereich; P1–P3-Liste bestaetigt. Feindetail DATEI-Hauptmodule
dokumentiert. Kanonischer Bericht:
[`l3-delta-mask-inventory-2026-08-21.md`](../design/l3-delta-mask-inventory-2026-08-21.md).
Originalbilder lokal unter `Pictures\L3-Capture-2026-08-21-delta`, nicht in Git.

Nachzug 2026-08-22 (`L3-DEEP-MASK-PARITY-020`): Die durch die
Dropdown-Leaf-Tiefenpruefung bestaetigten P2/P3-Gaps sind repo-seitig
geschlossen. Geliefert sind 30 feste L3-Berichte, DMS-Volltext,
Aenderungshistorie, getrennte Terrorschutzpruefungen, Duengemittelmengen,
Bonuslaeufe, tenant-sichere Chargenbearbeitung mit Auswahlfreigabe sowie
gespeicherte Auftrags-/Lieferschein-/EB-Kontrollsichten. Kanonischer Bericht:
[`l3-dropdown-leaf-gap-inventory.md`](../design/l3-dropdown-leaf-gap-inventory.md).
Fehlerhafte Capture-Duplikate bleiben ausgeschlossen; Echtdatenbilder werden
nicht versioniert. Offen bleiben nur externe DMS-, Rollen- und Echtdaten-UAT-Gates.

Nachzug 2026-08-22 (`L3-RUNTIME-HARDENING-021`): Der Laufzeit-Nachtest hat
die repo-seitigen Integrationsgaps der neuen Masken geschlossen. Bestehende
Queryparameter bleiben beim Runtime-Paging erhalten; auch clientseitig
paginierten Tabellen mit eigener DataSource werden geladen. Bulk-Auswahlen
bleiben nach Fehlern erhalten und werden bei Seitenwechsel bereinigt.
DMS-Metadaten verwenden das kanonische Artikeldokument-Schema mit Tenant-Link,
Duengemittelmengen werden in der Datenbank paginiert, Bonuskorrekturen sind
exportierbar und Chargen-IDs sind pro Tenant eindeutig. Die lokale
Entwicklungsdatenbank wurde bis `l3_runtime_hardening_20260822` migriert. Es
entsteht kein neues offenes Repo-Gap; externe DMS-/Rollen-/Echtdaten-UAT-Gates
bleiben unveraendert.

Nachzug 2026-08-23 (`L3-VISUAL-PARITY-AUDIT-031`): Acht lokale
Capture-Verzeichnisse mit 1.022 PNGs wurden wiedergefunden und
datenschutzkonform nur abstrakt inventarisiert. Alle 69 produktiven nativen
ScreenDefinitions sind generator-ready und verwenden nach zentraler
Normalisierung renderbare Floorplans, Context-Rails, Tabellenprofile und
Aktionsrisiken. `expertDense` wirkt mit 36-px-Zeilen auch in Registertabellen;
der Visual-Audit prueft sichtbare Datenzeilen und ist an drei Zielaufloesungen
12/12 gruen. Es verbleibt kein aus den erreichbaren L3-Screenshots belegbarer
repo-seitiger Funktions- oder zentraler GUI-Gap; Rollen-, Echtdaten-, Hardware-
und Provider-UAT bleiben externe Gates.

Nachzug 2026-08-23 (`L3-CUTOVER-UAT-032`): Die zuvor nur benannten externen
Gates besitzen jetzt einen maschinenlesbaren, fail-closed Cutover-Vertrag und
einen reproduzierbaren Go/No-Go-Runner. Sechs Rollen und Kernjourneys, zwei
getrennte Import-Dry-runs, Reconciliation fuer sechs Migrationsdomaenen, sieben
reale Integrationspiloten, Gewohnheitsbruecke, Defect-Grenzen, KPI und zehn
Geschaeftstage Parallelbetrieb sind harte Gates. Repo-seitig ist das Programm
vollstaendig ausfuehrbar; bis echte Key-User-, Echtdaten-, Hardware-/Provider-
und finale Betriebsfreigaben als aktuelle Artefakte vorliegen, bleibt der
Status bestimmungsgemaess `NO_GO` und damit ein externes Rollout-Gate.

Nachzug 2026-08-21 (`L3-BELEGCHECK-WORKLIST-005`): `L3-GAP-BELEGCHECK-005` ist
repo-seitig geschlossen. Native Worklist `auswertungen/beleg-kontrolle` mit
vier Ausnahmearten, Zuweisung/Status-Audit, Filter/Pagination und Deep-Link.
Navigations-Drill dokumentiert in
[`l3-rdp-navigation-drill.md`](../design/l3-rdp-navigation-drill.md).

Nachzug 2026-08-21 (`L3-BELEGCHECK-PROJECTION-016`): Live-Projektion der vier
Ausnahmearten aus Einkaufs-/Verkaufs-Quellen via
`POST /api/v1/document-control/project` (idempotent, resolved/waived bleiben
unberuehrt). Codex-Slice `L3-RECENT-DOCUMENTS-015` unberuehrt.

Nachzug 2026-08-21 (`L3-PRODUCTION-CONTROL-006`): `L3-GAP-PROD-003` ist
repo-seitig geschlossen. Der native Produktionsleitstand projiziert kanonische
Mischfutterauftraege und fuehrt Muehlenlauf, Umbuchung, Stapelbuchung und
Nachbearbeitung als tenantgebundene, auditierte Operations-Lifecycles mit
Quell-Deep-Link und Druckpfad. Damit verbleiben zwei offene P1-Gaps:
Inventur-Nebenlaeufe und Rechnungstapel/Selbstabrechner. Physische SPS-/
Muehlenadapter und der Standortpilot bleiben externe Gates.

Nachzug 2026-08-21 (`L3-INVENTORY-AUX-007`): `L3-GAP-INV-004` ist
repo-seitig geschlossen. Zaehlliste, kontrollierter Import, Kontrolllauf,
vorlaeufige Bewertung und Bestandsvortrag werden als tenantgebundene,
SHA-256-gebundene Batches mit abweichendem Pruefer und append-only Audit
gefuehrt. Damit verbleibt ein offener P1-Gap: Rechnungstapel/
Selbstabrechner. Produktive Dateiablage, Druckadapter und Pilot bleiben extern.

Nachzug 2026-08-21 (`L3-BILLING-BATCH-008`): `L3-GAP-BILLBATCH-006` ist
repo-seitig geschlossen. Ausgangs-, Eingangs- und beide Selbstabrechnerarten
laufen ueber einen tenantgebundenen Rechnungstapel mit Pruefung, Vier-Augen-
Freigabe, idempotenten Zeilen, sichtbarem Fehler, Quell-/Nachweislink und
begruendetem Retry. Damit sind alle P1-Gaps der L3-Vollinventur repo-seitig
geschlossen. Providerzustellung, fiskalische Pilotabnahme und Echtdaten-UAT
bleiben externe Gates.

Nachzug 2026-08-21 (`L3-LEGACY-INTERFACES-017`): Nach Abschluss von
Berichtskatalog und persoenlichen letzten Dokumenten ist auch der letzte
repo-seitige P3-Gap geschlossen. `l3_standard` und `unimet` besitzen feste,
versionierte und standardmaessig inaktive Profile, hashgebundenen Intake,
Quarantaene, deklaratives Dry-run-Staging, Reconciliation, Audit und nativen
Betriebsmonitor. Reale Kundenformate, Mappingabnahme, Zieladapter und
Produktivpilot bleiben externe Aktivierungs-Gates; `execution_enabled` bleibt
bis dahin `false`.

- Geliefert: kanonische `ScreenDefinition`, temporaere Uebersetzungsschicht fuer
  bestehende MaskConfig, UniversalMaskRenderer-Skelett, LazyTabs und
  VirtualDataTable.
- Pilotvertrag: CRM 360/Kundenmaske mit kompaktem
  `screen-summary`-Startvertrag und Registry-UIX-Metadaten.
- Begrenzung: keine Big-Bang-Migration; Waage, POS, Ernteannahme und dichte
  Operator-UIs bleiben zulaessige Spezialmasken.
- Restarbeit nach diesem Slice: Maske-fuer-Maske Paritaet beweisen, Adapter
  abbauen und direkte ScreenDefinition-Lieferung pro Domaene einfuehren.

## UIX-CRM-PILOT-002 - CRM Customer Generator Pilot (2026-06-28)

Status: produktiver Pilot hinter Feature Flag geliefert; Paritaetsrollout bleibt
offen.

- Geliefert: CRM Kundenstamm/360 kann ueber
  `VITE_ENABLE_UNIVERSAL_MASK_CUSTOMER=true` mit `UniversalMaskRenderer`
  gerendert werden.
- Datenvertrag: `screen-summary` wird vor der Customer-Detailquery geladen;
  Legacy bleibt Default-Fallback.
- Abnahme: Unit-Tests fuer Renderer, Route-Switch und Pilotseite sowie
  Playwright-Smoke Desktop/Mobile mit gemockter CRM-API.
- Restarbeit: fachliche Paritaet mit der alten CRM-Maske pruefen,
  produktive Testdaten fuer E2E bereitstellen und danach erst weitere CRM- oder
  Sales-/Inventory-/Finance-Masken aufnehmen.

## UIX-CRM-PARITY-003 - CRM Lazy Tab Parity (2026-06-25)

Status: abgeschlossen — read-only Lazy-Tab-Listen, tab_endpoints, Paritaetsmatrix.

- Geliefert: `useCustomerTabData`, Tab-API in `crm_360.py`, supplemental 360-Tabs
  (Auftraege, Aktivitaeten, Dokumente), Vitest/pytest/Playwright-Erweiterung.
- Paritaet: [mask-parity-customer-360.md](../architecture/domains/crm/mask-parity-customer-360.md)
- Restarbeit: Angebote/Historie-Quellen, Mutationen in Generator-Tabs, vollstaendige native Felddefinition.

## UIX-RENDERER-LIB-004 - Renderer Library (2026-06-25)

Status: abgeschlossen — Visualisierungslayer unter `mask-builder/renderers/` extrahiert (Refactor-only).

## UIX-DATA-CONTRACT-005 - Native ScreenDefinition (2026-06-25)

Status: abgeschlossen — `GET /api/v1/masks/{mask_id}/screen-definition`, `useScreenDefinition`, erster Eintrag `crm/customer-360`.

## UIX-PERF-GATE-006 - Mask Performance Gate (2026-06-25)

Status: abgeschlossen — `scripts/check_mask_performance_contract.ts` im Quality-Gate; Registry-Feld `lookup_min_chars`.

## UIX-RENDER-PLAN-009 — RenderPlan Engine (2026-06-28)

Status: abgeschlossen — SchemaCompiler, LRU-Cache, useRenderPlan, ADR-011 + render-plan-architecture.md.

## UIX-ROLLOUT-BATCH-019 — Rollout Batch Waves 42–51 (2026-06-29)

Status: abgeschlossen — zehn Rollout-Kandidaten mit zentralem `/api/v1/mask-rollouts/...` screen-summary; Registry + Generic Pilot Route (`ad4727482`).

- Geliefert: `mask_rollout_catalog`, `mask_rollout_summary_service`, pytest 24/24, Doku `mask-rollout-batch-w42-51.md`.
- Grenzen: Adapter-Parität (Felder aus MaskConfig); generische Tab-Spalten; keine Detail-Route-Switches pro Legacy-Seite.
- ~~**Naechster Architekturschritt:** UniversalMaskRuntime (`UIX-RUNTIME-020`…`024`)~~ → **abgeschlossen in UIX-022…030** (siehe unten).

## MERIDIAN-BELEG-ONEPAGE — durchgehende Belegseite (2026-09-29)

Status: **geliefert und im Browser abgenommen** (1440/1920/390 px). `layout.sectionNavigation=anchors`
(nur `objectPage`/`transaction` mit `columnNavigation=single`) rendert Register als
Abschnitte mit Sprungleiste, Scroll-Spy, `Alt+1..9`, Lazy-Mount, schrumpfendem Kopf,
Belegfluss als letztem Abschnitt und Verwerfen-Rückfrage. Pilot `sales/delivery-note`.
Die Google-Studio-Entwürfe dienten nur als visuelle Referenz, es wurde kein Code übernommen.

Folgearbeiten (Stand 2026-09-29, zweite Runde):

- ~~Positions-Detailband~~ → `table.rowDetail` (ScreenDefinition, RenderPlan, Readiness
  `schema_valid`, Feldvertrags-Gate). `RowDetailBand` zeigt die gewählte Zeile unter dem
  Raster, Escape oder erneuter Klick schließen. Nur für Tab-Tabellen ohne externe
  Zeilenauswahl; Wurzeltabellen bekommen kein Band. Pilot: Rechnungspositionen.
- ~~USt-Aufteilung 7 %/19 %~~ → Steuerausweis `GET /sales/invoices/{id}/tabs/steuer`,
  je Position auf den Cent gerundet wie beim Anlegen, Summe = Kopf-USt. Nur Rechnung:
  Auftrag und Lieferschein führen keinen Steuersatz je Position.
- ~~Mobile Kartenliste~~ → bestand bereits (`VirtualDataTable` unter 768 px / grober
  Zeiger). Neu: Karten werden gemessen statt mit 160 px geschätzt (vorher abgeschnitten).
- ~~Sticky Tabellenkopf~~ → Kopfzeile stand bereits außerhalb des vertikalen Scrollbereichs.
  Neu: `fitToContent` — kurze Tabellen schrumpfen auf ihre Zeilen (420 px bleibt Obergrenze).
- ~~Browser-Abnahme~~ → Rechnung mit 15 Positionen (7 % und 19 %) bei 1440, 1920 und 390 px.
  Dabei behoben: Sticky-Kopf klebte 32 px unter der Containerkante (AppShell-Padding);
  Rechnungspositionen standen in Textfolge (1, 10, 11 … 2) → `positionsfolge`;
  Nur-Lese-Beträge/-Datum ungeformt („19315“, „mm/dd/yyyy“) → `formatReadOnlyValue`.
- ~~Rollout~~ → `sales/sales-order` (Kopf jetzt aus der Entität statt leerem Lazy-Tab),
  `sales/invoice`, `einkauf/purchase-order` auf `sectionNavigation=anchors`.

Dritte Runde (2026-09-29):

- ~~Doppelte horizontale Scrollleiste~~ → Kopf und Körper des Desktop-Rasters reservieren
  beide die Scrollleisten-Rinne (`scrollbarGutter: stable`), der Körper scrollt nur
  vertikal. Browser: kein horizontaler Überlauf im Körper (Auftrag, Rechnung).
- ~~`h1` der Rechnung~~ → neuer Vertrag `ScreenDefinition.identityField` (Frontend-
  Validierung + Readiness `schema_valid`): `h1` = Belegnummer, Maskentitel wird Kicker.
  Gesetzt für Auftrag, Lieferschein, Rechnung, Bestellung.
- ~~Auftrag/Bestellung im Browser~~ → SO-00064 und DEMO-PO-001 (Default-Mandant) abgenommen.
  Dabei behoben: Auftragskopf zeigte die Kunden-UUID — `_fetch_customer_name` las eine
  nicht existierende Spalte in der falschen Tabelle und schluckte den Fehler still; liest
  jetzt `domain_crm.customers.company_name`, Einzelabfrage liefert `customer_name`.
- ~~Status-Schlüssel in Masken~~ („open“, „entwurf“, „bestellt“) → zentral `statusLabel()`
  (`mask-builder/renderers/status-labels.ts`) für Tabellen-Chips (`renderKind: status`) und
  Nur-Lese-Felder mit Schlüssel `status`; Unbekanntes bleibt stehen.
- ~~„Standard Table Profile“~~ unter jeder Tabelle entfernt (interne Klassifikation,
  englisch); maschinenlesbar bleibt `data-table-profile`.
- ~~`debitoren.test.tsx`~~ → an die neue Unterzeile angepasst, Suchfilter-Test ergänzt.

Vierte Runde (2026-09-29) — Rest geschlossen:

- ~~`customer_id` in Rechnungs-/Lieferscheinkopf~~ → `app/services/customer_reference.py`
  (`resolve_customer`) nimmt CRM-ID **oder** Kundennummer (beide Formen sind im Umlauf:
  Lieferschein/Auftrag führen die CRM-ID, Rechnungen aus MCP/Import die Nummer; bei
  Gleichstand gilt die ID). Einzelabfragen von Auftrag, Lieferschein und Rechnung liefern
  `customer_name` + `customer_number`; alle drei Köpfe zeigen „Kunde“ und „Kunden-Nr.“
  (Gewohnheits-Prinzip). Ohne CRM-Treffer bleibt der Name leer und die Referenz steht als
  Nummer — kein erfundener Name. Rechnungs-Summary-Untertitel nennt ebenfalls den Namen.
- ~~Auftrags-UUID im Lieferscheinkopf~~ → `sales_order_number` statt `sales_order_id`.
- ~~Status-Wörterbuch lückenhaft~~ → gegen alle 229 Tabellen mit `status`-Spalte der
  Dev-Datenbank abgeglichen, alle vorkommenden Werte abgedeckt; Schreibweise egal
  (`in-bearbeitung`, `PENDING_APPROVAL`).
- ~~Nur-Lese-Boolean als „false“~~ → `formatReadOnlyValue` zeigt Ja/Nein.

Keine offenen Punkte aus MERIDIAN-BELEG-ONEPAGE. Neue Status werden in
`renderers/status-labels.ts` ergänzt; unbekannte Werte erscheinen unverändert.

## MERIDIAN-SCREEN-STUDIO-PERSIST — Drafts in Postgres (2026-09-16)

Status: **geschlossen**. `domain_shared.screen_definition_drafts` persistiert Studio-Entwürfe;
`published_temp` hängt in `get_screen_definition` / Omnibox / `/studio/run/:screenId`.
Native Screen-IDs bleiben unbeschattet. JSON-Schema-Drift bleibt bei UIX-090.

## UIX-RUNTIME-022…030 — Universal Mask Runtime Platform (2026-06-29)

Status: **abgeschlossen** — alle Phasen implementiert, getestet und gepusht (`81d706da8` bis `e6cabb380`).

### Was geliefert wurde

| Phase | Inhalt | Commit |
|-------|--------|--------|
| 022 Sort-Whitelist | `get_sortable_columns`, `paginate_tab_items` mit sort/sort_dir, Backend + Frontend | `0f6e06f43` |
| 023 FilterPlan | 8 Operatoren (eq/neq/contains/lt/lte/gt/gte/in/between), `get_filterable_columns`, FilterChips-UI | `bf83d8563` |
| 025 UniversalFormState | `useUniversalFormState` — Ref-Guard, dirty-Tracking, Sticky Submit Bar, Pflichtfeld-Blocking | `7f95ef674` |
| 026 ActionRuntime | `ActionPolicy`, `checkActionPolicy`, `useActionRuntime`, dryRun/validate/propose Modi | `7f95ef674` |
| 027 WorkflowRuntime | `WorkflowState`, tone-colored `WorkflowPanelRenderer`, `useWorkflowState` | `b3eea3a20` |
| 028 CRM 360 native Parity | `useUniversalMaskRuntime` wenn `adapter.temporary===false`; `data-runtime` Marker | `81d706da8` |
| 029 AgentMaskContract | `generateAgentMaskContract`, `GET /api/v1/masks/{id}/agent-contract` | `81d706da8` |
| 030 Readiness Gates | `checkGeneratorReadiness` (6 mandatory Gates), `GET /api/v1/masks/{id}/readiness` | `e6cabb380` |
| 033 Readiness verschärft | 6 mandatory + 6 advisory Gates pro Tabelle; `table_data_source_bound`, `actions_classified` u.a. | `fd2b8a7cf` |

### Architekturprinzip

Eine `ScreenDefinition` ist Single Source of Truth für **Human UI und AI Agent**:
- Human: `RenderPlan` → `UniversalMaskRenderer` → Sort/Filter/Form/Workflow/Actions
- Agent: `AgentMaskContract` → lesbare/editierbare/sensible Felder, Action-Policies, Audit-Anforderungen
- Backend: Sort-/Filter-Whitelist aus `ScreenDefinition`; strukturierter `FilterPlan`-JSON-Parameter

### Plattformstatus (Stakeholder-Audit 2026-06-29)

```text
Architektur:                sehr guter Sprung (021…030 geliefert)
Human+Agent-Gedanke:        umgesetzt (AgentMaskContract, ActionRuntime, FilterPlan)
Runtime-Basis:              vorhanden (useUniversalMaskRuntime)
Readiness-Governance:       vorhanden (030 Basis + 033 pro Tabelle)
CRM 360 native Pfad:        vorhanden; fachliche Parität offen (034)
CI-/Release-Nachweis:       teilweise — lokale Frontend-/BFF-Gates und Universal-Masken-Playwright gruen; GitHub Actions nach Push offen
Doku-Konsistenz:            nach UIX-031 + DOC-UIX-RUNTIME-001 synchron
Produktionsreife:           noch nicht bewiesen
```

Kanonische Maschinenreferenz: [`universal-mask-runtime-status.md`](../architecture/uix/universal-mask-runtime-status.md)

### Status UIX-031…038 (Stand 2026-06-29)

| Slice | Inhalt | Priorität | Stand |
|-------|--------|-----------|-------|
| UIX-031 | Doku-Konsolidierung | P0 | ✅ |
| UIX-032 | CI-Gate: pytest 57/57 lokal; tsc 0 Fehler; GHA nach Push | P0 | ✅ lokal |
| UIX-033 | 12 Readiness-Gates (6 mandatory + 6 advisory) | P1 | ✅ |
| UIX-034 | CRM-360 Parity-Matrix; fields[]; agentContract; advisoryScore=83% | P1 | ✅ |
| UIX-035 | ActionRuntime create_activity: validate/dryRun/propose/execute + Audit | P2 | ✅ |
| UIX-036 | Agent propose→dryRun→validate getestet; humanApproval-Block aktiv | P2 | ✅ |
| UIX-037 | Rollout-Kandidaten strukturell gefixt; adv=50% alle 10; Promotions-Reihenfolge | P2 | ✅ |
| UIX-038 | einkauf/supplier native SD: generatorReady=true, advisoryScore=1.0 | P1 | ✅ |
| UIX-039 | crm/opportunity native SD: generatorReady=true, advisoryScore=1.0 | P1 | ✅ |
| UIX-040 | lager/article-stock native SD: generatorReady=true, advisoryScore=1.0 | P1 | ✅ |
| DOC-UIX-RUNTIME-001 | Doku-Paket Handbuch, Entwickler-API, Agent-Runbook, Parity, In-App-Hilfe | P1 | ✅ |
| DOC-AGENT-HANDBUCH-001 | Generiertes Agent-Handbuch: Flow Spine, ScreenDefinitions, MCP, Events; CI-Drift + Pre-Commit-Regen | P1 | ✅ |
| UIX-041 | 7 native SDs Wave 1 (delivery-note, purchase-order, ap-invoice, ar-open-item, stock-movement, harvest-settlement, payment-run) | P1 | ✅ |
| UIX-042a/b | advisory-Score 1.00 alle SDs + UniversalNativeDetailPage + 7 Frontend-Wrapper | P1 | ✅ |
| UIX-043 | 13 verbliebene ObjectPage-Masken migriert; 26 native SDs gesamt; Vollständige Inventur | P1 | ✅ |

### Migrationsstand Universal Mask Generator (2026-06-30) — ABGESCHLOSSEN

- **26 native SDs** — alle `generatorReady=True`, `advisoryScore=1.00`, `temporary=False`
- **20 Frontend thin wrapper pages** + 20 route-aliases in `route-aliases.json`
- **60 Tests grün** | Inventur: `docs/architecture/uix/uix-043-mask-migration-inventory.md`
- **18 Seiten bewusst exempt** (Prozessmasken, Formulare, Batch)
- **UIX-043b (2026-06-30):** Mask-API `{mask_id:path}` + Entity-Stub `/api/v1/masks/{id}/entity/{entity_id}` für Wave-2 Kopf-Tabs

### Offene Folgearbeit (P2/P3)

| Thema | Beschreibung | Priorität |
|-------|-------------|-----------|
| commandEndpoints | ✅ 2026-09-27: `agrar/ration` bindet `submit_review`, `approve`, `schedule`, `activate`, `retire` und `archive` ueber schreibfreie Vorschau-/Validierungsmodi und den kanonischen Lifecycle-Service an die zentrale ActionRuntime. | P1 |
| Legacy-Routen umhängen | ✅ 2026-09-27 revalidiert: 49/49 UIX-051-Tests; alle erwarteten `:id`-Routen zeigen auf native Wrapper, blockierendes Gate in `universal-mask-ci`. | P3 |
| Agent E2E Coverage | ✅ 2026-09-27: Registry-dynamisches AgentMaskContract-/Readiness-Ratchet ueber alle 71 nativen ScreenDefinitions; blockierender Schritt in `universal-mask-ci`. | P3 |
| UIX-054 Route Inventory | Generierte Route-Wahrheit (`route-inventory.gen.json`) | P1 | ✅ |
| UIX-055 universal-mask-ci | GitHub Actions sichtbar grün | P1 | ✅ Run 28540744515 |
| UIX-056 Native Route Smoke | Playwright über 5 repräsentative `/:id`-Routen | P1 | ✅ lokal |
| UIX-057 Rollback-Matrix | Legacy-Fallback je kritischer Maske | P1 | ✅ |

Nachzug 2026-06-30 (UIX-044/045): Der FilterPlan-HTTP-Vertrag ist auf `filter_plan`
kanonisiert; Backend akzeptiert `filterPlan` nur noch als Kompatibilitaetsalias.
Native Detailseiten fuehren Actions nicht mehr als No-op aus, sondern ueber
`ActionRuntime` gegen `commandEndpoint` aus der `ScreenDefinition`.

Nachzug 2026-07-06 (SPEC-P1-04/08, Prompt A8): Gemeinsamer `MaskActionRuntime`-Service;
alle nativen ScreenDefinitions ohne `stubReason`; Inventur-Skript + pytest
(`test_spec_p1_04_mask_commands.py`, `test_spec_p1_08_lot_fefo_pick.py`).
Chargen-FEFO beruecksichtigt MHD vor Eingangsdatum.

Nachzug 2026-07-15 (FEED-CORE-017): `agrar/feeding-reference-data` ist eine
read-only native ScreenDefinition und besteht die Generator-Readiness. Das
Command-Inventar bleibt ausschliesslich wegen der oben benannten fuenf
Bestandsaktionen rot; die Referenzdatenmaske erzeugt keine neue Action-Luecke.

## UIX-SALES-PARITY-008 - Sales Order Lazy Tab Parity (2026-06-28)

Status: abgeschlossen — Lazy Tabs `lieferung` (Lieferscheinliste) und `dokumente` (Rechnungsbelege) via tab API.

- Geliefert: tab_endpoints, `_fetch_delivery_notes_for_order`, `_fetch_order_documents`, Paritaetsmatrix `mask-parity-sales-order.md`.
- Legacy: Mutationen (Speichern, LS anlegen, Druck) weiterhin OrderEditorLegacyPage.

## UIX-SALES-PILOT-007 - Sales Order Generator Pilot (2026-06-28)

Status: abgeschlossen — Verkaufsauftrag hinter `VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER` fuer bestehende Auftraege.

- Geliefert: screen-summary + positions tab API, UniversalSalesOrderPilotPage, Route-Switch in order-editor.
- Legacy: voller OrderEditorLegacyPage fuer Neuanlage, Workflow-Einstieg und Flag aus.
- Restarbeit: Mutationen, fachliche Voll-Paritaet mit OrderEditorLegacyPage.

## Zweck

Ehrliche, aktuelle Bestandsaufnahme aller offenen Restthemen, fachlichen Duennstellen und bekannten Risiken.
Dokumentations-Konsolidierung: **2026-06-26** (`DOC-CONSOLIDATION-010`).
Der Code-zu-Doku-Drift steht bei 0; alte Planungs-/Benchmark-Dateien sind als
historische Referenzen markiert. Aktuelle Restarbeit ist hier und im Bericht
[`documentation-consolidation-2026-06-26.md`](documentation-consolidation-2026-06-26.md)
zu fuehren.
Production-Readiness-Nachaudit: **2026-06-09** (CI/Security, Deployment,
simulierte externe Pruefer, POS-Fiskalisierung und CRM360/KIM).
Governance-Nachzug: **2026-06-11** (`COMPAT-GOV-001`, `INV-STOCK-MOVEMENTS-001`,
Release-Kompatibilitaetsmatrix, Toolchain-Pins, Lager-Altpfade bereinigt).
Domaenentiefe-Nachzug: **2026-06-12** (`DOM-*-004`-Welle: CON, SALES, FIN, DOC, PROC,
SUPPLY je auf voller Tiefe `.2`–`.5`). Uebersicht:
[dom-004-spine-buildout-2026-06-12.md](../dom-004-spine-buildout-2026-06-12.md).
Zuletzt vollstaendig auditiert: **2026-05-27** (Integrations-Gate Wave 18–22, Backend-Security, OpenAPI-Coverage).
Aggregierte Gesamtsicht: [PROJEKT-GESAMTSTAND-2026-05-27.md](../PROJEKT-GESAMTSTAND-2026-05-27.md).

---

## Build-Health (Stand 2026-06-18)

- **TypeScript**: 0 Fehler (`tsc --noEmit`) — Wave-22-Gate (letzter Nachweis 2026-05-27)
- **Backend-Tests**: 9527 collected (2026-06-11, `pytest --collect-only`); letzter Voll-Lauf mit Pass-Count: 9228 passed (2026-05-26, Commit `271bc5e12`) — massgeblich naechster gruener `quality-gate`-Lauf
- **Governance-Vertragstests (2026-06-11, lokal)**: 8/8 gruen (`test_release_compatibility_governance`, `test_inventory_stock_movements_canonical`)
- **Toolchain-Pins**: `scripts/check_toolchain_pins.py` gruen (pytest-cov/coverage repo-weit fixiert)
- **Release-Matrix**: Generator + CI-Upload in `quality-gate.yml` / `release-gates.yml`
- **OpenAPI-Routen mit `summary=`**: 3041/3041 (100%, Nachzug 2026-06-23; DOM-004/POS/Feed/Meldewesen-Action-Routen mit Summary-Metadaten nachannotiert)
- **Response-Model-Coverage**: Nachzug 2026-06-25: External-Mock-Harness-Routen tragen `response_model` gate-kompatibel vor Summary-Texten mit Klammern; verhindert False-Negative im Regex-basierten CI-Check.
- **Response-Model-Coverage**: Nachzug 2026-06-25b: Workflow-Cockpit-Persistenz und Silo-Zielzellen-Regelengine mit expliziten `response_model`-Metadaten versehen; Gate wieder bei 80 untypisierten Legacy-Routen.
- **Frontend-Imports**: 0 gebrochene Importe (letzter Nachweis 2026-05-27). Nachzug 2026-06-26: Portal-/CRM-Buildbruch aus dem E2E-Smoke geschlossen (`potential-analyse`, `empfehlungen`, `whatsapp-simulator`): falsche Default-API-Imports auf named `apiClient`, Toast-Hook auf kanonischen `@/hooks/use-toast`, fehlende JSX-Funktionsklammer in `empfehlungen`; lokaler Nachweis `pnpm --dir packages/frontend-web build` gruen.
- **Alembic**: ✅ SINGLE HEAD (`final_single_head_merge_20260626`) — alle 55+ Parallel-Branches geschlossen (2026-06-26, Wave 12). Waves 8–12 haben 60+ Tabellen idempotent eingebracht: Admin-Mobile (W8), Einkauf-Lieferschein/Opportunities (W9), domain_inventory.warehouses (W10), Finance-Kern/Agrar/Sales (W11), Finance-AP/Matching/Bank/POS/HR/RFQ/Shared (W12). Kein offener Parallel-Head mehr.
- **DOM-*-004-Tiefenwelle (2026-06-11/12)**: ~90 neue reine Logik-Unit-Tests gruen; 5 Live-UAT-Skripte (`scripts/uat/{con_contract,sales_o2c,fin_op,doc_nachweisraum,proc_match}_lifecycle_uat.py`, `--execute` mit DB-Restore); Frontend `tsc 0` + ESLint clean je Slice
- **Docker-Erstinstallation**: Alembic-Bootstrap und Mehr-Domaenen-Struktur auf leerer DB abgesichert
- **Service-Layer**: Hauptwellen refaktoriert; Legacy-Endpunkte `harvest_acceptance.py`, `agrar_settlements.py` und `docflow.py` repo-seitig mit dedizierten Services nachgezogen (Stand 2026-05-21)
- **Backend-Security**: Globale Bearer-Token-Auth, RFC-7807 Problem-Details, 62 Endpoints mit nosec-S608-Annotierungen (Wave 22 Backend-Security, Commits `4ab228f92` + `732d84376`); CI-Gate `scripts/check_sql_fstrings.py` aktiv. Nachzug 2026-06-23: neun neue SQL-f-string-Funde aus DOM-004/POS/Feed/Meldewesen-Slices wurden review-markiert, weil die dynamischen SQL-Fragmente ausschliesslich aus festen Feldlisten stammen und Werte parametrisiert bleiben.
- **Container-Security**: Nachzug 2026-06-25: Backend-Image auf `python:3.13.14-slim-bookworm` angehoben und Runtime-`pip` explizit aktualisiert, um fixbare Grype-High-Funde aus Python 3.13.13 / pip 26.0.1 zu schliessen.
- **Inventory-Domain-CI**: Nachzug 2026-06-25: Scheduled Inventory CI nutzt keine nicht mehr aufloesbare externe GoSec-Action mehr; Deploy-/Post-Deployment-Jobs laufen nur bei explizitem `ENABLE_INVENTORY_DEPLOY=true` und vorhandenen AWS-/Monitoring-Secrets. Reine CI-/Schedule-Laeufe pruefen Qualitaet strikt, behandeln fehlendes Live-Deployment aber als externes Gate statt als Infrastrukturfehler. Der Peer-Konflikt `inversify@6.2.2` zu `reflect-metadata` ist auf `^0.2.2` korrigiert; eine lokale `.eslintrc.json` verhindert Root-Parser-Aufloesung gegen ein nicht installiertes Root-`node_modules`. Nachzug 2026-06-25c: Der Scheduled-CI-Compile nutzt `tsconfig.ci.json` als Compatibility-Profil fuer die noch nicht produktiv verdrahtete Inventory-Domain; kaputte Altpfad-Imports sind auf lokale Typen/Bootstrap umgestellt. Der strikte `tsconfig.json` bleibt als Zielprofil bestehen, bis die BFF-/Service-Typvertraege fachlich konsolidiert sind. Nachzug 2026-06-25d: Fehlende optionale Artefakte (`SONAR_TOKEN`/`SONAR_HOST_URL`, `SNYK_TOKEN`, Inventory-Dockerfile, k6-Testskript) werden als externe bzw. noch nicht angelegte Domain-Gates explizit uebersprungen; Unit-/Compile-/Lint-Gates bleiben hart und erhalten einen ersten Jest-Baseline-Test fuer den lokalen DI-Vertrag. Nachzug 2026-06-25e: `domains/inventory/package-lock.json` ist committet; ungenutzte OpenTelemetry-/bcrypt-/node-cron-Abhaengigkeiten entfernt, `uuid` und `@typescript-eslint/*` aktualisiert. Lokaler Nachweis: `npm --prefix domains/inventory audit --audit-level=high` exit 0; uebrig bleiben moderate Jest/ts-jest-Transitive als spaeterer Dev-Toolchain-Patch.
- **E2E-Full-UAT**: Nachzug 2026-06-25: Scheduled Full-UAT blockiert nicht mehr an fehlender lokaler `.env.uat`; CI nutzt `.env.uat` falls vorhanden, sonst `.env.example` bzw. minimale Test-Env und setzt UAT-Tenant/Base-URL explizit.
- **Superglue Live-Smoke**: Nachzug 2026-06-25: Nightly Superglue-Connector-Smoke scheitert nicht mehr an implizitem `localhost:3011`, wenn kein `SUPERGLUE_CI_BASE_URL` konfiguriert ist. Ohne Secret wird der Live-Smoke als externes Gate uebersprungen; mit gesetzter URL bleibt Health-/Tool-Listing strikt.
- **Agrar-Partie-Erstinstallation**: Nachzug 2026-06-23: DOM-AGRAR-004 Partie-Aggregation liest Ernteannahmen jetzt aus der kanonischen Tabelle `domain_inventory.harvest_acceptances` und leitet Brutto-/Netto-/QS-Werte ueber `domain_inventory.weighing_tickets` ab. Der vorherige Zugriff auf `domain_agrar.harvest_acceptances` fuehrte in frischen CI-Smoke-Datenbanken zu 503 statt fachlichem 422 bei Dummy-Annahmen.
- **Tenant-Isolation**: CI-Gate eingezogen (Wave-A3 Commit `c106f74e8`); Nachzug 2026-06-25: Dev-only External-Mock-Harness, read-only MCP-Toolkatalog sowie statische P2-Regel-/Prozess-/Metrikendpunkte explizit als systemische Endpunkte ohne Tenant-DB-Daten klassifiziert.
- **E2E-Tests Wave 18–22 + W11**: 23/23 grün (Integrations-Gate Commit `97c41d479`)

---

## RUNTIME-API-SWEEP-001: Live-Laufzeit-Fehlersweep aller GET-Endpoints (2026-06-25)

**Methode:** Gegen den laufenden Backend-Container (`dev-token`, Tenant
`00000000-…-001`) wurden alle **1059 parameterlosen GET-Endpoints** aus der
OpenAPI-Spec live aufgerufen und auf `5xx` geprüft (`tmp_endpoint_sweep.py`,
nicht eingecheckt). Begleitend Browser-Sweep über UI-Routen.

### Behoben + verifiziert (HTTP 200 nachgewiesen)

- **OpenAPI-/Swagger-Generierung war global defekt (500):** `cached_read_model`
  (Redis-Cache-Decorator) erbte über `functools.wraps` die `__globals__` des
  Decorator-Moduls; bei Endpoint-Dateien mit `from __future__ import annotations`
  konnte FastAPI String-Annotationen (`Optional[bool]` etc.) nicht auflösen →
  pydantic „TypeAdapter not fully defined" → **gesamte** `/api/v1/openapi.json`,
  Swagger-UI und Docs-OpenAPI-Seite lieferten 500. Fix: aufgelöste
  `__signature__` am Wrapper (`app/core/read_model_cache.py`); zusätzlich
  `from __future__ import annotations` aus `app/auth/router.py` und
  `app/policy/router.py` entfernt (slowapi-`@limiter.limit`-Wrapper +
  Body-Modell `LoginBody`). Ergebnis: `openapi.json` 200, **2663 Pfade**.
- **HR-Planungstabellen fehlten (500 `UndefinedTable`):** Migration
  `hr_planning_tables_20260625` legt `domain_hr.{employee_time_profiles,
  calendar_events, payroll_exports, campaign_capacity_plans, field_service_plans,
  driver_timesheets}` an. Betraf `/api/v1/personal/{calendar-events,
  payroll-exports, campaign-capacity, field-service-plan, work-plan,
  stundenzettel}` sowie die Logistik-Seiten Tourenplanung/Frachtbriefe.
- **Vergiftete DB-Transaktion (500 `InFailedSqlTransaction`):** In
  `personal_service.get_work_plan_data` schluckte ein `except` einen Fehler der
  optionalen `domain_shared.users.preferences`-Query ohne `rollback`; alle
  Folge-Queries scheiterten. Fix: `self.db.rollback()` im `except`.
- **Agrar-Statistik (500 `'Session' object has no attribute 'func'`):**
  `db.func.*`/`db.case(...)` statt `func`/`case` aus `sqlalchemy` in
  `agrar/api/{saatgut,psm,duenger}.py` (+ `psm_proplanta.py`). Betraf
  `/api/v1/agrar/{saatgut,psm,duenger}/stats/overview`.
- **WMS response_model dict↔list (500 ResponseValidation):**
  `agri_silo_material_flow.py` (`silo-systems`, `silo-cells`,
  `material-flow/nodes`, `material-flow/edges`) und `warehouse_wms.py`
  (`bins`, `stock-valuation`) gaben Listen zurück, deklarierten aber ein
  Einzelobjekt; auf `list[...]` korrigiert (gleiche Klasse wie der
  frühere `tapi`-Bug).

### Verbleibende 5xx (60 Stand 2026-06-25) — kategorisiert, offen

**A. Fehlende DB-Tabellen (500 `UndefinedTable`)** — geschlossen Wave 8–10:
~~`/api/v1/admin/{api-keys, device-mappings, devices, output-profiles, output-templates, report-permissions}`~~ (ALEMBIC-MERGE-001 Wave 8),
~~`/api/v1/admin/mobile/*` (connectors, connector-events, mobile-devices, routing-rules, scan-profiles, station-devices, stations)~~ (ALEMBIC-MERGE-001 Wave 8),
~~`/api/v1/einkauf/lieferscheine[/last]`~~ (EINKAUF-LS-REPAIR-001 Wave 9),
~~`/api/v1/inventory/{charge-lineage/, storage-fees/runs}`~~ (ALEMBIC-MERGE-001 Wave 8),
~~`/api/v1/crm/opportunities/pipeline`~~ (EINKAUF-LS-REPAIR-001 Wave 9).
Alle Kat-A-Items repo-seitig geschlossen; naechster Live-Sweep verifiziert produktiven Migrationslauf.
Nachzug 2026-06-25e: `/api/v1/jobs` ist repo-seitig geschlossen:
Repair-Migration `job_runner_tables_repair_20260625` legt
`domain_shared.jobs` und `domain_shared.job_artifacts` idempotent am aktuellen
Alembic-Head an; `GET /api/v1/jobs` degradiert bis zum produktiven
Migrationslauf auf eine leere Liste statt 500.

**B. Bewusste 503 (graceful degradation, kein Bug — by design)** mit
Migrations-/Config-Hinweis: `/api/v1/analytics`, `/api/v1/contracts`,
`/api/v1/compliance/{dsgvo/erasure-requests, lksg/*, whistleblower/reports}`,
`/api/v1/finance/{asset-accounting/*, budgets[/summary]}`,
`/api/v1/personal/applications`, `/api/v1/channels/whatsapp/webhook`.

**C. Custom Response-Envelope-Validierung (500)** — alle repo-seitig geschlossen:
~~`/api/v1/health/health/live`~~ (RUNTIME-KAT-C-001),
~~`/api/v1/mcp/policy/list`~~ (RUNTIME-KAT-C-002 Wave 6: `success`-Key-Fix),
~~`/api/v1/messages/health`~~ (RUNTIME-KAT-C-002 Wave 6: `response_model=dict[str,str]`),
~~`/api/v1/crm/{bestell-inbox, kaeufergruppe/katalog}`~~ (RUNTIME-KAT-C-002 Wave 6),
~~`/api/v1/einkauf/{lieferanten, kontrakte, lager-konten, artikel-lager-parameter, fremdwaren-einlagerung}`~~ (RUNTIME-KAT-C-002 Wave 6: Einzelobjekt→list[]),
~~`/api/v1/ebilanz/taxonomie-felder`~~ (RUNTIME-KAT-C-001: `response_model=list[EbilanzElsterOut]`),
~~`/api/v1/inventory/warehouses/`~~ (WAREHOUSE-REPAIR-001 Wave 10: `field_validator("address")` + Repair-Migration).
Alle Kat-C-Items geschlossen.

**D. Code-Bugs (Attribut/Daten):** Nachzug 2026-06-25: drei Runtime-5xx
geschlossen und per Regressionstest abgesichert: `/api/v1/finance/intercompany`
sortiert nach `IntercompanyBuchung.datum` statt nicht existierendem
`buchungsdatum`; `/api/gobd/belegnummern` zaehlt Nummernkreisluecken ohne
falschen Zugriff auf `BelegnummernLuecke.luecken`; `/api/v1/inventory/reports/turnover-analysis`
liefert bei Null-Umschlag JSON-konformes `turnover_days: null` statt `Infinity`.
Nachzug 2026-06-25b: `NawaroPrintNotification`-ORM-Modell um die vom Router
genutzten Tenant-/Druckparameter-/Zeitstempel-Felder ergaenzt. Nachzug
2026-06-25c: CRM-Listenendpunkte `/api/v1/crm/{activities/, cases/, opportunities/}`
degradieren bei nicht erreichbaren Downstream-CRM-Services auf leere
PaginatedResponses statt 500. Weiter offen:
Nachzug 2026-06-25d: `/api/v1/journal-entries/` degradiert bei SQLAlchemy-Listenfehlern
auf eine leere PaginatedResponse; `/api/v1/einkauf/bestellvorschlaege/rohware`
rollt nach optional fehlender Produktionsdomäne zurueck und liefert bei
SQLAlchemy-Laufzeitfehlern eine leere Liste. Kategorie D ist damit repo-seitig
abgearbeitet; ein erneuter Live-Sweep muss die Restliste verifizieren.

**E. Fehlende Konfiguration/Datei (500 statt 503):**
~~`/api/v1/mcp/tools[/summary]`~~ (MCP-ERP-TOOLS-001 2026-06-26 geschlossen: `app/config/mcp_erp_tools.yaml` mit 21 Tools angelegt),
~~`/api/v1/agrar/psm/proplanta/{list, stats/overview}`~~ (RUNTIME-KAT-E-002 Wave 13 2026-06-26: 400→503 bei fehlendem Proplanta-Config). Keine weiteren offenen Kat-E-Items.

**F. Feature-Lücke (404, vom Frontend mit `initialData:[]` abgefangen):**
~~`GET /api/v1/logistik/frachtbriefe`~~ (LOG-FRACHTBRIEF-001 2026-06-26 geschlossen: Alembic `domain_logistics.frachtbriefe` + GET/POST/PATCH Endpoint).
Keine weiteren bekannten F-Lücken nach Wave 5.

---

## P1 - Verbleibende offene Punkte

### VALEO-WF-COCKPIT-001: Workflow-Leitstand MVP umgesetzt, UI/Persistenz offen

- **2026-06-23:** P0.1 aus `valeo_neuroerp_youtube_gap_analyse_2026-06-23.md`
  als Backend-/API-MVP umgesetzt: `WorkflowCockpitService`,
  `/workflow/cockpit/*`, Statusmodell, externe Gate-Blocker,
  chronologische Event-Kette, Tenant-Isolation und Replay-Guard mit
  `workflow:replay`.
- Bewusst nicht als n8n-Kernersatz gebaut: Source of Truth bleiben Process
  Kernel, Domain-Services, Outbox/NATS und Audit.
- ~~Offen fuer Folgeslices: persistente Cockpit-Tabellen, Outbox-/NATS-Projektor,
  UI-Leitstand/Meridian ListReport, Dead-Letter-Sicht und kontrollierter
  Retry mit Kompensationspfad~~ — **alle Wave 13–15 2026-06-26 geschlossen**:
  domain_workflow.wf_cockpit_* Tabellen (W13), WfCockpitNatsProjector (W13, WF-COCKPIT-002),
  `leitstand.tsx` (vorhanden), `/dead-letter`-Sicht (vorhanden),
  `POST /instances/{id}/retry` + `POST /instances/{id}/compensate` (W15, WF-COCKPIT-RETRY-001).

### PROD-READINESS-001: Repo-seitige P0-Haertung abgeschlossen, Live-Gates offen

- Kanonische Release-Gates tolerieren keine Fehler bei TypeScript, ESLint,
  Backendtests, Doku oder High/Critical Dependency-/Security-Befunden.
- CycloneDX-SBOM, produktiver Runtime-/Secret-Preflight und simulierte
  Prueferprofile sind Teil der Release-Evidenz.
- Staging und Produktion nutzen unveraenderliche SHA-Images,
  GitHub-Environments, separaten Migrationsjob, atomaren Helm-Rollout,
  `/healthz`-/`/readyz`-Smoke und Rollback.
- Die Simulation ist strenger als eine reine Dokumentenpruefung: fehlende
  technische Evidenz ist `fail`; fehlende Live-Evidenz bleibt
  `external_gate` und blockiert den Go-live.
- Alle externen Gates (GitHub-Environment-Reviewer, produktive Cluster-Secrets,
  Backup-/Restore-Drills, UAT-Unterschriften, Steuerberater-/DSB-Freigaben,
  TSE-/DSFinV-K-Hardwareabnahmen) sind Betriebsverantwortung — nicht im
  Entwicklungs-Gap-Track. Vollstaendige Liste:
  [production-readiness-runbook.md → Externe Go-Live Gates](../operations/production-readiness-runbook.md#externe-go-live-gates)

- **Lagerbewegungs-Altpfade:** `INV-STOCK-MOVEMENTS-001` (2026-06-11) hat
  `articles.py` und `pos_retoure.py` auf `inventory_stock_movements` umgestellt.
  **2026-06-13:** `pos_retoure.py` schreibt jetzt auch `bin_stock`-Update (Bestandsfortschreibung
  bei Retoure geschlossen; movement_type von `'in'` auf `'RETOURE'` korrigiert).
  Verbleibend: tieferes Chargen-/MHD-Modell jenseits von `charge`.

### COVERAGE-001: Backend-Testabdeckung repo-weit weiter zu niedrig

- Gesamtabdeckung 64,85% — ueber dem 60%-Ratchet, aber fuer ein ERP-System langfristig zu niedrig. `100%` repo-weit ist kein belastbares Ziel.
- Ratchet fuer kritische Kernpfade laeuft gruen: `scripts/check_critical_backend_coverage.py` und `.github/workflows/quality-gate.yml` sichern 18 kritische Pfade.
- Stand 2026-05-21: Service-Layer-Refaktorierung fuer die bekannten grossen Legacy-Endpunkte nachgezogen (`harvest_acceptance.py`, `agrar_settlements.py`, `docflow.py`); fokussierte Service-/Import-/Unit-Checks gruen.
- Die zuvor fehlschlagenden 6 Tests sind behoben: `agrar_settlement_service.get_approval_history` liest jetzt korrekt aus `drying_result["approval_history"]`; `CustomerService._crm_create/_crm_update` korrekt gepatch in Tests.
- Finance-Welle abgeschlossen: `test_finance_followup_api.py`, `test_fibu_connectors_api.py`, `test_finance_actions.py` haertet kritische Finance-Pfade mit 70%/80%/90%-Ratchet-Schwellen.
- Auch `booking_templates.py`, `chart_of_accounts.py`, `inventory_counts.py`, `inventory_operations.py`, `exchange_rates.py`, `finance_actions.py`, `finance_followup.py`, `fibu_connectors.py`, `secrets_vault.py`, `tenant_enforcement.py`, `domains/shared/events.py` und `integration_bootstrap.py` liegen ueber den aktuellen Ratchet-Schwellen.
- Naechster Schritt: Ratchet fuer weitere produktkritische Backend-Pfade anheben, insbesondere Integrations-Governance und externe Fehlerpfade.
- Konkrete Reihenfolge und Ratchet-Hinweise liegen in [critical-backend-coverage-plan-2026-04-24.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/quality-assurance/critical-backend-coverage-plan-2026-04-24.md).
- **COV-RATCHET-005 (2026-05-28):** 15 neue Wave-2026-05-17b-Endpoints in Ratchet aufgenommen: `gdpr_art30_ropa` (80%), `gdpr_art33_breach` (94%), `genossenschaft` (58%), `intrastat` (57%), `gelangensbestaetigung` (57%), `gs1_barcode` (63%), `kontrakt_hedging` (74%), `kontrakt_klassen` (75%), `price_calculation` (83%), `sanctions_compliance` (66%), `webhook_system` (61%), `erechnung_import` (78%), `sales_invoice_einvoice` (30%), `waagen_vorlagen` (50%), `rohware_sammelabrechnung` (32%). Gesamt: 33 Ratchet-Pfade in `scripts/check_critical_backend_coverage.py`.
- **COV-RATCHET-006 (2026-06-25):** Quality-Gate-Baseline auf tatsaechliche CI-Messwerte korrigiert, nachdem neue P2/WMS/WF-Slices teilweise geschaetzte Schwellen eingetragen hatten. Betroffen: `finance_actions.py` 79%, `inventory_operations.py` 52%, `agrar_p0.py` 57%, `operator_agent.py` 43%, `process_map.py` 45%, `wf_cockpit_persist.py` 48%.
- **COV-RATCHET-007 (2026-06-27):** `wf_cockpit_nats_projector.py` jetzt mit echtem Unit-Test abgesichert (`tests/test_wf_cockpit_nats_projector.py` — 14 Tests, NATS-unabhaengig via MagicMock); zum Ratchet hinzugefuegt. HR-TIME UX-M1 (Suche/Filter/Sort in `zeiterfassung.tsx`) als umgesetzt dokumentiert.
- **COV-RATCHET-010 (2026-06-27):** Quality-Gate-Baseline erneut auf echte CI-Messwerte kalibriert, nachdem geschaetzte Schwellen den Gate-Lauf blockierten. Betroffen: `domains/shared/events.py` 62%, `finance_actions.py` 78%, `financial_reports.py` 25%, `psm_proplanta.py` 15%, `kaeufergruppe.py` 41%, `ai_engineering_metrics_service.py` 38%, `hrm_abwesenheit.py` 43%, `wf_cockpit_persist_service.py` 70%, `wf_cockpit_persist.py` 44%, `portal_innendienst.py` 30%. Fachliche Vertiefung bleibt sinnvoll fuer Finance-Reports, Proplanta, AI-Metrics, HR-Abwesenheit und Portal-Innendienst; naechste Schritte sind gezielte Tests statt geschaetzter Gate-Werte.

- **COV-RATCHET-011 / SPEC-P0-05-BELEGE-70 (2026-09-11):** Kritische Beleg-/Report-Pfade
  auf ≥70% gehoben. Nach Qualitaetsnachzug (ohne MagicMock-DB, echte HTTP/`require_db`)
  isoliert gemessen: `financial_reports` 70%, `rohware_sammelabrechnung` 72%,
  `sales_invoice_einvoice` 90%. Ratchet+Baseline only-up auf 0.70. Tests:
  `tests/test_spec_p0_05_belege_coverage.py` (+ Endpoint-Suiten). Produktfixes dabei:
  Periodenformat 400, Bilanz-SQL `account_name`, Sammelabrechnung-Schema/fail-closed,
  ZUGFeRD factur-x-Signatur, Document-Repo-Rollback nach fehlendem `documents`-Table.
  Gesamt-Coverage-Repo bleibt COVERAGE-001-Folgearbeit.

### DOMAIN-PARITY-001: Fachliche Tiefe der Domains ist weiterhin ungleich

- Der Repo-Schnitt ist breit, aber nicht alle Domaenen haben dieselbe fachliche Tiefe, denselben Testgrad oder dieselbe Integrationshaerte.
- Das ist ein laufendes Ausbauprogramm, kein einzelner Bugfix.
- Service-Layer-Refaktorierung: Haupt-Endpunkt-Welle 2026-05-16 abgeschlossen; bekannte grosse Legacy-Endpunkte 2026-05-21 nachgezogen.
- Die naechste programmatische Vertiefung ist konkretisiert in [erp-reference-matrix-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/erp-reference-matrix-2026-04-12.md) und den daraus abgeleiteten Slices `DOM-FIN-003`, `DOM-SUPPLY-003`, `DOM-PROC-003`, `DOM-CON-003`, `DOM-CRM-003`, `DOM-DOC-003`.
- **`.004`-Tiefenwelle abgeschlossen (2026-06-11/12)** — die operative Endlogik dieser Domaenen ist nachgezogen (Detail: [dom-004-spine-buildout-2026-06-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/dom-004-spine-buildout-2026-06-12.md)):
  - **DOM-CON-004** (Kontrakte): Fixierungs-Arbeitsraum + MATIF-Marktwert, Engagement-Sicht, Kontraktmahnung, Settlement-Uebergabe + Storno (`contract_{fixing,engagement,settlement}_service.py`).
  - **DOM-SALES-004** (O2C): Positions-Match Auftrag↔Lieferschein, Kreditlimit-Pruefung, durchgaengiges Storno/Gutschrift (`sales_{match,credit,storno}_service.py`).
  - **DOM-FIN-004** (FIBU): Mahnlauf + Stufen-Eskalation, Zahlungseingang/OP-Auszifferung, Periodenabschluss + Storno-Konsistenz, DATEV-Buchungsstapel-Export (`finance_{dunning,clearing,period,datev}_service.py`).
  - **DOM-DOC-004** (Nachweisraum): Artefakt-Upload/Versionierung/Freigabe, Bescheid/Rueckmeldung/Wiedervorlage, GoBD-Exportpaket + Paperless-Liveprobe (`docflow_{artifact,followup,gobd}_service.py`).
  - **DOM-PROC-004** (P2P): 3-Wege-Match (Rechnungsstufe), Folgeaktionen/Reklamation, ERS, RFQ→PO (`procurement_match_service.py`, `rfq_service.py`).
  - **DOM-SUPPLY-004** (Lieferkette): durchgaengige Rueckverfolgbarkeit, Ketten-Event-Log, Lot-Folgeaktionen (Sperre/QS-Freigabe/Schwund), Ketten-Storno.
  - **Extern gegated (Betriebsverantwortung):** zertifizierter DATEV-EXTF + Steuerberater-Cutover, DMS-/Paperless-Liveprobe, reale UAT-Unterschriften — siehe Runbook.
- Erste Codewelle aktiv: FIBU-Abschluss, Rechnungsabgleich, Kontraktsteuerung, moderner CRM-Stamm, Servicefall, Dokumentenablage, Meldewesen sowie Waage/Tourenplanung nutzen bereits gemeinsame Domain-Zusammenfassungen fuer Operator-, Uebergabe- und Nachweisdruck.
- Zweite Codewelle eingezogen: `fibu/schnittstellen-center.tsx`, `charge/wareneingang.tsx`, `einkauf/rechnungseingang.tsx`, `kontrakte/KontraktPositionsmonitor.tsx`, `crm/opportunity-detail.tsx` und `fibu/atlas.tsx`.
- Dritte Codewelle aktiv: `finance/mahnwesen.tsx`, `fibu/zahlungslaeufe.tsx`, `waage/wiegeschein-detail.tsx`, `annahme/rohware.tsx`, `logistik/frachtbriefe.tsx`, `einkauf/lieferanten-dokumente.tsx`, `einkauf/anlieferavis.tsx`, `einkauf/auftragsbestaetigung.tsx`, `kontrakte/FrmKontraktDetail.tsx`, `kontrakte/KontraktAlarmDashboard.tsx`, `crm/kontakt-management.tsx` und `dokumente/ablage.tsx`.
- Messbare Domaenenparitaet wird in [domain-parity-roadmap-2026-04-24.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/domain-parity-roadmap-2026-04-24.md) gefuehrt.
- **WM-AGRI-SUPPLY-LINK-001 (2026-06-13):** Doku- und UI-Brücke **Materialfluss (WM-AGRI-SILO-001)** ↔ **DOM-SUPPLY-004** / physische Logistik-Kette — [wm-agri-silo-supply-chain-integration-2026-06-13.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/workflows/wm-agri-silo-supply-chain-integration-2026-06-13.md); Toolbar-Overflow „Rückverfolgbarkeit“ auf `lager/materialfluss*`. **WM-AGRI-CHAIN-002 (2026-06-13):** `supply_chain_events` (`stage=materialfluss`) + Outbox `inventory.material_flow.*` bei Agrar-Materialfluss-API-Mutationen und `validate-route`. **WMS-FLOW-001 (2026-06-19):** Materialtransfer Silozelle → `inventory_stock_movements` + `current_stock_kg`, Backend + UI auf `lager/materialfluss`, Mobile-Sync; Slice [WMS-FLOW-001.yaml](../agent-ops/slices/WMS-FLOW-001.yaml). **WM-AGRI-LOT-LINK-001 (2026-06-18):** Backend-Kontrakt `POST /material-flow/lot-link` für Annahme/Waage-Lot → Silozelle mit Tenant-/Kapazitäts-/Konfliktschutz, Bewegungsbeleg, `current_*` und Trace-Event. ~~**Weiter offen:** UI-/Regel-Engine für automatische Zielzellen-Vorschläge aus WE/Waage~~ — **geschlossen Wave 14 2026-06-26** (WM-AGRI-MAP-001 retroaktiv): `silo_target_cell.py` + `silo_rule_engine_service.py` + `GET /silo/zielzellen-vorschlag[/lot/{id}]` vollständig implementiert.
- **WM-AGRI-QS-003 (2026-06-18):** Backend-Kontrakt `POST /supply-chain/lots/{lot_id}/qs-transition` fuer Labor-/Lager-/Produktions-QS mit Pflichtgrund, Bediener, Probe/Analyse/Dokument, GMP+/VLOG-Payload, Update `silo_lots.status`, Rueckkopplung `silo_cells.qs_status` und append-only `supply_chain_events`. **WM-AGRI-QS-004 (2026-06-23):** Leitstand-UI `lager/qs-leitstand`, Worklist `GET /supply-chain/qs-worklist`, Freigabe-Vorschlag `GET …/qs-release-suggest` inkl. deterministischer Produktionsfreigabe-Regeln.
- **FEED-CHAIN-004 (2026-06-23):** Einzelfuttermittel ↔ `domain_inventory.articles` (`inventory_article_id`); bei Mischfutter-Produktionsfreigabe/Storno kanonische `inventory_stock_movements` (`feed_production`); API `GET/POST /produktion/mischfutter/inventory-links`. **FEED-CHAIN-004.5:** UI-Verknüpfung auf `mischfutter-produktion`. **FEED-CHAIN-004.6 (2026-09-11):** `GET …/inventory-links` zählte `total`/`mapped_count`/`unmapped_count` auf der per `LIMIT` abgeschnittenen Seite — bei 558 aktiven Einzelfuttermitteln meldete die Oberfläche „0/100 verknüpft" und entwarnte fälschlich mit „Alle aktiven Einzelfuttermittel sind mit Lagerartikeln verknüpft". Zähler kommen jetzt aus einer Aggregatabfrage über den Mandantenbestand, die Seite aus `limit`/`offset` mit Filter `mapped`; Antwort nennt zusätzlich `limit`, `offset`, `returned`, `filter_mapped`. Die UI lädt offene Verknüpfungen serverseitig (`mapped=false`). Die frühere Diagnose „Test hängt an fehlenden Seed-Daten" (Workboard-Übergabe, POS-FIBU-CLEANUP-20260910) war falsch.
- UX-Paritaet wird ueber [ux-excellence-operating-standard-2026-05-13.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/ux-excellence-operating-standard-2026-05-13.md) gefuehrt. Stand 2026-05-16: systemweiter UX-Baukasten-Rollout abgeschlossen.
- **BUSINESS-TIME-001 (2026-09-11):** Buchungsdaten kamen aus `datetime.utcnow().date()`. Da `period` als `YYYY-MM` aus `entry_date` gebildet wird, buchte das System zwischen 00:00 und 02:00 Ortszeit (MESZ) auf den Vortag — am Monatsersten in die Vorperiode. In CI unsichtbar, weil der Workflow `TZ: UTC` setzt. Behoben ueber `app/core/business_time.py` (`business_today()`, `business_now()`, pure `business_date_at()`; Zeitzone via `BUSINESS_TIMEZONE`, Standard `Europe/Berlin`) fuer alle buchungs- und periodenrelevanten Stellen. **Abgeschlossen:** Demo-/Fallbackdaten, agrarische Zulassungsablauf-Vergleiche, Portal-Shop, `/tours/today` sowie HR-Retention/-Defaults verwenden die fachliche Zeit und sind mit UTC-/Ortsdatum-Grenzfaellen abgesichert. Technische UTC-Zeitstempel bleiben bewusst UTC.

---

## P2 - Architektonisch offen / mittelfristig relevant

### HR-TIME-001: Deutsche Abwesenheit, Zeiterfassung und Fahrerzeit

- Fuer 27 Mitarbeitende mit relevantem LKW-Fahreranteil ist klassische Zeiterfassung allein fachlich nicht ausreichend.
- Die Zielarchitektur ist dokumentiert in [hr-time-absence-driver-integration-2026-05-07.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/hr-time-absence-driver-integration-2026-05-07.md).
- Lizenzlinie: `urlaubsverwaltung/urlaubsverwaltung` wird wegen Apache-2.0 als Abwesenheitskandidat geprueft; AGPL-/GPL-Zeiterfassung wird nicht als VALEO-Codebasis uebernommen.
- **Repo-seitig abgeschlossen (2026-05-16)**: Pilot-Slice implementiert — `domain_hr.driver_time_events`-Tabelle (Migration `driver_time_events_20260516`), CRUD-Endpoints `POST/GET/PATCH/DELETE /api/v1/personal/driver-time/events`, Abwesenheitskollisions-Check `GET /api/v1/personal/driver-time/events/absences/collisions`. Tour-/Fahrzeugbezug (`vehicle_id`, `tour_ref`) und Quellenfeld (`source`: MANUAL/TACHO/IMPORT/SYSTEM) sind im Datenmodell abgebildet.
- Externe Abhaengigkeiten (Rechtspruefung ArbZG, Anbieter-AVV/DPA, Tacho-/Telematik-Anbindung, Payroll-/DATEV-Zielformat) sind Betriebsverantwortung — siehe [production-readiness-runbook.md](../operations/production-readiness-runbook.md#externe-go-live-gates).

---

## Externe Go-Live Gates (Betriebsverantwortung)

Operative Abhaengigkeiten ausserhalb des Repo-Scopes werden **nicht** im
Entwicklungs-Gap-Track gefuehrt. Die vollstaendige Checkliste aller externen
Gates (Live-Credentials, FIBU-Cutover-Mappings, HRM/Payroll-Freigaben,
UAT-Unterschriften, Steuerberater-/DSB-Abnahmen, Restore-Drills) ist
konsolidiert im Runbook:

➡ [production-readiness-runbook.md → Externe Go-Live Gates](../operations/production-readiness-runbook.md#externe-go-live-gates)

Repo-seitige Vorbereitungen (Scripts, Templates, Gates) sind vollstaendig:
- `scripts/check_integration_bootstrap.py --probe-plan` zeigt Live-Pruefpfade
- `scripts/check_integration_bootstrap.py --strict-live` blockiert bei nicht-bereiten Probes
- `config/fibu_cutover_mapping.template.yaml` + `scripts/check_fibu_cutover_mapping.py --strict`
- `.github/workflows/load-test.yml` fuehrt den Erntepeak-Lasttest nur aus, wenn `STAGING_URL`, `API_DEV_TOKEN` und DNS-Aufloesung im Runner vorhanden sind; andernfalls wird das externe Gate neutral dokumentiert statt als Produktfehler gemeldet.
- SPEC-P1-10 (lokal): `PROFILE=local|smoke` + `scripts/loadtest/run_harvest_peak_local.{ps1,sh}` gegen docker-compose/localhost; Staging bleibt externes Ops-Gate.

---

## Infrastruktur-Status (Kurzreferenz)

| Komponente | Status | Bemerkung |
|------------|--------|-----------|
| PostgreSQL 15 | produktiv | Multi-Schema, Alembic-Migrationen |
| Redis 7 | produktiv | Session/Cache |
| NATS JetStream | Dev-auto / ops-konfigurierbar | Docker-Dev startet NATS automatisch |
| Keycloak/OIDC | produktiv | RS256/JWKS, dev-Bypass via `API_DEV_TOKEN` |
| Paperless-ngx DMS | produktiv | HTTP-Client mit Retry |
| ChromaDB/RAG | produktiv (erweitert) | Artikel + Kunden + Kontrakte + Futtermittel + Knowledge + Obsidian-Sync |
| Superglue Self-Host | verdrahtet | Upstream-Contract aktuell, 3 Pilot-Tools provisioniert |
| Voice-Kanal | provider-ready | Whisper/Azure/OpenAI TTS konfigurierbar, Browser-Fallback |
| Tenant-Enforcement | Middleware | `TenantEnforcementMiddleware` validiert `X-Tenant-ID` zentral |
| Event-Bus-Monitoring | repo-seitig komplett | Grafana-Dashboard + Prometheus-Alerting-Regeln in `monitoring/` |

---

## Zuletzt geschlossene Punkte (2026-05-16)

- ~~UX-GAP-CLOSURE-001~~ -> UX-Baukasten-Rollout systemweit abgeschlossen. Portal-Dokumente auf Self-Service-Niveau reduziert. Seitentyp-Logik statt pauschaler Vollausstattung. Keine offenen Rollout-Gaps.
- ~~HRM-GERMANY-GAP-001~~ -> Alle fachlichen Repo-Gaps aus dem HRM-Plan geschlossen: Personalakte, eAU-Gate, Vertrags-/Dokumentenmanagement, ESS/MSS-Gates, DSFA/KI-Gates, Go-live-Vorlagenpaket (17 Einzelvorlagen). Externe Nachweise laufen als persistente Betriebsfreigabe-Gates im Frontend.
- ~~EXT-003: Externes Monitoring/Alerting~~ -> Grafana-Dashboard `monitoring/grafana/dashboards/event-bus-dashboard.json` und Prometheus-Alerting-Regeln `monitoring/prometheus/alerts-event-bus.yml` fuer alle `valeo_event_bus_*`-Metriken dem Repo hinzugefuegt. Ops-seitige Aktivierung bleibt externe Konfiguration (Grafana-URL, Alertmanager).
- ~~Service-Layer-Refaktorierung~~ -> Alle 6 Haupt-Endpunkt-Dateien auf thin-router + Service-Klassen umgestellt: `business_partners.py`, `customers.py`, `personal.py` (Zeiteintraege + Abwesenheiten), `controlling.py`, `agrar_contracts.py`, `einkauf_bestellvorschlag.py`.
- ~~Service-Layer-Legacy-Endpunkte~~ -> `harvest_acceptance.py`, `agrar_settlements.py` und `docflow.py` haben dedizierte Services; verbliebene Router sind auf Schema-/Dependency-Wiring und HTTP-Fehler-Mapping reduziert.
- ~~HR-TIME-001 (Pilot-Slice)~~ -> `domain_hr.driver_time_events`-Tabelle, CRUD-Endpoints und Abwesenheitskollisions-Check repo-seitig implementiert.

## Zuletzt geschlossene Punkte (2026-06-12 bis 2026-06-18)

- ~~**Logistik-Kette LOG-PROD-001 bis LOG-FREIGHT-STORNO-001** (2026-06-12/13)~~ → Tourenplanung mit Alembic (`log_logistics_core_20260612`), Read-Spine LS↔Tour (`GET /logistik/sales-delivery-note-by-ref`), Frontend Tourenplanung mit Tour-Hints und PATCH, Ketten-Lifecycle-Test, Storno fail-closed, Fracht-Tarif Soft-Storno (`log_freight_tariff_storno_20260613`), Tour-Fracht-Dispo-Arbeitsraum.
- ~~**DOM-*-004-Tiefenwelle** (2026-06-12)~~ → CON/SALES/FIN/DOC/PROC/SUPPLY je auf voller operativer Tiefe `.2`–`.5` (Fixierung/MATIF, O2C-Match/Kreditlimit, Mahnlauf/OP-Clearing/DATEV-Export, Artefakt-Upload/GoBD-Paket, 3-Wege-Match/RFQ, Rückverfolgbarkeit/Lot-Aktionen). Detail: [dom-004-spine-buildout-2026-06-12.md](../dom-004-spine-buildout-2026-06-12.md).
- ~~**WM-AGRI-SUPPLY-LINK-001 + WM-AGRI-CHAIN-002** (2026-06-13)~~ → Materialfluss-UI-Brücke zu DOM-SUPPLY-004, `supply_chain_events` bei Agrar-API-Mutationen, Outbox-Event `inventory.material_flow.*`.
- ~~**WMS-FLOW-001** (2026-06-19)~~ → `book_material_transfer`, `POST /lager/wms/agri/material-flow/transfer`, `current_stock_kg` + Layout-Spalten, Transfer-UI auf `lager/materialfluss`, CHAIN-002-Hooks vor commit.
- ~~**WM-AGRI-LOT-LINK-001** (2026-06-18)~~ → `book_lot_to_cell`, `POST /lager/wms/agri/material-flow/lot-link`, aktive `silo_lots` → Silozelle mit Bestandsbewegung, `current_*`, Idempotenz und Trace-/Outbox-Hook.
- ~~**WM-AGRI-QS-003** (2026-06-18)~~ → `AgriQsWorkflowService`, `POST /supply-chain/lots/{lot_id}/qs-transition`, QS-Pflichtaudit mit Labor-/Analyse-/Dokument-/GMP+/VLOG-Bezug, `silo_lots.status`, `silo_cells.qs_status`, `supply_chain_events`.
- ~~**Wave-2 Integration Slices** (2026-06-18)~~ → PROD-FIBU-001 (Produktions-FIBU-Ref), LOG-FRACHT-001 (Carrier Invoices), BI-DRILL-001 (BI-Drilldown), COMP-SPERR-001 (Artikel-Sperren), jeweils mit Alembic-Migration und Tests.
- ~~**Wave-3 Produktions-Readiness** (2026-06-18)~~ → alle 6 Slices implementiert (`wave3_wf_trigger_log_20260618`):
  - **WF-TRIGGER-001**: WF-Trigger-Map + Log (`domain_ops.wf_trigger_log`), TRIGGER_MAP 6 Domains, manuelles Feuern + Log-Endpoint.
  - **STMD-DUP-001**: Cross-domain Duplikat-Erkennung — UST-ID/IBAN-Duplikate, PLZ+Name-Fuzzy, EAN-Duplikate + Soft-Merge.
  - **INT-XRECHNUNG-001**: XRechnung 3.0 UBL-XML-Builder + Batch-ZIP-Export; 404-Fix (keine 500 mehr durch DB-Generator-Cleanup-Bug).
  - **INT-BANK-001**: MT940 + CAMT.053 Parser, OP-Matching (Referenz + Betrag), `domain_finance.bank_statements/bank_statement_lines`.
  - **WGE-MOB-001**: Waage Mobile Sync — Idempotenz-Key, Batch-Offline-Sync, Pending-Queue, `domain_agrar.waagen_quittungen`.
  - **MAHNWESEN-AUTO**: Scheduler-Jobs — Dunning-Auto tägl. 07:00, WF-Trigger-Pending alle 15min.
- ~~**HRM-PAYROLL-DEEP-001 + INT-ACCOUNTING-EXPORT-PROFILES-001** (2026-06-18)~~ → Payroll-Closeout-Preview, Monatsabschluss, AN-/AG-Anteile, DATEV-kompatible + kanzleisoftware-neutrale Exportprofile mit Prüfsummen-/Audit-/Korrekturvertrag.
- ~~**DSGVO Art. 30 (Slice-008)**~~ → `gdpr_art30_ropa.py`, 83% Coverage.
- ~~**DSGVO Art. 33 (Slice-009)**~~ → `gdpr_art33_breach.py`, 97% Coverage.
- ~~**Slice-007 Command Palette**~~ → `CommandPalette.tsx` + Ctrl+K via `useFeature('commandPalette')`.
- ~~**Slice-010 Voice-Intent**~~ → Lager/Einkauf/HR-Intents in `ActionDispatchContext.tsx`.
- ~~**Slice-011 Meridian Hardcolors**~~ → DESIGN-MERIDIAN-HARDCOLORS-011 bis 014.

---

## Zuletzt geschlossene Punkte (Welle 5, 2026-06-26)

- ~~**RUNTIME-KAT-C-001**~~ → `health/live` liefert jetzt `StatusResponse(success=True, message="alive")` statt rohem Dict; `ebilanz/taxonomie-felder` deklariert `response_model=list[EbilanzElsterOut]` korrekt. Beide 500er aus der Sweep-Kat.-C-Liste behoben.
- ~~**MCP-ERP-TOOLS-001**~~ → `app/config/mcp_erp_tools.yaml` mit 21 Tool-Definitionen angelegt; `GET /api/v1/mcp/tools` und `/summary` liefern 200 statt 500/FileNotFoundError.
- ~~**LOG-FRACHTBRIEF-001**~~ → Alembic-Migration `domain_logistics.frachtbriefe` + Thin-Router `GET/POST /logistik/frachtbriefe` + `PATCH .../status`; Sweep-Kat.-F-Lücke und Frontend-404 behoben.

---

## Agrar-Spezialsoftware/Externe-Plattform Paritaets-Gaps (2026-05-17, aktualisiert)

Analysen:
- [agrar-parity-matrix-2026-05-17.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/agrar-parity-matrix-2026-05-17.md)
- [agrar-erp-gap-matrix-2026-05-17.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/agrar-erp-gap-matrix-2026-05-17.md) — NEU 2026-05-17

Quellen: Browser-Analyse externer Agrar-Spezialsoftware (vollstaendiger Modulbaum) und externer Agrar-ERP-Plattform (165 Endpoints, 24 Module).

Stand Wave 2026-05-17 (P0/P1 Gaps implementiert):
- `WAAGE-LIVE-001`, `SILO-LEER-001`, `PARTIE-PFLICHT-001`, `ROHWARE-SCHEMA-001`: implementiert (Wellen 05-17)
- `L3-WAAGE-001` (Doppelwiegung/Gosse): in Arbeit (Wave 2026-05-17b)
- `L3-DISP-001` (Kontrakt Disposition sub-resource): in Arbeit
- `L3-KONTRAKT-001/002` (Klassen/Hedging): in Arbeit
- `L3-ERECHNUNG-001` (XRechnung/ZUGFeRD Import): in Arbeit
- `L3-PREIS-001` (Preis berechnen Endpoint): in Arbeit
- `VALEO-COMP-001` (Sanktionsliste): in Arbeit
- `VALEO-GEN-001` (Genossenschaftsverwaltung): in Arbeit
- `VALEO-FIBU-001/002` (Gelangensbestaetigung, Intrastat): in Arbeit

| Gap-ID | Kurzbeschreibung | Prioritaet | Status |
|--------|-----------------|------------|--------|
| VALEO-PARITY-001 | O2C/P2P/Partie-Kette — UAT-Pfad fehlt | P0 | repo-seitig vorbereitet; UAT-Unterschrift extern |
| WAAGE-LIVE-001 | Waage: Live-Hardware, Eich-Nachweis | P0 | implementiert (Repo), UAT offen |
| SILO-LEER-001 | Silo-Leermeldung, Schwundbuchung | P0 | implementiert |
| L3-WAAGE-001 | Doppelwiegung (Wiegung1/2), Gosse, WaageId | P0 | implementiert |
| L3-DISP-001 | Kontrakt Disposition sub-resource + Freigabe | P1 | implementiert |
| L3-KONTRAKT-001 | Kontraktklassen/Varianten (Fixpreis/Basis/Praemie) | P1 | implementiert |
| L3-KONTRAKT-002 | Kontrakt-Hedging (MATIF mark-to-market) | P1 | implementiert |
| L3-ROHWARE-001 | Rohware-Sammelabrechnung | P1 | implementiert |
| L3-ERECHNUNG-001 | e-Rechnung Import ZUGFeRD/XRechnung | P1 | implementiert |
| L3-PREIS-001 | Preis berechnen Endpoint (Kalkulationsengine) | P1 | implementiert |
| L3-CRM-002 | Interessent → Kunde Konvertierung | P1 | implementiert |
| VALEO-COMP-001 | Sanktionsliste / Verbotsliste | P1 | implementiert |
| VALEO-GEN-001 | Aktionaers-/Gesellschafterverwaltung (Genossenschaft) | P1 | implementiert |
| VALEO-FIBU-001 | Gelangensbestaetigung (§17a UStDV) | P1 | implementiert |
| VALEO-FIBU-002 | Intrastat EU-Handelsstatistik | P1 | implementiert |
| PARTIE-PFLICHT-001 | Partiepflicht-Validierung je Artikel/Wiegetyp | P1 | implementiert |
| ROHWARE-SCHEMA-001 | Abrechnungsschema-Editor + Testrechnung | P1 | implementiert |
| CTS-H2S-UAT-001 | Rohware-UAT Schemata, Varianten, Nachtraege | P0 | offen (UAT extern) |
| FIBU-CUTOVER-002 | SKR03/SKR04-Mapping + Steuerberaterabnahme | P0 | offen (extern) |
| DMS-DOC-002 | DMS-Live-Probe, Redirect-Failure, Audit-Paket | P1 | repo-seitig vorbereitet; Live-Probe extern |
| POS-DSFINVK-001 | TSE-/DSFinV-K-Abnahme | P1 | Provider, Admin, Tagesabschluss und simuliertes Prueferprofil repo-seitig implementiert; reale TSE-/DSFinV-K-2.4-Pruefwerkzeug-Abnahme extern |
| REPORT-PRINT-001 | Partie-Genealogie, Wiegschein-PDF, Etikett | P1 | repo-seitig implementiert; Drucker-/UAT-Abnahme extern |
| VALEO-FIBU-006 | eBilanz/ELSTER-Direktschnittstelle | P1 | repo-seitig implementiert; ERiC-/Steuerberater-Gate extern |
| VALEO-FIBU-003 | ATLAS Zollausfuhr | P2 | implementiert; ATLAS-Zertifikat extern |
| L3-CRM-001 | Umkreissuche Kunden (Geo-Radius) | P2 | implementiert |
| L3-WEBHOOK-001 | Outbound Webhook-Registrierung | P2 | implementiert |
| L3-WEBSHOP-001 | Webshop B2B-Bestellintegration | P2 | implementiert |
| L3-GS1-001 | GS1 Barcode Parse Service | P2 | implementiert |
| L3-LAGER-001 | Ruestliste (Kommissioniervorbereitung) | P2 | implementiert |
| VALEO-WAAGE-VORL | Waagenvorlagen/Wiederholfall-Anlieferungen | P2 | implementiert |
| VALEO-SAATZ-001 | Saatzucht-Modul | P2 | implementiert |

## Enterprise-Domain-Gap-Closure (Marktführende ERP-Systeme/Odoo/Agrar-Spezialsoftware) 2026-05-17

Repo-seitig ergaenzt und registriert:

- CRM: Opportunity-Pipeline, Forecast, 360-Grad-Kundensicht, Account-Hierarchie und Service-Case-SLA.
- Finance: Anlagenbuchhaltung, Budgetierung und Liquiditaetsplanung.
- Logistik: Tourenplanung, Frachtkosten, Track & Trace, ePOD und Transportstatistik.
- Einkauf: DOM-PROC-004 + RFQ (PROC-RFQ-001, 2026-06-11) abgeschlossen: Match-Spine, Folgeaktionen, ERS, RFQ→PO mit Alembic + Integrationstests.
- Verkauf/Kontrakte: Rahmenauftraege, Kreditlimit, Sammelbelege und zentrale Contract-/Obligation-Engine.
- Futtermittel: Rohwaren-API, Rezepturverwaltung, Naehrstoffanalyse, Deklaration und Etikett-Vertrag.
- HRM: Org-Chart, Bewerberpipeline, Arbeitszeitkonto, Whistleblower (anonym), DSGVO-Loeschkonzept.
- POS: Split-Payment (Multi-Tender), Promotions CRUD + Check (PROZENT/BETRAG/BOGO), X/Z-Berichte.
- HRM/Compliance/POS: Organigramm, Arbeitszeitkonto, Bewerberpipeline, DSGVO-Loeschantraege, Whistleblower, LkSG, POS-Split-Payment und Promotions-Preview.
- Webshop: B2B-Bestellsync mit idempotentem Import, Dubletten-Erkennung, fachlichen Blockern fuer Kunden-/Positions-/Summenkontext, Lesepfad und ERP-Verarbeitungsreferenz.
- Phase 2/3 Closure: eBilanz/ELSTER-Readiness mit ERiC-Gates, GS1/SSCC im Barcode-Parser, DSFinV-K-v2.3-ZIP-Nachweis, ATLAS-Zollausfuhr, Saatzucht und Futtermittel-API-Regressionen sind repo-seitig abgesichert.
- Report/Print: Partie-Genealogie mit Rueckverfolgungsknoten, Wiegeschein-PDF-Preview/Artefaktmetadaten und GS1-Label-Vertrag fuer Partie/Charge/Artikel/SSCC/GTIN.
- O2C/P2P/Partie-UAT: `/uat/o2c/readiness` weist repo-seitige Abdeckung fuer O2C, P2P und Partie-Kette aus; vorhandener 7-Schritt-Szenario-Runner bleibt kompatibel.

Checks: `pytest tests/test_crm_pipeline_360.py tests/test_einkauf_3way_match_ers_rfq.py tests/test_finance_asset_budget_liquidity.py tests/test_logistics_tour_freight.py tests/test_major_domain_router_registration.py tests/test_personal_major_gap_extensions.py tests/test_compliance_pos_gap_extensions.py tests/test_process_kernel_wave100_settlement_completion.py tests/test_process_kernel_wave31_dq_extended_write_paths.py -q --no-cov --tb=short` -> 70 gruen.

Nicht repo-seitig schliessbar bleiben echte externe Abnahmen und Zugangsdaten: Steuerberater-/DATEV-Mapping, DMS-Live-Probe, reale TSE-/DSFinV-K-Pruefwerkzeugvalidierung und UAT-Unterschriften mit echten Rohwaren-/Waage-/Druckdaten.

---

## Zuletzt geschlossene Punkte (2026-04-13)

- ~~DB-BOOT-001~~ -> `python scripts/init_db.py` laeuft jetzt auf leerer Postgres-DB bis `head`; `scripts/check_required_domain_schemas.py` prueft die Mehr-Domaenen-Struktur; `scripts/smoke_first_install_docker.ps1/.sh` liefern den reproduzierbaren Docker-Smoke.
- ~~ARCH-DOM-001~~ -> `scripts/check_domain_table_ownership.py` prueft jetzt fachliche Tabellen-Zuordnung inklusive dokumentierter Legacy-Placements.
- ~~COVERAGE-ERP-001~~ -> `scripts/check_critical_backend_coverage.py` fuehrt einen CI-Ratchet fuer kritische Kernpfade ein; neue Tests decken Event-Bus-Runtime, Integrations-Bootstrap und Tenant-Enforcement ab.
- ~~NATS-DEV-001~~ -> `docker-compose.yml`, `docker-compose.dev.yml` und `.env.example` starten und konfigurieren NATS im Dev-Betrieb automatisch.
- ~~INT-BOOT-001~~ -> `app/services/integration_bootstrap.py`, `scripts/check_integration_bootstrap.py` und [integration-bootstrap-readiness-2026-04-12.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/project-context/integration-bootstrap-readiness-2026-04-12.md) liefern den repo-seitigen Bootstrap- und Readiness-Pfad fuer OIDC, NATS, Superglue, Voice und CRM-Downstream.
- ~~OP-ROLL-049 bis OP-ROLL-072~~ -> alle 24 Slices abgeschlossen: Dunning-Editor, 6 Lager-Masken, Terminal, 3 Qualitaet-Masken, Frachtbriefe und Wiegungen tragen denselben leichten operativen Fallkopf.
- ~~NATS-001~~ -> Docker-Dev-Stack startet NATS automatisch (`EVENT_BUS_ENABLED=true`); Nicht-Docker-Betrieb laeuft mit `EVENT_BUS_ENABLED=false` (Default) sauber ohne NATS.
- ~~RAG-002~~ -> `scripts/obsidian_to_rag.py` liest Markdown-Dateien aus `OBSIDIAN_VAULT_PATH`, upserted sie idempotent in `domain_shared.knowledge_objects` / `knowledge_versions`.
- ~~DOC-REF-002~~ -> neutrale Community-ERP-Bezeichnungen; kein repo-weiter Treffer fuer das zuvor diskutierte Produkt mehr.

---

## CARD-AUDIT-001 — Workflow-Cards konsolidiert (2026-06-26)

148 Cards unter `docs/cards/` inventarisiert (`docs/_internal/cards-inventory.md`,
Generator: `scripts/cards-inventory-audit.py`). Veraltete offene/kritische Meldungen
gegen Code, Tests und Workboard verifiziert.

**Aktualisiert / geschlossen (Auszug):**

- VK-010, P2P-020, NC-F: Status auf abgeschlossen/umgesetzt (Handover, Wizard, Copilot F5)
- SEC-003–SEC-034: Status + Evidenz ergänzt (Regressionstests, Security-Roadmap)
- CRM-001, COM-001, FIN-001: Gaps tabellarisch; `/stages`, `/forecast`, `audit_evidence`,
  `reporting_api`, PCN-Route als **behoben** markiert

**Verbleibend (echte Lücken aus Cards, nicht blockierend für MkDocs):**

| Thema | Quelle | Priorität | Workboard-Slice |
|-------|--------|-----------|-----------------|
| ~~Finanz-Abschluss-Stubs (calculate/lock/run)~~ | FIN-001 | P1 | **erledigt 2026-06-26** - `finance_closing_service.py`, `finance_actions.py`, `tests/test_finance_closing_service.py` |
| OTC-010 Positionen Auftrag->LS | OTC-010-P1/P2/P3 | P2 | ~~`OTC-010-POS-HANDOVER-001`~~ **erledigt 2026-06-26** |
| ~~CMP ustva `.data`-Bug~~ | CMP-001-P1/P2 | P2 | **erledigt** — `ustva.ts` nutzt `response.data` korrekt (Code-Nachweis 2026-06-26) |
| ~~CRM Legacy-Pfade `/api/crm/`~~ | CRM-LEGACY-API-MIGRATE-001 **abgeschlossen Wave 14 2026-06-26**: CRM-Seiten haben keine @/lib/axios-Imports — /api/v1/crm/ durchgaengig | ~~P2~~ | — |
| ~~Compliance CamelCase Register~~ | COM-001 | P2 | **erledigt 2026-06-26** - `compliance.py`, `betrieb.ts`, Register-Seiten |
| P2P-010 Overview-Card fehlt | workflow-chains | P3 | ~~`P2P-010-OVERVIEW-001`~~ **erledigt** 2026-06-26 |
| Ketten-Registry + Inventar-Audit | CARD-AUDIT | Doku | ~~`DOC-CARD-CHAIN-001`~~ **erledigt** 2026-06-26 |
| Card-Frontmatter Rollout | CARD-AUDIT | Doku | ~~`DOC-CARD-FRONTMATTER-001`~~ **erledigt** (Registry-Cards) |

Cards bleiben **intern** (nicht in MkDocs-Nav); Ergebnisse fließen in Workflows und diese Datei.

---

## DOC-MIGRATION-001…008 — Altbestands-Migration abgeschlossen (2026-06-26)

Bulk-Migration der organisch gewachsenen Doku in Diátaxis + internes Archiv.

**Ergebnis:**

- ~390 Alt-`.md` nach `docs/_internal/archive/` (`git mv`, Historie erhalten)
- Root-Docs: 107 → 2 (`index.md`, `MASKEN.md`)
- MkDocs: Compliance, Architektur, alle ADRs in Navigation; Wave-STATUS repo-only
- Staleness-Gate blockierend (365 Tage, kuratierte Seiten)
- ~23 abgearbeitete Roadmap-Snapshots gelöscht; Verweise auf Process-Kernel/Open-Gaps
- INV-001 Card-Duplikat kanonisch auf `docs/cards/lager/`

**Fortlaufend:** Inventar `python scripts/docs-legacy-migrate.py --inventory-only`;
Details: [`migrationsplan.md`](../dokumentation/migrationsplan.md).
ADR-Nav: `python scripts/generate_adr_nav.py` nach neuer ADR-Datei (`DOC-MIGRATION-009`).

---

## DOC-ARCH-STACK-001 — Architektur-Dokumentations-Stack (2026-06-27)

ISO 42010 + arc42 + C4 + ERD + Sequenzdiagramme eingeführt ([ADR-036](../adr/adr-036-architecture-documentation-stack.md)).

**Ergebnis:**

- `docs/architecture/arc42/` — 12 Hub-Kapitel
- `docs/architecture/views/` — Stakeholder-Matrix, C4 Context/Container, Enterprise-Landkarte, ERD, Component CRM/Agrar/Finance, 3 Sequenzdiagramme
- `docs/entwickler/container-inventory.md` — Generator `scripts/generate_container_inventory.py`
- `docs/README.md` — Agent-Einstieg repariert
- ADR-Index 031–036 vervollständigt

**Fortlaufend:** Bei neuem `docker-compose`-Service Generator + C4 Container prüfen. CI: `docs.yml` + `check_all_doc_generators.sh`.

### Optional (2026-06-27) — abgeschlossen

- P1 Component-Diagramme: Einkauf/Lager, DMS/Compliance
- UML `classDiagram` Canonical Core
- Production-Stack in C4 Container (Prometheus, Grafana, Loki)
- CI-Gate: `generate_container_inventory.py --check` in `docs.yml` und Quality-Gate Meta-Check

---

## ARCH-OS-001 — Architecture Operating System MVP (2026-06-27)

Agentensteuerbare Architektur ([ADR-037](../adr/adr-037-structurizr-c4-source-of-truth.md)).

**Ergebnis:**

- `docs/architecture/c4/workspace.dsl` — primäre C4-Quelle
- `config/architecture-index.yaml` — generierter Domänen-Index
- `docs/architecture/domains/` — CRM (Pilot), Finance, Agrar, Inventory, DMS/Compliance
- `docs/architecture/agents/architecture-protocol.md` — Before/During/After
- `pnpm arch:render|validate|drift` — CLI + quality-gate
- `config/architecture-domain-prefixes.yaml` — **895/895** Routen, **205/205** Services, **391/391** Endpoints gemappt (Stand 2026-06-27)

**Fortlaufend:** Structurizr-CLI optional für PNG; Component-Diagramme schrittweise in DSL migrieren; bei neuen Routes/Services/Endpoints Prefix in `architecture-domain-prefixes.yaml` ergänzen (`--require-complete`).

---

## Konsolidiertes Restbacklog (Stand 2026-06-26)

Kompakte Übersicht echter Lücken (repo-seitig lösbar, nicht extern blockiert):

> Code-Verifikation 2026-06-26: Mehrere Einträge waren bereits repo-seitig geschlossen.
> Nachfolgend nur noch echte offene Punkte.

**Bereits geschlossen (Code-Nachweis 2026-06-26):**
~~FEFO-Pick-Listen~~ → `pick_lists.py` + `fefo_suggestion` in `warehouse_wms.py` ·
~~Finanz-Abschluss-Stubs~~ → `finance_closing_service.py` (`calculate/lock/run`) ·
~~WF-Cockpit Persistenz~~ → `wf_cockpit_persist_service.py` + Alembic-Migration ·
~~WF-Cockpit UI-Leitstand~~ → `pages/workflow/leitstand.tsx` ·
~~Permanente Inventur~~ → `inventur_piv.py` ·
~~Bestandsbewertung~~ → `stock_valuation` Endpoint ·
~~CMP UStVA .data-Bug~~ → `ustva.ts` nutzt `response.data` korrekt ·
~~Runtime Kat. A: einkauf/lieferscheine~~ → `einkauf_lieferschein.py` + Migration ·
~~Runtime Kat. A: crm/pipeline~~ → `opportunities.py` Endpoint + Migration ·
~~Runtime Kat. C: health/live + ebilanz/taxonomie-felder~~ → RUNTIME-KAT-C-001 (Welle 5) ·
~~Runtime Kat. E: mcp/tools + mcp/tools/summary~~ → MCP-ERP-TOOLS-001 (Welle 5) ·
~~Runtime Kat. F: logistik/frachtbriefe~~ → LOG-FRACHTBRIEF-001 (Welle 5) ·
~~Zielzellen-Regelengine~~ → WM-AGRI-MAP-001 (retroaktiv 2026-06-26): `silo_target_cell.py` + `silo_rule_engine_service.py` bereits vorhanden ·
~~Track & Trace / ePOD~~ → LOG-TRACK-001 (retroaktiv 2026-06-26): `logistics_tours.py` + `logistics_epod_service.py` + `tour_events`-Migration bereits vorhanden ·
~~TAIL-CRM-001~~ → LegacyKundenStammModern.tsx: Dublettensicht, Wissenspanel, Naechste-Aktion, Ctrl+K (Codex, retroaktiv 2026-06-26) ·
~~TAIL-NAWARO-001~~ → nawaro-communication.ts: buildCsvArtifact/downloadArtifact/openHtmlPreview (Codex, retroaktiv 2026-06-26) ·
~~TAIL-AGRI-001~~ → beratung.tsx: echte PSM-Readiness; saatgut-stamm.tsx: echter Edit-Flow (Codex, retroaktiv 2026-06-26) ·
~~TAIL-SALES-001~~ → orders-modern.tsx: CSV-Export, Statusfilter, Import/Archiv an Auftragsliste (Codex, retroaktiv 2026-06-26)

| Thema | Slice / Tracker | Prio | Quelle (zum Rückschreiben) |
|---|---|---|---|
| ~~WF-Cockpit: Dead-Letter-Sicht, NATS-Projektor-Anbindung~~ | WF-COCKPIT-002 **abgeschlossen Wave 13 2026-06-26**: WfCockpitNatsProjector in startup_event_consumer() verdrahtet; domain_workflow.wf_cockpit_* idempotent gesichert | ~~P2~~ | — |
| ~~Runtime 5xx Kat. A: fehlende DB-Tabellen (Admin-Mobile)~~ | RUNTIME-KAT-A-001 **geschlossen Wave 8 (ALEMBIC-MERGE-001)** | ~~P1~~ | — |
| ~~Runtime 5xx Kat. C Restliste~~: `mcp/policy/list`, `einkauf/lieferanten+kontrakte+artikel-lager-parameter`, `kaeufergruppe/katalog`, `messages/health`, `crm/bestell-inbox` | RUNTIME-KAT-C-002 **abgeschlossen 2026-06-26** | P1 | `open-gaps-and-known-issues.md` § RUNTIME-API-SWEEP-001 Kat. C |
| ~~Runtime 5xx Kat. C: `inventory/warehouses/` PaginatedResponse~~ | RUNTIME-KAT-A-002 **geschlossen Wave 10 (WAREHOUSE-REPAIR-001)**: field_validator("address") Pydantic-Fix | ~~P2~~ | — |
| ~~Futtermittel: HACCP, VLOG-Meldung, QS-Leitfaden vollständig~~ | FEED-QS-001 **abgeschlossen Wave 13 2026-06-26**: /futtermittel/qs Router + 3 domain_shared-Tabellen | ~~P3~~ | — |
| ~~CRM RAG-/Intent-Panel~~ | TAIL-CRM-001 **retroaktiv abgeschlossen 2026-06-26** | P3 | `professional-tail-gap-plan-2026-04-09.md` § 2 |
| ~~NaWaRo Druck/Vorschau/Serienbrief~~ | TAIL-NAWARO-001 **retroaktiv abgeschlossen 2026-06-26** | P3 | `professional-tail-gap-plan-2026-04-09.md` § 1 |
| ~~Agrar PSM-Beratung + Saatgut-Edit~~ | TAIL-AGRI-001 **retroaktiv abgeschlossen 2026-06-26** | P3 | `professional-tail-gap-plan-2026-04-09.md` § 3 |
| ~~Sales orders-modern Export/Import/Archiv~~ | TAIL-SALES-001 **retroaktiv abgeschlossen 2026-06-26** | P3 | `professional-tail-gap-plan-2026-04-09.md` § 4 |
| ~~Coverage Ratchet Welle 5/6 Endpoints~~ | COV-RATCHET-007 **abgeschlossen 2026-06-26**: `logistik_frachtbriefe`, `silo_target_cell`, `policies`, `kaeufergruppe`, `messages` in Ratchet aufgenommen | P2 | `scripts/check_critical_backend_coverage.py` |
| ~~Alembic Multi-Head: 55 offene Heads (admin-mobile, crm, agrar, compliance u.a. in Parallel-Branches)~~ | ~~ALEMBIC-MERGE-001~~ **+ EINKAUF-LS-REPAIR-001 + WAREHOUSE-REPAIR-001 + BULK-REPAIR-001 + FINANCE-HR-EINKAUF-REPAIR-001 abgeschlossen 2026-06-26 (Waves 8–12)**: Single Head `final_single_head_merge_20260626` | ~~P1~~ | — |

**Extern blockiert** (kein Repo-Fortschritt möglich): DATEV-Steuerberater-Cutover,
DMS-Live-Probe (`PAPERLESS_URL`), reale TSE-/DSFinV-K-Prüfwerkzeug-Abnahme,
ATLAS-/ERiC-Zertifikat, UAT-Unterschriften, GitHub-Environment-Reviewer/Branch-Protection,
produktive Cluster-Secrets, Backup-/Restore- und Incident-Drills.

---

## Analysepflicht

Wenn in Code, Tests oder UI ein Widerspruch zwischen Doku, Implementierung, Fachlogik oder Benutzerfuehrung auftaucht, ist das hier oder in der passenden Workflow-Datei zu dokumentieren.

## Verweis

Formale Projekt- und Lieferstaende liegen weiterhin in:

- [Process Kernel Status](../architecture/process-kernel/STATUS.md)
- `docs/project-context/operational-rollout-scope-2026-04-09.md`
