---
title: Kanonische Budget- und Rohware-Schemata
owner: Codex
type: reference
status: in Arbeit
last_reviewed: 2026-11-15
---

# Fehlende Tabellen und Routen

## Verbindliche Modellentscheidung

Budgetplaene und Budgetpositionen werden als domain_finance.budget_plans und
budget_lines eingefuehrt. Die Position referenziert mandantengleich ihren Plan,
das fuehrende Journal-Konto aus domain_erp.chart_of_accounts sowie optional die
Kostenstelle aus domain_finance.kostenstellen. Neue Konten- oder Kostenstellen-
Parallelmodelle entstehen nicht. Referenzen muessen auch bei nachtraeglichen
Aenderungen an den Datenbankgrenzen mandantengleich bleiben.

Rohware verwendet weiter domain_shared.rohware_abrechnungsschemata. Die alte,
nie migrierte Tabellenannahme rohware_schemata wird nicht als zweiter Katalog
nachgebaut. Schema-Code entspricht schema_nr, Name der bezeichnung; die Gruppe
wird ueber die vorhandene tenantgebundene Rohwarengruppe aufgeloest. Gueltigkeit,
Versionsfeld und Bearbeitungsstatus ergaenzen diesen Stamm. Formelpositionen
liegen in domain_shared.rohware_schema_lines mit zusammengesetztem Eltern-FK.
Vorhandene Qualitaetsdefinitionen und Zu-/Abschlagstaffeln bleiben erhalten.

Der gemeinsame Rohware-Schemadienst validiert beide API-Zugaenge. Der bisherige
Gruppenweg legt wie bisher ein aktives Schema an, jetzt ausdruecklich mit
heutigem Gueltigkeitsbeginn; der Editor legt einen Entwurf an. Status und aktiv
bleiben widerspruchsfrei. Ungueltige vorhandene Fremdverweise werden nicht
stillschweigend geloescht. Die Migration muss in diesem Fall abbrechen.

## Eingaben, Rollen und Routen

Beide Rohware-Router verwenden den geprueften Mandantenkontext. Header oder
Payload sind keine Autoritaet fuer den Mandanten. Fremde Eltern/Positionen
werden vor einer Mutation abgewiesen; Datenbankfehler liefern keine SQL-Details.
Die bestehende Lager-Schreibrolle bleibt erhalten. Budgetanlage und -aenderung
bleiben beim Finanzschreibrecht, die Genehmigung beim Finanzadministrationsrecht.
Neue Plaene starten ausschliesslich im Entwurf; die Eingabespezifikation drueckt
das ebenfalls aus. Ein initial genehmigter Plan kann die Pruefung nicht umgehen.
Nicht verfuegbare Istwerte werden nicht als Nullverbrauch ausgegeben.

GET /api/v1/rohware/gruppen/{gruppe_id}/schemata ergaenzt den tatsaechlich vom
bestehenden Client aufgerufenen Gruppen-Leseweg. Er benutzt den vorhandenen
Katalog statt eigener Daten. Fuer Budgets wird ohne Verbraucherbeleg kein
zweiter Positions-Leseweg erfunden; das Detail liefert seine Positionen bereits.
Die Budgetliste ist begrenzt und meldet die gesamte tenantbezogene Trefferzahl.

## Migration und Nachweis

Die Kette baut auf dem bereits gemergten altrechnungen_schutz_20261110 auf:
budget_planning_schema_20261115 -> rohware_schema_canonical_20261115.
Neue Tabellen erhalten sofort RLS und passende Indizes. Die Ruecknahme entfernt
nur die eigenen Ergaenzungen; neue Budget-/Formeldaten gingen dabei verloren,
weshalb eine geplante Ruecknahme eine Sicherung voraussetzt.

Zunaechst liegen isolierte Eingabe-/HTTP-/Handler-Nachweise vor. Beide neuen
PostgreSQL-Vertraege werden durch require_db tatsaechlich vom bestehenden
Strict-DB-Job ausgewaehlt. Dieser Job verwendet seine bestehende einzelne
Datenbank, exportiert nach erfolgreicher Pruefung die physischen Inventare und
erzeugt keine zusaetzliche Datenbank oder Dockerinstanz. Lokaler Pruefstand:
Metadatenzugriff auf alembic_version verweigert; keine Rechte geaendert und keine
DDL ausgefuehrt. Eine echte Schema-/RLS-Abnahme wird erst nach erfolgreichem
PostgreSQL-Lauf ausgewiesen. Keine neue MCP-Freischaltung oder Kanalabnahme wird
aus Unit-Tests abgeleitet. Die veroeffentlichte Studio-Definition und die
unveraenderliche Historie produktiver Belege sind hiervon zu unterscheiden.
