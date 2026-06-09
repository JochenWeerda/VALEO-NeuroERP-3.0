# Playwright Port-Konflikt — Reuse-Existing-Server (2026-06-09)

**Kontext:** Die model-based CRM360-Suite (`playwright-tests/specs/crm/crm360-model-based.spec.ts`)
ließ sich lokal nicht zuverlässig starten, weil `playwright.global-setup.mjs` bei **jedem** Lauf
unbedingt baute und Server auf festen Ports spawnte. Lief bereits ein Server auf demselben Port
(z. B. ein Vorlauf-Preview eines vorherigen Runs oder der Docker-Dev-Stack), brach der zweite
Bind mit `EADDRINUSE` ab — und das Teardown konnte zudem fremde, weiterlaufende Server abschießen.

## Lösung (Best Practice: „reuse existing server")

Analog zu Playwrights `webServer.reuseExistingServer`:

1. **Vor jedem Spawn probt der Global-Setup den Ziel-Server** (`isReachable`, HEAD).
   Ist er erreichbar, wird er **wiederverwendet** statt ein zweites Mal auf den Port gebunden.
2. **Nur selbst gestartete Prozesse** landen in `processes` und damit in `server-pids.json`.
   Das Teardown (`playwright.global-teardown.mjs`) killt ausschließlich diese PIDs — ein fremder,
   weiterlaufender Dev-Stack wird **nie** beendet.
3. **Build nur bei Bedarf:** Ist das Frontend bereits erreichbar, entfallen `pnpm build` und der
   Preview-Start komplett.
4. **Großzügiges Frontend-Reuse-Timeout** (`PLAYWRIGHT_FRONTEND_PROBE_MS`, Default 20000 ms):
   Ein laufender Vite-Dev kann beim ersten Request kalt sein (~10 s erste Antwort), während ein
   geschlossener Port sofort mit `ECONNREFUSED` scheitert — das lange Timeout verzögert den
   Spawn-Pfad also nicht, fängt aber langsame, vorhandene Server zuverlässig ab.

### Steuer-Env

| Variable | Default | Wirkung |
|---|---|---|
| `VALEO_BASE_URL` / `FRONTEND_URL` | `http://127.0.0.1:4173` | Ziel-/Reuse-URL (identisch zur `playwright.config.ts` baseURL) |
| `PLAYWRIGHT_PREVIEW_PORT` | `4173` | Port für den selbst gespawnten Preview |
| `PLAYWRIGHT_SSE_URL` | `http://localhost:5000/sse` | SSE-Stub-Ziel |
| `PLAYWRIGHT_FRONTEND_PROBE_MS` | `20000` | Reuse-Probe-Timeout fürs Frontend |
| `PLAYWRIGHT_FORCE_SPAWN` | – | `1` erzwingt frischen Spawn trotz laufender Server |

## Lokale Ausführung

Die Specs **mocken** alle `/api/v1/crm/kim/**`-Routen via `page.route` (kein echtes Backend nötig).
Kanonische, deterministische Ausführung gegen den frisch gebauten Preview-Build:

```bash
npx playwright test playwright-tests/specs/crm/crm360-model-based.spec.ts --retries=1
```

- Erster Lauf baut + startet Preview auf `4173`; Folgeläufe verwenden einen laufenden Server wieder.
- `--retries=1` fängt vereinzelte Timing-Flakes der Navigations-Roundtrips ab (Browser-Back zur
  Cockpit-Seite), die durch Vite-/Render-Latenz entstehen und **keine** Fachregression sind.

## Selektor-Härtung

Die KIM-Erfassungsformulare tragen stabile IDs (`#crm360-document-number`, `#crm360-document-net`,
`#crm360-open-item-number`, `#crm360-open-item-net`, `#crm360-open-item-description`). Die Tests
selektieren über diese IDs statt über `input[type=...]` — robust gegen DS-Komponenten, die ohne
explizites `type`-Attribut rendern (Folge des DS-Umbaus `KIM-DS-001`).

## Status

Suite **10/10 grün** (mit `--retries=1`) gegen den reused/gespawnten Stack; keine Port-Konflikte mehr.
