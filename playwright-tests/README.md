***REMOVED*** VALEO-NeuroERP - E2E Test Suite

Hybride UAT-Test-Suite mit automatisierten Playwright-Tests und manuellen Checklisten.

---

***REMOVED******REMOVED*** Quick Start

***REMOVED******REMOVED******REMOVED*** 1. Installation

```bash
***REMOVED*** Playwright installieren (falls noch nicht geschehen)
pnpm install

***REMOVED*** Playwright-Browser herunterladen
pnpm exec playwright install chromium
```

***REMOVED******REMOVED******REMOVED*** 2. Environment vorbereiten

Erstelle `.env` im Root mit:

```env
VALEO_BASE_URL=http://localhost:3000
VALEO_TENANT=QA-UAT-01
VALEO_USER_ADMIN=admin@example.com
VALEO_PASS_ADMIN=admin123
```

***REMOVED******REMOVED******REMOVED*** 3. Anwendung starten

```bash
***REMOVED*** Backend
python -m uvicorn main:app --reload

***REMOVED*** Frontend (separates Terminal)
cd packages/frontend-web
pnpm dev
```

***REMOVED******REMOVED******REMOVED*** 4. Tests ausführen

```bash
***REMOVED*** Smoke-Tests (schnell, ~5 Min)
pnpm test:e2e:smoke

***REMOVED*** Fallback-Verifikation
pnpm test:e2e:fallback

***REMOVED*** Full UAT (alle Tests)
pnpm test:e2e:full

***REMOVED*** Report anzeigen
pnpm test:e2e:report
```

---

***REMOVED******REMOVED*** Struktur

```
playwright-tests/
├── helpers/
│   ├── fallbackDetector.ts   ***REMOVED*** 3-Ebenen-Fallback-Erkennung
│   ├── api.ts                 ***REMOVED*** Auth & CRUD-Wrapper
│   └── reporters.ts           ***REMOVED*** Coverage-Matrix & Bug-List
├── fixtures/
│   └── testSetup.ts           ***REMOVED*** Auto-Login, Tenant, FallbackDetector
├── specs/
│   ├── sales/                 ***REMOVED*** Sales Domain Tests
│   ├── agrar/                 ***REMOVED*** Agrar Domain Tests
│   ├── crm/                   ***REMOVED*** CRM Domain Tests
│   ├── finance/               ***REMOVED*** Finance Domain Tests
│   ├── inventory/             ***REMOVED*** Inventory Domain Tests
│   └── fallback-verification.spec.ts
└── artifacts/                 ***REMOVED*** HAR, Screenshots, Videos (generiert)
```

---

***REMOVED******REMOVED*** Test-Tags

- `@smoke`: Schnelle Smoke-Tests (CRUD, Export, Print)
- `@full`: Vollständige UAT-Tests
- `@fallback`: Fallback-Verifikation

***REMOVED******REMOVED******REMOVED*** Spezifische Domain ausführen

```bash
***REMOVED*** Nur Sales-Tests
pnpm exec playwright test specs/sales/

***REMOVED*** Nur CRM-Tests
pnpm exec playwright test specs/crm/

***REMOVED*** Nur PSM-Tests
pnpm exec playwright test specs/agrar/psm-smoke.spec.ts
```

---

***REMOVED******REMOVED*** Fallback-System

***REMOVED******REMOVED******REMOVED*** 3-Ebenen-Architektur

1. **Level 1:** Seitenspezifischer onClick-Handler
2. **Level 2:** `useListActions`-Hook (seiten-spezifisch)
3. **Level 3:** `GlobalButtonHandler` (Default)

***REMOVED******REMOVED******REMOVED*** Console-Logging

Jede Ebene loggt in die Console:

```
FB:LEVEL=1 PAGE=angebote ACTION=export
FB:LEVEL=2 PAGE=kontakte-liste ACTION=print
FB:LEVEL=3 PAGE=unknown ACTION=delete
```

Die Tests extrahieren diese Logs automatisch und befüllen die Coverage-Matrix.

---

***REMOVED******REMOVED*** Manuelle Tests

***REMOVED******REMOVED******REMOVED*** Checklisten

Siehe `docs/uat/checklisten/`:

- `SALES.md`: Angebote, Order-Flow
- `AGRAR.md`: PSM, Saatgut, Dünger
- `CRM.md`: Kontakte, Leads, Aktivitäten
- `FINANCE.md`: Buchungsjournal, Debitoren, OP
- `INVENTORY.md`: Artikel, Lager, Charge

***REMOVED******REMOVED******REMOVED*** Smoke-Runbook

30-Min-Quick-Check: `docs/uat/SMOKE-RUNBOOK.md`

---

***REMOVED******REMOVED*** Artefakte

***REMOVED******REMOVED******REMOVED*** Automatisch generiert

- **HAR-Files:** `artifacts/<runID>/<domain>/*.har`
- **Screenshots:** `artifacts/<runID>/<domain>/*.png`
- **Videos:** `artifacts/<runID>/<domain>/*.webm`
- **Console-Logs:** `artifacts/<runID>/<domain>/console.log`
- **Traces:** `artifacts/<runID>/<domain>/trace.zip`

***REMOVED******REMOVED******REMOVED*** Berichte

- **Coverage-Matrix:** `docs/uat/COVERAGE-MATRIX.csv`
- **Bug-List:** `docs/uat/BUGLIST.json`
- **UAT-Summary:** `docs/uat/UAT-SUMMARY.md` (nach Full-Run)

---

***REMOVED******REMOVED*** CI/CD

***REMOVED******REMOVED******REMOVED*** GitHub Actions

- **e2e-smoke.yml:** Push/PR → Matrix (5 Domains parallel)
- **e2e-full.yml:** Nightly (2 Uhr) + manuell

***REMOVED******REMOVED******REMOVED*** Artefakte in CI

Alle Artefakte werden als GitHub Actions Artifacts hochgeladen (Retention: 7-90 Tage).

---

***REMOVED******REMOVED*** Debugging

***REMOVED******REMOVED******REMOVED*** Einzelner Test im UI-Mode

```bash
pnpm exec playwright test --ui specs/sales/angebote-smoke.spec.ts
```

***REMOVED******REMOVED******REMOVED*** Mit Trace

```bash
pnpm exec playwright test --trace on specs/sales/angebote-smoke.spec.ts
pnpm exec playwright show-trace trace.zip
```

***REMOVED******REMOVED******REMOVED*** Mit Debug-Logging

```bash
DEBUG=pw:api pnpm test:e2e:smoke
```

---

***REMOVED******REMOVED*** Häufige Probleme

***REMOVED******REMOVED******REMOVED*** "Browser not found"

```bash
pnpm exec playwright install chromium
```

***REMOVED******REMOVED******REMOVED*** "Connection refused"

Stelle sicher, dass Backend (`:8000`) und Frontend (`:3000`) laufen.

***REMOVED******REMOVED******REMOVED*** "Login failed"

Prüfe `.env`:
- `VALEO_USER_ADMIN=admin@example.com`
- `VALEO_PASS_ADMIN=admin123`

Falls Backend-Auth nicht implementiert: Tests laufen trotzdem (Warnung in Console).

---

***REMOVED******REMOVED*** Erweiterung

***REMOVED******REMOVED******REMOVED*** Neue Domain hinzufügen

1. Erstelle `playwright-tests/specs/<domain>/`
2. Erstelle `<domain>-smoke.spec.ts`
3. Importiere Fixtures: `import { test, expect } from '../../fixtures/testSetup'`
4. Nutze `@smoke` Tag
5. Füge zu `docs/uat/checklisten/<DOMAIN>.md` hinzu

***REMOVED******REMOVED******REMOVED*** Neue Test-Rolle

In `helpers/api.ts` → `TEST_USERS` erweitern, dann in `fixtures/testSetup.ts` Fixture hinzufügen.

---

***REMOVED******REMOVED*** Dokumentation

- **Testplan:** `docs/uat/TESTPLAN.md`
- **Backend-Status:** `docs/uat/BACKEND-STATUS.yml`
- **Implementierungs-Status:** `docs/uat/UAT-IMPLEMENTATION-COMPLETE.md`

---

**Happy Testing!** 🎯

