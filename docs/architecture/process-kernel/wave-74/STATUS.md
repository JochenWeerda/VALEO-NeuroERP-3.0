# Wave-74 Status

## Scope

Wave 74 umfasst **zwei unabhaengige Arbeitspakete** unter derselben Wellennummer. Beide sind abgeschlossen; die Testdateien spiegeln die getrennten Scopes wider (kein gemeinsamer Modulpfad).

## Zielbild

1. **AP-A — Knowledge Graph:** Traversierbarer Wissensgraph ueber Rollen, Prozesse, Entitaeten und Knowledge-Objekte fuer Agenten und Kanaele.
2. **AP-B — Rationsoptimierung (GfE-2023):** Fachliche Naehrstoff-Contracts und ERP-Proxy-Verhalten gegen den Rationsoptimierungs-Microservice.

> **Doppelscope-Klaerung:** `test_process_kernel_wave74_knowledge_graph.py` und `test_process_kernel_wave74_rations_optimization.py` gehoeren **beide** zu Wave 74, decken aber unterschiedliche Domains ab. Es handelt sich nicht um einen Testfehler, sondern um zwei parallele Lieferstrange derselben Wave.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP-A1 | `app/core/knowledge_graph.py` | Runtime-Graph aus Knowledge-Objekten | abgeschlossen |
| AP-A2 | `app/api/v1/endpoints/channel_work_surfaces.py` | Graph-Traversierung fuer Kanaele | abgeschlossen |
| AP-B1 | `rationsoptimierung/` (Microservice) | GfE-2023 Naehrstoffformeln | abgeschlossen |
| AP-B2 | ERP-Proxy-Router | 503 wenn `RATIONS_OPTIMIZATION_URL` fehlt | abgeschlossen |

## Abnahmekriterien

### AP-A — Knowledge Graph

- Graph enthaelt Knoten fuer Wissen, Rollen, Prozesse und Entitaeten.
- Traversierung liefert nachvollziehbare Nachbarschaft und Pfade.
- Kanal-Endpunkte koennen Graph-Snapshots ausliefern.

### AP-B — Rationsoptimierung

- GfE-2023-Contracts berechnen Naehrstoffwerte deterministisch.
- ERP-Proxy antwortet mit 503, solange der Microservice nicht konfiguriert ist.
- Konfigurierter Proxy leitet Anfragen an den Rationsoptimierungs-Service weiter.

## Tests

| Suite | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave74_knowledge_graph.py` | 9 | AP-A Knowledge Graph |
| `tests/test_process_kernel_wave74_rations_optimization.py` | 28 | AP-B GfE-2023 + Proxy |
| **Summe Wave 74** | **37** | |

- `python -m pytest tests/test_process_kernel_wave74_knowledge_graph.py tests/test_process_kernel_wave74_rations_optimization.py -q --no-cov`

## Status

`abgeschlossen` - 2026-03-19 - Knowledge Graph und Rationsoptimierungs-Contracts formal nachgewiesen.
