---
title: Kohaerente Studio Inbox und Domain Integration
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Quelllieferung mit synchronen Artefakten und ausdruecklich offenen Funktionsgates.
---

# Integrationsstand 2026-10-27

Nutzerziel: Alle fachlichen Masken werden Studio-build, versioniert und ueber
dieselbe Runtime Human/MCP/CLI bedienbar. Legacy-Wrapper und Katalogeintraege
allein erfuellen dies nicht. Funktionierende Altwege bleiben bis zur fachlichen
Abnahme ihres Studio-Ersatzes erhalten.

## Gelieferter Zusammenhang

Die bereits geprueften Detail-API-Vertraege und die gemeinsame Entityprojektion
werden zusammen mit DMS-Inbox, frischem autorisiertem Native-Create-Prefill und
Adaptive-Workspace-Komposition geliefert. Dispositionswrites bleiben deaktiviert;
sechs nicht abgenommene neue Dateien sind bytegenau unter ignorierten Artefakten
erhalten und nicht Teil dieser Lieferung. Diagnosedumps und Scratchskripte sind
vom Dateimanifest ausgeschlossen. Fuenf TSX-Testumbenennungen werden gepaart
mit ihren alten Dateien behandelt; fehlende Dateien des partiellen Quellbaums
werden sonst niemals als Loeschung interpretiert.

Claudes KI/Sales/CRM/Inventory/Einkauf folgen in genau dieser Reihenfolge
als eigene Mergecommits hinter Agrar. Autorhandshakes und QA sind uebernommen;
608 RLS-Tabellen und112 zurueckgestellte Tabellen stehen im aktualisierten
Schema-/Codeinventar. Dies ist kein Nachweis aktiver Live-Policies.
Der aktive Shared-Slice bei Claude bleibt unberuehrt. Die beiden Demo-Bestellungen
mit fremdem Lieferanten bleiben ein absichtlicher Live-Migrationsblocker.
Keine Live-Migration und kein fremder Pruefstandzugriff wurden ausgefuehrt.

## Eigene Nachweise und Grenzen

- Vor dieser Quelllieferung: 77 API-Vertraege und269 RLS-/Agrar-Vertraege bestanden
  auf dem damaligen integrierten Stand; die spaetere Domainkette hat zusaetzliche
  Autorbelege. Dies ist keine erneute komplette SQL-Abnahme der neuen Kette.
- 79 gezielte Frontendtests in11 Dateien, vollstaendige Typpruefung bestanden.
  Nach zentraler Notification-Projektion nochmals vollstaendige Typpruefung gruen.
- Notification-Verhaltenstest: zwei Zeilen, isolierter lokaler Lesestatus,
  Touch-Ziel, kein Serverwrite, Reset; Gate B direkt gruen. Nur dieser gefilterte
  Fall gilt als nachgeprueft, andere Faelle werden nicht als bestanden gezaehlt.
- Rechnungsaudit:5 Service-/Sessionattrappenfaelle gruen, kein realer SQL-/FK-Beleg.
- POS/UStVA:3 isolierte unveraenderte Funktionskoerpertests gruen; keine Router-,
  HTTP- oder Rechteabnahme. Nicht angebundener Checkout antwortet501 ohne Scheinbon;
  UStVA behauptet keine Uebermittlung, Datenbankfehler ergeben503.
- Produktionsbundle nach der zentralen Renderer-Aenderung erfolgreich gebaut.
- Python-Syntax aller ausgewaehlten Quelldateien geprueft. Ein zusaetzlicher
  enger Router-/RAG-Nachlauf mit Standard-Conftest sowie ein isolierter Importlauf
  wurden wegen Haengen abgebrochen und sind kein Testnachweis.

OpenAPI, Aktionsrechte149, Studio-Katalog848, Agentenhandbuch und Codeinventare
wurden in einem gemeinsamen Lauf aus diesen Quellen neu erzeugt. Der Gate-Report
ist absichtlich rot: A/B857/857, C856/857, E800/857, nur5 Definitionen strukturell
freigabefaehig. Portal-Zertifikatszuordnung,57 Runtime-Luecken, Browser-/Fachketten-
abnahme und gruene Gesamt-CI bleiben offen. Alte Zaehler gelten nur historisch.
Der letzte gezielte Drei-Dateien-UIX-Lauf vor Notification zeigte25 Fehler und15
bestandene Faelle; die Fehler enthalten echte fehlende Fachaktionen und alte
Quelltextpruefungen. Keine dieser Aussagen erlaubt eine Gesamtfreigabe.

qs-Sicherheitsfix229320530 liegt bereits auf dem Integrationszweig; keine
Reviewfrist oder Sicherheitsratsche wurde gelockert. Alle Quellen dieser
Lieferung werden durch Pfad-, Datenschutz-, Dokumentations- und Staging-Gates
geprueft. GitHub-Gesamtnachlauf nach der Lieferung bleibt erforderlich.

Staging-Nachlauf: doppelte Importe/Nicht-Null-Assertions ohne Ausnahme
beseitigt. Eine dabei entstandene Windows-Zeichensatzbeschaedigung wurde
vor Commit vollstaendig zurueckkorrigiert. Derselbe unveraenderte Nachtest
(native Create, Entityprojektion, Inbox-Prepare) besteht mit29 Tests in3
Dateien. Die Migrationsquellen wurden vollstaendig auf Revisionen abgebildet:
459 Dateien, genau ein Head rls_domain_einkauf_20261027. Kein SQL-Replay.

Letzter Gate-Nachlauf: 21 RAG-/Mandanten-/Policyformvertraege bestanden
(nur gemockte bzw. statische Vertrage, kein SQL-Replay). Neun verbleibende
Nicht-Null-Assertions wurden durch Guards/Typ-Praedikate ersetzt; enge
Lintpruefung ohne Warnung und27 Authoring-/Overlay-/Agrar-Tests bestanden.
Die duplizierten CSV-/Bestelllistenschemas wurden nach AST-Gleichheitsvergleich
mit den vorhandenen kanonischen Modellen zusammengefuehrt. PCN-Abbildung in
den zugehoerigen Service ausgelagert;10 kombinierte Ausgabe-/Audit-/Ergebnis-
Unitfaelle bestanden. Godfile-Ratsche nur gesenkt: compat3338->3333,
Compliance1003->992 und damit aus der Godfileliste entfernt. Kein
Grenzwertanstieg, keine Test-/Lintausnahme.
