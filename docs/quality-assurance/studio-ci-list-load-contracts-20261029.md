---
title: Studio Listenladegrenzen und Generatorabgleich
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-29
version: 1.0.0
description: Belegte Korrektur von Quellseiten-Grenzen und CLI-/Routingartefakten ohne Lockerung der APIs.
---

# Abnahme

Der gepushte Stand dca5062f8 forderte bei 15 Listenquellen standardmaessig
500 Datensaetze an, obwohl die jeweilige OpenAPI-Paginierungsgrenze 200 ist.
Der StammListenParent verwendet jetzt standardmaessig 100 pro Quellseite.
Explizite, vertraglich erlaubte 200er Seiten bleiben erhalten. Keine APIgrenze
wurde angehoben und keine Validierungspruefung entfernt.

Ein neuer Test prueft alle 148 registrierten Listen gegen die tatsaechlich
publizierten Paginierungsmaxima. Er besteht im korrigierten Stand; die isolierte
Gegenprobe des alten Defaultwerts ergibt genau 15 Grenzverletzungen, darunter
Chargen, Biostimulanzien und Kontenplan. Vorhandene komplette Quellsammlung,
Duplikat-/Bestandsaenderungs-/Unvollstaendigkeitsabweisung, Suche, Kennzahlen
und Export vor dem Seitenschnitt bleiben erhalten.

Die generierten CLI-Befehle sowie Routenbaum und Routeninventar sind synchron.
Der konkrete CLI-Registertest besteht. Die Routingintegritaetspruefung erkannte
zusaetzlich eine unreferenzierte Datei portal/zertifikate-legacy.tsx. Sie hatte
keinen aktiven Verbraucher und keinen sicheren Downloadvertrag. Nach Entfernung
der Altdatei besteht die Pruefung; die aktive NativeListPage bleibt erhalten.
Es wurde kein Alias fuer eine tote Maske hinzugefuegt.

68 gezielte Tests bestehen: 19 Parent-/Builder-/Identitaets-/Quellgrenzenfaelle,
31 gemeinsame Tabellen-/Collectortests, 17 echte Listen-Renderertests und der
CLI-Registertest. Vollstaendige Frontend-Typpruefung, Navigation-Targets und
Routingintegritaet sind gruen. Keine DB, kein Container, kein Reset und keine
Rollenvergabe in diesem Slice. Gates A/B/C851, E804/851; 47 Runtimepunkte offen.

## Weitere CI-Befunde

Die CI-Gesamtlage ist damit noch nicht gruen. Auf dca5062f8 sind unter anderem
Tabelleninventarabweichungen, weitere Backend-/Frontendvertraege und 261
page_no_route_or_nav-Befunde dokumentiert. Letzteres bezeichnet Frontendseiten,
nicht QA-/Handshake-Markdownseiten; keine Doku-Nav-Kosmetik oder abgesenkte
Schwelle verwenden. Jede unreferenzierte Seite muss anhand ihrer Verbraucher
und einer kanonischen Nachfolgemaske klassifiziert werden.

Im E2E-Smoke startet das Backend nach anfaenglich fehlgeschlagenen Pollversuchen
erfolgreich; diese Refusals sind kein Ausfallbeweis. Der erste belegte Fehler
ist waitForAppReady nach Navigation auf sales/angebote. Die finale Browser-URL
und der konkrete Render-/Anmeldestatus werden anhand der ignorierten
Workflow-Artefakte untersucht. Kein unbewiesener Login- oder Backendfehler
wird als Ursache festgeschrieben. Keine Gesamtfreigabe dieser CI-Lage.
