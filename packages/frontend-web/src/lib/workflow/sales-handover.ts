export interface SalesHandoverContext {
  customerId?: string
  customerNumber?: string
  customerName?: string
  entryMode?: string
  sourceOfferId?: string
  sourceOrderId?: string
  sourceDeliveryId?: string
  invoiceId?: string
  invoiceNumber?: string
}

const SALES_HANDOVER_KEYS = {
  customerId: 'customerId',
  customerNumber: 'kunde',
  customerName: 'kundeName',
  entryMode: 'entryMode',
  sourceOfferId: 'angebot',
  sourceOrderId: 'auftrag',
  sourceDeliveryId: 'lieferschein',
  invoiceId: 'rechnungId',
  invoiceNumber: 'rechnungsnr',
} as const

export function parseSalesHandover(searchParams: URLSearchParams): SalesHandoverContext {
  const clean = (value: string | null): string | undefined => value?.trim() || undefined
  return {
    customerId: clean(searchParams.get('customerId')),
    customerNumber: clean(searchParams.get('kunde')) ?? clean(searchParams.get('customerNumber')),
    customerName: clean(searchParams.get('kundeName')) ?? clean(searchParams.get('customerName')),
    entryMode: clean(searchParams.get('entryMode')),
    sourceOfferId: clean(searchParams.get('angebot')) ?? clean(searchParams.get('fromOffer')),
    sourceOrderId: clean(searchParams.get('auftrag')),
    sourceDeliveryId: clean(searchParams.get('lieferschein')),
    invoiceId: clean(searchParams.get('rechnungId')) ?? clean(searchParams.get('id')),
    invoiceNumber: clean(searchParams.get('rechnungsnr')) ?? clean(searchParams.get('rechnung')),
  }
}

export function buildSalesHandoverPath(path: string, context: SalesHandoverContext): string {
  const params = new URLSearchParams()
  for (const [contextKey, queryKey] of Object.entries(SALES_HANDOVER_KEYS)) {
    const value = context[contextKey as keyof SalesHandoverContext]
    if (value) params.set(queryKey, value)
  }
  const query = params.toString()
  return query ? `${path}?${query}` : path
}
