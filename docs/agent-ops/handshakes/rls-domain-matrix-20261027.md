---
title: Handshake RLS-DOMAIN-MATRIX-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die Vorbereitung der offenen RLS-Domains; Überschneidungen mit RLS-ORDERED-INTEGRATION-20261027.
---

# Handshake RLS-DOMAIN-MATRIX-20261027 (Claude Code → Codex)

## Reihenfolge und Basis

```
#55 → #56 … #63 (Codex integriert)  →  RLS-DOMAIN-MATRIX (dieser PR, Basis #63)
                                    →  RLS-DOMAIN-PRICING (Basis dieser PR)
```

Beide PRs zeigen auf `claude/rls-p7-guards-20261026`. Nach der Integration von #63 muss die
Basis auf den Integrationszweig umgestellt werden. Der Inhalt dieses PRs ist neu und berührt
keine Datei aus P0–P7 außer dem Workboard-Anhang.

## Überschneidungen — bitte bei der P3/P5-Korrektur berücksichtigen

1. **Policy-Form (Stand 27.10., nach 943ba2bb0).** Die Namen von Codex' Korrektur
   (`tenant_isolation_select/_insert/_update/_delete`) gelten jetzt überall:
   `scripts/rls_policy_shape.py` und die Domain-Migrationen. Es gibt nur noch eine Definition.
2. **`tests/test_rls_p5_rollout.py::test_alle_rls_tabellen_tragen_genau_die_mandantenpolicy`**
   (Codex-Fassung) verlangt in `tenant_isolation_select` immer `'system'`. Neue Domains
   lesen `system` aber nur mit Begründung (`rls-exceptions.json` → `system_lesbar`).
   Vorschlag: SELECT-USING darf `eigen` oder `eigen OR system` sein, Letzteres nur für
   begründete Tabellen und den Altbestand. Das prüft `tests/test_rls_policy_shape.py`
   bereits so.
3. **`altbestand_hoechstens`** (501) in `docs/admin/rls-exceptions.json` zählt ALL-Policy
   plus unbegründetes `system`-Lesen. Er sinkt, sobald eine Tabellenfamilie ihr
   `system`-Lesen begründet (Eintrag in `system_lesbar`) oder verliert.
4. **`scripts/provision_db_roles.py`**: Dienstrollen je Dienst kämen aus dem
   Dienst-Vorschlag. Nichts geändert.

## Was nicht passiert ist

Keine Live-Policy, kein P4-Cleanup, keine Rollenkennwörter, keine neue DB, kein Reset.
`valeo_probe` ist unverändert (Revision `loading_stop_fk_20261023`), alles lief in
zurückgerollten Transaktionen. Die gewachsene DB wurde nur gelesen.

## Vor der Live-Aktivierung abzunehmen

Siehe `docs/architecture/rls-domaenen-entscheidungsmatrix.md` §6 und die Worker-Spalte der
Matrix. Die Dienste brauchen zuerst die Entscheidung zu
`docs/architecture/rls-dienste-identitaet-vorschlag.md`.
