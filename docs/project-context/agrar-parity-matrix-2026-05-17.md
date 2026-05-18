# Agrar-Spezialsoftware Paritaetsmatrix

Stand: `2026-05-17`
Methodik: Direktvergleich Branchenspezifische-Agrarsoftware-Kernfunktionen gegen VALEO-IST-Routes und vorhandene Tests. Luecken werden als Gap-IDs gefuehrt und in `open-gaps-and-known-issues.md` nachgezogen. Prioritaeten P0–P2: P0 = Go-live-blockierend, P1 = Produktionsqualitaet erforderlich, P2 = UX-/Komfortlevel.

---

## Tabelle 1: Gap-Matrix (Agrar-Spezialsoftware-Funktion → VALEO-IST → Gap)

| # | Agrar-Spezialsoftware-Funktion | VALEO-IST (Kurzform) | Gap / Naechster Schritt | Gap-ID | Prioritaet |
|---|---------------|----------------------|------------------------|--------|------------|
| 1 | Warenwirtschaft Verbuchung — saubere Bestandsfuehrung, Dispo, Lieferung, Faktura, Rohertrag, Nebenbuecher | O2C/P2P/Inventory/Settlement Flow-Spines; `disposition.py`, `charges.py`, `agrar_settlements.py` | Browser-/CRUD-Abnahme der vollstaendigen Folgeobjektkette (Annahme→Silo→Settlement→FIBU-Buchung) fehlt als UAT-Pfad | AMIC-PARITY-001 | P0 |
| 2 | Rohware/Vermarktung — Qualitaets-, Mengen-, Preis-, Abschlags- und finale Abrechnung | `harvest_acceptance.py` (POST/PUT/release/cancel/qualitaetsprotokoll), `agrar_settlements.py` (preview/drying/post-fibu), Trocknungs-Engine | UAT gegen echte Rohwaren-Schemata, regionale Varianten (NRW, BY), Abrechnungsnachtraege; kein End-to-End-Testpfad mit realen Felddaten | CTS-H2S-UAT-001 | P0 |
| 3 | Abrechnungsschemata — Rohwarengruppen, Qualitaetszeilen, Sekundaerwaren, Kosten/Verguetung, Default-Schemata | Preis-/Settlement-Engine + Qualitaetsprotokolle vorhanden; keine Schema-Editor-UI | Schema-Editor/Katalog mit Versionierung, Gueltigkeit und Testrechnung fehlt; keine maschinenlesbare Schemadefinitions-API | ROHWARE-SCHEMA-001 | P1 |
| 4 | Rohwarenkontrakte — Gruppe, Schema, Abschlagspreise, Mindestpreis, Weltmarktpreisfestsetzung | `kontrakte.py` (CRUD + movements + cancel + MATIF-Lookup + positionen) | Teilmengen, Restmengen, Ueberbuchungs-Validierung, Nachtragsprozess und E2E-UAT von Kontraktanlage bis Settlement-Uebergabe fehlen | AMIC-PARITY-001 | P0 |
| 5 | Rohwaren-Anlieferung — Vorerfassung und Weiterbearbeitung | `harvest_acceptance.py` (POST/release/cancel/frachtkosten), Avis-/QR-Schnittstellen | Schnellstart/Vorerfassung ("unvollstaendig starten, sauber abschliessen"-Pfad) fehlt als gefuehrter Klienten-Pfad; UAT-Nachweis ausstehend | CTS-H2S-UAT-001 | P1 |
| 6 | Waage — ASCII-Waagenimport, Satzarten, Fehlerakzeptanz, Qualitaetsfelder | `waage.py` (CRUD Waagen + Wiegungen), Waagen-UX, API und Tests; Coverage-Ratchet gruen | Live-Hardware-/Dateiimport-Test, Eich-/Kalibrierungsnachweise, Offline-/Fehlerqueue bei Verbindungsabbruch fehlen | WAAGE-LIVE-001 | P0 |
| 7 | Waagenvorlagen — Vorlage mit Kontrakt/Fahrer/LKW/Lager/Silo/Sorte/Kunde/Schlag | Waagen- und Annahmeflaechen vorhanden; keine Wiederholfall-/Vorlagen-Logik sichtbar | Vorlage-/Wiederholfall-Mechanismus fuer wiederkehrende Anlieferungen fehlt (kein Endpunkt, kein UI-Pattern) | PARTIE-PFLICHT-001 | P2 |
| 8 | Partie/Charge — Soll-/Ist-Mengen, Werte, Partiepreise, Rohertrag, Rueckverfolgung EK-Produktion-VK | `charges.py` (CRUD + freigabe + qs-readiness), `silo.py` (lots + movements), Silo-Lot-Snapshots | Partie-Genealogie UAT + Druck/Etikett/Report + physische Kette Waage→Silo-Lot→Settlement→VK fehlt als Nachweis | AMIC-PARITY-001 | P0 |
| 9 | Partiepflicht Waage — Pflicht je Artikel/Wiegetyp (Rohware, Saatgut) | Artikel-, Saatgut-, Charge- und Waagen-Endpunkte vorhanden | Harte Validierungsregel "Artikel/Wiegetyp verlangt Partie" fehlt zentral (kein Backend-Constraint, kein Fehler-Feedback im Wiegefluss) | PARTIE-PFLICHT-001 | P1 |
| 10 | Silo-Leermeldung — Leermeldung ueber Waagenbeleg, Schwundsilo, Prozessvoraussetzungen | `silo.py` (kapazitaeten, lots, movements), `silo_operations_api.py` (einlagern/auslagern/bestand) | Leermeldung-Endpunkt, Schwundbuchung, Fehlermatrix und Waagenbeleg-Kopplung fehlen vollstaendig | SILO-LEER-001 | P0 |
| 11 | DATEV/FIBU — SKR03/SKR04, Steuerberaterabstimmung, Export | `fibu_connectors.py` (profiles + imports + validate/post), DATEV-Export, FIBU-Suite, Cutover-Validator | Extern freigegebenes Konto-/Steuer-Mapping + Steuerberaterabnahme fehlen (EXT-002); Cutover-Script repo-seitig bereit | FIBU-CUTOVER-002 | P0 |
| 12 | Bank/e-Clearing — MT940-Import, maschinelle Auszeichnung | `bank_statement_import.py` (POST import, GET lines), Bankabgleich, Auto-Matching | Realbank-Testdateien, Sonderfaelle (Ruecklastschrift, Sammelposten), UAT-Abgleich mit Steuerberater fehlen | AMIC-PARITY-001 | P1 |
| 13 | Kasse/DSFinV-K — DSFinV-K Pflicht-Export fuer Kassenpruefung | `pos_dsfinvk.py` (GET export, GET status), TSE-Endpunkte, POS-Offline-Queue | Produktive TSE-Abnahme + reales DSFinV-K-Exportpaket mit Pruefwerkzeug-Validierung fehlen | POS-DSFINVK-001 | P1 |
| 14 | UX — funktionsdicht, aber altmodisch | Systemweiter UX-Baukasten (ObjectPage/ListReport/Wizard) rollout abgeschlossen | Kein Flaechen-Gap; UAT-Reviews je Kernmaske ausstehend | AMIC-PARITY-001 | P2 |

---

## Tabelle 2: VALEO-API-Routen je Agrar-Spezialsoftware-Funktion

| Agrar-Spezialsoftware-Funktion | VALEO-Endpunkt-Datei | Repraesentative Routen |
|---------------|----------------------|------------------------|
| Warenwirtschaft Verbuchung | `agrar_settlements.py`, `disposition.py`, `charges.py` | `POST /agrar/settlements/`, `POST /agrar/settlements/{id}/post-fibu`, `GET /agrar/settlements/{id}/completion-status` |
| Rohware/Vermarktung | `harvest_acceptance.py`, `agrar_settlements.py` | `POST /agrar/harvest-acceptances/`, `POST /agrar/harvest-acceptances/{id}/release`, `POST /agrar/harvest-acceptances/{id}/qualitaetsprotokoll`, `POST /agrar/settlements/drying/compute`, `POST /agrar/settlements/preview` |
| Abrechnungsschemata | `agrar_settlements.py` | `GET /agrar/settlements/drying-rules`, `POST /agrar/settlements/drying-rules`, `PUT /agrar/settlements/drying-rules/{id}`, `GET /agrar/settlements/billing-weight/preview` |
| Rohwarenkontrakte | `kontrakte.py` | `GET/POST /kontrakte`, `PATCH/PUT/DELETE /kontrakte/{id}`, `POST /kontrakte/{id}/cancel`, `GET /kontrakte/{id}/movements`, `POST /kontrakte/{id}/movements`, `GET /kontrakte/positionen` |
| Rohwaren-Anlieferung | `harvest_acceptance.py` | `POST /agrar/harvest-acceptances/`, `PUT /agrar/harvest-acceptances/{id}`, `POST /agrar/harvest-acceptances/{id}/frachtkosten`, `POST /agrar/harvest-acceptances/{id}/derive-nuts2` |
| Waage | `waage.py` | `GET/POST /waagen`, `GET/PATCH/DELETE /waagen/{id}`, `GET/POST /wiegungen`, `GET/DELETE /wiegungen/{id}` |
| Waagenvorlagen | — (fehlt) | — kein dedizierter Endpunkt vorhanden — |
| Partie/Charge | `charges.py`, `silo.py` | `GET/POST /charges`, `POST /charges/{id}/freigabe`, `GET /charges/{id}/qs-readiness`, `GET /silo/silos/{id}/details`, `POST /silo/silos/{id}/lots`, `POST /silo/silos/{id}/lots/{lot_id}/movements` |
| Partiepflicht Waage | `waage.py`, `charges.py` | Validierungsregel fehlt — kein dedizierter Constraint-Endpunkt |
| Silo-Leermeldung | `silo.py`, `silo_operations_api.py` | `GET /silo/kapazitaeten`, `POST /silo_ops/einlagern`, `POST /silo_ops/auslagern`, `GET /silo_ops/bestand/{tenant_id}` — Leermeldung fehlt |
| DATEV/FIBU | `fibu_connectors.py` | `GET/POST /fibu-connectors/profiles`, `POST /fibu-connectors/{type}/imports`, `POST /fibu-connectors/imports/{run_id}/validate`, `POST /fibu-connectors/imports/{run_id}/post` |
| Bank/e-Clearing | `bank_statement_import.py`, `bank_reconciliation.py` | `POST /bank-statements/import`, `GET /bank-statements/{id}/lines` |
| Kasse/DSFinV-K | `pos_dsfinvk.py`, `admin_pos.py` | `GET /pos/dsfinvk/export`, `GET /pos/dsfinvk/status` |
| UX | — (Frontend-Baukasten) | ObjectPage / ListReport / Wizard in `packages/frontend-web/src/components/mask-builder/` |

---

## Top-10 Gap-Liste

| Gap-ID | Beschreibung | Prioritaet | Owner-Domain | Abnahmekriterium |
|--------|--------------|------------|--------------|------------------|
| AMIC-PARITY-001 | Vollstaendige Browser-/CRUD-Abnahme der O2C/P2P-Folgeobjektkette von Annahme bis FIBU-Buchung fehlt als UAT-Pfad | P0 | Agrar / Supply / Finance | Repo-seitig vorbereitet: `/uat/o2c/readiness` und 7-Schritt-Szenario-Runner decken O2C/P2P/Partie-Kette ab; externe Browser-UAT-Unterschrift bleibt Gate |
| WAAGE-LIVE-001 | Live-Hardware-/Dateiimport (ASCII-Waagenformat), Eich-/Kalibrierungsnachweise und Offline-Fehlerqueue nicht produktiv abgenommen | P0 | Agrar / Waage | Realgeraet oder ASCII-Datei-Import-Test gruen; Fehlerqueue-Roundtrip dokumentiert |
| SILO-LEER-001 | Leermeldung-Endpunkt, Schwundbuchung, Fehlermatrix und Waagenbeleg-Kopplung fehlen vollstaendig | P0 | Agrar / Lager | `POST /silo/silos/{id}/leermeldung` + Schwundbuchung + 3 Fehler-Szenario-Tests gruen |
| PARTIE-PFLICHT-001 | Harte Validierungsregel "Artikel/Wiegetyp verlangt Partie" fehlt zentral im Backend | P1 | Agrar / Waage | Backend-Constraint wirft 422 bei Wiegung ohne Charge wenn Artikelstamm Partiepflicht traegt |
| ROHWARE-SCHEMA-001 | Schema-Editor/Katalog mit Versionierung, Gueltigkeit und Testrechnung fehlt; keine maschinenlesbare API | P1 | Agrar / Settlement | `GET/POST/PUT /agrar/settlement-schemas` mit Versionshistorie; Testrechnung-Preview-Endpunkt gruen |
| CTS-H2S-UAT-001 | UAT gegen echte Rohwaren-Schemata, regionale Varianten und Abrechnungsnachtraege nicht durchgefuehrt | P0 | Agrar / QA | UAT-Protokoll fuer mind. 3 Rohwarengruppen (Getreide, Oelfruechte, Leguminosen) unterschrieben |
| FIBU-CUTOVER-002 | Extern freigegebenes SKR03/SKR04-Mapping und Steuerberaterabnahme fehlen (EXT-002) | P0 | Finance / Extern | `fibu_cutover_mapping.yaml` gegen Template validiert + Steuerberater-Freigabe-Dokument vorhanden |
| DMS-DOC-002 | DMS-Live-Probe, Redirect-Failure-Cases und Audit-Paket-Vollstaendigkeit nicht abgenommen | P1 | Finance / DMS | `check_integration_bootstrap.py --strict-live` liefert `ready` fuer DMS-Probe; Audit-Paket-Export gruen |
| POS-DSFINVK-001 | Produktive TSE-Abnahme und reales DSFinV-K-Exportpaket mit Pruefwerkzeug-Validierung fehlen | P1 | POS / Finance | DSFinV-K-Export mit DFKA-Taxonomie-Validator gruen; TSE-Signatur-Nachweis vorhanden |
| REPORT-PRINT-001 | Partie-Genealogie-Report, Wiegschein-Druck und Etiketten-Ausgabe nicht produktiv abgenommen | P1 | Agrar / Lager | Druckpfad Partie-Report + Wiegschein-PDF + Etikett-Layout laufen in Staging-Umgebung gruen |

---

## Umsetzungsplan (6 Phasen)

### Phase 1 — Rohware-UAT-Fundament (Woche 1–2)
**Ziel:** CTS-H2S-UAT-001 + AMIC-PARITY-001 (Rohware-Kette — Agrar-Spezialsoftware-Parität)

- UAT-Testdaten fuer mind. 3 Rohwarengruppen (Getreide, Oelfruechte, Leguminosen) anlegen
- Playwright-Pfad: Annahme → Qualitaetsprotokoll → Settlement-Preview → Settlement-Post → FIBU-Buchung
- Regionale Varianten-Tests: NRW (Rueben), BY (Braugerste) je 1 Szenario
- Abnahmeprotokoll mit Landhandel-Fachanwender unterschreiben

### Phase 2 — Silo-Leermeldung + Partiepflicht (Woche 2–3)
**Ziel:** SILO-LEER-001 + PARTIE-PFLICHT-001

- `POST /silo/silos/{id}/leermeldung` implementieren inkl. Schwundbuchungs-Logik
- Fehlermatrix (Silo nicht leer, Silo gesperrt, Waagenbeleg fehlt) als Backend-422-Responses
- Validierungsregel "Partiepflicht je Artikel/Wiegetyp" im Wiegungs-Endpunkt zentralisieren
- Unit-Tests + API-Tests fuer beide Gaps

### Phase 3 — Waage Live + Offline-Queue (Woche 3–4)
**Ziel:** WAAGE-LIVE-001

- ASCII-Waagenformat-Parser gegen reale Testdatei (min. 3 Satzarten) abnahmen
- Eich-/Kalibrierungsnachweis-Feld im Waagen-Stamm erganzen
- Offline-Fehlerqueue (Redis-backed) fuer Verbindungsabbrueche implementieren und testen
- Hardware-Integration-Test-Protokoll erstellen

### Phase 4 — Schema-Editor + Waagenvorlagen (Woche 4–5)
**Ziel:** ROHWARE-SCHEMA-001 + Waagenvorlagen-Gap

- `GET/POST/PUT /agrar/settlement-schemas` mit Versionshistorie und Gueltigkeit-Feld
- Testrechnung-Preview-Endpunkt (`POST /agrar/settlement-schemas/{id}/testrechnung`)
- Waagenvorlage-Endpunkte (`GET/POST /waagen/vorlagen`) fuer Wiederholfall-Anlieferungen
- Schema-Editor-UI als ListReport + ObjectPage im Frontend

### Phase 5 — FIBU-Cutover + DMS-Live-Probe (Woche 5–6)
**Ziel:** FIBU-CUTOVER-002 + DMS-DOC-002

- `config/fibu_cutover_mapping.yaml` mit Steuerberater abstimmen und gegen Template validieren
- `check_fibu_cutover_mapping.py --strict` in CI aufnehmen
- DMS-Live-Probe: `check_integration_bootstrap.py --strict-live` fuer DMS-Probe auf `ready` bringen
- Redirect-Failure-Cases und Audit-Paket-Export testen

### Phase 6 — POS/TSE-Abnahme + Report/Druck (Woche 6–7)
**Ziel:** POS-DSFINVK-001 + REPORT-PRINT-001

- DSFinV-K-Export gegen DFKA-Taxonomie-Validator (Offline-Tool) validieren
- TSE-Signatur-Nachweis in Staging-Umgebung produzieren
- Partie-Genealogie-Report, Wiegschein-PDF und Etikett-Layout in Staging abnahmen
- Druckpfade in CI-Smoke aufnehmen (PDF-Render-Smoke, keine Inhalts-Pruefung)
