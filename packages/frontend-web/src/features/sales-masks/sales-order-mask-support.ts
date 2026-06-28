import type { MaskConfig } from '@/components/mask-builder/types'

export const ENABLE_UNIVERSAL_MASK_SALES_ORDER =
  import.meta.env.VITE_ENABLE_UNIVERSAL_MASK_SALES_ORDER === 'true'

export const SALES_ORDER_MASK_OBJECT_PAGE_CONFIG: MaskConfig = {
  title: 'Verkaufsauftrag',
  subtitle: 'Universal Mask Generator Pilot',
  type: 'object-page',
  tabs: [
    {
      key: 'kopf',
      label: 'Kopfdaten',
      columns: 2,
      fields: [
        { name: 'order.order_number', label: 'Auftragsnummer', type: 'text', readonly: true },
        { name: 'order.customer_name', label: 'Kunde', type: 'text', readonly: true },
        { name: 'order.subject', label: 'Betreff', type: 'text', readonly: true },
        { name: 'order.status', label: 'Status', type: 'text', readonly: true },
        { name: 'order.contact_person', label: 'Ansprechpartner', type: 'text', readonly: true },
        { name: 'order.payment_terms', label: 'Zahlungsbedingungen', type: 'text', readonly: true },
      ],
    },
    {
      key: 'positionen',
      label: 'Positionen',
      columns: 1,
      fields: [],
    },
    {
      key: 'lieferung',
      label: 'Lieferung',
      columns: 2,
      fields: [
        { name: 'order.delivery_date', label: 'Liefertermin', type: 'date', readonly: true },
        { name: 'order.shipping_method', label: 'Versandart', type: 'text', readonly: true },
        { name: 'order.delivery_address', label: 'Lieferadresse', type: 'textarea', readonly: true },
      ],
    },
    {
      key: 'dokumente',
      label: 'Dokumente',
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
