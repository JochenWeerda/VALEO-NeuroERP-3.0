---
title: Business-Time-Ratchet fuer produktiven Python-Code
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-30
description: Messung und blockierende Ratsche fuer direkte Host- und UTC-Kalendertage unter app/.
---

# Business-Time-Ratchet

## Befund

Der zentrale Vertrag in `app/core/business_time.py` loest bereits bekannte
Buchungs-, Frist- und Tagesgrenzen. Eine Repo-Inventur zeigt trotzdem 244
direkte Kalenderableitungen in 125 produktiven Python-Dateien:

| Muster | Stellen |
|---|---:|
| `date.today()` einschliesslich Import-Aliasse | 232 |
| `datetime.now(...).date()` | 11 |
| `datetime.utcnow().date()` | 1 |

Die Schwerpunkte liegen in `app/api/v1` mit 135 und `app/services` mit 65
Stellen. Der Bestand mischt fachliche Tageswerte mit technischen Anzeige- und
Laufwerten. Eine automatische Massenersetzung waere fachlich falsch.

## Gate-Vertrag

`scripts/check_business_time_usage.py` analysiert den Python-AST und verfolgt
Aliasse aus `import datetime` sowie `from datetime import date, datetime`.
Die Baseline `config/business_time_usage_baseline.json` zaehlt je Datei und
Muster. Dadurch gelten folgende Regeln:

- Neue direkte Kalenderquellen schlagen fehl.
- Das Verschieben einer bekannten Stelle in eine andere Datei schlägt fehl.
- Nach einem Abbau schlägt die veraltete Baseline fehl und muss im selben
  Commit mit `--update-baseline` abgesenkt werden.
- `business_today()` und `business_date_at()` bleiben die zentrale Quelle fuer
  fachliche Tage; technische UTC-Zeitpunkte bleiben Datetime-Werte.

Der Backend-Job in `.github/workflows/quality-gate.yml` fuehrt das Gate vor den
weiteren Bestandsratschen aus. Die Baseline ist kein Freibrief fuer Altstellen,
sondern die Obergrenze fuer den schrittweisen Abbau.

## Nachweis

- `pytest tests/test_business_time_usage_gate.py -q --no-cov`: 5 bestanden.
- `python scripts/check_business_time_usage.py`: Exit 0, 244 Stellen in 125
  Dateien.
- Die Tests belegen Alias-Erkennung, erlaubte zentrale Helfer, pfad- und
  musterbezogene Zaehler, Verschiebungsschutz und Baseline-Absenkung.

## Priorisierung des Abbaus

Zuerst sind Werte mit Buchungs-, Perioden-, Faelligkeits-, Gueltigkeits- oder
Bestandswirkung zu klassifizieren. Danach folgen fachliche Tagesberichte und
ID-/Jahresableitungen. Rein technische Zeitpunkte werden als UTC-Datetime
beibehalten und nicht in ein fachliches Datum umgedeutet.
