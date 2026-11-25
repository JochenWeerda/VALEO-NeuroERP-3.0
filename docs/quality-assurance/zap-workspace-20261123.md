---
title: Isolierter ZAP-Arbeitsbereich
type: reference
audience: [entwickler, agent, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-11-23
version: 1.0.0
description: Nachweis fuer beschraenkte Scanner-Schreibrechte und blockierende Berichtsauswertung.
---

# ZAP-Arbeitsbereich

PR160 Job137506796501 scheiterte an `Permission denied: /zap/wrk/zap.yaml`, anschliessend fehlte ein auswertbarer Bericht. Der gleiche Scan war auf PR163 vor dieser Aenderung erfolgreich; es handelt sich um eine nicht durchgaengig auftretende Infrastrukturfehlerquelle.

Die Baseline laeuft nun mit demselben Scannerimage und Ziel gegen ein eigenes temporaeres, fuer den Scanner beschreibbares Verzeichnis. Nur dieses wird eingebunden; der Checkout wird nicht schreibbar freigegeben. Die vorhandenen Regeln werden kopiert, Host-Netz und aktiver/passiver Baseline-Umfang bleiben erhalten. Ein EXIT-Trap raeumt nur das eigene mktemp-Verzeichnis auf. Der JSON-Bericht wird vor dem Aufraeumen gesichert und auch bei Fehlern als CI-Artefakt hochgeladen.

Nur Scannerstatus0 oder2 wird zur Berichtsauswertung zugelassen. Status1 (konfigurierte FAIL-Regel), Betriebsfehler und fehlende, leere oder ungueltige Berichte blockieren. Ein nichtleeres site-Array mit alerts-Listen ist erforderlich; unbekannte Risikocodes sowie mittlere/hohe Risiken blockieren. Keine Ausnahme oder Schwellenabsenkung.

## Pruefung

12 isolierte Verhaltenstests bestanden in6,95s: erlaubte Berichte, Warnungen, konfigurierte FAIL-Regel, Scannerfehler, medium/high, fehlende Sites/Alerts, kaputter oder fehlender Bericht. Die Docker-Attrappe prueft die Regelkopie und den separaten Mount; nach jedem Fall ist das temporaere Verzeichnis entfernt. Kein echter Docker-/DB-Zugriff. Der eingeschraenkte Windows-Bash-Start hing; ausserhalb dieser Beschraenkung liefen alle12 Tests erfolgreich. Ein echter neuer GitHub-Scan dieses Fixes steht aus.
