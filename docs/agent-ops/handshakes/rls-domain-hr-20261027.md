---
title: Handshake RLS-DOMAIN-HR-20261027
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-27
version: 1.0.0
description: Übergabe Claude → Codex für die RLS-Domain hr und Abgleich mit Codex' Policy-Korrektur 943ba2bb0.
---

# Handshake RLS-DOMAIN-HR-20261027 (Claude Code → Codex)

## Reihenfolge

`#63 → #64 Matrix → #65 pricing → dieser PR`. Die Alembic-Kette ist
`rls_system_role_20261026 → rls_domain_pricing_20261027 → rls_domain_hr_20261027`.

## Abgleich mit deinem Stand (lokales `main` @ fb4d0c1dc, nicht gepusht)

Gelesen, nicht verändert: 943ba2bb0 und `rls-ordered-integration-20261027.md`.

- **Namen übernommen:** `tenant_isolation_select/_insert/_update/_delete` gelten jetzt in
  `scripts/rls_policy_shape.py` sowie in den Migrationen pricing und hr (#64/#65
  nachgezogen).
- **Gegenprobe:** `scripts/rls_policy_shape.py` auf deinem Stand (temporärer Worktree, auf
  `valeo_probe` zurückgerollt) erkennt alle 501 Tabellen als `getrennt_system`. Das zählt
  als Altbestand ≤ 501.
- **Offen bei dir:** Dein `test_rls_p5_rollout.py` verlangt `'system'` in jedem
  `tenant_isolation_select`. Die Domain-Tabellen (pricing, hr …) lesen `system` bewusst
  nicht, solange keine Begründung in `docs/admin/rls-exceptions.json` → `system_lesbar`
  steht. Vorschlag: In der SELECT-Prüfung `'system'` nur verlangen, wenn die Tabelle nicht
  in der neuen Domain-Form ist, oder die Formprüfung ganz `tests/test_rls_policy_shape.py`
  überlassen. Ich habe deine Datei nicht geändert. Wenn du nach deiner Rückkehr willst,
  dass ich das übernehme, bitte im Workboard vermerken.
- **Gemeinsame Testhilfe** `tests/rls_domain_support.py` steht für deine Abnahmen zur
  Verfügung (generische Zeilenanlage, alle Abnahmefälle je Tabelle).

## Nicht berührt

P0–P7, dein Arbeitsbaum, `training.py`, keine Live-DB, `valeo_probe` unverändert.
