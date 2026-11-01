# Made-by-Studio Gate-Report

Stand: 2026-10-31 (erzeugt mit `python scripts/verify_made_by_studio_gates.py`).

Bezug: [Made by Studio — Qualitätsversprechen](made-by-studio-qualitaetsversprechen.md).

## Zusammenfassung

| Metrik | Wert |
|--------|------|
| Registrierte ScreenDefinitions | 851 |
| Gate A (Meridian & Struktur) grün | 842 |
| Gate B (Rechte & Aktionen) grün | 846 |
| Gate C (Compiler & Kanal) grün | 837 |
| Gate E (Runtime-Verdrahtung) grün | 830 |
| Studio-Draft-Projektion ohne Violations | 847 |
| Ø Advisory-Score (Gate-C-Metrik) | 0.99 |
| Screen-IDs in runtime_wired-Routen (gesamt) | 2718 |

Gate D (Browser/Image) wird hier nicht automatisiert geprüft.

## Gate A — offene Screen-IDs (9)

- `beleg/goods-receipt`: readiness:[layout_metadata] layout missing Meridian metadata: density, contextRail, readiness:[table_profile] tables exist but layout.tableProfile is missing
- `beleg/purchase-credit-memo`: readiness:[layout_metadata] layout missing Meridian metadata: density, contextRail, readiness:[table_profile] tables exist but layout.tableProfile is missing
- `beleg/purchase-invoice`: readiness:[layout_metadata] layout missing Meridian metadata: density, contextRail, readiness:[table_profile] tables exist but layout.tableProfile is missing
- `beleg/purchase-order`: readiness:[layout_metadata] layout missing Meridian metadata: density, contextRail, readiness:[table_profile] tables exist but layout.tableProfile is missing
- `beleg/sales-credit-memo`: readiness:[layout_metadata] layout missing Meridian metadata: density, contextRail, readiness:[table_profile] tables exist but layout.tableProfile is missing
- `beleg/sales-delivery`: readiness:[layout_metadata] layout missing Meridian metadata: density, contextRail, readiness:[table_profile] tables exist but layout.tableProfile is missing
- `beleg/sales-invoice`: readiness:[layout_metadata] layout missing Meridian metadata: density, contextRail, readiness:[table_profile] tables exist but layout.tableProfile is missing
- `beleg/sales-offer`: readiness:[layout_metadata] layout missing Meridian metadata: density, contextRail, readiness:[table_profile] tables exist but layout.tableProfile is missing
- `beleg/sales-order`: readiness:[layout_metadata] layout missing Meridian metadata: density, contextRail, readiness:[table_profile] tables exist but layout.tableProfile is missing

## Gate B — offene Screen-IDs (5)

- `crm/campaign`: header_aktion_unklassifiziert:back
- `crm/consent`: header_aktion_unklassifiziert:back
- `crm/gdpr-request`: header_aktion_unklassifiziert:back
- `crm/segment`: header_aktion_unklassifiziert:back
- `mahnwesen/mahnlauf`: header_aktion_unklassifiziert:refresh

## Gate C — offene Screen-IDs (14)

- `beleg/goods-receipt`: compiler:[layout_metadata] layout missing Meridian metadata: density, contextRail, compiler:[table_profile] tables exist but layout.tableProfile is missing, compiler:[missing_process_chain] detail/transaction document screen missing processChain
- `beleg/purchase-credit-memo`: compiler:[layout_metadata] layout missing Meridian metadata: density, contextRail, compiler:[table_profile] tables exist but layout.tableProfile is missing, compiler:[missing_process_chain] detail/transaction document screen missing processChain
- `beleg/purchase-invoice`: compiler:[layout_metadata] layout missing Meridian metadata: density, contextRail, compiler:[table_profile] tables exist but layout.tableProfile is missing, compiler:[missing_process_chain] detail/transaction document screen missing processChain
- `beleg/purchase-order`: compiler:[layout_metadata] layout missing Meridian metadata: density, contextRail, compiler:[table_profile] tables exist but layout.tableProfile is missing, compiler:[missing_process_chain] detail/transaction document screen missing processChain
- `beleg/sales-credit-memo`: compiler:[layout_metadata] layout missing Meridian metadata: density, contextRail, compiler:[table_profile] tables exist but layout.tableProfile is missing, compiler:[missing_process_chain] detail/transaction document screen missing processChain
- `beleg/sales-delivery`: compiler:[layout_metadata] layout missing Meridian metadata: density, contextRail, compiler:[table_profile] tables exist but layout.tableProfile is missing, compiler:[missing_process_chain] detail/transaction document screen missing processChain
- `beleg/sales-invoice`: compiler:[layout_metadata] layout missing Meridian metadata: density, contextRail, compiler:[table_profile] tables exist but layout.tableProfile is missing, compiler:[missing_process_chain] detail/transaction document screen missing processChain
- `beleg/sales-offer`: compiler:[layout_metadata] layout missing Meridian metadata: density, contextRail, compiler:[table_profile] tables exist but layout.tableProfile is missing, compiler:[missing_process_chain] detail/transaction document screen missing processChain
- `beleg/sales-order`: compiler:[layout_metadata] layout missing Meridian metadata: density, contextRail, compiler:[table_profile] tables exist but layout.tableProfile is missing, compiler:[missing_process_chain] detail/transaction document screen missing processChain
- `crm/campaign`: compiler:[actions_classified] actions missing dangerLevel or permission: back, api_bindung:endpoint_nicht_in_openapi:/api/v1/crm/campaigns/{entity_id}/timeline
- `crm/consent`: compiler:[actions_classified] actions missing dangerLevel or permission: back
- `crm/gdpr-request`: compiler:[actions_classified] actions missing dangerLevel or permission: back
- `crm/segment`: compiler:[actions_classified] actions missing dangerLevel or permission: back
- `mahnwesen/mahnlauf`: compiler:[actions_classified] actions missing dangerLevel or permission: refresh

## Gate E — offene Screen-IDs (21)

- `admin/control-center`: runtime:screen_id_nicht_runtime_wired
- `admin/webhooks-liste`: runtime:screen_id_nicht_runtime_wired
- `crm/kunden-cockpit`: runtime:screen_id_nicht_runtime_wired
- `einkauf/rechnungseingang/neu`: runtime:screen_id_nicht_runtime_wired
- `finance/bank-abgleich`: runtime:screen_id_nicht_runtime_wired
- `finance/debitoren/new`: runtime:screen_id_nicht_runtime_wired
- `finance/invoices/new`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/einzelfuttermittel/stamm/new`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/fuetterungsdokumentation-mobil`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/mischfuttermittel/stamm/new`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/rationseditor`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/rationsoptimierung`: runtime:screen_id_nicht_runtime_wired
- `lager/materialfluss`: runtime:screen_id_nicht_runtime_wired
- `mahnwesen/mahnlauf`: runtime:screen_id_nicht_runtime_wired
- `portal/rationsoptimierung`: runtime:screen_id_nicht_runtime_wired
- `sales/credit-notes`: runtime:screen_id_nicht_runtime_wired
- `sales/lieferungen/neu`: runtime:screen_id_nicht_runtime_wired
- `verkauf/auftraege/neu`: runtime:screen_id_nicht_runtime_wired
- `verkauf/kunde`: runtime:screen_id_nicht_runtime_wired
- `verkauf/kunden-stamm`: runtime:screen_id_nicht_runtime_wired
- `verkauf/rechnungen`: runtime:screen_id_nicht_runtime_wired

## Studio-Draft-Projektion (Auszug)

- `logistik/frachttabellen`: action_ungueltiger_dangerLevel:loeschen:destructive
- `planung/kalender`: schreibender_transport_nicht_im_katalog
- `sales/lieferungen-liste`: action_ungueltiger_dangerLevel:auftrag_oeffnen:low
- `workflow/flow-spine-studio`: flow_spine_katalog_maske_ungueltig
