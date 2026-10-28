# Made-by-Studio Gate-Report

Stand: 2026-10-28 (erzeugt mit `python scripts/verify_made_by_studio_gates.py`).

Bezug: [Made by Studio — Qualitätsversprechen](made-by-studio-qualitaetsversprechen.md).

## Zusammenfassung

| Metrik | Wert |
|--------|------|
| Registrierte ScreenDefinitions | 853 |
| Gate A (Meridian & Struktur) grün | 853 |
| Gate B (Rechte & Aktionen) grün | 853 |
| Gate C (Compiler & Kanal) grün | 852 |
| Gate E (Runtime-Verdrahtung) grün | 801 |
| Studio-Draft-Projektion ohne Violations | 5 |
| Ø Advisory-Score (Gate-C-Metrik) | 0.99 |
| Screen-IDs in runtime_wired-Routen (gesamt) | 2655 |

Gate D (Browser/Image) wird hier nicht automatisiert geprüft.

## Gate A — offene Screen-IDs (0)

Keine — alle grün.

## Gate B — offene Screen-IDs (0)

Keine — alle grün.

## Gate C — offene Screen-IDs (1)

- `portal/zertifikat`: api_bindung:endpoint_nicht_in_openapi:/api/v1/portal/zertifikate/{entity_id}

## Gate E — offene Screen-IDs (52)

- `admin/control-center`: runtime:screen_id_nicht_runtime_wired
- `admin/webhooks-liste`: runtime:screen_id_nicht_runtime_wired
- `annahme/lkw-registrierung`: runtime:screen_id_nicht_runtime_wired
- `annahme/qualitaets-check`: runtime:screen_id_nicht_runtime_wired
- `annahme/warteschlange`: runtime:screen_id_nicht_runtime_wired
- `auth/callback`: runtime:screen_id_nicht_runtime_wired
- `auth/login`: runtime:screen_id_nicht_runtime_wired
- `crm/aktivitaeten-liste`: runtime:screen_id_nicht_runtime_wired
- `crm/campaign`: runtime:screen_id_nicht_runtime_wired
- `crm/campaign-template`: runtime:screen_id_nicht_runtime_wired
- `crm/consent`: runtime:screen_id_nicht_runtime_wired
- `crm/gdpr-request`: runtime:screen_id_nicht_runtime_wired
- `crm/kunden-cockpit`: runtime:screen_id_nicht_runtime_wired
- `crm/segment`: runtime:screen_id_nicht_runtime_wired
- `einkauf/rechnungseingang/neu`: runtime:screen_id_nicht_runtime_wired
- `fibu/debitoren`: runtime:screen_id_nicht_runtime_wired
- `fibu/debitoren-liste`: runtime:screen_id_nicht_runtime_wired
- `finance/bank-abgleich`: runtime:screen_id_nicht_runtime_wired
- `finance/debitoren/new`: runtime:screen_id_nicht_runtime_wired
- `finance/invoices/new`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/einzelfuttermittel/stamm/new`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/fuetterungsdokumentation-mobil`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/mischfuttermittel/stamm/new`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/rationseditor`: runtime:screen_id_nicht_runtime_wired
- `futtermittel/rationsoptimierung`: runtime:screen_id_nicht_runtime_wired
- `kontrakte/FrmKontraktProtokoll`: runtime:screen_id_nicht_runtime_wired
- `lager/materialfluss`: runtime:screen_id_nicht_runtime_wired
- `mahnwesen/mahnlauf`: runtime:screen_id_nicht_runtime_wired
- `portal/rationsoptimierung`: runtime:screen_id_nicht_runtime_wired
- `sales/angebote-liste`: runtime:screen_id_nicht_runtime_wired
- `sales/credit-notes`: runtime:screen_id_nicht_runtime_wired
- `sales/lieferungen-liste`: runtime:screen_id_nicht_runtime_wired
- `sales/lieferungen/neu`: runtime:screen_id_nicht_runtime_wired
- `verkauf/auftraege/neu`: runtime:screen_id_nicht_runtime_wired
- `verkauf/kunde`: runtime:screen_id_nicht_runtime_wired
- `verkauf/kunden-stamm`: runtime:screen_id_nicht_runtime_wired
- `verkauf/rechnungen`: runtime:screen_id_nicht_runtime_wired
- `waage/liste`: runtime:screen_id_nicht_runtime_wired
- `waage/neu`: runtime:screen_id_nicht_runtime_wired
- `waage/waagen-liste`: runtime:screen_id_nicht_runtime_wired
- `waage/wiegungen`: runtime:screen_id_nicht_runtime_wired
- `waage/wiegungen-liste`: runtime:screen_id_nicht_runtime_wired
- `workflow/flow-spine-complaint-to-resolution`: runtime:screen_id_nicht_runtime_wired
- `workflow/flow-spine-compliance-to-report`: runtime:screen_id_nicht_runtime_wired
- `workflow/flow-spine-contract-to-settlement`: runtime:screen_id_nicht_runtime_wired
- `workflow/flow-spine-finance-to-close`: runtime:screen_id_nicht_runtime_wired
- `workflow/flow-spine-harvest-to-settlement`: runtime:screen_id_nicht_runtime_wired
- `workflow/flow-spine-inventory-to-settlement`: runtime:screen_id_nicht_runtime_wired
- `workflow/flow-spine-order-to-cash`: runtime:screen_id_nicht_runtime_wired
- `workflow/flow-spine-procure-to-pay`: runtime:screen_id_nicht_runtime_wired
- `workflow/flow-spine-service-to-customer`: runtime:screen_id_nicht_runtime_wired
- `workflow/flow-spine-studio`: runtime:screen_id_nicht_runtime_wired

## Studio-Draft-Projektion (Auszug)

- `abrechnung/eb-lieferschein-kontrolle`: datenquelle_nicht_im_katalog:/api/v1/document-control/summary, datenquelle_nicht_im_katalog:/api/v1/document-control/exceptions?exception_type=missing_inbound_document, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:assign_me
- `admin/agenten-integration`: datenquelle_nicht_im_katalog:/api/v1/agent/integrations/providers/superglue/tenants/{entity_id}/admin-state, action_nicht_im_katalog:bearbeiten
- `admin/ai-approvals`: datenquelle_nicht_im_katalog:/api/v1/finance/ap/invoices/?status=ZUR_FREIGABE, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open_source
- `admin/api-keys`: datenquelle_nicht_im_katalog:/api/v1/admin/benutzer/{entity_id}, action_nicht_im_katalog:bearbeiten
- `admin/audit-log`: datenquelle_nicht_im_katalog:/api/v1/admin/audit-log, datenquelle_nicht_im_katalog:/api/v1/admin/audit-log, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/audit-log-liste`: datenquelle_nicht_im_katalog:/api/v1/admin/audit-log, action_nicht_im_katalog:export
- `admin/backup-restore`: datenquelle_nicht_im_katalog:/api/v1/admin/benutzer/{entity_id}, action_nicht_im_katalog:bearbeiten
- `admin/belegfolgekonfig`: datenquelle_nicht_im_katalog:/api/v1/admin/number-ranges/, datenquelle_nicht_im_katalog:/api/v1/admin/number-ranges/, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/benutzer-liste`: datenquelle_nicht_im_katalog:/api/v1/admin/benutzer, action_nicht_im_katalog:export
- `admin/berechtigungen-matrix`: datenquelle_nicht_im_katalog:/api/v1/admin/report-permissions/{entity_id}, action_nicht_im_katalog:bearbeiten
- `admin/branches`: datenquelle_nicht_im_katalog:/api/v1/admin/branches/{entity_id}, action_nicht_im_katalog:bearbeiten
- `admin/command-monitor`: datenquelle_nicht_im_katalog:/api/v1/articles/{entity_id}, action_nicht_im_katalog:bearbeiten
- `admin/compliance-dashboard`: datenquelle_nicht_im_katalog:/api/v1/compliance/stats, action_nicht_im_katalog:refresh
- `admin/control-center`: datenquelle_nicht_im_katalog:/api/v1/agents/neuroassist/ops/control-center, datenquelle_nicht_im_katalog:/api/v1/agents/neuroassist/ops/control-center, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/control-center/ai-approvals`: datenquelle_nicht_im_katalog:/api/v1/finance/ap/invoices/, datenquelle_nicht_im_katalog:/api/v1/finance/ap/invoices/, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/control-center/incident-response`: datenquelle_nicht_im_katalog:/api/v1/agents/neuroassist/ops/incidents, datenquelle_nicht_im_katalog:/api/v1/agents/neuroassist/ops/incidents, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/control-center/operations`: datenquelle_nicht_im_katalog:/api/v1/admin-suite/operations, datenquelle_nicht_im_katalog:/api/v1/admin-suite/operations, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/control-center/security`: datenquelle_nicht_im_katalog:/api/v1/admin-suite/security, datenquelle_nicht_im_katalog:/api/v1/admin-suite/security, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/core/audit-governance`: datenquelle_nicht_im_katalog:/api/v1/governance/audit-trail, datenquelle_nicht_im_katalog:/api/v1/governance/audit-trail, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/data-quality`: datenquelle_nicht_im_katalog:/api/v1/admin/data-quality/rules, datenquelle_nicht_im_katalog:/api/v1/admin/data-quality/rules, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/devices`: datenquelle_nicht_im_katalog:/api/v1/admin/devices, datenquelle_nicht_im_katalog:/api/v1/admin/devices, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/dms-integration`: datenquelle_nicht_im_katalog:/api/v1/admin/dms/status, datenquelle_nicht_im_katalog:/api/v1/admin/dms/status, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/erntepeak-stabilitaet`: datenquelle_nicht_im_katalog:/api/v1/admin/erntefenster-campaigns, datenquelle_nicht_im_katalog:/api/v1/admin/erntefenster-campaigns, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/forst/kalkulation`: datenquelle_nicht_im_katalog:/api/v1/agrar/contracts/, datenquelle_nicht_im_katalog:/api/v1/agrar/contracts/, navigation_muss_lokaler_maskenpfad_sein, action_nicht_im_katalog:open
- `admin/identity-budgets`: datenquelle_nicht_im_katalog:/api/v1/identity/session, datenquelle_nicht_im_katalog:/api/v1/identity/budgets, action_nicht_im_katalog:allocate, action_nicht_im_katalog:root
