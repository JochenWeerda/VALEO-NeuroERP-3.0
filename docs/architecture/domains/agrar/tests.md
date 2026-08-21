---
title: Agrar — Tests
type: reference
audience: [qa]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-06-27
version: 1.0.0
---

# Agrar — Tests

```bash
pytest tests/test_agri*.py tests/test_agrar*.py tests/test_drying_rule_engine.py
pytest tests/test_rations_herd_data_connectors.py -q --no-cov
pytest tests/test_feed_advice_screen_definition.py tests/test_workspace_cockpits_uix061.py -q --no-cov
pytest tests/test_rations_lifecycle_domain.py tests/test_rations_lifecycle_api.py -q --no-cov
pytest tests/test_rations_readiness.py -q --no-cov
pytest tests/test_rations_controlling.py -q --no-cov
pytest tests/test_feeding_groups_core.py tests/test_rations_lifecycle_api.py -q --no-cov
pytest tests/test_feeding_reference_data.py tests/test_rations_reference_data_api.py -q --no-cov
pytest tests/test_feeding_feed_catalog.py tests/test_feeding_feed_catalog_api.py tests/test_futter_stamm.py -q --no-cov
pytest tests/test_feeding_feed_analysis.py tests/test_feeding_feed_analysis_api.py tests/test_grundfutteranalysen.py -q --no-cov
pytest tests/test_feeding_ration_editor.py tests/test_feeding_ration_editor_api.py -q --no-cov
pytest tests/test_feeding_ration_templates.py tests/test_feeding_ration_templates_api.py -q --no-cov
pytest tests/test_feeding_plan.py tests/test_feeding_plan_api.py -q --no-cov
pytest tests/test_feeding_events.py tests/test_feeding_import_monitor_api.py -q --no-cov
pytest tests/test_feeding_measure_lifecycle.py tests/test_feeding_measure_lifecycle_api.py tests/test_feeding_consulting_report_api.py -q --no-cov
```

Produktionsleitstand:
`pytest tests/test_production_control.py -q --no-cov` und
`vitest run src/__tests__/pages/produktion/produktionsleitstand.test.tsx`.

Frontend: `packages/frontend-web/src/pages/agrar/`

Fuetterungsberatung UX: `packages/frontend-web/src/__tests__/pages/portal/feed-advice-entry.test.tsx`

Analyse-UX: `packages/frontend-web/src/__tests__/features/feed-advice/feeding-analysis-detail.test.tsx`

Rationseditor-Grenzen: `packages/frontend-web/src/__tests__/features/feed-advice/ration-editor.test.tsx`

Betriebsakte/Vorlagen: `packages/frontend-web/src/__tests__/features/feed-advice/feeding-business-detail.test.tsx`

Plan-ObjectPage/Mobil: `feeding-plan-detail.test.tsx`,
`feeding-plan-mobile.test.tsx` und `tests/e2e/rations-mobile-feeding.spec.ts`.

Lifecycle Browser-Abnahme:
`packages/frontend-web/tests/e2e/feed-advice-lifecycle.spec.ts`

Massnahmen-/Beratungs-UI:
`packages/frontend-web/src/__tests__/features/feed-advice/consulting-cases.test.tsx`
