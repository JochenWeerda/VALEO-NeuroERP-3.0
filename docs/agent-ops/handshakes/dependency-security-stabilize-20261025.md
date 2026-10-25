---
title: Handshake Abhaengigkeitssicherheit 2026-10-25
type: handshake
audience: [agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-25
---

# Handshake: Abhaengigkeitssicherheit stabilisiert

**Von:** Claude Code. **An:** Codex (Lead PENDING-INTEGRATION-20261024).
**Zweig:** `claude/dependency-security-20261025`, PR gegen `codex/migration-parity-repair-20261022`.
**QA:** [dependency-security-stabilize-20261025.md](../../quality-assurance/dependency-security-stabilize-20261025.md).

## Stand

Prod-Audit 11/12 auf 1/1 (`node-forge`, gebundener Review). Gate `release_allowed: true`.
body-parser 1.20.9, nodemailer 10.1.7, fast-uri 3.1.9, multer entfernt (ungenutzt),
zod 4.6.7 in allen 27 Manifesten mit echter Verbrauchermigration.

## Fuer Codex relevant

- **Keine Datei aus deinem Besitz geaendert** (Studio-API, Entity-Projektion,
  Maskenruntime, Adaptive Workspace, DMS, Disposition). Im Frontend nur
  `lib/mcp-schema.ts` (`.issues`), `policy/schema.ts` (`z.record`) und
  `pages/crm/opportunity-detail-legacy.tsx` (`.guid()`).
- `config/security/npm-backport-reviews.json`: nur `lock_sha256`/`manifest_sha256`
  beider Reviews neu gebunden; Owner, Daten, Patch- und Quellhashes unveraendert.
  **`review_by` 2026-10-28** fuer node-forge/braces: deine Wiedervorlage.
- Jede weitere Aenderung an `package.json` oder `pnpm-lock.yaml` auf deinem Zweig
  entwertet die Bindung erneut; danach Gate laufen lassen und neu binden.
- Zod-4-Regeln fuer neuen Code: `.guid()` statt `.uuid()`, wenn die System-IDs
  `00000000-…-0001` gueltig bleiben muessen; `.prefault()` statt `.default()`
  hinter `transform()`; `.meta()` statt `.openapi()`.
- Vorbestehend rot, nicht von mir: `mask-objectpage-stamm-native-route.test.ts` (17 Faelle).

## Offen

Dev-only-Befunde (drizzle-kit 0.21/zod 3, undici, msal-node, http-cache-semantics,
@vitest/mocker, stream-json) liegen ausserhalb des Gate-Umfangs; eigener Slice noetig.
