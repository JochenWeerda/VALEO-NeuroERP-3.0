# Wave-69 Status

## Scope

Central Knowledge Core — versionierte Wissensobjekte, einheitliche Retrieval-Schicht und Onboarding-Bundles fuer Mensch und Agent.

## Zielbild

Wave 69 fuehrt einen tenant-agnostischen Knowledge Core ein, der SOPs, Produktwissen, KPI-Hinweise und Supportwissen als versionierte Objekte haelt. Retrieval, Agentenfaehigkeit und Onboarding-Bundles werden ueber stabile Core-Contracts und Process-Kernel-API-Endpunkte exponiert.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/knowledge_core_contracts.py` | Wissensobjekte, Versionen, Retrieval, Onboarding-Bundles | abgeschlossen |
| AP2 | `app/api/v1/endpoints/knowledge_api.py` | Knowledge-Core-HTTP-API | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | Process-Kernel-Surfacing fuer Knowledge-Contracts | abgeschlossen |
| AP4 | `packages/frontend-web/src/lib/api/knowledge.ts` | Frontend-API-Client fuer Knowledge Core | abgeschlossen |

## Abnahmekriterien

- Default-Wissensobjekte sind ladbar; aktive Version ist die juengste freigegebene Version.
- `ist_agentenfaehig()` ist nur fuer freigegebene Markdown-Objekte true.
- Retrieval priorisiert relevante Objekte nach Query und Typ-Filter.
- Onboarding-Bundles aggregieren rollenbezogene Wissensobjekte.
- Kein Import von `app/api/` in `app/core/`.

## Tests

`tests/test_process_kernel_wave69_knowledge_core.py` — 27 Tests

- Contract-Tests fuer Objekte, Retrieval, Bundles und API-Surfacing
- `python -m pytest tests/test_process_kernel_wave69_knowledge_core.py -q --no-cov`

## Status

`abgeschlossen` - 2026-03-18 - Central Knowledge Core Contracts und API-Surfacing lieferfaehig.
