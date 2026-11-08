---
title: Sonar Workflow-Lieferung und Optimierungshistorie
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-11
description: Drei reproduzierte Laufzeitbefunde ohne DB, LLM oder Gate-Ausnahmen schliessen.
---

# Workflow-Lieferung und Optimierungshistorie

## Abnahmestand

Der [develop-Lauf 38129008652](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38129008652)
auf 4594ae7a1 besteht alle Jobs einschliesslich Sonar. Der neuere
[main-Lauf 38129343758](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/runs/38129343758)
auf 5fe269093 besteht Backend, Frontend, Docker, Dokumentation, Security und
Dependencies; nur der getrennte Sonar-Scan scheitert. Der gruene develop-Lauf
beweist damit nicht das gruene main-Gate.

Die oeffentliche main-Sonar-Abfrage am 11.10.2026 nennt 175 offene Bugs/
Vulnerability-Befunde. Gate: Reliability D, Security C, New-Code-Abdeckung
55,4 Prozent statt mindestens 80, Duplikate 3,3 statt hoechstens 3 Prozent,
Hotspot-Bewertungen 0 statt 100 Prozent. Keine dieser Schwellen, Baselines
oder Scanner-Ausnahmen wurde geaendert. Die Abfrage ist ein zeitgebundener
Scannerstand, kein Beleg fuer 175 durch diesen Slice verursachte Fehler.

## Drei reparierte Ursachen

- Zwei Workflow-Wege erzeugten unbehaltene SSE-Tasks. Nachrichten wurden erst
  nach der Antwort eingeplant; fehlgeschlagene Tasks erzeugten zudem ungepruefte
  Ausnahmeprotokolle. Der bestehende SSE-Hub stellt nur lokal und nicht blockierend
  in begrenzte Queues zu. Beide Wege warten jetzt gezielt diese kurze Lieferung ab.
  Keine zusaetzliche Hintergrundaufgabe und kein wachsender Task-Speicher.
- Benachrichtigungsfehler bleiben vom bereits gespeicherten Fachuebergang getrennt.
  Ein fester Warntext ersetzt ungepruefte Teilnehmer-/Fehlerdaten; Antwort und
  Audit bleiben erfolgreich. Abbrueche werden nicht als normale Fehler verschluckt.
- get_optimization_history stand nach dem return des Workflow-Builders und war
  weder erreichbar noch Mitglied des Agenten. Die Methode liegt jetzt in der
  bestehenden Agentenklasse. Sie liefert die letzten Eintraege als separate Liste;
  null liefert eine leere Liste, negative Grenzen werden abgewiesen.

## Nachweise und Grenzen

Original-Gegenprobe: neun Fehler, ein bestandener Vertrag. Echte SSE-Queues
reproduzieren die fehlende Lieferung; echte Agenteninstanzen reproduzieren den
fehlenden Methodenaufruf. Fehlergegenproben belegen auch private Daten im
ungeprueften Task-Ausnahmelog.

Reparierter Stand: 39 Tests bestanden in 11,25 Sekunden, darin zehn neue
Workflow-/Historienvertraege sowie 29 bestehende MCP-/Krypto-Vertraege.
Zusaetzlich 23 bestehende fachliche Workflow-/Guardtests bestanden in
0,44 Sekunden. SQLAlchemy-Verbindungen sind in den neuen Tests explizit
verboten. Keine DB, Dockerinstanz, LLM-Anfrage oder externe Nachricht.

Router-/Antwortschemata, Rechte, Mandantenmodell, Fachpersistenz und SSE-
Queuepolitik bleiben bestehende Vertraege. Weitere Auth-/Mandanten-/Fehlertext-
Pruefungen des Legacy-Workflow-Routers, Agenten-Checkpointer-Lebensdauer und
echte automatische Ressourcenoptimierung sind mit diesem Slice nicht abgenommen.
Weitere Sonar-Befunde und die externe Nachabnahme bleiben offen.

Scannerstand: [SonarCloud main](https://sonarcloud.io/dashboard?id=JochenWeerda_VALEO-NeuroERP-3.0&branch=main).
