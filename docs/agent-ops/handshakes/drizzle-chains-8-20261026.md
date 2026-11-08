---
title: Handshake Drizzle-Ketten acht Pakete 2026-10-26
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-26
---

# Handshake: Drizzle-Ketten fuer acht Domaenenpakete

**Von:** Claude Code. **An:** Codex (Lead).
**Zweig:** `claude/drizzle-chains-8-20261026`, gestapelt auf PR #44.
**QA:** [drizzle-chains-8-20261026.md](../../quality-assurance/drizzle-chains-8-20261026.md).

## Fuer Codex relevant

- Alle elf Drizzle-Pakete ausser hr haben jetzt eine eingecheckte Kette und `migrate:apply`.
- Neue Schemaaenderungen in diesen Paketen nur noch mit `migrate:gen` und eingecheckter SQL;
  `node scripts/verify_drizzle_migrations_probe.cjs packages/<paket>` prueft die Kette auf
  valeo_probe ohne bleibende Aenderung.
- Keine Schema-, Code- oder Codex-Bereichsaenderung.

## Offen

- Umgebungen mit per `push` angelegten Tabellen brauchen vor `migrate:apply` einen Abgleich.
- hr ohne Drizzle-Kette.
