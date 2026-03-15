# Wave-31 Status

## Scope
MCP/OpenAPI Tool Contracts fuer externe Agenten (Gap 017) + Datenqualitaetsregeln (Gap 040)

## Zielbild

Wave 31 schliesst zwei P1-Luecken:
Gap 017 (MCP/OpenAPI Tool Contracts — 20 produktive Agent-Tools freigeschaltet)
und Gap 040 (Datenqualitaetsregeln — Stammdatenfehler -50%).

Die MCP Tool Contracts definieren alle Agent-Tools des Process-Kernels
maschinenlesbar (Name, Beschreibung, Input-/Output-Schema) — kompatibel
mit dem Model Context Protocol (MCP) und OpenAPI Tool-Schemas.
Die Datenqualitaetsregeln pruefen Stammdaten auf Pflichtfelder, Duplikate,
Referenzintegritaet und Formatvorgaben — ohne Datenbankzugriff im Core-Layer.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/mcp_tool_contracts.py` | `MCPToolParameter`, `MCPToolContract`; Konvention `valeo_{domain}_{operation}`; `get_process_kernel_mcp_tools()` — 23 Tool-Contracts | abgeschlossen |
| AP2 | `app/core/mcp_tool_contracts.py` | `MCPToolRegistry`; `validate_all_names()` Konventions-Pruefung; `by_domain()`, `by_tool_name()`, `as_mcp_tools()` | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/agent/tool-registry[?domain=]` | abgeschlossen |
| AP4 | `app/core/data_quality_rules.py` | `DQRegelTyp`, `DQRegel`, `DQRuleSet`; `validate_datensatz(ruleset, datensatz)` → `DQValidationResult` | abgeschlossen |
| AP5 | `app/core/data_quality_rules.py` | `get_default_dq_rulesets()` — Default-Regelsets fuer Lieferant, Kontrakt, Wiegeschein, Artikel | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `POST /process/data-quality/validate` + `GET /process/data-quality/rulesets` | abgeschlossen |

## Abnahmekriterien

- Alle MCP Tool Contracts folgen `valeo_{domain}_{operation}`-Konvention, maschinell pruefbar
- Mindestens 20 Tool-Contracts abgedeckt (agrar, finance, workflow, compliance, process)
- `validate_datensatz()` erkennt PFLICHTFELD_FEHLT, DUPLIKAT_VERDACHT, REFERENZ_FEHLT, FORMAT_VERLETZUNG, BEREICH_VERLETZUNG
- Default-Regelsets fuer Lieferant/Kontrakt/Wiegeschein/Artikel vollstaendig und validierbar
- Kein Import von `app/api/` in `app/core/`

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave31_mcp_dq.py` | 49 | AP1: MCPToolContract (8 Tests); AP2: MCPToolRegistry (13 Tests); AP4: DQRegel/DQRuleSet (5 Tests); AP5: validate_datensatz/default rulesets (16 Tests); AP3/AP6: API-Endpoints (7 Tests) |

**Gesamt Wave 31: 49 Tests gruen**

## Gaps geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 017 | MCP/OpenAPI Tool Contracts — 20 produktive Agent-Tools freigeschaltet | `mcp_tool_contracts.py`: 23 Tool-Contracts in 6 Domains (agrar×6, finance×5, workflow×4, compliance×3, process×3, inventory×2); Konvention `valeo_{domain}_{operation}`; `MCPToolRegistry` mit `by_domain()`, `by_tool_name()`, `as_mcp_tools()`, `validate_all_names()`; API `GET /process/agent/tool-registry[?domain=]` |
| Gap 040 | Datenqualitaetsregeln — Stammdatenfehler -50% | `data_quality_rules.py`: `DQRegelTyp` (PFLICHTFELD/DUPLIKAT_VERDACHT/REFERENZ_FEHLT/FORMAT_VERLETZUNG/BEREICH_VERLETZUNG), `DQRegel`, `DQRuleSet`, `validate_datensatz()`, 4 Default-Regelsets (Lieferant/Kontrakt/Wiegeschein/Artikel); API `GET /process/data-quality/rulesets` + `POST /process/data-quality/validate` |

## Status
`abgeschlossen` — 2026-03-15 — 49 Tests gruen, Gaps 017 + 040 geschlossen
