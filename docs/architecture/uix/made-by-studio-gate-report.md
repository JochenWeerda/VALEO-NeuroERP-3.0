# Made-by-Studio Gate-Report

Stand: 2026-10-22 (erzeugt mit `python scripts/verify_made_by_studio_gates.py`).

Bezug: [Made by Studio — Qualitätsversprechen](made-by-studio-qualitaetsversprechen.md).

## Zusammenfassung

| Metrik | Wert |
|--------|------|
| Registrierte ScreenDefinitions | 749 |
| Gate A (Meridian & Struktur) grün | 744 |
| Gate B (Rechte & Aktionen) grün | 749 |
| Gate C (Compiler & Kanal) grün | 718 |
| Gate E (Runtime-Verdrahtung) grün | 673 |
| Studio-Draft-Projektion ohne Violations | 749 |
| Ø Advisory-Score (Gate-C-Metrik) | 0.99 |
| Screen-IDs in runtime_wired-Routen (gesamt) | 919 |

Gate D (Browser/Image) wird hier nicht automatisiert geprüft.

## Gate A — offene Screen-IDs (5)

- `finance/umsatz`: readiness:[table_profile] expected layout.tableProfile=financial for finance/umsatz
- `inventory-reports`: readiness:[table_profile] expected layout.tableProfile=inventory for inventory-reports
- `lager/silo-uebersicht`: readiness:[table_profile] expected layout.tableProfile=inventory for lager/silo-uebersicht
- `pos/tse-journal`: readiness:[table_profile] expected layout.tableProfile=financial for pos/tse-journal
- `workflow/flow-spine-inventory-to-settlement`: readiness:[table_profile] expected layout.tableProfile=inventory for workflow/flow-spine-inventory-to-settlement

## Gate B — offene Screen-IDs (0)

Keine — alle grün.

## Gate C — offene Screen-IDs (31)

- `agrar/schlaege-karte-liste`: compiler:[table_columns_complete] tables with <2 non-trivial columns: list
- `einkauf/reports`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `fibu/abschluss-checklist-detail`: api_bindung:endpoint_nicht_in_openapi:/api/v1/fibu/anlagen/{entity_id}
- `fibu/buchhaltungsuebersicht`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `fibu/geschaeftsjahre`: api_bindung:endpoint_nicht_in_openapi:/api/v1/fibu/anlagen/{entity_id}
- `fibu/op-skonto-auszifferung`: api_bindung:endpoint_nicht_in_openapi:/api/v1/fibu/anlagen/{entity_id}
- `fibu/stammdaten`: api_bindung:endpoint_nicht_in_openapi:/api/v1/fibu/anlagen/{entity_id}
- `fibu/zahlungsmeldungen`: api_bindung:endpoint_nicht_in_openapi:/api/v1/fibu/anlagen/{entity_id}
- `finance/umsatz`: compiler:[table_data_source_bound] tables missing bound dataSource: list, compiler:[table_profile] expected layout.tableProfile=financial for finance/umsatz
- `futtermittel/rationsoptimierung`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `inventory-reports`: compiler:[table_data_source_bound] tables missing bound dataSource: list, compiler:[table_profile] expected layout.tableProfile=inventory for inventory-reports
- `kontrakte/KontraktAlarmDashboard`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `kontrakte/LstKontraktUebersicht`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `lager/massebilanz`: api_bindung:endpoint_nicht_in_openapi:/api/v1/lager/bestaende/{entity_id}
- `lager/permanente-inventur`: api_bindung:endpoint_nicht_in_openapi:/api/v1/lager/bestaende/{entity_id}
- `lager/silo-uebersicht`: compiler:[table_data_source_bound] tables missing bound dataSource: list, compiler:[table_profile] expected layout.tableProfile=inventory for lager/silo-uebersicht
- `portal/naehrstoffbilanzen`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `pos/tse-journal`: compiler:[table_profile] expected layout.tableProfile=financial for pos/tse-journal
- `preise/individualpreise`: api_bindung:endpoint_nicht_in_openapi:/api/v1/preise/historie/{entity_id}
- `preise/rabattgruppen`: api_bindung:endpoint_nicht_in_openapi:/api/v1/preise/historie/{entity_id}
- `preise/zu-abschlaggruppen`: api_bindung:endpoint_nicht_in_openapi:/api/v1/preise/historie/{entity_id}
- `produktion/rezepturgruppen`: api_bindung:endpoint_nicht_in_openapi:/api/v1/produktion/mischfutter/auftraege/{entity_id}
- `reports`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `reports/ReportsDashboardCharts`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `start-dashboard`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `strecke/nawaro-uebersicht`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `strecke/nawaro-uebersicht-drucken`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `vertrag/neu`: compiler:[table_columns_complete] tables with <2 non-trivial columns: list
- `workflow/flow-spine-compliance-to-report`: compiler:[table_data_source_bound] tables missing bound dataSource: list
- `workflow/flow-spine-inventory-to-settlement`: compiler:[table_profile] expected layout.tableProfile=inventory for workflow/flow-spine-inventory-to-settlement
- `workflow/process-mining-analytics`: compiler:[table_data_source_bound] tables missing bound dataSource: list

## Gate E — offene Screen-IDs (76)

- `admin/audit-log-liste`: runtime:screen_id_nicht_runtime_wired
- `admin/qualitaets-cockpit`: runtime:screen_id_nicht_runtime_wired
- `admin/webhooks-liste`: runtime:screen_id_nicht_runtime_wired
- `agrar/ernte-liste`: runtime:screen_id_nicht_runtime_wired
- `agrar/feed-advice`: runtime:screen_id_nicht_runtime_wired
- `agrar/feldbuch-massnahmen-liste`: runtime:screen_id_nicht_runtime_wired
- `agrar/kulturpflanzen-liste`: runtime:screen_id_nicht_runtime_wired
- `agrar/psm-liste`: runtime:screen_id_nicht_runtime_wired
- `agrar/saatzucht-partien-liste`: runtime:screen_id_nicht_runtime_wired
- `banken/konten-liste`: runtime:screen_id_nicht_runtime_wired
- `compliance/enni-meldungen-liste`: runtime:screen_id_nicht_runtime_wired
- `compliance/gelangensbestaetigung-liste`: runtime:screen_id_nicht_runtime_wired
- `compliance/intrastat-liste`: runtime:screen_id_nicht_runtime_wired
- `compliance/lksg-liste`: runtime:screen_id_nicht_runtime_wired
- `compliance/saatgut-nachbau-liste`: runtime:screen_id_nicht_runtime_wired
- `crm/aktivitaeten-liste`: runtime:screen_id_nicht_runtime_wired
- `crm/campaign-performance`: runtime:screen_id_nicht_runtime_wired
- `crm/dsgvo-anfragen-liste`: runtime:screen_id_nicht_runtime_wired
- `crm/einwilligungen-liste`: runtime:screen_id_nicht_runtime_wired
- `crm/kampagnen-liste`: runtime:screen_id_nicht_runtime_wired
- `crm/kampagnenvorlagen-liste`: runtime:screen_id_nicht_runtime_wired
- `crm/segmente-liste`: runtime:screen_id_nicht_runtime_wired
- `dms/inbox`: runtime:screen_id_nicht_runtime_wired
- `einkauf/frachtauftraege-liste`: runtime:screen_id_nicht_runtime_wired
- `fibu/kontenplan-liste`: runtime:screen_id_nicht_runtime_wired
- `fibu/kostenstellenrechnung`: runtime:screen_id_nicht_runtime_wired
- `fibu/zahlungseingaenge-liste`: runtime:screen_id_nicht_runtime_wired
- `finance/ap-invoices-liste`: runtime:screen_id_nicht_runtime_wired
- `finance/audit-trail-liste`: runtime:screen_id_nicht_runtime_wired
- `finance/bookings/new`: runtime:screen_id_nicht_runtime_wired
- `finance/kreditoren-liste`: runtime:screen_id_nicht_runtime_wired
- `finance/offene-posten`: runtime:screen_id_nicht_runtime_wired
- `finance/payment-matching-liste`: runtime:screen_id_nicht_runtime_wired
- `finance/periods-liste`: runtime:screen_id_nicht_runtime_wired
- `finance/skonto-optimizer-liste`: runtime:screen_id_nicht_runtime_wired
- `fuhrpark/ausgehende-dokumente`: runtime:screen_id_nicht_runtime_wired
- `fuhrpark/auswertung-kosten`: runtime:screen_id_nicht_runtime_wired
- `fuhrpark/auswertungen-menu`: runtime:screen_id_nicht_runtime_wired
- `fuhrpark/rechnungen`: runtime:screen_id_nicht_runtime_wired
- `fuhrpark/rechnungen-liste`: runtime:screen_id_nicht_runtime_wired
- `fuhrpark/terminarten`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/einzelfuttermittel-liste`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/mischfuttermittel-liste`: runtime:screen_id_nicht_runtime_wired
- `genossenschaft/mitglieder-liste`: runtime:screen_id_nicht_runtime_wired
- `kontrakte/kontraktklassen-liste`: runtime:screen_id_nicht_runtime_wired
- `kontrakte/liste`: runtime:screen_id_nicht_runtime_wired
- `lager/foreign-goods-queue`: runtime:screen_id_nicht_runtime_wired
- `lager/inventur-liste`: runtime:screen_id_nicht_runtime_wired
- `lager/lagerbewegungen-liste`: runtime:screen_id_nicht_runtime_wired
- `lager/leitstand`: runtime:screen_id_nicht_runtime_wired
- `lager/partiestamm-liste`: runtime:screen_id_nicht_runtime_wired
- `lager/silo-uebersicht-liste`: runtime:screen_id_nicht_runtime_wired
- `logistik/frachtbrief`: runtime:screen_id_nicht_runtime_wired
- `marketing/kampagnen-liste`: runtime:screen_id_nicht_runtime_wired
- `personal/zeiterfassung-liste`: runtime:screen_id_nicht_runtime_wired
- `platform/analytics`: runtime:screen_id_nicht_runtime_wired
- `process/approval-density`: runtime:screen_id_nicht_runtime_wired
- `process/background-jobs`: runtime:screen_id_nicht_runtime_wired
- `qualitaet/ausnahmen-liste`: runtime:screen_id_nicht_runtime_wired
- `qualitaet/reklamationen-liste`: runtime:screen_id_nicht_runtime_wired
- `sales/auftraege-liste`: runtime:screen_id_nicht_runtime_wired
- `sales/gutschrift`: runtime:screen_id_nicht_runtime_wired
- `sales/invoices`: runtime:screen_id_nicht_runtime_wired
- `sales/lieferungen-liste`: runtime:screen_id_nicht_runtime_wired
- `service/anfragen-liste`: runtime:screen_id_nicht_runtime_wired
- `tankstelle/zapfungen-liste`: runtime:screen_id_nicht_runtime_wired
- `transporte/fahrer-liste`: runtime:screen_id_nicht_runtime_wired
- `verkauf/betriebsauftrag`: runtime:screen_id_nicht_runtime_wired
- `vertrag/rahmenvertraege-liste`: runtime:screen_id_nicht_runtime_wired
- `waage/liste`: runtime:screen_id_nicht_runtime_wired
- `waage/waagen-liste`: runtime:screen_id_nicht_runtime_wired
- `waage/wiegungen-liste`: runtime:screen_id_nicht_runtime_wired
- `workflow/process-mining`: runtime:screen_id_nicht_runtime_wired
- `workflow/workflow-monitoring`: runtime:screen_id_nicht_runtime_wired
- `workspace/start-dashboard`: runtime:screen_id_nicht_runtime_wired
- `zertifikate/liste`: runtime:screen_id_nicht_runtime_wired

## Studio-Draft-Projektion (Auszug)

Alle Projektionen ohne Violations.
