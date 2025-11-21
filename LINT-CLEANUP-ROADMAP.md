# Lint-Aufräum-Roadmap - Umsetzungsstatus

## Fundament gelegt ✅

- [x] ESLint-Command bereits in package.json: `eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0`
- [x] Aktueller Lint-Output dokumentiert: `lint-output-current.txt`
- [x] CI-Konfiguration vorhanden: `.github/workflows/lint-check-all.yml`

## Regel-Cluster - Fortschritt

### Navigation/Core ✅ (TEILWEISE)
- [x] `src/app/navigation/manifest.tsx` - Non-null assertion entfernt
- [x] `src/app/providers/SSEProvider.tsx` - Unused params mit _-Prefix versehen
- [x] `src/components/GlobalButtonHandler.tsx` - Unused param mit _-Prefix versehen

### SSE/Realtime/Lib (IN ARBEIT)
- [ ] `src/components/realtime/RealtimeProvider.tsx` - eslint-disable entfernen, unused params
- [ ] `src/lib/api/*.ts` - URLSearchParams template expressions
- [ ] `src/lib/hooks/useSSE.ts` - eslint-disable entfernen
- [ ] `src/lib/sse-client.ts` - unused params

### Mask-Builder/Forms (IN ARBEIT)
- [x] `src/components/mask-builder/ListReport.tsx` - unused params, prefer-optional-chain
- [ ] `src/components/mask-builder/ObjectPage.tsx` - unused params, no-case-declarations
- [ ] `src/components/mask-builder/OverviewPage.tsx` - unused params, prefer-optional-chain
- [ ] `src/components/mask-builder/Wizard.tsx` - unused params, no-case-declarations
- [ ] `src/components/mask-builder/Worklist.tsx` - unused params
- [ ] `src/components/mask-builder/adapters/l3-mask-adapter.ts` - unused vars
- [ ] `src/components/mask-builder/hooks/useMaskActions.ts` - unused params
- [ ] `src/components/mask-builder/types.ts` - unused params
- [ ] `src/components/mask-builder/utils/api.ts` - restrict-template-expressions
- [ ] `src/components/mask-builder/utils/formatting.ts` - prefer-template
- [ ] `src/components/mask-builder/utils/validation.ts` - no-useless-escape, unused params

### Copilot/AI (IN ARBEIT)
- [x] `src/components/ai/AskVALEO.tsx` - eslint-disable entfernt
- [x] `src/components/copilot/AskValeo.tsx` - unused params (teilweise)
- [ ] `src/components/copilot/SkillRegistry.tsx` - unused params in ExecuteFn (Type-Definition)

### Pages (Finance/Agrar/etc.) (AUSSTEHEND)
- [ ] `src/pages/finance/*.tsx` - wiederkehrende `data`-Parameter
- [ ] `src/pages/agrar/*.tsx` - non-null assertions, prefer-template
- [ ] `src/pages/crm/*.tsx` - non-null assertions, unused imports

### Lib/API (AUSSTEHEND)
- [ ] `src/lib/api/crm.ts` - restrict-template-expressions (URLSearchParams)
- [ ] `src/lib/api/inventory.ts` - restrict-template-expressions
- [ ] `src/lib/api/dashboard.ts` - eslint-disable entfernen
- [ ] `src/lib/api/workflows.ts` - eslint-disable entfernen, no-inferrable-types
- [ ] `src/services/psm-service.ts` - restrict-template-expressions

## Aktueller Status

**Gesamt:** 207 Probleme (28 Errors, 179 Warnings)

**Behoben:**
- Navigation/Core: 3 Warnungen
- Mask-Builder: 3 Warnungen (ListReport)
- Copilot/AI: 2 Warnungen + 1 Error

**Verbleibend:** ~199 Probleme

## Nächste Schritte

1. Mask-Builder-Dateien systematisch durchgehen
2. eslint-disable Direktiven entfernen (28 Errors)
3. URLSearchParams template expressions beheben
4. Wiederkehrende Muster in Pages beheben
5. Finale Prüfung und Tests

