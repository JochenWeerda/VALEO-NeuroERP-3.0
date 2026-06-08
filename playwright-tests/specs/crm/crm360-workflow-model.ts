export type CrmRevenueState =
  | 'customer'
  | 'offer'
  | 'order'
  | 'delivery'
  | 'invoice'
  | 'receivables'

export interface CrmRevenueTransition {
  from: CrmRevenueState
  action: string
  to: CrmRevenueState
  route: string
  requiredContext: string[]
}

export const CRM_REVENUE_MODEL: readonly CrmRevenueTransition[] = [
  {
    from: 'customer',
    action: 'createOffer',
    to: 'offer',
    route: '/sales/angebot-erstellen',
    requiredContext: ['kunde', 'kundeName', 'entryMode'],
  },
  {
    from: 'offer',
    action: 'createOrder',
    to: 'order',
    route: '/sales/order-editor',
    requiredContext: ['kunde'],
  },
  {
    from: 'order',
    action: 'createDelivery',
    to: 'delivery',
    route: '/sales/delivery-editor',
    requiredContext: ['kunde'],
  },
  {
    from: 'delivery',
    action: 'createInvoice',
    to: 'invoice',
    route: '/sales/invoice-editor',
    requiredContext: ['kunde'],
  },
  {
    from: 'invoice',
    action: 'openReceivables',
    to: 'receivables',
    route: '/finance/op-debitoren',
    requiredContext: ['kunden_nr'],
  },
] as const
