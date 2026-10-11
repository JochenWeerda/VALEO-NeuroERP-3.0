---
title: Quality Gate Sonar Backend-Verhalten 2026-10-11
type: reference
audience: [entwickler, qa, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-11
description: Gezielte Korrektur echter verbleibender Sonar-Codebefunde ohne Gate-Abschwaechung.
---

# Sonar Backend-Verhalten

Die oeffentliche Sonar-Abfrage vom 11.10.2026 nennt weiterhin echte
Backendfehler neben fachlich zu bewertenden Scannerbefunden. Dieser Slice
behebt genau folgende Punkte:

- Newsletter-Fehler loggen weder fremde SMTP-Fehlertexte noch Empfaenger.
  Zeilenumbrueche in einer SMTP-Antwort koennen keine Logzeilen injizieren.
  Die Versand-/Fehlerzaehlung und der HTTP-Vertrag bleiben erhalten.
- Rechnungsfreigaben erhalten eine eigene Variable fuer den verifizierten
  Nutzer statt Ueberschreibung des ignorierten Query-Parameters. Beide
  Workflow-Aufrufe und die gespeicherte Freigeberidentitaet nutzen diesen Nutzer.
- Die Losgroessenrechnung entfernt eine immer wahre Folgepruefung.
  Nichtpositiver Abverkauf wird weiterhin vorher ohne Division zurueckgegeben.
- Der unerreichbare zweite Return der Kulturenliste entfaellt.
- Bestandskorrekturen deklarieren den unveraenderten Bewegungstyp direkt,
  statt zwei identische Zweige fuer positive/negative Mengen zu verwenden.

Fuenf neue echte Funktionsvertraege bestanden in 3,85 Sekunden. Sie pruefen
Log-Injection/Empfaengerschutz, gefaelschten Freigeber sowie positiven,
Null- und negativen Abverkauf einschliesslich der berechneten Kosten.
DB- und SMTP-Zugriffe sind ersetzt; keine Datenbank/Container/echte Nachricht.

Die sieben MCP-Drift-Vertraege und die 13 Generatorpruefungen sind im
[separaten Drift-Nachweis](quality-gate-mcp-drift-20261011.md) dokumentiert.
Der parallele Versand-Meilenstein `93fd84042` enthaelt die beiden bereits
publizierten Driftkorrekturen und ersetzt deren vorherigen CI-Lauf.

Weitere Sonar-Codebefunde, Hotspot-Reviews, Abdeckung und Duplikate bleiben
offen bis zur fachlichen Korrektur und externen Nachabnahme. HTTP-URIs als
XML-Namensraeume sind keine Transportverbindungen und duerfen nicht pauschal
auf HTTPS umgeschrieben werden. Keine automatische False-Positive-Freigabe,
keine Scanner-Ausnahme und keine Schwellen-/Baseline-Absenkung in diesem Slice.
