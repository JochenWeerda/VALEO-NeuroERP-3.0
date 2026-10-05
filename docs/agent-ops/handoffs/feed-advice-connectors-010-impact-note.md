---
title: FEED-ADVICE-CONNECTORS-010 Architecture Impact Note
type: reference
audience: [architekt, entwickler, qa]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-14
version: 1.0.0
---

# FEED-ADVICE-CONNECTORS-010 — Architecture Impact Note

## Meta

- **Slice / Ticket:** FEED-ADVICE-CONNECTORS-010
- **Domain(s):** Agrar / Fütterungsberatung
- **Entscheidungsstufe:** Significant
- **Agent / Autor:** Codex

## Änderung

Providerneutraler Herd-Data-Vertrag mit DDW-Profil, Delta-Sync, tenantgebundener
Verbindung, Consent-/Contract-/Secret-/Egress-Gates, Beobachtungsspeicher und
täglichem Worker im bestehenden Rationsintegrationspfad.

## Betroffene Artefakte

- [x] Code (`app/`)
- [ ] `docs/architecture/c4/workspace.dsl` — kein neuer Container
- [x] `config/architecture-index.yaml` — bestehende Prefixe, Generatorprüfung
- [x] Domain Pack (`docs/architecture/domains/agrar/`)
- [x] ADR-040 (Proposed)
- [x] Tests
- [x] Workboard

## Drift-Check

`pnpm arch:validate` und `pnpm arch:drift` grün. Mapping: 898/898 Routes,
210/210 Services, 406/406 Endpoints; Alembic: ein Head
`feed_advice_connectors_20260714`.

## Offene Risiken / Follow-ups

- Reale DDW-Pfade, Query-Namen, Auth-Vertrag und Credentials müssen aus einem
  lizenzierten Partnerpaket kommen; Mock-Pfade sind nicht produktiv.
