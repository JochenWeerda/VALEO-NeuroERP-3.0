---
title: Physischer Tabellenkatalog mit korrekten zusammengesetzten Fremdschluesseln
type: qa
audience: [entwickler, qa, agent]
owner: Codex-01a0f3fc
status: active
last_reviewed: 2026-10-08
version: 1.0.0
---

# Zusammengesetzte Fremdschluessel im Tabellenkatalog

## Bestaetigter Fehler

Die bisherige Ernte verbindet Quellspalten ueber den Constraintnamen mit
saemtlichen Zielspalten. Bei zusammengesetzten Schluesseln entsteht ein
Kreuzprodukt: eine Konto-ID zeigt angeblich auch auf eine Mandanten-ID.
Ausserdem sind wiederverwendete Constraintnamen keine eindeutige Identitaet.

Realer lesender Vergleich auf der bestehenden `valeo_probe`, Revision
`postfach_microsoft_20261008`: bisher 542 Beziehungen, tatsaechlich 534.
Acht zusaetzliche, nicht existente Paare betreffen vier zusammengesetzte
Schluessel: Bankkonto zum Sachkonto, Bewerbungseinwilligung zur Erklaerung,
HR-Gate-Nachweise und HR-Gate-Probes jeweils zum Gate.

## Reparatur und Abnahme

Der Generator liest die echte Constraint-Identitaet aus `pg_constraint`.
Die Arrays `conkey` und `confkey` werden positionsgleich gepaart. Tabellen
und Spalten werden ueber ihre PostgreSQL-Identitaeten zugeordnet; die
vollstaendige Sortierung umfasst Quelle, Ziel, Constraint und Position.
Keine Datenbankbedingung oder fachliche Beziehung wurde veraendert.

Vier reale lesende Regressionen scheitern mit dem urspruenglichen Query
(4 Fehler in 15,48 Sekunden) und bestehen mit der Reparatur.
Zusammen mit den vorhandenen Katalog-/Lineage-/Aktionsvertraegen:
24 Tests bestanden in 5,05 Sekunden; ein separater Consent-Integrationstest
wurde in diesem isolierten Aufruf nicht ausgefuehrt. Dessen bisheriger
lesender Nachweis steht in `ci-catalog-sync-20261008.md`.

Die neuen Datenbanktests sind explizit `needs_live_db` markiert, verwenden
die bereits konfigurierte Datenbank und eine lesende Transaktion. Fehlt die
Konfiguration oder ein migrierter Schluessel, scheitern sie verbindlich.
Keine neue Datenbank, kein Docker-Container und keine Testdatenanlage.

Katalogregenerierung und beide Kataloggeneratoren mit `--check` bestanden.
Tabellenbestand unveraendert: 661, keine Tabelle hinzugefuegt oder entfernt.
Exakt die vier genannten Tabellen unterscheiden sich und ausschliesslich
im Feld `foreign_keys`. Fremde Arbeitsfassungen wurden nicht ersetzt.

## Noch offene frische Schemaabnahme

Die autorisierte GitHub-Diagnose ist aktiviert; Lauf37822738063 wartet auf
einen Runner. Das bestehende rote Gate wird nicht abgeschwaecht. Das lokale
Ergebnis ist kein Beleg fuer einen gruenen GitHub-Lauf.

Ein weiterer moeglicher Unterschied ist sichtbar im Initialisierungsweg:
`scripts/init_db.py` fuehrt nach Alembic noch additive ORM-Tabellenanlage aus,
waehrend der gemeinsame Pruefstand seine Migrationsrevision meldet. Die
Revision allein beweist daher keine identische physische Tabellenmenge.
Ohne frische Ernte wird weder eine zusaetzliche Tabelle angenommen noch
eine fremde gemeinsame Datenbank zur Angleichung veraendert.

Nachweis der frischen Ernte: Quality Gate37825542282 auf 3f3927045 liefert
670 Tabellen. Alle bisherigen 661 Definitionen einschliesslich der
reparierten zusammengesetzten Fremdschluessel stimmen exakt ueberein.
Neun zuvor lesend identifizierte additive ORM-Tabellen werden separat im
CI-Katalog-Sync integriert; siehe ci-catalog-sync-20261008.md. Der gemeinsame
Pruefstand wurde nicht veraendert.
