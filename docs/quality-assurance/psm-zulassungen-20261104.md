---
title: PSM-Zulassungen - Pruefstand und Grenzen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-04
version: 1.1.0
---

# PSM-Zulassungen: Pruefstand und Grenzen (04.11.2026)

Die native Liste verwendet ausschliesslich den lokalen PSM-Stamm des angemeldeten Mandanten. Artikelnummer, Name, Wirkstoff, Mitteltyp, BVL-Nummer und Ablaufdatum kommen unveraendert aus dem Stamm. Der nullable Aktivwert bleibt bei unbekanntem Wert leer. Ablauf bedeutet nicht Widerruf oder Sperre. Die Ablaufzahl vergleicht den Kalendertag in der Betriebszeitzone und umfasst alle Seiten der gefilterten Ergebnismenge.

Nutzerentscheidung 04.11.2026: „vorhandene zeilen sin nur testdaten. tabelle kann entfernt werden, wenn nicht mehr passend“. Das ersetzte Register wird nach Verbraucherpruefung auch mit Zeilen unter Tabellensperre ohne CASCADE entfernt. Weiter genutzte Tabellen sind nicht umfasst. Eine transaktionale Migrationspruefung mit belegter Tabelle und Rollback steht noch aus; Pruefungen mit gewachsener Datenbank sind nicht erfolgt.

Fuenf reine Vertragstests bestanden mit deaktiviertem Plugin-Autoload und Prozess-Exitcode 0. Auf dem gemeinsamen Pruefstand wurden nach Status- und Clientkontrolle zwei eigene PSM-Testmandanten, getrennte Leseergebnisse und Ablaufzaehlungen in einer anschliessend zurueckgerollten Transaktion geprueft. Ein Windows-pyreadline3-Destructorfehler trat nach Abschluss der reinen Tests auf. Offen sind die koordinierte transaktionale Migrationspruefung, Generatoren, Gates und visuelle Abnahme.


## Nachlauf 05.11.2026

Ein Alembic-Kopf; die vollstaendige noch ausstehende Kette wurde auf `valeo_probe` als `valeo_migrator` in einer Transaktion ausgefuehrt und vollstaendig zurueckgerollt. Ein Savepoint-Test belegte DROP der gefuellten ersetzten Tabelle und Wiederherstellung der Zeile durch Rollback. Zwei PostgreSQL-Tests bestanden: dieser Migrationstest und die SQL-Mandantenfilterung mit eigenen PSM-Zeilen. Letztere ist kein JWT- oder valeo_app-RLS-Nachweis.

Der bestehende PSM-Readvertrag bildet nullable ORM-Felder ab; `ist_aktiv` und `is_active` spiegeln denselben Wert. BVL-Felder ohne Quelle und ungueltige Ablaufdaten bleiben unbekannt. Create- und Updatevalidierung sind unveraendert. Neun reine PSM-/Parser-/Guard-/Routenvertragsfaelle bestanden (Exit 0). Der PSM-Zulassungsguard verweigert unbekannte, ungueltige und abgelaufene Daten; valide Zeitpunkte werden im Geschaeftstag verglichen. Die native Batch-11/12-Pruefung ergab 147 bestandene und einen erwarteten historischen Altlastfall; der Hook-Wrappertest bestand. Vollstaendige Frontend-Typpruefung bestanden. Browser-/visuelle Abnahme steht aus.

Maskenfeldvertrag nach Readschema-Anpassung: 5 bestanden. Der Dokumentgenerator-Gesamtcheck lief nach Schema- und Inventarnachzug erfolgreich; Pagination-, Godfile- und SQL-f-String-Gates bestanden, Doku-Drift 0. Pruefstandsrevision nach den Rollbacks unveraendert `ruestlisten_tabelle_20261103`, keine fremden aktiven Clients. Ein zunaechst versuchtes globales Batch-9-Testfixture scheiterte vor dem Test an fehlender `SET ROLE valeo_app`-Berechtigung; der isolierte SQL-Praedikat-Test bestand ohne Rollenaenderung.
