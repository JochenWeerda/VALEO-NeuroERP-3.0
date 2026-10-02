---
title: Journalstempel ohne stillen Rueckfall
type: reference
audience: [qa, agent, entwickler]
owner: Codex
status: aktiv
last_reviewed: 2026-10-02
version: 1.0.0
---

# Journalstempel ohne stillen Rueckfall

## Vertrag und Umsetzung

FinanceTransactionService.create und reverse brechen ab, wenn der Stempel
nicht ermittelt werden kann. Keine Teilzuweisung der Stempelfelder und kein
Add/Flush/Commit bei Stempelfehler. SQL-/Verbindungsdetails werden nicht in
die fachliche Fehlermeldung kopiert. Fremder Tenant und Ueberschreiben eines
vorhandenen Stempels sind abgewiesen.

Eine mandantenbezogene PostgreSQL-Transaktionssperre serialisiert die
Sequenzvergabe bis Commit/Rollback. READ COMMITTED ist Voraussetzung:
REPEATABLE READ koennte nach dem Warten einen alten Snapshot verwenden und
wird ausdruecklich abgewiesen. Ein gemeinsamer Abfragevertrag bestimmt
Sequenz und Vorgaenger und prueft vollstaendige positive, eindeutige,
lueckenlose Sequenzen, Hashformat und jeden gespeicherten Vorgaengerlink.
Keine fehlenden Hashes erraten oder Entwicklungsdaten automatisch reparieren.
Die alten getrennten MAX-/Vorgaengerhelfer sind entfernt.

## Nachweis

115 Tests bestanden (4.18 Sekunden): 19 neue Stempelvertraege, 31 bisherige
Journalservicetests und 65 Regressionen fuer Perioden, Belegfluss und Einkauf.
14 der neuen Vertraege verwenden echtes PostgreSQL. Der Paralleltest weist
ueber pg_locks die wartende zweite Transaktion nach und prueft deren Sequenz
und Vorgänger nach dem ersten Commit. Kein zeitbasierter Erfolgsersatz.
Ruff fuer die drei geaenderten Python-Dateien bestanden.
Datierter lokaler Testlog: artifacts/journal-stamp-tests.log.

Vorhandener valeo_probe (Revision eudr_uebermittlung_20261001), eine eigene
kleine journalstamp_-Tabellenkopie pro Modul. Eigene Testzeilen und Schema
gezielt entfernt, keine weitere Datenbank oder Dockerinstanz, keine
Migration/Revision/Reset auf gemeinsamem Bestand. Read-only Bestandsprobe:
0 gemeinsame Journalzeilen, 0 fehlende Stempel (2026-10-02).

## Grenzen und Folgearbeit

Dieser Nachweis schliesst den verschluckten Stempelfehler und die
Sequenz-Race im vorhandenen Service. Er ist keine GoBD-Gesamtabnahme.
Andere Journal-Schreiber verwenden den Helfer noch nicht. Der bisherige
Hash-Payload deckt nicht alle Attribute oder Zeilen ab; ein gespeicherter
Hash wird hier nicht aus dem historischen Beleg neu berechnet. Draft-Delete
kann eine Kettenluecke verursachen; der Guard erkennt sie, der kanonische
Journal-Lifecycle muss dies kuenftig verhindern. Kontenaufloesung verwechselt
weiter IDs und Kontonummern und sucht global. Diese Gaps bleiben offen.

Die Metadatenpruefung liest die bestehende Tenant-Kette, statt deren Fehler
mit einem MAX-Fallback zu uebergehen. Ihre Kosten wachsen mit der Kette;
langfristiger zentraler Schreibvertrag und indizierter Kettenzustand brauchen
Performance- und Vollstaendigkeitsnachweise. Hoechste Skalierung ist damit
noch nicht behauptet. Keine neue API/Domain/Containergrenze (Minor-Bugfix).
