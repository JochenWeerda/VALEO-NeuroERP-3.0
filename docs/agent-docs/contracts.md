---
title: ai_harness-Vertragsmodell
type: reference
audience: [ki-agent, entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# ai_harness-Vertragsmodell

Jeder Slice trägt im Slice-YAML (`docs/agent-ops/slices/<SLICE>.yaml`) einen
`ai_harness`-Block mit **sieben Pflichtverträgen**. Sie machen Erwartungen
maschinenlesbar und prüfbar (Slice-Readiness-Check).

## Die sieben Verträge

| Vertrag | Frage, die er beantwortet |
|---|---|
| `fachlicher_vertrag` | Welchen fachlichen Nutzen liefert der Slice? |
| `architektur_vertrag` | Wie fügt er sich in die Architektur ein? |
| `daten_vertrag` | Welche Daten/Schemata sind betroffen (inkl. Tenant)? |
| `test_vertrag` | Wie wird Korrektheit nachgewiesen (CI)? |
| `security_vertrag` | Welche Sicherheits-/Datenschutzaspekte gelten? |
| `betriebs_vertrag` | Wie wird betrieben/überwacht/zurückgerollt? |
| `dokumentations_vertrag` | Welche Doku entsteht/aktualisiert sich? |

## Pflicht-Topfelder eines Slice

`slice_id`, `title`, `owner`, `status`, `goal`, `file_ownership`, `acceptance`,
`tests`, `risks`, `external_gates`, `ai_harness`.

## Prüfung

```bash
node scripts/ai-slice-readiness-check.cjs --slice <SLICE-ID>
```

Der Check verlangt alle Topfelder, mindestens je einen Listeneintrag bei
`file_ownership`/`acceptance`/`tests`/`risks`, alle sieben `ai_harness`-Felder
sowie eine Referenz des Slice im aktiven Workboard.

## Bedeutung für Agents

- **Coding-Agents** füllen die Verträge beim Anlegen eines Slice aus.
- **Operator-Agents** lesen die Verträge, um Absicht, Grenzen und Freigaben zu
  verstehen.
- Siehe auch [Guardrails](guardrails.md) und [Capability-Katalog](capability-catalog.md).
