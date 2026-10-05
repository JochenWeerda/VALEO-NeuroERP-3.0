---
title: Journalanlage ueber einen zentralen Schreibweg
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-05
version: 1.0.0
---

# Kanonische Journalanlage

## Umsetzung

Repository-Create delegiert an FinanceTransactionService. Der konkurrierende
JSON-Hashhelper mit Float-Betraegen und eigener ungesperrter Sequenzvergabe
ist entfernt. Header-Tenant, Totals und frei gesetzte Stempel/Status/IDs
koennen den zentralen Betrag/Konto/Status/Stempelvertrag nicht umgehen.
Das Eingabedictionary einschliesslich Zeilen bleibt unveraendert.

Die seit Maerz migrierte currency-Spalte ist jetzt im ORM gemappt. Service-
Create erhaelt explizite Waehrung und abweichendes Buchungsdatum; ohne
Angabe gelten die vorhandenen EUR-/Belegdatum-Defaults. Storno kopiert die
Waehrung, auch explizites NULL. SQLAlchemy evaluates_none verhindert, dass
sein Standardwert fehlende historische Waehrung als EUR umdeutet.
Die Schreibpruefung verlangt drei ASCII-Grossbuchstaben; sie ist keine
ISO-Waehrungsverzeichnis- oder Wechselkursvalidierung.

Nicht speicherbare Steuer/Kostenstelle/Profitcenter/Segment-Werte werden
abgewiesen statt still verworfen. Die leeren DTO-Defaults (NULL/Steuerbetrag
0) enthalten keine Fachinformation. Unbekannte Keys werden auch bei NULL
abgewiesen. Zeilennummern muessen der fortlaufenden Reihenfolge entsprechen.
Die Serviceanlage prueft Datumstypen, Kalenderreihenfolge und Pflichttexte
vor Datenbankzugriff. Der reale Probe speichert Tage, keine Uhrzeiten.

## Verifikation

321 Tests bestanden in 17.68 Sekunden, davon 39 neue Vertraege mit fuenf
echten PostgreSQL-Faellen. EUR/USD bleiben in ORM und Response-DTO erhalten,
ebenso das vom Belegdatum abweichende Buchungsdatum. Post/Storno verwendet
die zentrale Sequenz/Spiegelzeilen und erhaelt die Waehrung. Fremdes Konto
verhindert neue Header/Zeilen. Alte explizite NULL-Waehrung wird nicht erfunden.
34 Negativfaelle pruefen vor Datenbankzugriff Header/Zeilen/Metadaten und
unveraenderten Input. Bestehende Journal-, Konto-, Betrag-, Lifecycle-, Hash-,
Posting-, CRM-, Storno-, Agrar-, Harvest- und Procurement-Vertraege bestanden.

Vor Tests wurde der vorhandene valeo_probe auf Revision
zusammenfuehrung_20261005 festgestellt. Kleine eigene Tabellenfixtures mit
gezieltem Cleanup, keine neue DB oder Dockerinstanz, kein gemeinsamer
Reset/Migrationslauf. Logs: artifacts/journal-create-tests.log.
Service/Modell/neuer Test und gesamte Journal-Repositoryklasse Ruff-sauber;
13 bestehende Befunde anderer Repositoryklassen bleiben ausserhalb des
Slices. Keine globale Lint-/CI-Gruenbehauptung.

## Handoff und offene Vertraege

Claim 72aafed8a. Bestehende Service-/Repositorygrenze, vorhandene Spalte,
keine neue Route/Domain/Schema-Migration. API/DTO nicht editiert, weil
L3-JOURNAL-SOURCE-20260910 weiterhin fremd in arbeit im Workboard steht.
Die API macht aus Domainfehlern noch HTTP 500 und hat getrennte Session,
Audit und Anchor. Response-DTO erlaubt NULL-Waehrung noch nicht; der
Widerspruch wird sichtbar statt als EUR verschleiert. Kanonisierung dieses
Vertrags und der fachlichen Zusatzfelder erfordert den API/DTO-Slice.

Schema-Lesebefund: currency VARCHAR(3) nullable DEFAULT EUR vorhanden;
entry_number VARCHAR(50), reference VARCHAR(255), description TEXT nullable,
posting_date DATE. ORM beschreibt noch 20/50/200 und DateTime. Diese
Laengen-/Null-/Datumsdifferenzen sind nicht durch diese Mappingreparatur
geloest. Vollstaendiger Hashpayload einschliesslich Zeilen/Waehrung und
persistierter Datumskanonisierung bleibt offen; keine GoBD-Gesamtabnahme.
Weitere rohe SQL-Schreiber/Consumer-Atomizitaet und Cancel-Grund offen.

User-Handshake: logistics_tours.py ist von 1033 auf 1059 Zeilen gewachsen
und bricht laut dokumentierter Meldung die Godfile-Ratsche. Datei hier nicht
editiert, Baseline nicht angehoben, kein eigener gruener Gesamtgate-Nachweis.
