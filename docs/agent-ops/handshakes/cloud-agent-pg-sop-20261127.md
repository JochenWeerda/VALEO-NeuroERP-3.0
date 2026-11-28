# Handshake: 2026-11-27 — CLOUD-AGENT-PG-SOP

**Von:** Cursor Cloud `bc-e6058277-d007-5f6b-a9b0-a58684d8ce0c`  
**An:** Lead / Claude Admin  
**Ziel:** Alternative A (CI-only Evidence) als verbindlichen Cloud-Postgres-Pfad dokumentieren.

## Stand (zur Abnahme, Europe/Berlin)

- Branch: `cursor/cloud-agent-pg-sop-ce0c` · PR #233
- SOP: `docs/quality-assurance/cloud-agent-postgres-pruefstand.md` (v1.1 nach Lead REQUEST CHANGES)
- Querverweise: `AGENTS.md`, `docs/agent-ops/session-start-checklist.md`,
  `docs/quality-assurance/pruefstand-datenbank.md`,
  `docs/quality-assurance/test-database-resource-policy-20261001.md`
- Slice-YAML: `docs/agent-ops/slices/CLOUD-AGENT-PG-SOP.yaml`
- Workboard: `CLOUD-AGENT-PG-SOP` → zur Abnahme (kein Self-Merge)

## Review-Nachzug (Lead REQUEST CHANGES)

- P1: P0-Evidence pro Fall (Test-ID, Fixture, Ergebnis); Skip/Deselect = offen
- P2: Erkennung zuerst Agententyp/Probe; PR-Trigger statt Feature-Push;
  Artifact-SHA = `github.sha` des Laufs, Identitätsmodell `consume_backend_evidence.py`

## Abnahme

- Docs-Governance / vom PR getriggerte Doc-Gates
- Manuelle Review: Cloud-Zweig widerspricht Host-`valeo_probe`-Regel nicht
- Diff enthält kein Workflow, Compose, Secret, Port oder Environment-Edit

## Abgrenzung

- `CLOUD-AGENT-PG-DISPATCH` und `CLOUD-AGENT-PG-ENV` nicht umgesetzt
- Keine Fachänderungen zu PR #232

## Nächster Schritt

1. PR mergen (Claude Admin)
2. Workboard/Slice auf `abgeschlossen` setzen
3. Optional: Lead gibt `CLOUD-AGENT-PG-DISPATCH` frei
