import type { MaskConfig } from '@/components/mask-builder/types'
import type { ScreenTableDefinition } from '@/components/mask-builder/schema'

export type RolloutPilotSpec = {
  screenId: string
  domain: string
  title: string
  envFlag: keyof ImportMetaEnv
  legacyRouteHint?: string
}

export const ENABLE_UNIVERSAL_MASK_ROLLOUTS =
  import.meta.env.VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS === 'true'

export const ROLLOUT_PILOT_SPECS: RolloutPilotSpec[] = [
  { screenId: 'lager/stock-movement', domain: 'lager', title: 'Lagerbewegung', envFlag: 'VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS' },
  { screenId: 'lager/article-stock', domain: 'lager', title: 'Artikelbestand', envFlag: 'VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS' },
  { screenId: 'finance/ap-invoice', domain: 'finance', title: 'Eingangsrechnung', envFlag: 'VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS' },
  { screenId: 'finance/ar-open-item', domain: 'finance', title: 'OP Debitor', envFlag: 'VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS' },
  { screenId: 'einkauf/purchase-order', domain: 'einkauf', title: 'Bestellung', envFlag: 'VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS' },
  { screenId: 'einkauf/supplier', domain: 'einkauf', title: 'Lieferant', envFlag: 'VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS' },
  { screenId: 'crm/opportunity', domain: 'crm', title: 'Opportunity', envFlag: 'VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS' },
  { screenId: 'sales/delivery-note', domain: 'sales', title: 'Lieferschein', envFlag: 'VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS' },
  { screenId: 'agrar/harvest-settlement', domain: 'agrar', title: 'Ernte-Abrechnung', envFlag: 'VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS' },
  { screenId: 'finance/payment-run', domain: 'finance', title: 'Zahlungslauf', envFlag: 'VITE_ENABLE_UNIVERSAL_MASK_ROLLOUTS' },
]

export function isRolloutPilotEnabled(screenId: string): boolean {
  if (!ENABLE_UNIVERSAL_MASK_ROLLOUTS) return false
  return ROLLOUT_PILOT_SPECS.some((spec) => spec.screenId === screenId)
}

export function getRolloutSpec(screenId: string): RolloutPilotSpec | undefined {
  return ROLLOUT_PILOT_SPECS.find((spec) => spec.screenId === screenId)
}

function genericColumns(keys: string[]) {
  return keys.slice(0, 8).map((key) => ({
    key,
    label: key.replace(/_/g, ' '),
    numeric: /amount|quantity|betrag|menge|preis|count|total|stock/i.test(key),
  }))
}

export function buildGenericTabTables(
  tabKey: string,
  sampleItem?: Record<string, unknown>,
): ScreenTableDefinition[] {
  const keys = sampleItem ? Object.keys(sampleItem) : ['value']
  return [
    {
      key: `${tabKey}_table`,
      label: tabKey,
      virtualized: true,
      rowHeight: 52,
      columns: genericColumns(keys),
    },
  ]
}

export function buildRolloutMaskConfig(screenId: string, title: string): MaskConfig {
  const spec = getRolloutSpec(screenId)
  const domain = spec?.domain ?? 'admin'
  return {
    title,
    subtitle: 'Universal Mask Rollout Pilot',
    type: 'object-page',
    tabs: [
      {
        key: 'kopf',
        label: 'Kopfdaten',
        columns: 2,
        fields: [
          { name: 'summary.status', label: 'Status', type: 'text', readonly: true },
          { name: 'summary.title', label: 'Bezeichnung', type: 'text', readonly: true },
        ],
      },
    ],
    actions: [],
    api: { baseUrl: '', endpoints: {} },
    domain,
  }
}
