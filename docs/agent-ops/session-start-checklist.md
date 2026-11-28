---
title: Session Start Checklist
type: reference
audience: [agent, entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Pflichtschritte beim Start einer neuen Agenten-Sitzung — Workboard lesen, Memory laden, Branch pruefen, Governance-Gates.
---

# Session Start Checklist

## Zweck

Diese Checkliste minimiert Kontextverlust bei Neustarts oder Agentenwechseln.

## Reihenfolge

1. [AGENTS.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/AGENTS.md) lesen
2. [Active Workboard](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/active-workboard.md) lesen
3. passenden Handoff oder Resume-Block lesen
4. betroffene Source-of-Truth-Dateien oeffnen
5. bei Mask-Generator-/Runtime-Arbeit zusaetzlich [`universal-mask-runtime-status.md`](../architecture/uix/universal-mask-runtime-status.md)
6. bei API-/Prozess- oder Masken-Automatisierung [`Agent-Handbuch`](../agent-handbuch/index.md) (generiert; Pre-Commit regen bei Quell-Aenderungen)
7. offenen Dateibesitz und Risiken pruefen
8. erst dann in Code oder Tests einsteigen

## Pflichtfragen

- Was ist das aktuelle Ziel?
- Welche Dateien sind bereits in Bearbeitung?
- Welche Risiken oder Blocker bestehen?
- Welche Annahmen wurden bereits getroffen?
- Welche Tests oder Checks sind Pflicht?
- Welcher vorhandene Testpruefstand wird wiederverwendet? Keine neue Datenbank
  oder Dockerinstanz pro Test/Suite/Slice/Agent anlegen. `--status` pruefen;
  keine Ruecksetzung oder Migration waehrend fremder Nutzung. Verbindliche
  Ressourcenregel in [AGENTS.md](../../AGENTS.md) und
  [Pruefstand-Runbook](../quality-assurance/test-database-resource-policy-20261001.md).
- Ist die autorisierte Probe (`valeo_probe` / `TEST_DATABASE_URL`) von dieser
  Sitzung aus erreichbar? Wenn nein (typisch Cloud-VM): CI-only Evidence laut
  [Cloud-Agent-Pruefstand-SOP](../quality-assurance/cloud-agent-postgres-pruefstand.md);
  keine DB-/Container-Anlage, keine Portoeffnung. Docker/Port/Env nur Diagnose —
  fehlendes Docker allein schaltet nicht um, solange die Probe erreichbar ist.
  Wenn ja (Host mit Probe): bestehende Pruefstand-Regel unveraendert.
- Welche Doku muss nachgezogen werden?

## Cloud-VM ohne Postgres

1. Zuerst Agententyp und Erreichbarkeit der autorisierten Probe pruefen;
   Docker/Port/Env nur als Diagnose.
2. DB-freie Checks lokal ausfuehren.
3. `needs_live_db`-Tests trotzdem implementieren.
4. PR gegen `main`/`develop` oeffnen oder aktualisieren; require_db und
   Quality-Gate-Backend am zugehoerigen Lauf pruefen (Feature-Push allein startet sie nicht).
5. P0-Evidence pro Fall: Test-ID, PostgreSQL-Fixture, Ergebnis im verlinkten Lauf;
   Skip/Deselect laesst den Fall offen.
6. Bei Katalog-Drift CI-Artifact des konkreten PR-Laufs konsumieren
   (Artifact-SHA ≠ Checkout-Head); fehlendes Artefakt = Nachweis offen.
7. Interaktives Schema-Debug an Host-Agent mit `valeo_probe` handoffen.

## Vor dem ersten Edit

- **Ist-Stand pruefen:** Code, Tests, Workboard, `open-gaps-and-known-issues.md` und
  betroffene Slice-/Handshake-Doku lesen — nicht erneut implementieren, was bereits
  erledigt oder parallel in Arbeit ist
- eigenen Slice im Workboard aktualisieren
- klaren Dateibesitz oder Themenbesitz festhalten
- bei Ueberschneidung mit anderem Agenten Integrationspunkt dokumentieren

## Nach jeder relevanten Aenderung (Pflicht)

- Workboard-Stand und Slice-YAML (`status`, Ergebnis, offene Risiken)
- betroffene Fach-/Operations-Doku (`open-gaps`, Runbooks, Handshakes)
- README-/Index-Verweise, wenn neue Artefakte oder Gates entstehen
- **nicht** nur Code committen und Doku offen lassen
