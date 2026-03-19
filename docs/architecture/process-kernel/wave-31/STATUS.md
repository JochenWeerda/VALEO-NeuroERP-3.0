# Wave-31 Status

## Scope
MCP/OpenAPI Tool Contracts fuer externe Agenten (Gap 017) plus Datenqualitaetsregeln (Gap 040)

## Zielbild

Wave 31 schliesst zwei P1-Luecken:
Gap 017 fuer belastbare MCP/OpenAPI Tool Contracts und
Gap 040 fuer gemeinsame Datenqualitaetsregeln auf produktiven Schreibpfaden.

Die MCP Tool Contracts definieren alle Agent-Tools des Process-Kernels
maschinenlesbar mit realen API-Zielen.
Die Datenqualitaetsregeln pruefen Stammdaten und prozessnahe Belege auf
Pflichtfelder, Duplikate, Referenzwerte und Wertebereiche.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `app/core/mcp_tool_contracts.py` | `MCPToolParameter`, `MCPToolContract`; Konvention `valeo_{domain}_{operation}`; `get_process_kernel_mcp_tools()` mit 23 Tool-Contracts und realen API-Zielen | abgeschlossen |
| AP2 | `app/core/mcp_tool_contracts.py` | `MCPToolRegistry`; `validate_all_names()`; `by_domain()`, `by_tool_name()`, `as_mcp_tools()` | abgeschlossen |
| AP3 | `app/api/v1/endpoints/process_kernel_api.py` | `GET /process/agent/tool-registry[?domain=]` | abgeschlossen |
| AP4 | `app/core/data_quality_rules.py` | `DQRegelTyp`, `DQRegel`, `DQRuleSet`; `validate_datensatz(ruleset, datensatz)` -> `DQValidationResult` | abgeschlossen |
| AP5 | `app/core/data_quality_rules.py` | `get_default_dq_rulesets()` mit Default-Regelsets fuer Debitor, Lieferant, Kontrakt, Wiegeschein, Artikel, APRechnung, Abrechnung, ErnteAnnahme, Qualitaetsprotokoll, SelfBilling, FeldbuchMassnahme, KontoauszugImport, JournalImport, Zahlungsimport, PayrollConnectorImport, AssetLedgerConnectorImport und DailyPriceImport | abgeschlossen |
| AP6 | `app/api/v1/endpoints/process_kernel_api.py` | `POST /process/data-quality/validate` plus `GET /process/data-quality/rulesets` | abgeschlossen |

## Abnahmekriterien

- Alle MCP Tool Contracts folgen der Konvention `valeo_{domain}_{operation}` und sind maschinell pruefbar
- Mindestens 20 Tool-Contracts sind abgedeckt
- `validate_datensatz()` erkennt Pflichtfeld-, Duplikat-, Referenz-, Format- und Bereichsverletzungen
- Default-Regelsets fuer Debitor, Lieferant, Kontrakt, Wiegeschein, Artikel, APRechnung, Abrechnung, ErnteAnnahme, Qualitaetsprotokoll, SelfBilling, FeldbuchMassnahme, KontoauszugImport, JournalImport, Zahlungsimport, PayrollConnectorImport, AssetLedgerConnectorImport und DailyPriceImport sind vollstaendig und validierbar
- Kein Import von `app/api/` in `app/core/`

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave31_mcp_dq.py` + `tests/test_process_kernel_wave31_dq_write_enforcement.py` + `tests/test_process_kernel_wave31_dq_extended_write_paths.py` + `tests/test_process_kernel_wave31_dq_import_edge_paths.py` + `tests/test_process_kernel_wave31_dq_finance_import_paths.py` + `tests/test_process_kernel_wave31_dq_connector_imports.py` + `tests/test_process_kernel_wave31_dq_daily_price_imports.py` + `tests/test_process_kernel_wave31_dq_feldbuch_service.py` + `tests/test_process_kernel_wave31_dq_quality_protocol_service.py` | 105 | MCP/OpenAPI Tool-Contracts inkl. Route-gegen-Contract-Verifikation; DQ-Regeln und Default-RuleSets; API-Endpoints; Write-Path-Enforcement fuer Debitor, Kreditor, Agrar-Kontrakt, Artikel, Wiegeschein, Customer-Proxy, CSV-Importe, AP-Rechnung, Settlement, ErnteAnnahme, Qualitaetsprotokoll, Self-Billing, Feldbuch-Import, Kontoauszugsimport, Journal-Import, Payment-Matching-Import, FIBU-Connector-Importe fuer Payroll und Asset Ledger sowie Daily-Price-CSV/JSON-Importe; service-seitiges Feldbuch- und Quality-Protocol-Enforcement ohne stilles Zeilenskip |

**Gesamt Wave 31: 105 Tests gruen**

## Gaps geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 017 | MCP/OpenAPI Tool Contracts - 20 produktive Agent-Tools freigeschaltet | `mcp_tool_contracts.py`: 23 Tool-Contracts in 6 Domains; Konvention `valeo_{domain}_{operation}`; `MCPToolRegistry` mit `by_domain()`, `by_tool_name()`, `as_mcp_tools()`, `validate_all_names()`; alle `api_endpoint`-Eintraege gegen den real registrierten FastAPI-Router verifiziert; API `GET /process/agent/tool-registry[?domain=]` |
| Gap 040 | Datenqualitaetsregeln - Stammdatenfehler -50% | `data_quality_rules.py`: `DQRegelTyp`, `DQRegel`, `DQRuleSet`, `validate_datensatz()`, 17 Default-Regelsets; gemeinsames Write-Path-Enforcement ueber `data_quality_enforcement.py` in `debtors.py`, `creditors.py`, `agrar_contracts.py`, `articles.py`, `weighing_tickets.py`, `customers.py`, `harvest_acceptance.py`, `quality_protocols.py`, `self_billing.py`, `ap_invoices.py` und `agrar_settlements.py`; strukturierte CSV- und Integrationsimporte in `compat.py`, `portal_feldbuch.py`, `modules/agrar/services/feldbuch_service.py`, `modules/agrar/services/quality_protocol_service.py`, `bank_statement_import.py`, `bulk_journal_import.py`, `payment_matching.py`, `daily_prices.py` und den FIBU-Connector-Parsern fuer `PAYROLL` und `ASSET_LEDGER` validieren dieselben Kernvertraege vor Persistenz statt lokaler Parser-Checks; `gap.py` wurde geprueft, aber als Analyse-/Debug-Schicht und nicht als produktiver CSV-Write-Pfad eingeordnet; der produktive ETL-Loader `scripts/import_l3.py` bricht bei Mapping-/Datei-/Header-Drift jetzt ueber einen expliziten Source-Contract ab statt Tabellen still per `continue` zu ueberspringen; API `GET /process/data-quality/rulesets` plus `POST /process/data-quality/validate` |

## Status
`abgeschlossen` - 2026-03-15 - 105 Tests gruen, Gaps 017 und 040 inkl. gemeinsamem Write-Path-Enforcement, importseitigem Finance-DQ-Enforcement, Connector-DQ fuer Payroll/Asset-Ledger, Daily-Price-Import-DQ sowie service-seitigem Feldbuch- und Quality-Protocol-Enforcement belastbar geschlossen

## Angrenzende ETL-Haertung

- `scripts/import_l3.py` verwendet jetzt dieselbe strikte Mapping-Topologie wie `scripts/validate_mapping.py` und beendet produktive L3-Dateiimporte bei fehlenden Exportdateien, leeren Tabellen, Header-Drift oder ungueltigen JSON-Zeilen deterministisch.
- Verifiziert ueber `tests/l3_import/test_import_l3.py` und `tests/l3_import/test_validate_mapping.py` mit `16` grünen Tests.
- `scripts/migration/migrate_data.py` wurde geprueft und als Batch-Migrationspfad ohne lokale CSV-Zeilenlogik eingeordnet; der tatsaechliche produktive Restpfad lag in `scripts/simple_activate_reflect_archive.py`.
- `scripts/simple_activate_reflect_archive.py` verwendet jetzt einen gemeinsamen Archiv-Datei-Contract fuer `tasks`, `context` und `README`: Pflichtdateien, Null-Bytes und unlesbare Inhalte fuehren zu einem harten `ReflectArchiveSourceError` statt zu lokalem Skip-/Warning-Verhalten.
- Verifiziert ueber `tests/test_reflect_archive_loader.py` mit `5` grünen Tests.
- `scripts/activate_pipeline_integration.py` und `scripts/apm_pipeline_runner.py` verwenden jetzt mit `scripts/apm_pipeline_contract.py` denselben JSON-Konfigurationsvertrag fuer `config/apm_pipeline_integration.json` statt duplizierter `FileNotFound`-/`JSONDecodeError`-Sonderpfade.
- Der gemeinsame Contract prueft Top-Level- und Feldtypen fuer `pipeline_integration`, `pipelines` und `apm_phases`; Schema-Drift fuehrt zu einem harten `PipelineConfigContractError`.
- Verifiziert ueber `tests/test_apm_pipeline_contract.py` mit `4` grünen Tests.
- `scripts/activate_pipeline_mode.py` verwendet jetzt denselben JSON-State-Contract statt auf beliebige Loaderfehler mit einem stillen `{\"pipelines\": {}}`-Fallback zu reagieren.
- Die fruehere Script- und Dashboard-Nebenwelt ist inzwischen aus dem produktiven Anwendungspfad entfernt; die fachliche Orchestrierung liegt unter `app/agents`.
