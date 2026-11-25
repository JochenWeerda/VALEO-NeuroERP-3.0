/**
 * Gate D (Browser) — Made-by-Studio Sichtnachweis fuer Studio-Cockpits
 * aus den Open-Routes-Hebungen (Batch 24–28).
 *
 * Mockt ScreenDefinition + flache Listen/Overview-APIs; prueft Routing,
 * native-cockpit Runtime-Shell und sichtbaren Titel (publizierte Route).
 */
import { expect, test, type Page } from '@playwright/test'
import { setzeUiTestsitzung } from './helpers/ui-testsitzung'

type CockpitCase = {
  label: string
  path: string
  screenId: string
  testId: string
  title: string
  listEndpoint?: string
  overviewEndpoint?: string
  /** Specialized workbench contract — mounts Fach-Surface inside native-cockpit. */
  specializedType?:
    | 'pricing_workbench'
    | 'fleet_workbench'
    | 'lager_workbench'
    | 'agrar_workbench'
    | 'finance_workbench'
    | 'feed_workbench'
    | 'admin_workbench'
    | 'weighing'
    | 'intake'
  specializedFields?: Array<{ key: string; label: string }>
  /** ARIA tablist name inside the specialized surface (Studio Tabs-Invariante). */
  specializedTablist?: string
  /** Accessible name / text proving the specialized surface mounted. */
  specializedLandmark?: string
}

const COCKPIT_CASES: CockpitCase[] = [
  {
    label: 'admin/externe-gates',
    path: '/admin/externe-gates',
    screenId: 'admin/externe-gates',
    testId: 'screen-admin/externe-gates',
    title: 'Externe Gates',
    overviewEndpoint: '/api/v1/external-gates/overview',
    listEndpoint: '/api/v1/external-gates/items',
  },
  {
    label: 'admin/command-monitor',
    path: '/admin/command-monitor',
    screenId: 'admin/command-monitor',
    testId: 'screen-admin/command-monitor',
    title: 'Command-Monitor',
  },
  // Admin Suite Cockpits (Batch 63): UniversalNativeCockpitPage + ScreenDefinition
  {
    label: 'admin-suite',
    path: '/admin-suite',
    screenId: 'admin-suite',
    testId: 'screen-admin-suite',
    title: 'VALEO Admin Suite',
    overviewEndpoint: '/api/v1/admin-suite/readiness',
    listEndpoint: '/api/v1/admin-suite/readiness/evidence',
  },
  {
    label: 'admin-suite/migration',
    path: '/admin-suite/migration',
    screenId: 'admin-suite/migration',
    testId: 'screen-admin-suite/migration',
    title: 'Migration Cockpit',
    overviewEndpoint: '/api/v1/admin-suite/migration/overview',
    listEndpoint: '/api/v1/admin-suite/migration/profiles',
  },
  {
    label: 'admin-suite/security',
    path: '/admin-suite/security',
    screenId: 'admin-suite/security',
    testId: 'screen-admin-suite/security',
    title: 'Security und Agent Governance',
    overviewEndpoint: '/api/v1/admin-suite/security/overview',
    listEndpoint: '/api/v1/admin-suite/security/roles',
  },
  {
    label: 'admin-suite/ki-anbieter',
    path: '/admin-suite/ki-anbieter',
    screenId: 'admin-suite/ki-anbieter',
    testId: 'screen-admin-suite/ki-anbieter',
    title: 'KI-Anbieter (NeuroAI)',
    overviewEndpoint: '/api/v1/admin-suite/llm-gateway',
  },
  {
    label: 'admin-suite/connectoren',
    path: '/admin-suite/connectoren',
    screenId: 'admin-suite/connectoren',
    testId: 'screen-admin-suite/connectoren',
    title: 'Auto-Capture-Connectoren',
    overviewEndpoint: '/api/v1/admin-suite/capture-connectors/overview',
  },
  {
    label: 'admin-suite/pos-fiscalization',
    path: '/admin-suite/pos-fiscalization',
    screenId: 'admin-suite/pos-fiscalization',
    testId: 'screen-admin-suite/pos-fiscalization',
    title: 'POS-Fiskalisierung',
    overviewEndpoint: '/api/v1/pos/fiscalization/overview',
    listEndpoint: '/api/v1/pos/fiscalization/products',
  },
  {
    label: 'agrar/milchvieh-crosssell',
    path: '/agrar/milchvieh-crosssell',
    screenId: 'agrar/milchvieh-crosssell',
    testId: 'screen-agrar/milchvieh-crosssell',
    title: 'Milchvieh Cross-Sell',
  },
  // Domain cockpits (Batch 64): already UniversalNativeCockpitPage — Gate-D Sichtnachweis
  {
    label: 'finance/offene-posten-cockpit',
    path: '/finance/offene-posten-cockpit',
    screenId: 'finance/offene-posten-cockpit',
    testId: 'finance-offene-posten-cockpit',
    title: 'Offene-Posten-Cockpit',
    overviewEndpoint: '/api/v1/finance/offene-posten',
  },
  {
    label: 'fibu/abschluss-cockpit',
    path: '/fibu/abschluss-cockpit',
    screenId: 'fibu/abschluss-cockpit',
    testId: 'fibu-abschluss-cockpit',
    title: 'Abschluss-Cockpit',
    overviewEndpoint: '/api/v1/finance/closing-checklists/cockpit/summary',
  },
  {
    label: 'crm/bedarfsdeckung-cockpit',
    path: '/crm/bedarfsdeckung-cockpit',
    screenId: 'crm/bedarfsdeckung-cockpit',
    testId: 'crm-bedarfsdeckung-cockpit',
    title: 'Bedarfsdeckung',
    overviewEndpoint: '/api/v1/crm/bedarfsdeckung/pipeline',
  },
  {
    label: 'crm/crm-dashboard',
    path: '/crm/crm-dashboard',
    screenId: 'crm/crm-dashboard',
    testId: 'crm-crm-dashboard',
    title: 'CRM-Dashboard',
    overviewEndpoint: '/api/v1/crm/dashboard',
  },
  {
    label: 'lager/qs-leitstand',
    path: '/lager/qs-leitstand',
    screenId: 'lager/qs-leitstand',
    testId: 'lager-qs-leitstand',
    title: 'QS-Leitstand',
    overviewEndpoint: '/api/v1/qualitaet/stats',
  },
  {
    label: 'lager/inventory-dashboard',
    path: '/inventory-dashboard',
    screenId: 'lager/inventory-dashboard',
    testId: 'lager-inventory-dashboard',
    title: 'Lager-Dashboard',
    overviewEndpoint: '/api/v1/lager/dashboard',
  },
  {
    label: 'controlling/benchmark-cockpit',
    path: '/controlling/benchmark-cockpit',
    screenId: 'controlling/benchmark-cockpit',
    testId: 'screen-controlling/benchmark-cockpit',
    title: 'Benchmark-Cockpit',
    overviewEndpoint: '/api/v1/benchmark/read-model',
  },
  {
    label: 'workflow/leitstand',
    path: '/workflow/leitstand',
    screenId: 'workflow/leitstand',
    testId: 'workflow-leitstand',
    title: 'Workflow-Leitstand',
    overviewEndpoint: '/api/v1/workflow/cockpit/summary',
  },
  {
    label: 'admin/compliance-dashboard',
    path: '/admin/compliance-dashboard',
    screenId: 'admin/compliance-dashboard',
    testId: 'screen-admin/compliance-dashboard',
    title: 'Compliance-Dashboard',
    overviewEndpoint: '/api/v1/compliance/stats',
  },
  {
    label: 'subventionen/dashboard',
    path: '/subventionen/dashboard',
    screenId: 'subventionen/dashboard',
    testId: 'subventionen-dashboard',
    title: 'Foerder-Dashboard',
    overviewEndpoint: '/api/v1/foerderung/stats',
  },
  // Controlling + Dashboards (Batch 65)
  {
    label: 'controlling/dashboard-verwaltung',
    path: '/controlling/dashboard-verwaltung',
    screenId: 'controlling/dashboard-verwaltung',
    testId: 'controlling-dashboard-verwaltung',
    title: 'Dashboard-Verwaltung',
    overviewEndpoint: '/api/v1/controlling/dashboards',
  },
  {
    label: 'controlling/kpi-verwaltung',
    path: '/controlling/kpi-verwaltung',
    screenId: 'controlling/kpi-verwaltung',
    testId: 'controlling-kpi-verwaltung',
    title: 'KPI-Verwaltung',
    overviewEndpoint: '/api/v1/controlling/kpis',
  },
  {
    label: 'controlling/massnahmen',
    path: '/controlling/massnahmen',
    screenId: 'controlling/massnahmen',
    testId: 'controlling-massnahmen',
    title: 'Controlling-Massnahmen',
    overviewEndpoint: '/api/v1/controlling/actions',
  },
  {
    label: 'controlling/timeseries-erfassung',
    path: '/controlling/timeseries-erfassung',
    screenId: 'controlling/timeseries-erfassung',
    testId: 'controlling-timeseries-erfassung',
    title: 'Zeitreihen-Erfassung',
    overviewEndpoint: '/api/v1/controlling/timeseries',
  },
  {
    label: 'controlling/widget-verwaltung',
    path: '/controlling/widget-verwaltung',
    screenId: 'controlling/widget-verwaltung',
    testId: 'controlling-widget-verwaltung',
    title: 'Widget-Verwaltung',
    overviewEndpoint: '/api/v1/controlling/dashboards',
  },
  {
    label: 'crm/campaign-performance',
    path: '/crm/campaign-performance-dashboard',
    screenId: 'crm/campaign-performance',
    testId: 'screen-crm/campaign-performance',
    title: 'Kampagnen-Performance',
    overviewEndpoint: '/api/v1/crm/dashboard',
  },
  {
    label: 'crm/dubletten-pruefung',
    path: '/crm/dubletten',
    screenId: 'crm/dubletten-pruefung',
    testId: 'screen-crm/dubletten-pruefung',
    title: 'Dubletten-Pruefung',
    overviewEndpoint: '/api/v1/crm/duplicates',
  },
  {
    label: 'management/executive-dashboard',
    path: '/management/executive-dashboard',
    screenId: 'management/executive-dashboard',
    testId: 'management-executive-dashboard',
    title: 'Executive Dashboard',
    overviewEndpoint: '/api/v1/management/dashboard',
  },
  {
    label: 'dashboard/einkauf',
    path: '/dashboard/einkauf-dashboard',
    screenId: 'dashboard/einkauf',
    testId: 'dashboard-einkauf',
    title: 'Einkaufs-Dashboard',
    overviewEndpoint: '/api/v1/belege/purchase_order/kennzahlen',
  },
  {
    label: 'einstellungen/system',
    path: '/einstellungen/system',
    screenId: 'einstellungen/system',
    testId: 'screen-einstellungen-system',
    title: 'Systemeinstellungen',
    overviewEndpoint: '/api/v1/config/system',
  },
  // Workspace / Dashboards (Batch 66)
  {
    label: 'dashboard/customizable',
    path: '/dashboard/customizable',
    screenId: 'dashboard/customizable',
    testId: 'dashboard-customizable',
    title: 'Anpassbares Dashboard',
    overviewEndpoint: '/api/v1/analytics/kpis',
  },
  {
    label: 'dashboards/geschaeftsfuehrung',
    path: '/dashboards/geschaeftsfuehrung',
    screenId: 'dashboards/geschaeftsfuehrung',
    testId: 'dashboards-geschaeftsfuehrung',
    title: 'Geschaeftsfuehrung',
    overviewEndpoint: '/api/v1/management/dashboard',
  },
  {
    label: 'lager/silo-uebersicht-liste',
    path: '/lager/silo-uebersicht',
    screenId: 'lager/silo-uebersicht-liste',
    testId: 'lager-silo-uebersicht',
    title: 'Silo-Uebersicht',
  },
  {
    label: 'workspace/einkauf',
    path: '/workspace/einkauf',
    screenId: 'workspace/einkauf',
    testId: 'workspace-einkauf',
    title: 'Verkaufs-Dashboard',
    overviewEndpoint: '/api/v1/sales/reports/summary',
  },
  {
    label: 'workspace/verkauf',
    path: '/workspace/verkauf',
    screenId: 'workspace/verkauf',
    testId: 'workspace-verkauf',
    title: 'Anpassbares Dashboard',
    overviewEndpoint: '/api/v1/analytics/kpis',
  },
  {
    label: 'workspace/fibu',
    path: '/workspace/fibu',
    screenId: 'workspace/fibu',
    testId: 'workspace-fibu',
    title: 'FiBu-Cockpit',
    overviewEndpoint: '/api/v1/finance/offene-posten',
  },
  {
    label: 'workspace/lager',
    path: '/workspace/lager',
    screenId: 'workspace/lager',
    testId: 'workspace-lager',
    title: 'Executive Dashboard',
    overviewEndpoint: '/api/v1/management/dashboard',
  },
  {
    label: 'workspace/leitung',
    path: '/workspace/leitung',
    screenId: 'workspace/leitung',
    testId: 'workspace-leitung',
    title: 'Compliance-Dashboard',
    overviewEndpoint: '/api/v1/compliance/stats',
  },
  // Reports / Analytics (Batch 67)
  {
    label: 'platform/analytics',
    path: '/analytics',
    screenId: 'platform/analytics',
    testId: 'screen-platform-analytics',
    title: 'Analytics',
    overviewEndpoint: '/api/v1/analytics/kpis',
  },
  {
    label: 'einkauf/reports',
    path: '/einkauf/reports',
    screenId: 'einkauf/reports',
    testId: 'einkauf-reports',
    title: 'Reports',
    overviewEndpoint: '/api/v1/einkauf/anfragen',
  },
  {
    label: 'finance/umsatz',
    path: '/finance/umsatz',
    screenId: 'finance/umsatz',
    testId: 'finance-umsatz',
    title: 'Reports',
    overviewEndpoint: '/api/v1/finance/financial-reports/bwa',
  },
  {
    label: 'inventory-reports',
    path: '/inventory-reports',
    screenId: 'inventory-reports',
    testId: 'inventory-reports',
    title: 'Inventory reports',
    overviewEndpoint: '/api/v1/inventory/reports/stock-alerts',
  },
  {
    label: 'reports',
    path: '/reports',
    screenId: 'reports',
    testId: 'reports',
    title: 'Reports',
    overviewEndpoint: '/api/v1/agrar/rations-optimization/feeding/reports',
  },
  {
    label: 'strecke/nawaro-uebersicht',
    path: '/strecke/nawaro-uebersicht',
    screenId: 'strecke/nawaro-uebersicht',
    testId: 'strecke-nawaro-uebersicht',
    title: 'NaWaRo',
  },
  {
    label: 'workflow/process-mining-analytics',
    path: '/workflow/process-mining-analytics',
    screenId: 'workflow/process-mining-analytics',
    testId: 'workflow-process-mining-analytics',
    title: 'Process mining analytics',
    overviewEndpoint: '/api/v1/workflow/cockpit-db/dead-letter',
  },
  // Admin-Suite NativeList (Batch 69) — NativeListPage → UniversalNativeCockpitPage
  {
    label: 'admin-suite/compliance',
    path: '/admin-suite/compliance',
    screenId: 'admin-suite/compliance',
    testId: 'screen-admin-suite/compliance',
    title: 'Compliance Evidence',
    listEndpoint: '/api/v1/admin-suite/compliance',
  },
  {
    label: 'admin-suite/connectors',
    path: '/admin-suite/connectors',
    screenId: 'admin-suite/connectors',
    testId: 'screen-admin-suite/connectors',
    title: 'Connector Hub',
    listEndpoint: '/api/v1/admin-suite/connectors',
  },
  {
    label: 'admin-suite/devices',
    path: '/admin-suite/devices',
    screenId: 'admin-suite/devices',
    testId: 'screen-admin-suite/devices',
    title: 'Hardware Center',
    listEndpoint: '/api/v1/admin-suite/devices',
  },
  {
    label: 'admin-suite/operations',
    path: '/admin-suite/operations',
    screenId: 'admin-suite/operations',
    testId: 'screen-admin-suite/operations',
    title: 'Operations Center',
    listEndpoint: '/api/v1/admin-suite/operations',
  },
  {
    label: 'admin-suite/system-status',
    path: '/admin-suite/system-status',
    screenId: 'admin-suite/system-status',
    testId: 'screen-admin-suite/system-status',
    title: 'System Status',
    listEndpoint: '/api/v1/admin-suite/system-status',
  },
  {
    label: 'admin-suite/diagnostics',
    path: '/admin-suite/diagnostics',
    screenId: 'admin-suite/diagnostics',
    testId: 'screen-admin-suite/diagnostics',
    title: 'Diagnosepaket',
    listEndpoint: '/api/v1/admin-suite/diagnostics',
  },
  {
    label: 'admin-suite/setup',
    path: '/admin-suite/setup',
    screenId: 'admin-suite/setup',
    testId: 'screen-admin-suite/setup',
    title: 'Ersteinrichtungs-Assistent',
    listEndpoint: '/api/v1/admin-suite/setup/steps',
  },
  {
    label: 'foerderung/liste',
    path: '/foerderung/liste',
    screenId: 'foerderung/liste',
    testId: 'screen-foerderung/liste',
    title: 'Foerderantraege',
  },
  // Admin + Fachlisten NativeList (Batch 70)
  {
    label: 'admin/ai-approvals',
    path: '/admin/ai-approvals',
    screenId: 'admin/ai-approvals',
    testId: 'screen-admin/ai-approvals',
    title: 'AI-Aktionen zur Freigabe',
    listEndpoint: '/api/v1/belege/purchase_invoice',
  },
  {
    label: 'admin/nummernkreise',
    path: '/admin/nummernkreise',
    screenId: 'admin/nummernkreise',
    testId: 'screen-admin-nummernkreise',
    title: 'Nummernkreise',
  },
  {
    label: 'admin/rollen-verwaltung',
    path: '/admin/rollen-verwaltung',
    screenId: 'admin/rollen-verwaltung',
    testId: 'screen-admin-rollen-verwaltung',
    title: 'Rollen',
  },
  {
    label: 'admin/webhooks-liste',
    path: '/admin/webhooks',
    screenId: 'admin/webhooks-liste',
    testId: 'native-webhooks',
    title: 'Webhook-Verwaltung',
    listEndpoint: '/api/v1/webhooks',
  },
  {
    label: 'admin/terminologie',
    path: '/admin/terminologie',
    screenId: 'admin/terminologie',
    testId: 'screen-admin-terminologie',
    title: 'Terminologie',
    listEndpoint: '/api/v1/terminology/begriffe',
  },
  {
    label: 'agrar/duenger-liste',
    path: '/agrar/duenger-liste',
    screenId: 'agrar/duenger-liste',
    testId: 'screen-agrar/duenger-liste',
    title: 'Duenger',
    listEndpoint: '/api/v1/agrar/duenger/',
  },
  {
    label: 'agrar/saatgut-liste',
    path: '/agrar/saatgut-liste',
    screenId: 'agrar/saatgut-liste',
    testId: 'screen-agrar/saatgut-liste',
    title: 'Saatgut',
    listEndpoint: '/api/v1/agrar/saatgut/',
  },
  {
    label: 'agrar/bodenproben-liste',
    path: '/agrar/bodenproben/liste',
    screenId: 'agrar/bodenproben-liste',
    testId: 'screen-agrar/bodenproben-liste',
    title: 'Bodenproben',
    listEndpoint: '/api/v1/labor/proben',
  },
  {
    label: 'einkauf/lieferanten',
    path: '/einkauf/lieferanten',
    screenId: 'einkauf/lieferanten',
    testId: 'screen-einkauf/lieferanten-liste',
    title: 'Lieferanten',
    listEndpoint: '/api/v1/einkauf/lieferanten',
  },
  {
    label: 'einkauf/anfragen',
    path: '/einkauf/anfragen',
    screenId: 'einkauf/anfragen',
    testId: 'screen-einkauf/anfragen-liste',
    title: 'Anfragen',
    listEndpoint: '/api/v1/einkauf/anfragen',
  },
  {
    label: 'finance/debitoren-liste',
    path: '/finance/debitoren-liste',
    screenId: 'finance/debitoren-liste',
    testId: 'screen-finance/debitoren-liste',
    title: 'Debitoren',
    listEndpoint: '/api/v1/finance/debitoren',
  },
  // Admin/Fachlisten NativeList (Batch 71)
  {
    label: 'admin/benutzer-liste',
    path: '/admin/benutzer-liste',
    screenId: 'admin/benutzer-liste',
    testId: 'screen-admin/benutzer-liste',
    title: 'Benutzer',
  },
  {
    label: 'admin/audit-log',
    path: '/admin/audit-log',
    screenId: 'admin/audit-log',
    testId: 'screen-admin/audit-log',
    title: 'Audit log',
    listEndpoint: '/api/v1/admin/audit-log',
  },
  {
    label: 'admin/data-quality',
    path: '/admin/data-quality',
    screenId: 'admin/data-quality',
    testId: 'screen-admin/data-quality',
    title: 'Data quality',
    listEndpoint: '/api/v1/admin/data-quality/rules',
  },
  {
    label: 'admin/webshop',
    path: '/admin/webshop',
    screenId: 'admin/webshop',
    testId: 'screen-admin-webshop',
    title: 'Webshop-Anbindungen',
    listEndpoint: '/api/v1/webshop/konfigurationen',
  },
  {
    label: 'admin/webshop-bestellungen',
    path: '/admin/webshop/bestellungen',
    screenId: 'admin/webshop-bestellungen',
    testId: 'screen-admin-webshop-bestellungen',
    title: 'Webshop-Bestellungen',
    listEndpoint: '/api/v1/webshop/bestellungen/liste',
  },
  {
    label: 'admin/belegfolgekonfig',
    path: '/admin/belegfolgekonfig',
    screenId: 'admin/belegfolgekonfig',
    testId: 'screen-admin/belegfolgekonfig',
    title: 'Belegfolgekonfig',
  },
  {
    label: 'admin/report-berechtigungen',
    path: '/admin/report-berechtigungen',
    screenId: 'admin/report-berechtigungen',
    testId: 'screen-admin-report-berechtigungen',
    title: 'Report-Berechtigungen',
    listEndpoint: '/api/v1/admin/report-permissions',
  },
  {
    label: 'agrar/biostimulanzien-liste',
    path: '/agrar/biostimulanzien-liste',
    screenId: 'agrar/biostimulanzien-liste',
    testId: 'screen-agrar/biostimulanzien-liste',
    title: 'Biostimulanzien',
    listEndpoint: '/api/v1/agrar/biostimulanzien',
  },
  {
    label: 'agrar/erntefenster-konfig',
    path: '/agrar/erntefenster-konfig',
    screenId: 'agrar/erntefenster-konfig',
    testId: 'screen-agrar/erntefenster-konfig',
    title: 'Erntefenster-Konfiguration',
    listEndpoint: '/api/v1/admin/erntefenster-campaigns',
  },
  {
    label: 'agrar/daily-prices',
    path: '/agrar/daily-prices',
    screenId: 'agrar/daily-prices',
    testId: 'screen-agrar/daily-prices',
    title: 'Daily prices',
    listEndpoint: '/api/v1/agrar/daily-prices',
  },
  {
    label: 'finance/kreditoren-liste',
    path: '/finance/kreditoren',
    screenId: 'finance/kreditoren-liste',
    testId: 'screen-finance/kreditoren-liste',
    title: 'Kreditoren',
    listEndpoint: '/api/v1/finance/kreditoren',
  },
  {
    label: 'crm/kunden-liste',
    path: '/crm/kunden-liste',
    screenId: 'crm/kunden-liste',
    testId: 'screen-crm/kunden-liste',
    title: 'Kunden',
    listEndpoint: '/api/v1/crm/customers/lookup',
  },
  // CRM NativeList (Batch 72)
  {
    label: 'crm/aktivitaeten-liste',
    path: '/crm/aktivitaeten',
    screenId: 'crm/aktivitaeten-liste',
    testId: 'crm-aktivitaeten',
    title: 'Aktivitaeten',
  },
  {
    label: 'crm/betriebsprofile-liste',
    path: '/crm/betriebsprofile-liste',
    screenId: 'crm/betriebsprofile-liste',
    testId: 'screen-crm/betriebsprofile-liste',
    title: 'Betriebsprofile',
  },
  {
    label: 'crm/kampagnen-liste',
    path: '/crm/campaigns',
    screenId: 'crm/kampagnen-liste',
    testId: 'screen-crm/kampagnen-liste',
    title: 'Kampagnen',
  },
  {
    label: 'crm/kampagnenvorlagen-liste',
    path: '/crm/campaign-templates',
    screenId: 'crm/kampagnenvorlagen-liste',
    testId: 'screen-crm/kampagnenvorlagen-liste',
    title: 'Kampagnenvorlagen',
  },
  {
    label: 'crm/kontakte-liste',
    path: '/crm/kontakte-liste',
    screenId: 'crm/kontakte-liste',
    testId: 'screen-crm/kontakte-liste',
    title: 'Kontakte',
  },
  {
    label: 'crm/leads-liste',
    path: '/crm/leads',
    screenId: 'crm/leads-liste',
    testId: 'screen-crm/leads-liste',
    title: 'Leads',
  },
  {
    label: 'crm/lieferanten-liste',
    path: '/crm/lieferanten-liste',
    screenId: 'crm/lieferanten-liste',
    testId: 'screen-crm/lieferanten-liste',
    title: 'Lieferanten',
  },
  {
    label: 'crm/opportunities-liste',
    path: '/crm/opportunities-liste',
    screenId: 'crm/opportunities-liste',
    testId: 'screen-crm/opportunities-liste',
    title: 'Verkaufschancen',
  },
  {
    label: 'crm/segmente-liste',
    path: '/crm/segments',
    screenId: 'crm/segmente-liste',
    testId: 'screen-crm/segmente-liste',
    title: 'Segmente',
  },
  {
    label: 'crm/einwilligungen-liste',
    path: '/crm/consents',
    screenId: 'crm/einwilligungen-liste',
    testId: 'screen-crm/einwilligungen-liste',
    title: 'Einwilligungen',
  },
  {
    label: 'crm/dsgvo-anfragen-liste',
    path: '/crm/gdpr-requests',
    screenId: 'crm/dsgvo-anfragen-liste',
    testId: 'screen-crm/dsgvo-anfragen-liste',
    title: 'DSGVO-Anfragen',
  },
  {
    label: 'crm/kontakt-management-liste',
    path: '/crm/kontakt-management',
    screenId: 'crm/kontakt-management-liste',
    testId: 'screen-crm/kontakt-management-liste',
    title: 'Kontakt-Management',
  },
  // Einkauf/Verkauf/Lager NativeList (Batch 73)
  {
    label: 'einkauf/angebote',
    path: '/einkauf/angebote',
    screenId: 'einkauf/angebote',
    testId: 'screen-einkauf/angebote-liste',
    title: 'Angebote',
  },
  {
    label: 'einkauf/auftragsbestaetigungen',
    path: '/einkauf/auftragsbestaetigungen',
    screenId: 'einkauf/auftragsbestaetigungen',
    testId: 'screen-einkauf/auftragsbestaetigungen-liste',
    title: 'Auftragsbestaetigungen',
  },
  {
    label: 'einkauf/anlieferavis-liste',
    path: '/einkauf/anlieferavis-liste',
    screenId: 'einkauf/anlieferavis-liste',
    testId: 'screen-einkauf/anlieferavis-liste',
    title: 'Anlieferavis',
  },
  {
    label: 'einkauf/retouren-liste',
    path: '/einkauf/retouren',
    screenId: 'einkauf/retouren-liste',
    testId: 'screen-einkauf/retouren-liste',
    title: 'Retouren',
  },
  {
    label: 'einkauf/warengruppen',
    path: '/einkauf/warengruppen',
    screenId: 'einkauf/warengruppen',
    testId: 'screen-einkauf/warengruppen',
    title: 'Warengruppen',
  },
  {
    label: 'einkauf/zahlungsbedingungen',
    path: '/einkauf/zahlungsbedingungen',
    screenId: 'einkauf/zahlungsbedingungen',
    testId: 'screen-einkauf/zahlungsbedingungen',
    title: 'Zahlungsbedingungen',
  },
  {
    label: 'einkauf/rechnung-abgleich-liste',
    path: '/einkauf/rechnung-abgleich',
    screenId: 'einkauf/rechnung-abgleich-liste',
    testId: 'screen-einkauf/rechnung-abgleich-liste',
    title: 'Rechnungsabgleich',
  },
  {
    label: 'einkauf/wareneingangsabgleich',
    path: '/einkauf/wareneingangsabgleich',
    screenId: 'einkauf/wareneingangsabgleich',
    testId: 'screen-einkauf/wareneingangsabgleich',
    title: 'Wareneingangsabgleich',
  },
  {
    label: 'verkauf/betriebs-auftraege',
    path: '/verkauf/betriebs-auftraege',
    screenId: 'verkauf/betriebs-auftraege',
    testId: 'screen-verkauf/betriebs-auftraege',
    title: 'Betriebs auftraege',
  },
  {
    label: 'verkauf/kommissions-auftraege',
    path: '/verkauf/kommissions-auftraege',
    screenId: 'verkauf/kommissions-auftraege',
    testId: 'screen-verkauf/kommissions-auftraege',
    title: 'Kommissions auftraege',
  },
  {
    label: 'lager/inventur-liste',
    path: '/lager/inventur',
    screenId: 'lager/inventur-liste',
    testId: 'screen-lager/inventur',
    title: 'Inventur',
  },
  {
    label: 'lager/partiestamm-liste',
    path: '/lager/partiestamm',
    screenId: 'lager/partiestamm-liste',
    testId: 'screen-lager/partiestamm',
    title: 'Partiestamm',
  },
  // Specialized workbenches (Batches 28–38): native-cockpit shell + specialized surface
  {
    label: 'lager/materialfluss',
    path: '/lager/materialfluss',
    screenId: 'lager/materialfluss',
    testId: 'screen-lager/materialfluss',
    title: 'Materialfluss',
    specializedType: 'lager_workbench',
    specializedFields: [
      { key: 'warehouse_id', label: 'Lager' },
      { key: 'node_count', label: 'Knoten' },
      { key: 'edge_count', label: 'Kanten' },
    ],
    specializedLandmark: 'Materialfluss Arbeitsbereich',
  },
  {
    label: 'konditionen/konditionssystem',
    path: '/konditionen/konditionssystem',
    screenId: 'konditionen/konditionssystem',
    testId: 'screen-konditionen/konditionssystem',
    title: 'Konditionssystem',
    specializedType: 'pricing_workbench',
    specializedFields: [
      { key: 'preisliste_count', label: 'Preislisten' },
      { key: 'rabattgruppe_count', label: 'Rabattgruppen' },
      { key: 'individualpreis_count', label: 'Individualpreise' },
    ],
    specializedTablist: 'Konditionssystem',
  },
  {
    label: 'fuhrpark/fahrzeug-vertiefung',
    path: '/fuhrpark/fahrzeug-vertiefung',
    screenId: 'fuhrpark/fahrzeug-vertiefung',
    testId: 'screen-fuhrpark/fahrzeug-vertiefung',
    title: 'Fahrzeug-Vertiefung',
    specializedType: 'fleet_workbench',
    specializedFields: [
      { key: 'fahrzeug_id', label: 'Fahrzeug' },
      { key: 'status', label: 'Status' },
      { key: 'schaden_offen', label: 'Offene Schäden' },
      { key: 'bussgeld_offen', label: 'Offene Bußgelder' },
    ],
    specializedTablist: 'Fahrzeug-Vertiefung',
  },
  {
    label: 'agrar/kunden-schlagkartei',
    path: '/agrar/kunden-schlagkartei',
    screenId: 'agrar/kunden-schlagkartei',
    testId: 'screen-agrar/kunden-schlagkartei',
    title: 'Kundenschlagkartei',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'kunden_nr', label: 'Kunde' },
      { key: 'schlag_count', label: 'Schläge' },
      { key: 'massnahme_count', label: 'Maßnahmen' },
      { key: 'gesamt_flaeche_ha', label: 'Fläche ha' },
    ],
    specializedTablist: 'Schlagkartei',
  },
  {
    label: 'agrar/ernte-annahme-erfassung',
    path: '/agrar/ernte-annahme-erfassung',
    screenId: 'agrar/ernte-annahme-erfassung',
    testId: 'screen-agrar/ernte-annahme-erfassung',
    title: 'Ernte-Annahme-Erfassung',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'acceptance_number', label: 'Annahmenummer' },
      { key: 'customer_id', label: 'Kunde' },
      { key: 'release_status', label: 'Freigabe' },
      { key: 'delivery_date', label: 'Lieferdatum' },
    ],
    // Ohne Annahme-ID erscheint oft die Listen-/Ansichts-Registerleiste zuerst.
    specializedTablist: 'Annahme-Ansichten',
  },
  {
    label: 'finance/bank-abgleich',
    path: '/finance/bank-abgleich',
    screenId: 'finance/bank-abgleich',
    testId: 'native-cockpit-finance-bank-abgleich',
    title: 'Bankabgleich',
    specializedType: 'finance_workbench',
    specializedFields: [
      { key: 'kontoId', label: 'Bankkonto' },
      { key: 'camtFile', label: 'Kontoauszug' },
      { key: 'statementId', label: 'Statement' },
      { key: 'startSaldo', label: 'Startsaldo' },
      { key: 'endSaldo', label: 'Endsaldo' },
      { key: 'gebuchteUmsaetze', label: 'Umsätze' },
      { key: 'zugeordnet', label: 'Zugeordnet' },
      { key: 'nichtZugeordnet', label: 'Nicht zugeordnet' },
      { key: 'abgleichsDifferenz', label: 'Differenz' },
      { key: 'accountingBalance', label: 'Hauptbuchsaldo' },
      { key: 'zuordnungData', label: 'Umsatzzeilen' },
      { key: 'importErrors', label: 'Importprotokoll' },
      { key: 'differences', label: 'Differenzen' },
      { key: 'comparisonState', label: 'Nachweisstatus' },
    ],
    specializedLandmark: 'Bankabgleich Arbeitsbereich',
  },
  {
    label: 'mahnwesen/mahnlauf',
    path: '/mahnwesen/mahnlauf',
    screenId: 'mahnwesen/mahnlauf',
    testId: 'native-cockpit-mahnwesen-mahnlauf',
    title: 'Mahnlauf',
    specializedType: 'finance_workbench',
    specializedFields: [
      { key: 'op_id', label: 'Posten' },
      { key: 'rechnungsnr', label: 'Rechnung' },
      { key: 'partner', label: 'Partner' },
      { key: 'tage_ueberfaellig', label: 'Überfällig' },
      { key: 'offen', label: 'Offen' },
      { key: 'aktuelle_stufe', label: 'Aktuelle Stufe' },
      { key: 'naechste_stufe', label: 'Nächste Stufe' },
      { key: 'dunning_fee', label: 'Gebühr' },
      { key: 'interest', label: 'Zinsen' },
      { key: 'total_amount', label: 'Gesamt' },
      { key: 'id', label: 'Mahnung' },
      { key: 'stufe', label: 'Stufe' },
      { key: 'gesamt', label: 'Gesamtbetrag' },
      { key: 'frist', label: 'Frist' },
      { key: 'datum', label: 'Datum' },
      { key: 'status', label: 'Status' },
      { key: 'versand_art', label: 'Versandart' },
      { key: 'empfaenger', label: 'Empfänger' },
      { key: 'auswahl', label: 'Auswahl' },
    ],
    specializedLandmark: 'Mahnlauf Arbeitsbereich',
  },
  {
    label: 'agrar/milchvieh-karte',
    path: '/agrar/milchvieh-karte',
    screenId: 'agrar/milchvieh-karte',
    testId: 'screen-agrar/milchvieh-karte',
    title: 'Milchvieh-Karte',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'feature_count', label: 'Betriebe' },
    ],
    specializedLandmark: 'Milchvieh-Karte Arbeitsbereich',
  },
  {
    label: 'futtermittel/fuetterungsdokumentation-mobil',
    path: '/futtermittel/fuetterungsdokumentation-mobil',
    screenId: 'futtermittel/fuetterungsdokumentation-mobil',
    testId: 'feed-mobile-documentation',
    title: 'Fütterungsdokumentation mobil',
    specializedType: 'feed_workbench',
    specializedFields: [
      { key: 'plan_version_id', label: 'Planversion' },
      { key: 'group_id', label: 'Gruppe' },
      { key: 'actual_kg', label: 'Ist-Menge' },
      { key: 'rest_kg', label: 'Restfutter' },
      { key: 'tm_pct', label: 'TM' },
    ],
    specializedLandmark: 'Mobile Fütterungsdokumentation Arbeitsbereich',
  },
  {
    label: 'futtermittel/rationseditor',
    path: '/futtermittel/rationseditor',
    screenId: 'futtermittel/rationseditor',
    testId: 'feed-ration-editor',
    title: 'Rationseditor',
    specializedType: 'feed_workbench',
    specializedFields: [
      { key: 'ration_id', label: 'Ration' },
      { key: 'group_id', label: 'Gruppe' },
      { key: 'version_no', label: 'Version' },
      { key: 'status', label: 'Status' },
    ],
    specializedLandmark: 'Rationseditor Arbeitsbereich',
  },
  {
    label: 'futtermittel/rationsoptimierung',
    path: '/futtermittel/rationsoptimierung',
    screenId: 'futtermittel/rationsoptimierung',
    testId: 'feed-ration-optimization',
    title: 'Willkommen bei der Rationsoptimierung',
    specializedType: 'feed_workbench',
    specializedFields: [
      { key: 'feed_id', label: 'Futter' },
      { key: 'cow_profile', label: 'Kuhprofil' },
      { key: 'optimization_result', label: 'Ergebnis' },
      { key: 'review_status', label: 'Review' },
    ],
    specializedLandmark: 'Rationsoptimierung Arbeitsbereich',
  },
  {
    label: 'portal/rationsoptimierung',
    path: '/portal/rationsoptimierung',
    screenId: 'portal/rationsoptimierung',
    testId: 'portal-feed-advice',
    title: 'Willkommen bei der Rationsoptimierung',
    specializedType: 'feed_workbench',
    specializedFields: [
      { key: 'view', label: 'Ansicht' },
      { key: 'ration_id', label: 'Ration' },
      { key: 'group_id', label: 'Gruppe' },
      { key: 'plan_status', label: 'Planstatus' },
    ],
    specializedLandmark: 'Portal Rationsoptimierung Arbeitsbereich',
  },
  {
    label: 'waage/liste',
    path: '/waage/liste',
    screenId: 'waage/liste',
    testId: 'native-cockpit-waage-liste',
    title: 'Waagen',
    specializedType: 'weighing',
    specializedFields: [
      { key: 'id', label: 'Waage' },
      { key: 'standort', label: 'Standort' },
      { key: 'typ', label: 'Typ' },
      { key: 'maxKapazitaet', label: 'Max. Kapazität' },
      { key: 'letzteEichung', label: 'Letzte Eichung' },
      { key: 'naechsteEichung', label: 'Nächste Eichung' },
      { key: 'status', label: 'Status' },
      { key: 'letztes_eichdatum', label: 'Eichdatum' },
      { key: 'naechste_eichfaelligkeit', label: 'Eichfälligkeit' },
      { key: 'eichamt', label: 'Eichamt' },
      { key: 'zertifikat_nr', label: 'Zertifikat' },
      { key: 'importScaleId', label: 'Import-Waage' },
      { key: 'importFile', label: 'Import-Datei' },
      { key: 'fehlerToleranz', label: 'Fehlertoleranz' },
      { key: 'importRaw', label: 'Import roh' },
      { key: 'importError', label: 'Importfehler' },
      { key: 'importRetryCount', label: 'Import-Retries' },
    ],
    specializedLandmark: 'Waagenliste Arbeitsbereich',
  },
  {
    label: 'annahme/warteschlange',
    path: '/annahme/warteschlange',
    screenId: 'annahme/warteschlange',
    testId: 'native-cockpit-annahme-warteschlange',
    title: 'Annahme-Warteschlange',
    specializedType: 'intake',
    specializedFields: [
      { key: 'kennzeichen', label: 'Kennzeichen' },
      { key: 'lieferant', label: 'Lieferant' },
      { key: 'artikel', label: 'Artikel' },
      { key: 'status', label: 'Status' },
      { key: 'ankunft', label: 'Ankunft' },
      { key: 'wartezeit', label: 'Wartezeit' },
      { key: 'lieferschein_nr', label: 'Lieferschein' },
    ],
    specializedLandmark: 'Annahme-Warteschlange Arbeitsbereich',
  },
  {
    label: 'annahme/lkw-registrierung',
    path: '/annahme/lkw-registrierung',
    screenId: 'annahme/lkw-registrierung',
    testId: 'native-cockpit-annahme-lkw-registrierung',
    title: 'LKW-Registrierung',
    specializedType: 'intake',
    specializedFields: [
      { key: 'kennzeichen', label: 'Kennzeichen' },
      { key: 'lieferant', label: 'Lieferant' },
      { key: 'lieferscheinNr', label: 'Lieferschein' },
      { key: 'articleId', label: 'Artikel-ID' },
      { key: 'artikel', label: 'Artikel' },
      { key: 'ankunftszeit', label: 'Ankunft' },
      { key: 'prioritaet', label: 'Priorität' },
      { key: 'attachmentIds', label: 'Anhänge' },
    ],
    specializedLandmark: 'LKW-Registrierung Arbeitsbereich',
  },
  {
    label: 'annahme/qualitaets-check',
    path: '/annahme/qualitaets-check',
    screenId: 'annahme/qualitaets-check',
    testId: 'native-cockpit-annahme-qualitaets-check',
    title: 'Qualitätsprüfung',
    specializedType: 'intake',
    specializedFields: [
      { key: 'lieferscheinNr', label: 'Lieferschein' },
      { key: 'artikel', label: 'Artikel' },
      { key: 'feuchtigkeit', label: 'Feuchtigkeit' },
      { key: 'protein', label: 'Protein' },
      { key: 'verunreinigung', label: 'Verunreinigung' },
      { key: 'fremdgeruch', label: 'Fremdgeruch' },
      { key: 'schaedlinge', label: 'Schädlinge' },
      { key: 'farbe', label: 'Farbe' },
      { key: 'bemerkungen', label: 'Bemerkungen' },
      { key: 'ergebnis', label: 'Ergebnis' },
    ],
    specializedLandmark: 'Qualitätsprüfung Arbeitsbereich',
  },
  {
    label: 'annahme/rohware',
    path: '/annahme/rohware',
    screenId: 'annahme/rohware',
    testId: 'native-cockpit-annahme-rohware',
    title: 'Rohware-Annahme',
    specializedType: 'intake',
    specializedFields: [
      { key: 'lieferant', label: 'Lieferant' },
      { key: 'kennzeichen', label: 'Kennzeichen' },
      { key: 'lieferscheinNr', label: 'Lieferschein' },
      { key: 'datum', label: 'Datum' },
      { key: 'artikel', label: 'Artikel' },
      { key: 'bruttoKg', label: 'Brutto' },
      { key: 'taraKg', label: 'Tara' },
      { key: 'lagerZiel', label: 'Lagerziel' },
      { key: 'feuchtePct', label: 'Feuchte' },
      { key: 'besatzPct', label: 'Besatz' },
      { key: 'fallzahl', label: 'Fallzahl' },
      { key: 'customer_id', label: 'Kunde' },
    ],
    specializedLandmark: 'Rohware-Annahme Arbeitsbereich',
  },
  {
    label: 'waage/wiegungen',
    path: '/waage/wiegungen',
    screenId: 'waage/wiegungen',
    testId: 'native-cockpit-waage-wiegungen',
    title: 'Wiegungen',
    specializedType: 'weighing',
    specializedFields: [
      { key: 'ticketNumber', label: 'Wiegeschein' },
      { key: 'scaleId', label: 'Waage' },
      { key: 'vehiclePlate', label: 'Kennzeichen' },
      { key: 'grossWeight', label: 'Brutto' },
      { key: 'tareWeight', label: 'Tara' },
      { key: 'moisturePct', label: 'Feuchte' },
      { key: 'impuritiesPct', label: 'Besatz' },
      { key: 'selectedTicketId', label: 'Ticket' },
      { key: 'selectedContractId', label: 'Kontrakt' },
    ],
    specializedLandmark: 'Wiegungen Arbeitsbereich',
  },
  {
    label: 'annahme/abrechnung',
    path: '/annahme/abrechnung',
    screenId: 'annahme/abrechnung',
    testId: 'screen-annahme/abrechnung',
    title: 'Annahme-Abrechnung',
    specializedType: 'agrar_workbench',
    specializedFields: [
      { key: 'settlement_count', label: 'Abrechnungen' },
    ],
    specializedLandmark: 'Annahme-Abrechnung Arbeitsbereich',
  },
  {
    label: 'admin/voice-channel',
    path: '/admin/voice-channel',
    screenId: 'admin/voice-channel',
    testId: 'native-cockpit-admin-voice-channel',
    title: 'Voice-Kanal',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'enabled', label: 'Aktiv' },
      { key: 'last_utterance', label: 'Letzte Äußerung' },
    ],
    specializedLandmark: 'Voice-Kanal Arbeitsbereich',
  },
  {
    label: 'admin/vordruck-editor',
    path: '/admin/vordruck-editor',
    screenId: 'admin/vordruck-editor',
    testId: 'native-cockpit-admin-vordruck-editor',
    title: 'Belegformular-Vordruck-Editor',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'id', label: 'ID' },
      { key: 'name', label: 'Name' },
      { key: 'kategorie', label: 'Kategorie' },
    ],
    specializedLandmark: 'Vordruck-Editor Arbeitsbereich',
  },
  {
    label: 'admin/screen-studio',
    path: '/admin/screen-studio',
    screenId: 'admin/screen-studio',
    testId: 'native-cockpit-admin-screen-studio',
    title: 'Masken-Studio',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'screen_id', label: 'Maske' },
      { key: 'status', label: 'Status' },
    ],
    specializedLandmark: 'Masken-Studio Arbeitsbereich',
  },
  {
    label: 'admin/GapPipelineConsole',
    path: '/admin/GapPipelineConsole',
    screenId: 'admin/GapPipelineConsole',
    testId: 'native-cockpit-admin-GapPipelineConsole',
    title: 'GAP-Pipeline Konsole',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'year', label: 'Jahr' },
      { key: 'pipeline_complete', label: 'Pipeline fertig' },
      { key: 'gap_payments_count', label: 'GAP-Zahlungen' },
    ],
    specializedLandmark: 'GAP-Pipeline Arbeitsbereich',
  },
  {
    label: 'admin/agenten-integration',
    path: '/admin/agenten-integration',
    screenId: 'admin/agenten-integration',
    testId: 'native-cockpit-admin-agenten-integration',
    title: 'Agenten-Integration',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'tenant_id', label: 'Mandant' },
      { key: 'section', label: 'Abschnitt' },
    ],
    specializedLandmark: 'Agenten-Integration Arbeitsbereich',
  },
  {
    label: 'admin/setup/dms-integration',
    path: '/admin/setup/dms-integration',
    screenId: 'admin/setup/dms-integration',
    testId: 'native-cockpit-admin-setup-dms-integration',
    title: 'DMS-Integration',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'status', label: 'Status' },
      { key: 'connected', label: 'Verbunden' },
    ],
    specializedLandmark: 'DMS-Integration Arbeitsbereich',
  },
  {
    label: 'admin/control-center',
    path: '/admin/control-center',
    screenId: 'admin/control-center',
    testId: 'native-cockpit-admin-control-center',
    title: 'Admin Kontroll- und Ueberwachungszentrum',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'tenant_id', label: 'Mandant' },
      { key: 'incident_id', label: 'Vorfall' },
      { key: 'source', label: 'Quelle' },
      { key: 'severity', label: 'Priorität' },
      { key: 'status', label: 'Status' },
      { key: 'title', label: 'Titel' },
      { key: 'owner', label: 'Verantwortlich' },
      { key: 'recommended_action', label: 'Empfehlung' },
      { key: 'scheduled_for', label: 'Geplant' },
      { key: 'plan_id', label: 'Plan' },
      { key: 'kind', label: 'Art' },
      { key: 'calendar_window', label: 'Kalender' },
      { key: 'open_quarantine_count', label: 'Quarantäne' },
      { key: 'journal_error_count', label: 'Journalfehler' },
    ],
    specializedLandmark: 'Admin Kontroll- und Ueberwachungszentrum Arbeitsbereich',
  },
  {
    label: 'admin/setup',
    path: '/admin/setup',
    screenId: 'admin/setup',
    testId: 'native-cockpit-admin-setup',
    title: 'Ersteinrichtung',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'step', label: 'Schritt' },
      { key: 'status', label: 'Status' },
    ],
    specializedLandmark: 'Ersteinrichtung Arbeitsbereich',
  },
  {
    label: 'studio/workspace-composition-preview',
    path: '/studio/workspace-composition-preview',
    screenId: 'studio/workspace-composition-preview',
    testId: 'native-cockpit-studio-workspace-composition-preview',
    title: 'WorkspaceComposition Studio',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'draft_id', label: 'Entwurf' },
      { key: 'status', label: 'Status' },
    ],
    specializedLandmark: 'WorkspaceComposition Studio Arbeitsbereich',
  },
  {
    label: 'admin/control-center/agent-ops',
    path: '/admin/control-center/agent-ops',
    screenId: 'admin/control-center/agent-ops',
    testId: 'native-cockpit-admin-control-center-agent-ops',
    title: 'Admin Kontrollzentrum: Agent Ops',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'persisted', label: 'Persistiert' },
      { key: 'history_count', label: 'Historie' },
      { key: 'state_path', label: 'State-Pfad' },
    ],
    specializedLandmark: 'Admin Kontrollzentrum: Agent Ops Arbeitsbereich',
  },
  {
    label: 'admin/control-center/superglue',
    path: '/admin/control-center/superglue',
    screenId: 'admin/control-center/superglue',
    testId: 'native-cockpit-admin-control-center-superglue',
    title: 'Admin Kontrollzentrum: Superglue',
    specializedType: 'admin_workbench',
    specializedFields: [
      { key: 'tenant_id', label: 'Mandant' },
      { key: 'storage_path', label: 'Storage' },
    ],
    specializedLandmark: 'Admin Kontrollzentrum: Superglue Arbeitsbereich',
  },
  // Prefixe, die vor Batch 41 an page-module-loader scheiterten
  {
    label: 'dms/archiv-suche',
    path: '/dms/archiv-suche',
    screenId: 'dms/archiv-suche',
    testId: 'dms-archiv-suche',
    title: 'Archiv-Suche',
  },
  {
    label: 'betrieb/maschinen-stamm',
    path: '/betrieb/maschinen-stamm',
    screenId: 'betrieb/maschinen-stamm',
    testId: 'betrieb-maschinen-stamm',
    title: 'Maschinen-Stamm',
  },
]

function maskPath(screenId: string): string {
  return screenId.replace(/\//g, '__')
}

function minimalCockpitDefinition(c: CockpitCase) {
  const contractFields = (c.specializedFields ?? []).map((field) => ({
    key: field.key,
    label: field.label,
    type: 'number' as const,
    readOnly: true,
  }))
  return {
    schemaVersion: 1,
    id: c.screenId,
    domain: c.screenId.split('/')[0],
    mode: 'cockpit',
    title: c.title,
    adapter: { type: 'native', sourceId: c.screenId, temporary: false },
    fields: [
      { key: 'label', label: 'Name', type: 'text', readOnly: true },
      { key: 'status', label: 'Status', type: 'text', readOnly: true },
      ...contractFields,
    ],
    dataSources: [
      ...(c.overviewEndpoint
        ? [{ key: 'entity', endpoint: c.overviewEndpoint }]
        : [{ key: 'entity', endpoint: `/api/v1/masks/${maskPath(c.screenId)}/overview` }]),
      ...(c.listEndpoint
        ? [{ key: 'items', endpoint: c.listEndpoint, pageSize: 50 }]
        : [{ key: 'items', endpoint: `/api/v1/masks/${maskPath(c.screenId)}/items`, pageSize: 50 }]),
    ],
    summary: [
      { key: 'gesamt', label: 'Gesamt', tone: 'neutral' },
    ],
    tables: [
      {
        key: 'items',
        label: 'Eintraege',
        dataSourceKey: 'items',
        pageSize: 50,
        columns: [
          { key: 'label', label: 'Name', priority: 'primary' },
          { key: 'status', label: 'Status', priority: 'primary' },
        ],
        rowActions: [],
      },
    ],
    actions: [
      {
        key: 'refresh',
        label: 'Aktualisieren',
        kind: 'secondary',
        zone: 'header',
        dangerLevel: 'safe',
        localEffect: 'refetch',
      },
    ],
    permissions: ['*'],
    layout: {
      preferredMode: 'desktopDense',
      mobileMode: 'mobileStack',
      touchTargetPx: 44,
      floorplan: 'cockpit',
      density: 'compact',
      contextRail: 'combined',
      tableProfile: 'audit',
    },
    performance: {
      initialPayloadBudgetKb: 48,
      requiresLazyTabs: false,
      requiresVirtualTables: true,
      lookupMinChars: 2,
    },
    noWorkflowReason: 'Gate-D-Smoke ohne Beleg-Lebenszyklus.',
    ...(c.specializedType
      ? {
          specialized: {
            type: c.specializedType,
            id: c.screenId,
          },
        }
      : {}),
  }
}

async function installCockpitMocks(page: Page, c: CockpitCase): Promise<void> {
  const encoded = maskPath(c.screenId)
  const sd = minimalCockpitDefinition(c)

  await page.route(new RegExp(`/api/v1/masks/${encoded}/screen-definition$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(sd),
    })
  })

  const overviewPath = c.overviewEndpoint ?? `/api/v1/masks/${encoded}/overview`
  await page.route(new RegExp(`${overviewPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?:\\?.*)?$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ gesamt: 1, ok_count: 1, problem_count: 0 }),
    })
  })

  const listPath = c.listEndpoint ?? `/api/v1/masks/${encoded}/items`
  await page.route(new RegExp(`${listPath.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}(?:\\?.*)?$`), async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 'smoke-1', label: c.title, status: 'ok' }]),
    })
  })

  // Overlay ohne Backend — leeres Overlay, kein Crash in der Runtime.
  await page.route(new RegExp(`/api/v1/ux/overlays/${c.screenId.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`), async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: 'null' })
  })

  // Specialized-Surface-Fetches: Arrays (nicht {items}), sonst crasht z. B. Konditionen-Map.
  if (c.specializedType === 'pricing_workbench') {
    await page.route(/\/api\/v1\/price-lists\/?(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
  if (c.specializedType === 'lager_workbench') {
    await page.route(/\/api\/v1\/inventory\/warehouses(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })
  }
  if (c.specializedType === 'finance_workbench') {
    await page.route(/\/api\/v1\/banken\/konten(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })
    await page.route(/\/api\/v1\/finance\/bank-accounts(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      })
    })
    await page.route(/\/api\/v1\/finance\/mahnlauf\/candidates(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      })
    })
    await page.route(/\/api\/v1\/finance\/mahnlauf\/notices(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      })
    })
  }
  if (c.screenId === 'agrar/milchvieh-karte') {
    await page.route(/\/api\/v1\/agrar\/milchvieh-crosssell\/map(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ type: 'FeatureCollection', features: [] }),
      })
    })
  }
  if (c.screenId === 'agrar/kunden-schlagkartei') {
    // PortalKontoGate: ein Konto → Auto-Wahl → Tabs der Specialized-Surface.
    await page.route(/\/api\/v1\/portal\/kundenkonten(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            customer_id: 'smoke-kunde-1',
            customer_number: 'K-1',
            name: 'Smoke-Hof',
            rolle: 'betreiber',
            rechte: ['*'],
          },
        ]),
      })
    })
    await page.route(/\/(?:api\/v1\/)?innendienst\/kunden\/[^/]+\/schlaege(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ schlaege: [], count: 0 }),
      })
    })
    await page.route(/\/(?:api\/v1\/)?innendienst\/kunden\/[^/]+\/massnahmen(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ massnahmen: [], count: 0 }),
      })
    })
  }
  if (c.specializedType === 'feed_workbench') {
    await page.route(
      /\/api\/v1\/agrar\/rations-optimization\/feeding\/plans\/current(?:\?.*)?$/,
      async (route) => {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      },
    )
    await page.route(
      /\/api\/v1\/agrar\/rations-optimization\/lifecycle\/rations(?:\?.*)?$/,
      async (route) => {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      },
    )
    await page.route(
      /\/api\/v1\/agrar\/rations-optimization\/feeding\/actuals(?:\?.*)?$/,
      async (route) => {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      },
    )
    await page.route(
      /\/api\/v1\/agrar\/rations-optimization\/feeds(?:\?.*)?$/,
      async (route) => {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      },
    )
    if (c.screenId === 'portal/rationsoptimierung') {
      // Portal-Layout: genau ein Kundenkonto → Auto-Wahl (PORTAL-CONTEXT-001).
      await page.route(/\/api\/v1\/portal\/kundenkonten(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              customer_id: 'smoke-betrieb-1',
              customer_number: 'B-001',
              name: 'Smoke-Testbetrieb',
              rolle: 'betrieb',
              rechte: ['*'],
            },
          ]),
        })
      })
    }
  }
  if (c.specializedType === 'weighing') {
    await page.route(/\/api\/v1\/waage\/waagen(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
    await page.route(/\/api\/v1\/weighing-tickets(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
    await page.route(/\/api\/v1\/contracts(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
  if (c.specializedType === 'intake') {
    await page.route(/\/api\/v1\/annahme\/warteschlange(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], total: 0 }),
      })
    })
    await page.route(/\/api\/v1\/articles(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      })
    })
  }
  if (c.screenId === 'annahme/abrechnung') {
    await page.route(/\/api\/v1\/agrar\/settlements(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
  if (c.specializedType === 'admin_workbench') {
    // Nur Voice-Stack-API — nicht Masken-URLs mit "voice" im Screen-Id abfangen.
    await page.route(/\/api\/v1\/voice\/(?:status|resolve|polish|summary|synthesize|pipeline|transcribe)(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ enabled: false, ready: false, last_utterance: null }),
      })
    })
  }
  if (c.screenId === 'admin/vordruck-editor') {
    await page.route(/\/api\/v1\/admin\/vordrucke(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
  if (c.screenId === 'admin/screen-studio') {
    await page.route(/\/api\/v1\/studio\/catalog(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ semantic: null, domains: [] }),
      })
    })
    await page.route(/\/api\/v1\/studio\/drafts(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ drafts: [] }),
      })
    })
    await page.route(/\/api\/v1\/studio\/validate$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          definitionReady: true,
          violations: [],
          readiness: { generatorReady: true, errors: [], warnings: [] },
        }),
      })
    })
  }
  if (c.screenId === 'admin/GapPipelineConsole') {
    await page.route(/\/api\/v1\/gap\/pipeline\/status(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          year: new Date().getFullYear() - 1,
          gap_payments_count: 0,
          snapshot_count: 0,
          customers_with_analytics_count: 0,
          pipeline_complete: false,
        }),
      })
    })
  }
  if (c.screenId === 'admin/setup/dms-integration' || c.screenId === 'admin/setup') {
    await page.route(/\/api\/v1\/admin\/dms\/status(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ ok: false, configured: false, message: 'offline' }),
      })
    })
  }
  if (
    c.screenId === 'admin/control-center'
    || c.screenId === 'admin/control-center/agent-ops'
    || c.screenId === 'admin/control-center/superglue'
    || c.screenId === 'admin/agenten-integration'
  ) {
    const tenantId = '00000000-0000-0000-0000-000000000001'
    await page.route(/\/api\/v1\/admin\/agent-manifest(?:\?.*)?$/, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          version: '1',
          generated_at: new Date().toISOString(),
          auth: {},
          headers: [],
          links: [],
          examples: [],
          notes: [],
        }),
      })
    })
    await page.route(/\/api\/v1\/commands\/catalog(?:\?.*)?$/, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
    if (c.screenId === 'admin/control-center') {
      await page.route(/\/api\/v1\/agents\/neuroassist\/ops\/planning(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tenant_id: tenantId,
            storage_path: 'runtime/planning.json',
            calendar_window: 'week',
            suggested_items: [],
            planned_items: [],
            summary: {
              heartbeat_count: 0,
              planned_item_count: 0,
              blocked_connector_count: 0,
            },
          }),
        })
      })
      await page.route(/\/api\/v1\/agents\/neuroassist\/ops\/incidents(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tenant_id: tenantId,
            incident_count: 0,
            open_quarantine_count: 0,
            blocked_connector_count: 0,
            stale_ticket_count: 0,
            review_ticket_count: 0,
            journal_error_count: 0,
            incidents: [],
          }),
        })
      })
    }
    if (c.screenId === 'admin/control-center/agent-ops') {
      await page.route(/\/api\/v1\/agents\/neuroassist\/ops\/persistence(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tenant_id: tenantId,
            state_path: 'runtime/agent-ops/state.json',
            history_path: 'runtime/agent-ops/history.jsonl',
            persisted: false,
            history_count: 0,
            recent_events: [],
            snapshot_counts: {},
          }),
        })
      })
    }
    if (c.screenId === 'admin/control-center/superglue') {
      await page.route(/\/api\/v1\/agent\/integrations\/providers\/superglue\/tenants\/default\/admin-state(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tenant_id: 'default',
            storage_path: 'runtime/superglue/admin-state.json',
            connector_overrides: {},
            policy_overrides: {},
            wizard: { current_step: 'credentials', completed_steps: [] },
          }),
        })
      })
      await page.route(/\/api\/v1\/agent\/integrations\/providers\/superglue\/tenants\/default\/wizard(?:\?.*)?$/, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            tenant_id: 'default',
            current_step: 'credentials',
            completed_steps: [],
            recommended_actions: [],
            steps: [],
          }),
        })
      })
    }
  }
}

async function applyTheme(page: Page, theme: 'light' | 'dark'): Promise<void> {
  await page.addInitScript((mode) => {
    try {
      window.localStorage.setItem('theme', mode)
    } catch {
      /* storage may be blocked in locked-down browsers */
    }
    const root = document.documentElement
    root.classList.toggle('dark', mode === 'dark')
    root.classList.toggle('light', mode === 'light')
  }, theme)
}

test.describe('Gate D — Studio Cockpit Browser Smoke (Made-by-Studio)', () => {
  test.beforeEach(async ({ page }) => {
    // UI-Testsitzung: unsigniertes Token nur fuer Render/Routing (kein Live-SSO / keine API-Rechte).
    await setzeUiTestsitzung(page)
  })

  for (const c of COCKPIT_CASES) {
    for (const theme of ['light', 'dark'] as const) {
      test(`${c.label} — native-cockpit Runtime, Titel sichtbar (${theme})`, async ({ page }) => {
        await applyTheme(page, theme)
        await installCockpitMocks(page, c)
        const response = await page.goto(c.path, { waitUntil: 'domcontentloaded' })
        expect(response?.status() ?? 200).toBeLessThan(400)

        await expect(page.locator('html')).toHaveClass(
          theme === 'dark' ? /(?:^|\s)dark(?:\s|$)/ : /(?:^|\s)light(?:\s|$)/,
        )

        // Cockpit-Shell und Renderer teilen oft denselben testId — Runtime-Attribut ist eindeutig.
        const root = page.locator(`[data-testid="${c.testId}"][data-runtime="native-cockpit"]`)
        await expect(root).toBeVisible({ timeout: 30_000 })
        await expect(page.getByRole('heading', { name: c.title }).first()).toBeVisible({
          timeout: 30_000,
        })

        if (c.specializedTablist) {
          await expect(page.getByRole('tablist', { name: c.specializedTablist })).toBeVisible({
            timeout: 30_000,
          })
        } else if (c.specializedLandmark) {
          await expect(page.getByRole('region', { name: c.specializedLandmark })).toBeVisible({
            timeout: 30_000,
          })
        }

        await page.screenshot({
          path: `test-results/gate-d-${c.screenId.replace(/\//g, '_')}-${theme}.png`,
          fullPage: true,
        })
      })
    }
  }
})
