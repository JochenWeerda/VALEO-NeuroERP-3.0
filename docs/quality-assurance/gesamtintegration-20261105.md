---
title: Gemeinsame Integration der geprueften November-Slices
type: reference
audience: [agent, entwickler, qa]
owner: Codex Lead
status: lokal abgenommen
last_reviewed: 2026-11-05
version: 1.0.0
---

# Gemeinsamer Integrationsstand

Ausgangspunkt PSM 2a43fd5dc, hinzugefuegt Omnibox 29c5e8ea0, Preis 059c7e744 und VVVO d991345d7. Die Stilllegungsmigrationen aus PR106/108 sind enthalten und bytegleich mit deren geprueften Staenden. Die Gesamt-CI aller sechs Einzel-PRs 104/106/108/110/111/112 war vor Beginn vollstaendig gruen (keine laufenden/fehlgeschlagenen Checks).

Nur eigener Arbeitsbaum artifacts/psm-zulassungen-20261104, eigener Branch codex/gesamtintegration-20261105. Keine Aenderung des geteilten Hauptbaums oder des geschuetzten main. Workboard-Konflikte behalten beide fachlich getrennten Nachweise; generierte Artefakte werden aus dem gemeinsamen Code neu erzeugt. Eine ueberfluessige Leerzeile am Ende eines Preistests ist bereinigt.

## Umfang und Sicherheitsgrenzen

Omnibox initialisiert die vollstaendige native Registry vor dem Katalog-Snapshot. PSM liest den lokalen Mandantenstamm mit echten nullable Werten. Nicht angebundene Preiswege liefern einen typisierten 404 statt Ersatzpreisen. RLS-Rueckstellungen bleiben bis zur Domain-Abnahme begruendet aktiv. VVVO/Sachkunde-Einzelwege filtern SQL-seitig nach Mandant; Wiedervorlagen enthalten ueberfaellige/offene Termine und verwenden den Geschaeftstag.

Keine Live-Migration, keine neue Rolle, keine neue Datenbank oder Containerinstanz. Die vorhandenen separaten PostgreSQL- und visuellen Nachweise behalten ihren datierten Geltungsbereich. Eine gemeinsam gruene CI wird erst nach dem Integrations-Push behauptet. Die authentifizierte PSM-Gesamtansicht ist damit noch nicht abgenommen.

## Gemeinsame Abnahme

Alle zwoelf Generatoren erfolgreich ausgefuehrt. Gemeinsamer Backend-/Maskenfeld-Vertragslauf: **46 passed, 4 warnings**, Exit 0, ohne Datenbank. Nach dem unten beschriebenen Zusatzfix: zwei fokussierte Tests bestanden. Alle neun Verbesserungsscanner gruen, stabiler Snapshot, Exit 0. Vollstaendiger unabhaengiger Doc-Generator-Check ebenfalls gruen, Exit 0. Gesamt-CI folgt erst auf dem neuen Integrations-PR. Der kanonische Tabellenkatalog stammt unveraendert aus der zuvor zurueckgerollten Migrationsabnahme; dieser Integrationsschritt braucht kein weiteres Datenbankfenster.

## Zusaetzlicher Befund: Reihenfolgeabhaengiger Listenrouten-Generator

Die gemeinsame Initialisierung zeigte einen bislang verborgenen Fehler: Der Generator verwendete die bereits erweiterte Runtime-Map als urspruengliche kuratierte Menge. Nach Vorinitialisierung verschwanden deshalb 107 Zuordnungen aus seinem Artefakt.

Die urspruenglichen kuratierten IDs werden jetzt unmittelbar an der einzigen kanonischen Map als frozenset gekennzeichnet. Es gibt keine zweite Routenmap oder Maskenregistry. Der Generator verwendet diese unveraenderliche Menge statt eines zeitabhaengigen Snapshots. Ein veralteter Kommentar mit historischen Maskenzaehlern ist gekuerzt; der Kernbestand waechst dadurch nicht.

Der neue Test wahrt auch die Aliasbeziehung der Registry-Builder. Kalter, vorinitialisierter und wiederholter Lauf sind identisch; unter anderem Artikelstamm, Waage und Benutzerverwaltung bleiben enthalten. Neuer Fall und bestehender Omnibox-Vertrag: **2 passed in 9.94s**. Gegenprobe nur mit altem Generator im Arbeitsspeicher: **1 failed** genau an kaltem/warmem Ergebnisvergleich. Keine Produktivdatei dafuer zurueckgesetzt.

Regeneriertes Artefakt: 447 Zuordnungen, 65 ohne Route; standalone --check bestanden. Die 65 offenen Zuordnungen werden durch diese technische Reparatur nicht als fachlich abgeschlossen ausgegeben. Die sechs vorhandenen PSM-Komponentenbilder behalten ihren unveraenderten UI-/Schemaumfang; kein neuer authentifizierter Browsernachweis.
