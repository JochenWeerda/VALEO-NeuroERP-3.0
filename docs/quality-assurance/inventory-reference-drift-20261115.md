---
title: Begrenzte Reparatur zweier bestehender Inventory-Referenzen
type: reference
audience: [entwickler, agent, betrieb, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-15
---

# Inventory-Referenzdrift

## Befund und Entscheidung

Claim `INVENTORY-AISLE-DRIFT-20261115`, Erweiterung `0ee53cce1`: Die gewachsene
lokale Datenbank `valeo_neuro_erp` steht auf
`runtime_ddl_to_migrations_20261026`. Laut lesender Katalogpruefung des Leads
fehlen zwei bereits in Vorgaengermigrationen definierte Referenzspalten:

| Referenz | Kanonischer Vorgaenger | Wiederherzustellender Vertrag |
|---|---|---|
| `domain_inventory.warehouse_bins.aisle_id` | `wms_warehouse_aisles_20260612` | nullable `VARCHAR(36)`, `fk_wb_aisle` auf `warehouse_aisles(id)`, `idx_wb_aisle` |
| `domain_inventory.lkw_annahme_queue.article_id` | `lkw_annahme_queue_article_reference_20260328` | nullable `VARCHAR` ohne Laenge, `fk_lkw_annahme_queue_article_id` auf `articles(id)` mit `ON DELETE SET NULL`, `ix_lkw_annahme_queue_article_id` |

Das ist Fall (b) aus `scripts/check_schema_drift.py`: bestehende lokale
Schemaabweichung, keine fehlende kanonische Migration. Bestehende Migrationen
bleiben unveraendert. Eine Head-Reparatur waere hinter der scheiternden
Inventory-RLS-Migration unerreichbar. Das neue explizite Betriebswerkzeug
`scripts/repair_inventory_reference_drift.py` stellt ausschliesslich diese
beiden Vertraege wieder her. Es fuehrt weder Alembic noch eine Revisionstempelung
aus und ist kein Bestandteil des Anwendungsstarts.

Die ebenfalls noch fehlende Spalte
`domain_sales.delivery_note_positions.tenant_id` ist am beobachteten
Ausgangsstand **erwartet**: `rls_domain_sales_20261027` fuegt sie vor CRM und
Inventory hinzu und fuellt sie aus dem Elternbeleg. Sie gehoert nicht zur
Reparatur. Weitere lokale Schemaabweichungen sind mit diesem Werkzeug nicht
abgenommen oder automatisch behoben.

## Begrenzung und Erhaltung

- Standard ist ein Plan in einer explizit lesenden, anschliessend
  zurueckgerollten Transaktion. Kein DDL und keine implizite Anwendung.
- Datenbank und einzelne Alembic-Revision muessen ausdruecklich erwartet und
  tatsaechlich identisch sein; die Repository-DAG muss beide kanonischen
  Vorgaenger enthalten. Zugelassen sind nur die vorhandenen lokalen Namen
  `valeo_neuro_erp` und `valeo_probe`, lokale Hostnamen auf Port 5432; die URL
  kommt ausschliesslich aus einer benannten Umgebungsvariable. Zieluebersteuernde
  URL-Queryparameter sind gesperrt.
- `--anwenden` verlangt tatsaechlich `session_user=valeo_migrator` und
  `current_user=valeo_owner`, ohne Superuser-/BYPASSRLS-Flags am Login. Das
  Werkzeug setzt keine Rollen, Eigentumsrechte, Kennwoerter oder Grants.
- Alle vier Tabellen muessen normale, `valeo_owner` gehoerende Tabellen mit
  passendem Primaerschluessel und den belegten exakten ID-/Mandantentypen sein.
  Bei Bins/Gaengen werden auch Zone und Lager geprueft. Widerspruechliche
  vorhandene Spalten, benannte Indizes oder Referenzbedingungen blockieren.
- Beide Referenzen werden in derselben Transaktion bearbeitet. Vor jedem DDL
  sind alle Voraussetzungen geprueft. Ein fehlender zweiter Vertrag darf keinen
  Teilabschluss des ersten verursachen.
- Bestehende kanonische Referenzen werden idempotent erkannt. Nach der
  Inventory-RLS-Revision werden ausschliesslich die bereits entwickelten
  validierten Mandanten-Verbund-FKs akzeptiert, einschliesslich
  `SET NULL (article_id)` fuer die Queue. Sie werden nie zu einfachen FKs
  zurueckgebaut. Fehlende Spalten oder fehlende Verbund-FKs nach RLS blockieren.
- `application_name=agent:codex-inventory-reference-drift`; Verbindungsaufbau
  maximal 5s, Tabellenlocks maximal 5s, jede Anweisung maximal 30s. Anwendung
  sperrt die vier betroffenen Tabellen und prueft den Revisionsstand erneut.
- Nur `ADD COLUMN`, `ADD CONSTRAINT`, `CREATE INDEX` auf den beiden festen
  Referenzen; keine Fach-DML, keine Zuordnung oder Datenloeschung. Vorhandene
  Spalten/Schluessel, Eigentum, RLS-Flags, Policies und Zeilenzahlen werden nach
  der Ausfuehrung erneut verglichen. Abweichungen rollen die Transaktion zurueck.
  Ein kompletter Inhaltsvergleich aller Geschaeftszeilen wird nicht behauptet.
- `--anwenden --rollback` fuehrt denselben Reparatur- und Nachpruefungsweg aus
  und rollt ihn ausdruecklich zurueck. Der Betriebsanwender muss ein
  abgestimmtes Wartungsfenster herstellen; das Werkzeug beendet keine Sitzung
  und stoppt keinen Dienst.
- Fehlerausgaben enthalten keine SQL-Treiberexception, Verbindungs-URL,
  Zugangsdaten oder Geschaeftswerte. Ein fehlgeschlagener Commit bzw.
  Verbindungsabbruch erfordert eine erneute lesende Katalogpruefung.

## Bedienung

Beispiel fuer den belegten Ausgangsstand; eine andere tatsaechliche Revision
erfordert einen erneut geprueften ausdruecklichen Erwartungswert:

```powershell
python scripts/repair_inventory_reference_drift.py --expected-database valeo_neuro_erp --expected-revision runtime_ddl_to_migrations_20261026 --url-env MIGRATION_DATABASE_URL
python scripts/repair_inventory_reference_drift.py --expected-database valeo_neuro_erp --expected-revision runtime_ddl_to_migrations_20261026 --url-env MIGRATION_DATABASE_URL --anwenden --rollback
```

Eine dauerhafte Anwendung ist derselbe Aufruf mit `--anwenden` ohne
`--rollback`, erst nach konkreter operativer Freigabe und erfolgreicher
Katalog-/Rollbackpruefung durch den Lead. Danach wird der regulaere kanonische
Alembic-Pfad separat ausgefuehrt. `valeo_probe` wird weder neu angelegt noch
zurueckgesetzt. Ein gewachsener Entwicklungsstand wird nicht als Testdatenbank
fuer Fachtests verwendet.

## Lokale Abnahme und offene Betriebsgates

`tests/test_repair_inventory_reference_drift.py` prueft den reinen Planer,
inkompatible Typ-/Schluessel-/Indexformen, Teilbestaende, idempotente bestehende
und weiterentwickelte Verbund-FKs, Ziel-/Revisions-/Rollengrenzen,
Transaktionsabschluss und atomaren Rollback bei DDL- oder Nachpruefungsfehlern.
Die Verbindungsgrenze wird vor einem Verbindungsaufbau auf externe und per
Queryparameter ueberschriebene Ziele geprueft. Saemtliche SQL-Ausfuehrungen in
diesen Tests sind isolierte Testdoubles, keine Datenbanksitzungen.

Finaler Lauf: **53 Tests bestanden**, 50,21s, Exit 0, mit
`python -m pytest tests/test_repair_inventory_reference_drift.py -q --no-cov`.
Ein vorhandener Starlette/httpx-Deprecationhinweis und ein
pyreadline-Konsolen-Finalizerhinweis erschienen ausserhalb der Testergebnisse;
keine fehlgeschlagenen oder uebersprungenen Faelle.

Der implementierende Subagent hat keine DB-/Dockeraktionen, Commits oder Pushes
ausgefuehrt. Die anschliessenden Operationsnachweise des Leads stehen im
folgenden Abschnitt. Die bestehenden RLS-Fachtests bleiben verbindlich und
werden nicht durch Planer-Unit-Tests ersetzt.

## Lead-Operationsnachweis

Der lesende Plan gegen die gewachsene lokale Datenbank auf
`runtime_ddl_to_migrations_20261026` ergab genau sechs DDL-Anweisungen.
Im begrenzten Wartungsfenster wurde nur der bereits abstuerzende Backendcontainer
angehalten. Eine lokale Schema-Sicherung der vier Tabellen umfasst 32.830 Bytes.
Der echte Probelauf als `valeo_migrator` mit aktiver Rolle `valeo_owner` wurde
vollstaendig zurueckgerollt: Katalog, vier vollstaendige Zeilenhashes und Revision
waren danach identisch. Anschliessend wurden genau diese sechs DDL-Anweisungen
dauerhaft angewendet. Alle Bestandszeilenhashes blieben identisch; der erneute
Plan enthielt keine Aenderung. Rechte, Eigentum und RLS blieben unveraendert.

Die unveraenderte Sicherheitsmigration erkannte danach alte Testdatenkonflikte:

- Zwei verwaiste `article_batches`-Zeilen des Alt-Testmandanten `valeo` besassen
  weder Artikel- noch Lagereltern. Eingehende Fremdschluessel existierten nicht;
  sieben moegliche Batch-ID-Referenztabellen enthielten keine Verweise.
- Zwei alte Testbestellungen im Entwicklungs-Testmandanten zeigten auf
  Lieferanten eines anderen Mandanten. Unter elf geprueften ID-Verweisspalten
  bestanden ausschliesslich drei zugehoerige Positionsverweise.

Nach jeweils eigenem Workboardclaim wurden ausschliesslich diese sieben alten
Testzeilen vollstaendig lokal gesichert und atomar entfernt: zwei Chargen,
drei Bestellpositionen und zwei Bestellkoepfe. Exakte IDs, Status, Mandant,
Revision und Referenzfreiheit wurden vor jedem Eingriff erneut geprueft.
Die Hashes aller uebrigen Bestellungen und Positionen blieben identisch.
Es gab weder erfundene Mandantenzuordnungen noch eine Lockerung von Fremdschluesseln
oder Sicherheitsmigrationen. Die Sicherungen liegen ausschliesslich im ignorierten
lokalen Verzeichnis `artifacts/inventory-reference-drift-20261115/`.

Der regulaere Backendstart ist anschliessend belegt:

- Lokaler Migrationskopf des eingebundenen Baums: `ruestlisten_tabelle_20261103`.
- 618 Tabellen haben RLS aktiviert. Beide reparierten Referenzen besitzen nach
  dem Upgrade validierte Mandanten-Verbundfremdschluessel; bei SET NULL wird nur
  `article_id` geleert, niemals die Mandantenspalte.
- Anwendung als `valeo_app`, ohne Superuser-, BYPASSRLS- oder Rollenverwaltungsrecht.
- Container gesund, keine weiteren Neustarts seit dem Start; `/health` liefert
  HTTP 200 und `/api/v1/docflow/` ohne Token HTTP 401.
- Erneuter lesender Reparaturplan am erreichten Kopf: keine Aenderung. Die
  weiterentwickelten Verbundschluessel werden nicht auf einfache FKs zurueckgebaut.

Diese Betriebsabnahme betrifft den bestehenden, noch an den alten Hauptbaum
gebundenen lokalen Container. Sie belegt keine Bereitstellung des aktuellen
Artifact-Arbeitsbaums, keine positive OIDC-/Browser-Fachkette und keinen
Vollstaendigkeitsnachweis der Datenmigration gegen den neueren GitHub-Stand.
Die 53 Unit-Tests und der echte Operations-Rollback ersetzen keine RLS-Fachtests
auf dem gemeinsamen Pruefstand. Sicherungsinhalte und Zugangsdaten werden nicht
versioniert.
