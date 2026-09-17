---
title: Arbeitsliste Datenmodell-Katalog
type: reference
audience: [agent, entwickler, architect]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-17
version: 1.0.0
description: Phasenplan fuer Tabellenkatalog, Besitz, Lineage und Masken-Lebenszyklus — gemessen gegen Best Practice, nicht gegen ein Gesamt-UML.
---

# Arbeitsliste: Datenmodell-Ueberblick

Anlass: Masken aendern sich, Tabellen bleiben, und niemand sieht Besitz und
Verbraucher in einem Artefakt. `domain_crm.crm_consents` hatte zwei Fachmodelle
unter einem Namen, weil die physische Tabelle, der schreibende Code und die
Maske nicht aneinanderhingen. UML allein haette das nicht verhindert.

**Leitlinie:** Canonical-UML fuer Aggregate. Generierter Katalog fuer Spalten.
Maske ist eine Sicht, kein Lebensrecht ueber die Tabelle.

## Was andere Schmieden tun

| Wer / Werkzeug | Was es wirklich haelt | Was wir uebernehmen | Was wir lassen |
|---|---|---|---|
| SAP Data Dictionary / CDS | Das laufende System ist die Wahrheit; Sichten werden daraus abgeleitet, nicht aus Visio | Katalog aus der Datenbank nach `alembic upgrade head` | Kein SE11 nachbauen |
| Odoo `ir.model` | Reflexion der geladenen Modelle; Spalte loeschen nur explizit (`remove_field`, `drop_column`) | Maske/View weg ≠ Spalte weg | Kein zweites Metadaten-ORM neben SQLAlchemy |
| Data Catalogs 2026 (Collibra, Alation, Atlan, OpenMetadata, DataHub) | Aktiver Katalog: Schema ernten, Owner, Lineage, Glossary | Reihenfolge Ernten → Besitz → Lineage | Keine Plattform in Welle 1 (Betrieb, Identitaet, Connectoren) |
| tbls | Ein Binary, Markdown/JSON/Mermaid aus Postgres, `tbls diff` in CI | Spaeter optional als ERD-Artefakt | Nicht als erste Abhaengigkeit (Go-Binary neben Python-Generatoren) |
| SchemaSpy | Klickbares HTML-ERD aus JDBC | Idee „Diagramm aus der DB, nicht von Hand" | Java + Graphviz nicht in den bestehenden Docs-Generator zwingen |
| dbt / Warehouse-Lineage | Spaltenlinie in der Analytics-Schicht | Nur die Metapher Impact Analysis | dbt ist kein OLTP-ERP-Modell |
| Postgres `COMMENT ON` | Data Dictionary in `pg_description`, sichtbar in `\d` und Generatoren | Kommentare in neuen Migrationen | Kein nachtraegliches Kommentar-Projekt fuer alle Alt-Tabellen in Welle 1 |
| Hand-UML der ganzen DB | Frueher ueblich, driftet | Canonical Core (ADR-003) bleibt klein | Kein Klassendiagramm aller Tabellen |

Gemeinsamer Nenner der Best Practice: **aktive Metadaten** (Schema aendert sich
→ Katalog aendert sich in CI) statt eines gepflegten Gesamtbildes. Rollen
getrennt: fachlicher Owner (Domäne), technischer Custodian (Schema/Migration),
Verbraucher (API/Maske).

## Schichten (bleiben getrennt)

```
Canonical Model (ADR-003, ERD, UML-Klassen)
  → fachliche Aggregate und Belegkette, selten

Physisches Schema (Alembic + information_schema)
  → Tabellen, Spalten, FK, Schema-Besitz

Vertrag (OpenAPI, ScreenDefinition, Studio-Katalog)
  → was Masken und Agenten lesen duerfen

Verbraucher-Lineage
  → Tabelle → Endpunkt → ScreenDefinition / Frontend-Aufruf
```

Eine Maske loeschen aendert Schicht 3. Spalten leben in Schicht 2, bis eine
Migration sie mit Nachweis streicht (GoBD, Belegkette, noch lesender Code).

## Phasen

Status je Zeile: `offen` / `in arbeit` / `erledigt`. Nicht parallelisieren,
was dieselbe Datei braucht; Lineage braucht den Katalog.

### P0 — Regel festschreiben — erledigt 2026-09-17

Die Lebenszyklus-Regel steht, bevor der Generator existiert.

- [x] Abschnitt in `docs/entwickler/datenmodell-tenancy.md`: Schichten,
      Maske ≠ Drop, neue Spalte nur per Alembic
- [x] Zeile im Viewpoint-Katalog: „Wem gehoert welche Tabelle?"
- [x] Verweis von ADR-003 Consequences auf den Katalog (logisch ≠ physisch)

**Abnahme:** Ein Agent findet die Regel in unter zwei Klicks von
`docs/architecture/views/viewpoint-catalog.md` oder
`docs/entwickler/datenmodell-tenancy.md`.

### P1 — Physischen Katalog ernten — erledigt 2026-09-17

Wie SAP-DD und tbls: nach Migration die Datenbank lesen, das Ergebnis
versionieren, Drift in CI.

- [x] Generator `scripts/generate_table_catalog.py` gegen `information_schema`
      (Schemas `domain_*`), Output `docs/admin/table-catalog.md` + JSON
- [x] `--check` wie `generate_openapi.py` / `generate_code_inventories.py`
- [x] Lauf nach `alembic upgrade head` im Quality-Gate (nicht im Doc-Meta-Check ohne DB)
- [x] Namenskollisionen sichtbar: Geschwister `crm_consents` /
      `crm_contact_consents`; gleicher Name in mehreren Schemas

**Abnahme:** `python scripts/generate_table_catalog.py --check` Exit 0.
Stand der Ernte: 29 Schemas, 635 Tabellen, 8368 Spalten. `crm_consents`
(partner_id) und `crm_contact_consents` (contact_id) getrennt.

**Nicht in P1:** Bedeutungen aller Spalten, ERD aller Relationen, OpenMetadata.

### P2 — Besitz vollstaendig — erledigt 2026-09-17

Heute wies der Check nur Anker und fuenf Praefixe. Jetzt hat jede
`domain_*`-Tabelle einen Schema-Custodian und eine Architecture-Domain.

- [x] `scripts/table_ownership.py`: 29 Schemas → Domain (only-up: unbekanntes Schema faellt)
- [x] Praefix-Konflikt ohne Legacy-Zeile faellt; 13 benannte Legacy-Lagen
- [x] Katalog nennt `owner_domain` und `placement` (native / prefix / legacy)
- [x] Architecture Index `database_schemas` listet die physischen Schemas je Domain

**Abnahme:** `check_domain_table_ownership.py` — 635 Tabellen, 29 Schemas, 13
Legacy. `sales_orders` in `domain_crm` und Kontrakte in `domain_inventory`
bleiben begruendet.

### P3 — Verbraucher-Lineage — erledigt 2026-09-17

Catalogs 2026: ohne Lineage ist Impact Analysis Ratei. Erntet wird
Tabelle → Code unter `app/` → native ScreenDefinition, nicht Spalte durch dbt.

- [x] Katalog-Felder `written_by` / `read_by` / `screens` aus SQL, ORM
      `__tablename__` und ScreenDefinition-`dataSources` (Router-Praefix oder
      optionales Feld `table`)
- [x] Gate: `dataSources.entity.table` muss im Katalog stehen (`--check` und Test)
- [x] Verbraucher-Suche vor Maskenumbau: Abschnitt Verbraucher im Katalog;
      Spalten-Drop bleibt eine eigene Migration

**Abnahme:** `crm_consents` listet `app/crm/router.py`; `crm_contact_consents`
listet `app/api/v1/endpoints/crm_consents.py`. Native Entity mit unbekanntem
`table`-Feld faellt.

### P4 — Feldvertrag Maske ↔ JSON — erledigt 2026-09-17

Der Adresszaehler ist 0 und prueft keine Spalten. Claude hat das Gate gebaut
(`check_field_contracts.py`, 0 Abweichungen). Die 13 blinden Bruecken-Koepfe
waren `extra="allow"` ohne Felder.

- [x] Native Kopffelder gegen deklarierte Antwortschluessel (Bruecken zuerst)
- [x] Gate only-up: Abweichungen = 0, ungetypt darf sinken nicht steigen
- [x] Studio-Katalog bleibt Allowlist von Endpunkten, nicht von Tabellen

**Abnahme:** 12 Bruecken-Masken aus Abschnitt B haben ein Antwortmodell mit
Kopffeldern. `sales/invoice` hat Claude parallel typisiert — ungetypt = 0.

### P5 — Canonical UML pflegen, nicht ausweiten — erledigt 2026-09-17 (dauerhaft)

Review gegen ADR-003 (Accepted 2026-03-11): kein neues Kernaggregat. Katalog,
Consent-Geschwister und Rechnungs-Feldvertrag sind physisch bzw. Vertrag,
keine neuen Aggregate. `last_reviewed` auf 2026-09-17 gezogen.

- [x] `docs/architecture/views/erd-canonical-domain.md` und
      `uml-canonical-domain-class.md` nur bei neuem ADR-003-Aggregat
      (`last_reviewed` ziehen)
- [x] Kein Ticket „alle Tabellen ins classDiagram"
- [x] Belegkette bleibt `docs/MASKEN.md` (Layout) plus Canonical-ERD (Objekte)

**Abnahme:** Review-Datum 2026-09-17, juenger als die letzte Aggregat-Entscheidung
(2026-03-11). Permission stand im ERD, fehlte im classDiagram — nachgezogen,
kein neues Aggregat. PSM/Duenger/Saatgut-Anwendung bleibt Item auf Field;
physische Tabellen im Katalog. Gate: `tests/test_canonical_domain_views.py`
(Klassenzahl begrenzt, Katalog nicht im Mermaid).

Naechster UML-Claim nur, wenn ADR-003 ein Aggregat erhaelt. P6 nicht starten.

### P6 — Optional nach P1–P3 — nicht starten

- tbls auf die JSON aus P1 oder direkt auf Postgres, Artefakt in CI, nicht
  Ersatz fuer den Python-`--check`
- `COMMENT ON` in **neuen** Migrationen (Owner, Fachbedeutung, Einheit)
- OpenMetadata/DataHub erst, wenn mehrere Speicher (Warehouse, NATS, DMS)
  dieselbe Governance brauchen — heute reicht Postgres + Git

## Reihenfolge (nicht umdrehen)

```
P0 Regel  →  P1 Ernten  →  P2 Besitz  →  P3 Lineage  →  P4 Feldvertrag
                 └─ P5 Canonical UML parallel, ohne den Katalog zu ersetzen
```

P4 ohne P1 ist wieder Blick in die Antwort per Hand. P2 ohne P1 inventiert
Owner an Tabellen, die der Check nicht sieht.

## Nicht tun

- Maske loeschen und `DROP COLUMN` in dieselbe Änderung packen
- Collibra/Alation/OpenMetadata als ersten Slice
- SchemaSpy-Java in den MkDocs-Build
- MagicMock-Katalog ohne echte `information_schema`
- `lager/leitstand` als Begruendung, Tabellen anzulegen, solange die Fachfrage offen ist

## Einstieg fuer den naechsten Slice

Datei: `docs/agent-ops/slices/DATA-MODEL-CATALOG-20260917.yaml` — P0–P5 geliefert.
Naechster Claim: keiner aus dieser Liste. P5 ist dauerhaft: UML nur bei neuem
ADR-003-Aggregat anfassen. **P6 nicht starten** (tbls / COMMENT ON / OpenMetadata).
Alembic-Head zum Zeitpunkt der Liste: `crm_kreditlimite_20260917`.
