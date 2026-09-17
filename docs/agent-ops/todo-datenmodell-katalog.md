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

### P2 — Besitz vollstaendig — offen

Heute prueft `scripts/check_domain_table_ownership.py` Anker und Praefixe,
nicht den Rest. Best Practice ist eine Owner-Matrix je Asset, nicht nur
Beispiele.

- [ ] Jede `domain_*`-Tabelle hat Schema-Owner oder dokumentierte Legacy-Zeile
- [ ] Unbekannte Tabellen fallen im Check durch (only-up, wie die Frontend-Ratsche)
- [ ] Architecture Index `database_schemas` bleibt die Domänen-Klammer;
      der Katalog nennt den technischen Custodian (Schema) plus fachliche
      Domain aus `architecture-domain-prefixes.yaml`

**Abnahme:** Ownership-Check ohne neue unbegruendete Ausnahmen. Bekannte
Legacy-Placements (`sales_orders` in `domain_crm`, Kontrakte in
`domain_inventory`) bleiben benannt, nicht still.

### P3 — Verbraucher-Lineage — offen

Catalogs 2026: ohne Lineage ist Impact Analysis Ratei. Fuer uns reicht
Tabelle → schreibender/lesender Endpunkt → ScreenDefinition, nicht
Spalte-durch-alle-dbt-Modelle.

- [ ] Katalog-Feld `written_by` / `read_by` aus SQL in `app/` (Roh-SQL und ORM
      `__tablename__`) und aus ScreenDefinition-`dataSources`
- [ ] Gate: ScreenDefinition-Entity darf nicht auf eine Tabelle zeigen, die
      der Katalog nicht kennt (das haette die Bruecken-Leerlese gefangen)
- [ ] Beim Loeschen oder Umbauen einer Maske: Verbraucher-Suche ist Pflicht,
      Spalten-Drop bleibt verboten ohne eigene Migration

**Abnahme:** `crm_consents` listet `app/crm/router.py`; `crm_contact_consents`
listet `app/api/v1/endpoints/crm_consents.py`. Ein Test oder `--check` fällt,
wenn eine native Entity-Quelle ohne Katalog-Treffer bleibt.

### P4 — Feldvertrag Maske ↔ JSON — offen

Der Adresszaehler ist 0. Er prueft keine Spalten. Best Practice fuer UI-Bindung
(Odoo `fields_get`, SAP CDS Consumption View): der Vertrag der Maske ist
abgeleitet, nicht parallel erfunden.

- [ ] Fuer native ScreenDefinitions: Kopffelder gegen tatsaechliche
      Response-Schluessel (zuerst Bruecken-Endpunkte, die Claude nicht
      gegen Felder gehalten hat)
- [ ] Gate darf nur wachsen (neue Ungleichheit fällt), kein Vollscan aller
      70 Masken in Iteration 1
- [ ] Studio-Katalog (`config/studio_data_sources.yaml`) bleibt Allowlist
      von Endpunkten, nicht von Tabellen

**Abnahme:** Mindestens die Bruecken-Masken aus
`docs/agent-ops/todo-frontend-backend-luecken.md` Abschnitt B haben einen
Feldvertrag oder sind als bewusstes View-Mapping dokumentiert.

### P5 — Canonical UML pflegen, nicht ausweiten — offen (dauerhaft)

- [ ] `docs/architecture/views/erd-canonical-domain.md` und
      `uml-canonical-domain-class.md` nur bei neuem ADR-003-Aggregat
      (`last_reviewed` ziehen)
- [ ] Kein Ticket „alle Tabellen ins classDiagram"
- [ ] Belegkette bleibt `docs/MASKEN.md` (Layout) plus Canonical-ERD (Objekte)

**Abnahme:** Review-Datum nicht aelter als die letzte Aggregat-Entscheidung.

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

Datei: `docs/agent-ops/slices/DATA-MODEL-CATALOG-20260917.yaml`.
Erster Claim: **P0+P1** (Regel + Generator), nicht P2–P4 gleichzeitig.
Alembic-Head zum Zeitpunkt der Liste: `crm_kreditlimite_20260917`.
