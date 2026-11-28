---
title: Cloud-Agent PostgreSQL-Prüfstand (CI-only Evidence)
type: runbook
audience: [agent, entwickler, qa, betrieb]
owner: Cursor Cloud
status: aktiv
last_reviewed: 2026-11-27
version: 1.1.0
description: Verbindliche Alternative A — Cloud-Agenten ohne lokalen valeo_probe nutzen GitHub-Actions-Postgres als kanonischen Nachweis.
---

# Cloud-Agent PostgreSQL-Prüfstand

**Leitentscheidung:** Alternative A (CI-only Evidence) ist für Cursor-Cloud-VMs
ohne erreichbaren Host-`valeo_probe` **verbindlich**. Host-Agenten mit vorhandenem
Prüfstand folgen unverändert dem gemeinsamen Runbook
[Prüfstand-Datenbank](pruefstand-datenbank.md) und der
[Ressourcenpolitik](test-database-resource-policy-20261001.md).

## 1. Erkennung: Cloud-ohne-DB-Modus

Zuerst entscheiden Agententyp und Erreichbarkeit der **autorisierten Probe**
(`valeo_probe` bzw. konfigurierte `TEST_DATABASE_URL` auf denselben Prüfstand):

| Schritt | Frage | Folge |
| --- | --- | --- |
| 1 | Host-Agent mit erreichbarer autorisierter Probe? | Host-Pfad (dieser SOP gilt nicht) |
| 2 | Autorisierte Probe von dieser Sitzung aus erreichbar? | Ja → Host-/Probe-Pfad; Nein → weiter |
| 3 | Cloud-/CI-ähnliche Sitzung ohne erreichbare Probe? | Cloud-ohne-DB → dieser SOP |

Docker-Status, Listener `:5432` und unset `TEST_DATABASE_URL` sind **nur Diagnose**,
kein Umschaltkriterium für sich. Fehlendes Docker allein schaltet **nicht** auf
CI-only um, solange die autorisierte Probe erreichbar ist.

Im Cloud-ohne-DB-Modus **nicht** erwarten: lokalen `pruefstand_db.py --status`,
`vor_push` mit Live-DB oder Schema-Harvest auf der Cloud-VM.

## 2. Was lokal trotzdem läuft

- Unit-/Contract-Tests **ohne** Live-Postgres
- Architecture-Index und verwandte Generatoren mit `--check`, sofern kein Live-Schema nötig
- Doc-Generatoren und Docs-Governance ohne DB
- Implementierung von `needs_live_db`-Tests als Code (Schreiben ja, lokales Grün erwarten nein)

## 3. Was nur CI liefert

| Nachweis | Workflow / Job | Hinweis |
| --- | --- | --- |
| Marker `-m needs_live_db` | `.github/workflows/pytest-postgres-require-db.yml` | Job-lokales `valeo_probe`, `PYTEST_REQUIRE_DB_STRICT=1` |
| Frisches Schema, Katalog, Backend-Suite | `.github/workflows/quality-gate.yml` → Job `backend` | Alembic → Rollen → Tabellenkatalog |
| Tabellenkatalog / RLS-Harvest | QG-Backend bzw. require_db-Artifacts | siehe Artifact-Consume |

**Trigger:** `require_db` und Quality Gate starten bei Push nur auf `main`/`develop`
sowie bei `pull_request` gegen `main`/`develop`. Ein Push allein auf einen
Feature-Branch startet diese Jobs **nicht**. Ablauf:

1. PR gegen `main` oder `develop` öffnen oder aktualisieren.
2. Den zum PR-Event gehörigen Workflow-Lauf prüfen (nicht einen älteren Lauf eines anderen Heads).
3. Kein neuer Parallel-Workflow und kein Environment-Postgres in diesem Betriebsvertrag.

## 4. Artifact-Consume

Bei Katalog-/Inventar-Drift:

1. Den konkreten PR-Lauf im Repo finden (Workflow, Run-ID, Head-/Base-SHA des PR-Events).
2. Artifact `schema-inventories-<sha>` bzw. `fresh-schema-table-catalog` aus **diesem** Lauf laden.
3. Regenerierte Artefakte committen und den PR erneut pushen (neuer Head → neuer Nachweis).
4. **Keine** Secrets, Connection-Strings oder Passwörter aus CI-Logs in Chat, Reports oder Commits kopieren.

### Artifact-SHA ≠ Checkout-Head

Der Suffix in `schema-inventories-${{ github.sha }}` ist die `github.sha` des
PR-Laufs (bei `pull_request` typischerweise der Merge-Commit des Events), **nicht**
automatisch der Checkout-Head des Feature-Branches.

Beispiel (PR #233): Head `7e964f917…`, Artefakt
`schema-inventories-6fd2407611efc7bd85ef64eff296cf8d801db44c` aus Run `46063708738`.

Abruf und Zuordnung:

| Feld | Bedeutung |
| --- | --- |
| Repo | kanonisches Repository des PR |
| PR-Nummer | bindet Head-/Base-Refs |
| Head-SHA / Base-SHA | aus dem PR-Event; getrennt von Artifact-Suffix notieren |
| Checkout-SHA | `git rev-parse HEAD` am lokalen/Cloud-Checkout — separat führen |
| Run-ID / Attempt | konkreter Workflow-Lauf; fehlendes Artefakt = Nachweis offen |
| Neuer Push | neuer Head und neuer Lauf — alter Artifact-Nachweis ist ungültig |

Identitätsmodell und fail-closed Zuordnung: `scripts/consume_backend_evidence.py`
(`event_identity`, `matches`, Kontext mit `head_sha` / `base_sha` / `checkout_sha` /
`run_id`). Dieselben Bindungen gelten sinngemäß für require_db-Artifacts:
ohne passende Repo-/PR-/Lauf-Zuordnung bleibt der Nachweis offen.

Lokaler Schema-Harvest auf der Cloud-VM ist kein Ersatz.

## 5. Evidence-Formulierung

Ein grüner Job allein reicht **nicht**. Aggregierte Zähler (passed/skipped/deselected)
schließen keinen geforderten P0-Fall. Beispiel: Job `140723839652` meldete
713 passed, 3 skipped, 28112 deselected — ohne Test-ID bleibt unklar, ob der
P0-Fall überhaupt ausgewählt wurde.

Für Cloud-ohne-DB gilt pro gefordertem P0-Postgres-Fall:

| Pflichtfeld | Inhalt |
| --- | --- |
| Test-ID | pytest node id (Datei::Test/Funktion) |
| PostgreSQL-Fixture | genutzte Live-DB-Fixture / Marker (`needs_live_db`) |
| Ergebnis im verlinkten Lauf | passed im genannten Run; Log-/Report-Stelle |
| Lauf-Bindung | Jobname, Run-ID, Attempt, Repo, PR, Head-/Base-/Checkout-SHA |

**Offen** bleibt der Fall, wenn er im Lauf **skipped**, **deselected** oder sonst
nicht ausgewählt ist — auch wenn der Job insgesamt grün ist.

Nicht formulieren: „lokal auf Probe grün“, wenn die VM keine Probe hat.
Fehlende lokale Probe ist **kein** Abnahmeverzicht und **kein** Grund, P0-Postgres-Fälle
auf P1 herabzustufen.

## 6. Handoff an Host-Agent

Interaktives Schema-Debug (Migration, RLS, rohes SQL vor Push) gehört an einen
Host-Agenten mit bestehendem `valeo_probe` (eigener Workboard-Claim). Der Cloud-Agent
liefert Testcode und DB-freie Verträge; der Host-Agent liefert Probe-Evidence.

## 7. Verbotsliste

| # | Verboten |
| --- | --- |
| 1 | Portöffnung / Tunnel Cloud → Host/Staging/Prod-Postgres |
| 2 | Secrets, Connection-Strings, Passwörter in Chat, Store-Reports, Commits, SOP-Beispielen |
| 3 | Reset/Drop/`pruefstand_db.py` ohne Option ohne Wartungs-Claim |
| 4 | Neue DB/Container pro Agent/Suite/Slice (`valeo_probe_<id>`, UUID-Namen) |
| 5 | Schema-Prüfungen gegen gewachsenes `valeo_neuro_erp` |
| 6 | Eigenmächtige Cursor-Environment-/Firewall-/Secret-Änderungen |
| 7 | Self-Merge von SOP-/Dispatch-/Fach-PRs |
| 8 | P0-Postgres-Nachweise wegen fehlender Cloud-Probe auf P1 herabstufen |
| 9 | Neuer Parallel-Workflow oder zweites Architecture-Subsystem „Cloud-DB“ |
| 10 | `quality-gate.yml` ohne Lead-OK für schmale Dispatch-Inputs anfassen |

## 8. Folge-Slices (nicht dieser SOP)

| Slice | Status |
| --- | --- |
| `CLOUD-AGENT-PG-DISPATCH` | optional, erst nach SOP-Merge und Lead-Freigabe |
| `CLOUD-AGENT-PG-ENV` | nur Owner-/Dashboard-Entscheidung — kein Agent-Claim ohne Freigabe |

## 9. Querverweise

- [AGENTS.md](../../AGENTS.md) — Abschnitt Cloud-Agenten ohne lokalen Prüfstand
- [Session Start Checklist](../agent-ops/session-start-checklist.md)
- [Prüfstand-Datenbank](pruefstand-datenbank.md) — Host-Pfad unverändert
- [Ressourcenpolitik](test-database-resource-policy-20261001.md)
- Slice: `docs/agent-ops/slices/CLOUD-AGENT-PG-SOP.yaml`
- Evidence-Identität: `scripts/consume_backend_evidence.py`
