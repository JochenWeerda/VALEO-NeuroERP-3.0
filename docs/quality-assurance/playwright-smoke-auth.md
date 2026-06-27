---
title: Playwright Smoke — Auth (Dev / Preview / CI)
type: how-to
audience: [entwickler, qa]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: SSO-only Login-Seite korrekt in Playwright-Tests handhaben — API-Token-Auth statt UI-Login.
---

# Playwright @smoke — Authentifizierung (Dev / Preview / CI)

## Problem

Die Login-Seite (`/auth/login`) ist **SSO-only** (Button „Mit SSO anmelden“). Es gibt **keine**
E-Mail-/Passwort-Felder. Der frühere Helper `loginToPage` füllte nicht existente Inputs — Tests
schlugen lokal gegen **Vite :3001** fehl, während **Preview :4173** ohne OIDC oft zufällig funktionierte.

## Lösung (Task 0)

`playwright-tests/helpers/api.ts` → `loginToPage`:

- **Standard (`VALEO_PLAYWRIGHT_USE_SSO` nicht `1`):** `addInitScript` setzt `access_token` in
  `localStorage` (analog `packages/frontend-web/src/lib/auth.ts` im Dev-Modus ohne OIDC), dann
  `page.goto('/')` und `networkidle` (best effort).
- **Optional OIDC:** `VALEO_PLAYWRIGHT_USE_SSO=1` aktiviert den Legacy-Pfad mit Formular (nur wenn
  die UI wieder Form-Login bietet oder ein Fork das nutzt).

## Umgebungsvariablen

| Variable | Bedeutung |
|----------|-----------|
| `VALEO_BASE_URL` / `FRONTEND_URL` | Frontend-Root (Default in `playwright.config.ts`: `http://127.0.0.1:4173`) |
| `VALEO_API_DEV_TOKEN` | Token für `localStorage` (Default `dev-token`) |
| `VALEO_TENANT` | `X-Tenant-ID` im Browser-Kontext (Default Dev-Tenant-UUID) |
| `VALEO_PLAYWRIGHT_USE_SSO` | `1` = Formular-Login statt Dev-Token |

## CI

Wenn der **Preview-Build** mit echtem OIDC gebaut wird, muss CI entweder:

- ein gültiges **`storageState`** erzeugen und an Playwright übergeben, oder
- `VALEO_PLAYWRIGHT_USE_SSO=1` + Test-IdP-Credentials setzen (sofern die UI das unterstützt).

Ohne OIDC (reiner Dev-/Preview-Build wie `global-setup` nach `pnpm build`) sind die @smoke-Specs
mit Dev-Token **deterministisch**.

## Referenz

- Fixture: `playwright-tests/fixtures/testSetup.ts` (`X-Tenant-ID` Header)
- Global-Setup: `playwright.global-setup.mjs` (Preview-Start / Reuse)
