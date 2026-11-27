---
title: Cloud-Agent PostgreSQL-Prüfstand (CI-only Evidence)
type: runbook
audience: [agent, entwickler, qa, betrieb]
owner: Cursor Cloud
status: aktiv
last_reviewed: 2026-11-27
version: 1.0.0
description: Verbindliche Alternative A — Cloud-Agenten ohne lokalen valeo_probe nutzen GitHub-Actions-Postgres als kanonischen Nachweis.
---

# Cloud-Agent PostgreSQL-Prüfstand

**Leitentscheidung:** Alternative A (CI-only Evidence) ist für Cursor-Cloud-VMs
ohne erreichbaren Host-`valeo_probe` **verbindlich**. Host-Agenten mit vorhandenem
Prüfstand folgen unverändert dem gemeinsamen Runbook
[Prüfstand-Datenbank](pruefstand-datenbank.md) und der
[Ressourcenpolitik](test-database-resource-policy-20261001.md).

## 1. Erkennung: Cloud-ohne-DB-Modus

Eine Sitzung gilt als **Cloud-ohne-DB**, wenn mindestens eines zutrifft:

| Signal | Typische Beobachtung |
| --- | --- |
| Kein Listener `:5432` | Connection refused |
| Docker unavailable | kein `docker.sock` / keine Container-Runtime |
| `TEST_DATABASE_URL` unset | und keine erreichbare Probe-URL |

Dann gilt dieser SOP-Pfad. **Nicht** erwarten: lokalen `pruefstand_db.py --status`,
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

Push auf den Feature-Branch löst die autorisierte Job-DB aus. Kein neuer Parallel-Workflow
und kein Environment-Postgres in diesem Betriebsvertrag.

## 4. Artifact-Consume

Bei Katalog-/Inventar-Drift:

1. Artifact `schema-inventories-<sha>` aus dem require_db-Lauf herunterladen (wo vorhanden).
2. Artifact `fresh-schema-table-catalog` aus dem QG-Backend-Lauf bei Katalog-Drift nutzen.
3. Regenerierte Artefakte committen und erneut pushen.
4. **Keine** Secrets, Connection-Strings oder Passwörter aus CI-Logs in Chat, Reports oder Commits kopieren.

Lokaler Schema-Harvest auf der Cloud-VM ist kein Ersatz.

## 5. Evidence-Formulierung

Für Cloud-ohne-DB lautet der Postgres-Nachweis:

> Postgres-Nachweis = CI-Job \<Name\> Run \<ID\> grün auf SHA \<Commit\>

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
