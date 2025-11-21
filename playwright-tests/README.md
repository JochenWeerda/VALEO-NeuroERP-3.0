# VALEO-NeuroERP - E2E Test Suite

Hybride UAT-Test-Suite mit automatisierten Playwright-Tests und manuellen Checklisten.

---

## Quick Start

### 1. Installation

```bash
# Playwright installieren (falls noch nicht geschehen)
pnpm install

# Playwright-Browser herunterladen
pnpm exec playwright install chromium
```

### 2. Environment vorbereiten

Erstelle `.env` im Root mit:

```env
VALEO_BASE_URL=http://localhost:3000
VALEO_TENANT=QA-UAT-01
VALEO_USER_ADMIN=admin@example.com
VALEO_PASS_ADMIN=admin123
```

### 3. Anwendung starten

```bash
# Backend
python -m uvicorn main:app --reload

# Frontend (separates Terminal)
cd packages/frontend-web
pnpm dev
```

### 4. Tests ausführen

```bash
# Smoke-Tests (schnell, ~5 Min)
pnpm test:e2e:smoke

# Fallback-Verifikation
pnpm test:e2e:fallback

# Full UAT (alle Tests)
pnpm test:e2e:full

# Report anzeigen
pnpm test:e2e:report
```

---

## Struktur

```
playwright-tests/
├── helpers/
│   ├── fallbackDetector.ts   # 3-Ebenen-Fallback-Erkennung
│   ├── api.ts                 # Auth & CRUD-Wrapper
│   └── reporters.ts           # Coverage-Matrix & Bug-List
├── fixtures/
│   └── testSetup.ts           # Auto-Login, Tenant, FallbackDetector
├── specs/
│   ├── sales/                 # Sales Domain Tests
│   ├── agrar/                 # Agrar Domain Tests
│   ├── crm/                   # CRM Domain Tests
│   ├── finance/               # Finance Domain Tests
│   ├── inventory/             # Inventory Domain Tests
│   └── fallback-verification.spec.ts
└── artifacts/                 # HAR, Screenshots, Videos (generiert)
```

---

## Test-Tags

- `@smoke`: Schnelle Smoke-Tests (CRUD, Export, Print)
- `@full`: Vollständige UAT-Tests
- `@fallback`: Fallback-Verifikation

### Spezifische Domain ausführen

```bash
# Nur Sales-Tests
pnpm exec playwright test specs/sales/

# Nur CRM-Tests
pnpm exec playwright test specs/crm/

# Nur PSM-Tests
pnpm exec playwright test specs/agrar/psm-smoke.spec.ts
```

---

## Fallback-System

### 3-Ebenen-Architektur

1. **Level 1:** Seitenspezifischer onClick-Handler
2. **Level 2:** `useListActions`-Hook (seiten-spezifisch)
3. **Level 3:** `GlobalButtonHandler` (Default)

### Console-Logging

Jede Ebene loggt in die Console:

```
FB:LEVEL=1 PAGE=angebote ACTION=export
FB:LEVEL=2 PAGE=kontakte-liste ACTION=print
FB:LEVEL=3 PAGE=unknown ACTION=delete
```

Die Tests extrahieren diese Logs automatisch und befüllen die Coverage-Matrix.

---

## Manuelle Tests

### Checklisten

Siehe `docs/uat/checklisten/`:

- `SALES.md`: Angebote, Order-Flow
- `AGRAR.md`: PSM, Saatgut, Dünger
- `CRM.md`: Kontakte, Leads, Aktivitäten
- `FINANCE.md`: Buchungsjournal, Debitoren, OP
- `INVENTORY.md`: Artikel, Lager, Charge

### Smoke-Runbook

30-Min-Quick-Check: `docs/uat/SMOKE-RUNBOOK.md`

---

## Artefakte

### Automatisch generiert

- **HAR-Files:** `artifacts/<runID>/<domain>/*.har`
- **Screenshots:** `artifacts/<runID>/<domain>/*.png`
- **Videos:** `artifacts/<runID>/<domain>/*.webm`
- **Console-Logs:** `artifacts/<runID>/<domain>/console.log`
- **Traces:** `artifacts/<runID>/<domain>/trace.zip`

### Berichte

- **Coverage-Matrix:** `docs/uat/COVERAGE-MATRIX.csv`
- **Bug-List:** `docs/uat/BUGLIST.json`
- **UAT-Summary:** `docs/uat/UAT-SUMMARY.md` (nach Full-Run)

---

## CI/CD

### GitHub Actions

- **e2e-smoke.yml:** Push/PR → Matrix (5 Domains parallel)
- **e2e-full.yml:** Nightly (2 Uhr) + manuell

### Artefakte in CI

Alle Artefakte werden als GitHub Actions Artifacts hochgeladen (Retention: 7-90 Tage).

---

## Debugging

### Einzelner Test im UI-Mode

```bash
pnpm exec playwright test --ui specs/sales/angebote-smoke.spec.ts
```

### Mit Trace

```bash
pnpm exec playwright test --trace on specs/sales/angebote-smoke.spec.ts
pnpm exec playwright show-trace trace.zip
```

### Mit Debug-Logging

```bash
DEBUG=pw:api pnpm test:e2e:smoke
```

---

## Häufige Probleme

### "Browser not found"

```bash
pnpm exec playwright install chromium
```

### "Connection refused"

Stelle sicher, dass Backend (`:8000`) und Frontend (`:3000`) laufen.

### "Login failed"

Prüfe `.env`:
- `VALEO_USER_ADMIN=admin@example.com`
- `VALEO_PASS_ADMIN=admin123`

Falls Backend-Auth nicht implementiert: Tests laufen trotzdem (Warnung in Console).

---

## Erweiterung

### Neue Domain hinzufügen

1. Erstelle `playwright-tests/specs/<domain>/`
2. Erstelle `<domain>-smoke.spec.ts`
3. Importiere Fixtures: `import { test, expect } from '../../fixtures/testSetup'`
4. Nutze `@smoke` Tag
5. Füge zu `docs/uat/checklisten/<DOMAIN>.md` hinzu

### Neue Test-Rolle

In `helpers/api.ts` → `TEST_USERS` erweitern, dann in `fixtures/testSetup.ts` Fixture hinzufügen.

---

## Dokumentation

- **Testplan:** `docs/uat/TESTPLAN.md`
- **Backend-Status:** `docs/uat/BACKEND-STATUS.yml`
- **Implementierungs-Status:** `docs/uat/UAT-IMPLEMENTATION-COMPLETE.md`

---

**Happy Testing!** 🎯

