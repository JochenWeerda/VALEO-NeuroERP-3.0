import type { MaskConfig } from '@/components/mask-builder/types'

export const ENABLE_UNIVERSAL_MASK_AGRAR_KONTRAKT =
  import.meta.env.VITE_ENABLE_UNIVERSAL_MASK_AGRAR_KONTRAKT === 'true'

export const KONTRAKT_MASK_OBJECT_PAGE_CONFIG: MaskConfig = {
  title: 'Kontrakt',
  subtitle: 'Universal Mask Generator Pilot',
  type: 'object-page',
  tabs: [
    {
      key: 'kopf',
      label: 'Kopfdaten',
      columns: 2,
      fields: [
        { name: 'contract.contract_no', label: 'Kontraktnummer', type: 'text', readonly: true },
        { name: 'contract.party_name', label: 'Geschaeftspartner', type: 'text', readonly: true },
        { name: 'contract.contract_type', label: 'Kontraktart', type: 'text', readonly: true },
        { name: 'contract.status', label: 'Status', type: 'text', readonly: true },
        { name: 'contract.valid_from', label: 'Gueltig ab', type: 'date', readonly: true },
        { name: 'contract.valid_to', label: 'Gueltig bis', type: 'date', readonly: true },
        { name: 'contract.total_quantity', label: 'Gesamtmenge', type: 'number', readonly: true },
        { name: 'contract.rest_quantity', label: 'Restmenge', type: 'number', readonly: true },
        { name: 'contract.unit', label: 'Einheit', type: 'text', readonly: true },
        { name: 'contract.payment_terms', label: 'Zahlungsbedingungen', type: 'text', readonly: true },
        { name: 'contract.notes', label: 'Notizen', type: 'textarea', readonly: true },
      ],
    },
    {
      key: 'positionen',
      label: 'Positionen',
      columns: 1,
      fields: [],
    },
    {
      key: 'umsaetze',
      label: 'Umsaetze',
      columns: 1,
      fields: [],
    },
  ],
  actions: [],
  api: {
    baseUrl: '',
    endpoints: {},
  },
}
