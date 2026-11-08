---
title: Sicherheitsmetadaten von Studio-Vorschlaegen
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: abgeschlossen
last_reviewed: 2026-10-13
---

# Sicherheitsmetadaten von Studio-Vorschlaegen

## Befund und Korrektur

Studio pruefte bislang nur root.actions. Tabellen-Zeilenaktionen, Reiter-/Abschnittsaktionen und explizite Agentenaktionen konnten die kuratierte Commandliste umgehen. forbiddenForAgents liess sich durch Weglassen statt False entfernen; ein fehlender dangerLevel wurde gegen den Katalogdefault geprueft, obwohl die Laufzeit safe verwendet.

Der bestehende Validator prueft jetzt alle Metadatenobjekte und Actions, rowActions sowie availableActions. Der Katalog bleibt fuehrend fuer Endpoint, Methode, Schutzflags und vorhandene Berechtigung. Neue Transportbindungen, Commands, menschliche Eingabewege und Navigationsziele sind nur erlaubt, wenn der Katalog genau diese deklariert. Eine Agentensperre oder andere verbindliche Schutzflags muessen explizit boolesch erhalten bleiben. Fehlender dangerLevel darf den effektiven Laufzeitdefault nicht unter die Katalogklasse absenken.

Studio-Adapter sind native, explizit temporaer und an die eigene screen_id gebunden. Verschachtelte Datenquellen und Optionsquellen unterliegen derselben Endpoint-Allowlist. Fehlerhafte Action-, Quellen- und Adapterstrukturen liefern Verletzungen statt Exceptions im Validator. Explizite Agentenvertraege duerfen keine nicht deklarierte Maskenaktion anbieten und weder Gefahr, Berechtigung, Bestaetigung, menschliche Freigabe noch Agentensperre gegenueber der Maske lockern.

Der existierende UI-Permissionschluessel studio.draft.execute bleibt nur der bisherige Katalogdefault fuer Vorschlaege. Es wird weder eine neue Rolle angelegt noch eine Domainberechtigung dadurch erteilt; die Geschaefts-Endpunkte muessen ihre bestehenden Rollen weiterhin selbst durchsetzen.

## Abnahme

51 reine Unit-Faelle in test_uix090_studio_validation.py bestanden (ohne conftest oder Datenbank): verschachtelte unbekannte Commands, fehlende/umgedeutete Agentensperren, transport- und berechtigungsfremde Metadaten, fehlerhafte Strukturen, Adapterwechsel und widerspruechliche Agentenvertraege. Die vier vorhandenen Vorschlaege Kunden/Lieferanten/offene Posten/Artikel bestehen zusaetzlich den echten Studio-_report- und Readiness-Pfad. Kein Container, Datenbankreset oder persistenter Vorschlag erzeugt. Der lokale pyreadline3-Cleanup meldet nach erfolgreichem pytest ein Windows-Handleproblem; Exitcode und Tests sind erfolgreich.

## Verbleibende Gesamtzielarbeit

Die Studio-API nimmt den Urheber weiterhin aus X-Actor-ID. Tokengebundene Identitaet, menschliche Publikationsberechtigung, unabhaengige Vier-Augen-Entscheidung, Inhalts-/Versionsbindung und dauerhaft nachvollziehbare Vorschlags-/Simulationsnachweise sind noch nicht durch diesen Slice geschlossen. Es wurde keine neue Prozessvariante produktiv freigeschaltet.

BELEG-021 liefert inzwischen einen weiteren serverseitigen Maskenaktionsadapter. Konsolidierung mit dem bestehenden DocFlow-Frontendadapter erfordert vorherige Pruefung von echter schreibfreier Simulation, Version, Idempotenz, atomarer Verarbeitung und Freigabebindung. Der neue Weg wird hier weder aktiviert noch entfernt. Die bisherigen zwei Array.at-Typecheck-Befunde und der Gesamt-CI-Nachweis bleiben offen.
