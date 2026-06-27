---
title: Business Rules — Fachliche Leitregeln
type: reference
audience: [entwickler, agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Wichtigste fachliche Leitregeln fuer Workflow-Analyse und Implementierungsentscheidungen in VALEO NeuroERP.
---

# Business Rules

## Zweck

Sammelt die wichtigsten fachlichen Leitregeln fuer Workflow-Analyse und Implementierungsentscheidungen.

## Leitregeln

- Nummernkreise werden serverseitig vergeben, nicht im Browser.
- Belegfluesse muessen auditierbar und nachvollziehbar bleiben.
- Teillieferungen, Restmengen und Korrekturpfade duerfen nicht zu Datenverlust fuehren.
- Delete ist in fachkritischen Prozessen haeufig durch Storno, Abschluss oder Ruecknahme zu ersetzen.
- Externe Uebernahmen muessen fachlich klar als Start- oder Importpfad modelliert sein.
- Jeder Direktstart braucht einen belastbaren Rueckweg in den regulaeren Folgeprozess.

## Workflow-Pruefregeln

- pro Card nur eine Hauptaktion oder ein klarer Entscheidungspunkt
- Alternativstarts immer separat betrachten
- Rueckspruenge und Schleifen nie implizit annehmen
- Sonderfaelle nur dann zusammenziehen, wenn sie dieselbe Daten-, UI- und Regellogik haben

## Testregeln

- positiver Standardfall
- negativer Validierungsfall
- mindestens ein Edge Case
- Browser-Use-Pruefbarkeit
- CRUD- und Statuswechsel-Pruefung
