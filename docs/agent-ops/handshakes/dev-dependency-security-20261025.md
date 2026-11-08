---
title: Handshake Dev-Abhaengigkeiten 2026-10-25
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-25
---

# Handshake: Dev-Abhaengigkeiten bereinigt

**Von:** Claude Code. **An:** Codex (Owner der Security-Welle 2026-09/10).
**Zweig:** `claude/dev-dependency-security-20261025`, gestapelt auf PR #40.
**QA:** [dev-dependency-security-20261025.md](../../quality-assurance/dev-dependency-security-20261025.md).

## Fuer Codex relevant

- **Deine Patches fuer stream-json 1.9.1 und Artillery 2.0.33 sind entfernt**, samt
  `patchedDependencies`, Override `stream-json`, Provenance-Eintraegen, README-Abschnitten
  und den elf Faellen in `verify_node_dependency_security.cjs`. Grund: Detox (mobile-app)
  und Artillery (analytics/scheduler) waren tote Werkzeuge ohne Konfiguration bzw.
  Szenariodatei. Bitte nicht aus aelteren Rootkopien zurueckholen.
- node-forge/braces-Reviews: nur Lock-/Manifest-Hash neu gebunden; `review_by` 2026-10-28 bleibt deine Wiedervorlage.
- hr-domain: drizzle-kit 0.31.11, Konfiguration im neuen Format. Der Generator stoppt an
  doppelten Indexnamen im hr-Schema (vorbestehend, nicht geaendert).
- hr-Tests importieren `testcontainers` undeklariert und starten Container.

## Offen

- 12 Pakete mit drizzle-kit 0.22 und `:pg`-Skripten (gegen orm 0.45 nicht lauffaehig).
- hr-Schema-Indexnamen; testcontainers-Nutzung in hr-Tests gegen Pruefstandsregel.
