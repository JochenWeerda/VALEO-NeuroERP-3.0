---
title: Drill-Protokolle (Restore/Notfall)
type: reference
audience: [betrieb, lead]
owner: Claude
status: aktiv
last_reviewed: 2026-07-03
version: 1.0.0
description: Ablage fuer committete Backup-/Restore-Drill-Protokolle als Release-Evidenz (SPEC-P0-08, 15-min-RTO).
---

# Drill-Protokolle

Ablage fuer die Protokolle der Backup-/Restore-Drills (`restore-drill-<datum>.json`).

- **Erzeugen:** `DRILL_OPERATOR="<name>" bash scripts/run_restore_drill.sh` gegen eine
  produktionsnahe Umgebung (Staging). Das Skript misst die Wiederherstellungszeit
  gegen das RTO-Ziel (Default 15 min) und schreibt das Protokoll hierher.
- **Pruefen:** `python scripts/check_restore_drill_evidence.py` — Exit 2 solange kein
  Protokoll existiert (external_gate), Exit 1 bei failed/RTO-Verfehlung/aelter 90 Tage.
- **Governance:** Der Drill selbst ist Betriebsverantwortung (external gate im
  Production-Readiness-Runbook). Dieses Verzeichnis macht die Evidenz versionierbar
  und fuer Assessor-Simulation/Release-Gates maschinenlesbar.

Kein Protokoll committen, das reale Zugangsdaten, Hostnamen mit Geheimhaltungsbedarf
oder personenbezogene Daten enthaelt.
