---
title: Dev-Abhaengigkeiten bereinigt (2026-10-25)
type: qa
audience: [entwickler, qa, sicherheit]
owner: Claude Code
status: active
last_reviewed: 2026-10-25
---

# Dev-Abhaengigkeiten bereinigt (2026-10-25)

Slice `DEV-DEPENDENCY-SECURITY-20261025`, Zweig `claude/dev-dependency-security-20261025`,
Basis `ee8a27f37` (PR #40, [dependency-security-stabilize-20261025.md](dependency-security-stabilize-20261025.md)).

## Scanumfang

Voller `pnpm audit --json` inklusive devDependencies (pnpm 9.12.0), zusaetzlich
zum unveraenderten Prod-Gate (`pnpm audit --prod` + `check_npm_backport_audit.cjs`).

## Ergebnis

| Messpunkt | Basis ee8a27f37 | Geliefert |
| --- | --- | --- |
| Voller Audit (inkl. dev) | 16 Versionsbefunde (5 High, 11 Moderate) | 1 (node-forge, High, Prod-Pfad via expo, gebundener Review) |
| Prod-Gate | 1 Befund, 0 blocked | 1 Befund, 0 blocked, `release_allowed: true` |
| Installierte Pakete laut Audit | - | 2801 |
| `verify_node_security_releases.cjs` | 60/60 | 49/49 (11 Faelle mit den entfernten Werkzeugen entfallen, siehe unten) |

Keine Ausnahme, keine Severity-Aenderung, keine neue Override-Zwangsaufloesung.

## Reparaturen je Wurzel

| Wurzel | Befunde | Massnahme |
| --- | --- | --- |
| undici 7.29.1 (testcontainers, cheerio) | 3 (1 High, 2 Moderate) | bestehender globaler Override `^7.30.1` |
| vitest 4.1.11 / @vitest/mocker | 2 Moderate | vitest, @vitest/coverage-v8, @vitest/ui `^4.1.12` in allen Workspaces |
| drizzle-kit 0.21.4 / zod 3.25.76 | 1 High | hr-domain auf drizzle-kit `^0.31.11`; production-domain ohne Schema/Config/Migrationen: drizzle-kit und `migrate:*` entfernt |
| artillery 2.0.33 (analytics, scheduler) | http-cache-semantics (High, kein Fix verfuegbar), @azure/msal-node (High), undici-Pfade | entfernt: `performance:test` verwies auf nicht vorhandenes `tests/performance/load-test.yml` |
| detox 20.45.1 (mobile-app) | stream-json 1.9.1, 3 Moderate | entfernt: kein `e2e`-Verzeichnis, keine Detox-Konfiguration; `test:e2e` war nicht lauffaehig |

## Verbraucher und Kompatibilitaet

- **drizzle-kit:** 0.21/0.22 lehnen drizzle-orm 0.45 mit "This version of drizzle-kit
  is outdated" ab; die `:pg`-Befehle sind seit 0.21 nur noch Deprecation-Hinweise.
  hr-domain jetzt mit 0.31.11 (Begleitrelease zu orm 0.45), Konfiguration im
  `dialect`/`url`-Format, Skripte `drizzle-kit generate`/`up`. Ein Generierungslauf
  in ein Wegwerf-Verzeichnis (ohne Datenbank) liest Konfiguration und Schema und
  validiert; er stoppt an einem **vorbestehenden Schemafehler**: Indexnamen wie
  `tenant_status_idx` sind in mehreren hr-Tabellen doppelt (in PostgreSQL je Schema
  eindeutig). Schema nicht im Dateibesitz dieses Slices.
- **Rueckbau artillery/detox:** CI, Workflows, Doku und Skripte durchsucht; keine
  Nutzung ausser den toten Skripten und den eigenen Sicherheitsartefakten. Mit
  entfernt: `config/security/npm-patches/artillery@2.0.33.patch`,
  `stream-json@1.9.1.patch`, ihre `patchedDependencies`, der Override
  `stream-json`, die Provenance-Eintraege und README-Abschnitte. Aus
  `scripts/verify_node_dependency_security.cjs` entfallen die zehn stream-json-Faelle
  (Detox-Pfad) und der Artillery-CSV-Fall, weil ihr Pruefgegenstand nicht mehr
  installiert ist; der procurement-sharp/faker-Fall bleibt. Das ist Rueckbau nach
  AGENTS.md (Altlasten mit Tests und Doku gemeinsam), keine Abschwaechung fuer Gruen.
- **testcontainers bleibt:** `hr-domain/tests/setup/testcontainers.ts` nutzt es,
  obwohl nur `procurement-domain` es deklariert (Phantom-Abhaengigkeit ueber Hoisting).
  undici darunter ist ueber den Override gepatcht.
- `playwright@1.60.0` fuer `@playwright/test` bleibt; entfallen sind nur die
  Artillery-eigenen 1.61-Kopien.

## Abnahme

- M1 `3fe0fa632` und M2: je Zod-/Vitest-Workspace `tsc --noEmit` und `pnpm run test`
  gegen die Basis verglichen: Testzahlen in allen 25 Paketen identisch, Typfehlermengen identisch.
- `frontend-web`: Typecheck 0 Fehler, `vite build` gruen, voller Vitest-Lauf
  (vitest 4.1.12) 214 failed / 1506 passed mit **identischer Fallmenge** wie CI 40187054625 (0 neue).
- `verify_node_security_releases.cjs` 49/49, Prod-Gate 0 blocked, Review-Hashes nur neu gebunden.
- `pnpm install --frozen-lockfile`: Exit 0, Lockfile byteidentisch.
- Eigener Folgefehler in CI 40198319893: `tests/test_improvement_workflow_contract.py`
  pinnt den Frontend-Coverage-Provider exakt; der Sollwert folgt der Versionsanhebung
  auf `4.1.12` (exakte Pin-Pflicht unveraendert). Improvement-Suite lokal 97/97.
- Keine Datenbank, kein Container; der drizzle-Lauf schrieb nur in ein Scratch-Verzeichnis.

## Restbefunde und Grenzen

- node-forge 1.4.0: Prod-Pfad, gebundener Review, `review_by` 2026-10-28 (Codex).
- Die uebrigen 12 Pakete mit drizzle-kit 0.22 und `:pg`-Skripten sind gegenueber
  drizzle-orm 0.45 weiter nicht lauffaehig (kein Sicherheitsbefund, vorbestehend);
  eigener Folgeslice.
- hr-Schema: doppelte Indexnamen; hr-Tests nutzen testcontainers undeklariert und
  starten Docker-Container, was der Pruefstandsregel widerspricht. Beides offen.
- Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.
