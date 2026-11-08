---
title: Handshake RLS-DOMAIN-NACHWEISRAUM-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die RLS-Domain nachweisraum und Gesamtstand der Domain-Kette #64–#68.
---

# Handshake RLS-DOMAIN-NACHWEISRAUM-20261027 (Claude Code → Codex)

## Kette zur Integration (alle gestapelt, nur in dieser Reihenfolge)

| PR | Inhalt | Alembic |
|---|---|---|
| #64 | Entscheidungsmatrix, Ausnahmeliste, Formprüfung (Namen = deine Korrektur) | – |
| #65 | pricing | `rls_domain_pricing_20261027` |
| #66 | hr + gemeinsame Prüfhilfe | `rls_domain_hr_20261027` |
| #67 | audit/compliance | `rls_domain_audit_compliance_20261027` |
| #68 | nachweisraum | `rls_domain_nachweisraum_20261027` |

Alle Domain-Migrationen hängen hinter `rls_system_role_20261026`. Basis der Kette ist #63;
deine Integration auf `main` (fb4d0c1dc) liegt nur lokal. Nach deinem Push stelle ich die
Basis von #64 um, wenn du willst.

## Für Codex nach deiner Rückkehr

1. **P5-Formtest** (deine Fassung) verlangt `'system'` in jedem `tenant_isolation_select`.
   Er muss für die Domain-Tabellen ohne `system`-Lesen gelockert werden. Details stehen im
   Handshake hr.
2. **OpenAPI:** Nachgezogen sind nur `/price-lists` und `/nachweisraum/*`. Die vorbestehende
   Drift `/finance/closing-checklists*` liegt bei dir.
3. **Neue FKs auf P5-Tabellen:**
   - `compliance_pcn_meldungen` und `nachweisraum_dokumente` bekommen `UNIQUE (id, tenant_id)`;
   - `onboarding_runs`, `training_assignments`, `compliance_pcn_status_log` und
     `nachweisraum_audit_log` bekommen Verbund-FKs.

   Policies dieser Tabellen sind unverändert.
4. **Live-Aktivierung:** Alle vier Domain-Migrationen nehmen `ACCESS EXCLUSIVE` auf kleinen
   Tabellen (live je 0 Zeilen) und brechen bei ungeklärten Daten ab. Vorher sind die
   Masken laut QA-Berichten abzunehmen. Worker gibt es in keiner dieser Domains.

## Nicht berührt

P0–P7, dein Arbeitsbaum und dein lokales `main`, keine Live-DB, kein Reset;
`valeo_probe` steht unverändert auf `loading_stop_fk_20261023`.
