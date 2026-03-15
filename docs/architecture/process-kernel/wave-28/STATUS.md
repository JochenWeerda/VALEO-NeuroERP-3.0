# Wave-28 Status

## Scope
SLA-Eskalations-Engine (Gap 013) + OpenTelemetry Span-Contracts (Gap 039)

## Zielbild

Wave 28 liefert produktionsreife Observability: Gap 013 (SLA/Timeout/Eskalationsknoten
standardisiert, >=95% SLA-Einhaltung) und Gap 039 (End-to-End Tracing UI→API→DB→Worker,
MTTR -40%). Die SLA-Eskalations-Engine wertet Prozessfristen aus und erzeugt typisierte
Eskalationsstufen. Die OTel-Span-Contracts geben Span-Namen, Attribute und Sampling-Regeln
verbindlich vor — ohne Library-Abhaengigkeit im app/core/-Layer.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/sla_eskalation_engine.py` | `SLABreachEvaluation`, `EskalationsStufe` (WARNUNG/KRITISCH/BLOCKIERT); `evaluate_sla_breach()` aus Ist-Dauer + Policy | abgeschlossen |
| AP2 | `app/core/otel_span_contracts.py` | `SpanContract`, `SpanAttributeSchema`; Span-Name-Konvention `valeo.{domain}.{operation}`; `get_process_kernel_spans()` | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/sla/eskalationen` — alle aktiven Eskalationen; `GET /process/sla/eskalationen/{prozess_key}` | abgeschlossen |
| AP4 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/otel/span-registry` — registrierte Span-Contracts | abgeschlossen |
| AP5 | `app/core/sla_eskalation_engine.py` | `validate_sla_policy()` — Konsistenzpruefung (Warnung < Kritisch < Max) | abgeschlossen |
| AP6 | `app/core/sla_eskalation_engine.py` | `get_default_sla_eskalations_policies()` — Default-Policies fuer agrar_settlement, wareneingang, qualitaetspruefung, intrastat_meldung | abgeschlossen |

## Abnahmekriterien

- `evaluate_sla_breach()` klassifiziert korrekt in OK/WARNUNG/KRITISCH/BLOCKIERT
- Grenzwerte werden deterministisch ausgewertet (Warnung < Kritisch < Blockiert)
- `validate_sla_policy()` erkennt inkonsistente Schwellenwerte
- Span-Contracts folgen `valeo.{domain}.{operation}`-Konvention, maschinell pruefbar
- Kein Import von `opentelemetry`-Library in `app/core/` (reiner Contract-Layer)
- Keine Schichtverletzungen

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave28_sla_otel.py` | 47 | AP1: evaluate_sla_breach() (11 Tests, alle Stufen + Grenzwerte); AP5: validate_sla_policy() (8 Tests, alle Violation-Codes); AP6: Default-Policies (6 Tests); AP2: SpanContract/Registry (12 Tests, Convention, Sampling, Source-Check); AP3/AP4: API-Endpoints (10 Tests) |

**Gesamt Wave 28: 47 Tests gruen**

## Gaps geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 013 | SLA/Timeout/Eskalationsknoten standardisiert, >=95% SLA-Einhaltung | `sla_eskalation_engine.py`: `evaluate_sla_breach()` (OK/WARNUNG/KRITISCH/BLOCKIERT), `validate_sla_policy()`, 6 Default-Policies fuer Agrar-Kernprozesse; API-Endpoints `GET /process/sla/eskalationen{/prozess_key}` |
| Gap 039 | End-to-End Tracing UI→API→DB→Worker, MTTR -40% | `otel_span_contracts.py`: 14 SpanContracts (5 Domains), `valeo.{domain}.{operation}`-Konvention, kein OTel-Library-Import im Core-Layer; API-Endpoint `GET /process/otel/span-registry` |

## Status
`abgeschlossen` — 2026-03-15 — 47 Tests gruen, Gaps 013 + 039 geschlossen
