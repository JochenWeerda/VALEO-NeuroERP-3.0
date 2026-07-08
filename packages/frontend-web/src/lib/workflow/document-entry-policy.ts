export type DocumentDirection = 'incoming' | 'outgoing'
export type DocumentWorkflowPolicy = 'attach-or-start' | 'standalone'
export type DocumentPartyRole = 'customer' | 'supplier'
export type DocumentWorkflowIntentMode = 'attach' | 'start' | 'standalone'

export type DocumentEntryPolicy = {
  id: string
  label: string
  direction: DocumentDirection
  documentType: string
  partyRole: DocumentPartyRole
  targetRoute: string
  workflowPolicy: DocumentWorkflowPolicy
  matchKeys: readonly string[]
}

export type DocumentMatchValues = Partial<Record<string, string | number | null | undefined>>

export type DocumentWorkflowIntent = {
  mode: DocumentWorkflowIntentMode
  matchedKeys: string[]
  targetRoute: string
  reason: string
}

export const DOCUMENT_ENTRY_POLICIES = [
  {
    id: 'outgoing-offer',
    label: 'Angebot erfassen',
    direction: 'outgoing',
    documentType: 'sales_offer',
    partyRole: 'customer',
    targetRoute: '/sales/angebot/neu',
    workflowPolicy: 'attach-or-start',
    matchKeys: ['customerId', 'customerNumber', 'opportunityId', 'contractId'],
  },
  {
    id: 'outgoing-order',
    label: 'Auftrag erfassen',
    direction: 'outgoing',
    documentType: 'sales_order',
    partyRole: 'customer',
    targetRoute: '/sales/order',
    workflowPolicy: 'attach-or-start',
    matchKeys: ['customerId', 'customerNumber', 'offerId', 'contractId'],
  },
  {
    id: 'outgoing-delivery-note',
    label: 'Sofort-Lieferschein erfassen',
    direction: 'outgoing',
    documentType: 'delivery_note',
    partyRole: 'customer',
    targetRoute: '/verkauf/lieferschein-erfassung',
    workflowPolicy: 'standalone',
    matchKeys: ['customerId', 'customerNumber', 'orderId', 'deliveryNoteId'],
  },
  {
    id: 'outgoing-invoice',
    label: 'Rechnung erfassen',
    direction: 'outgoing',
    documentType: 'sales_invoice',
    partyRole: 'customer',
    targetRoute: '/sales/invoice',
    workflowPolicy: 'attach-or-start',
    matchKeys: ['customerId', 'customerNumber', 'orderId', 'deliveryNoteId'],
  },
  {
    id: 'outgoing-credit-note',
    label: 'Gutschrift erfassen',
    direction: 'outgoing',
    documentType: 'credit_note',
    partyRole: 'customer',
    targetRoute: '/sales/credit-notes',
    workflowPolicy: 'attach-or-start',
    matchKeys: ['customerId', 'customerNumber', 'invoiceId', 'deliveryNoteId'],
  },
  {
    id: 'incoming-delivery-advice',
    label: 'Anlieferavis erfassen',
    direction: 'incoming',
    documentType: 'delivery_advice',
    partyRole: 'supplier',
    targetRoute: '/einkauf/anlieferavis/neu',
    workflowPolicy: 'attach-or-start',
    matchKeys: ['supplierId', 'supplierNumber', 'purchaseOrderId', 'contractId'],
  },
  {
    id: 'incoming-goods-receipt',
    label: 'Wareneingang erfassen',
    direction: 'incoming',
    documentType: 'goods_receipt',
    partyRole: 'supplier',
    targetRoute: '/einkauf/wareneingang',
    workflowPolicy: 'attach-or-start',
    matchKeys: ['supplierId', 'supplierNumber', 'purchaseOrderId', 'deliveryAdviceId'],
  },
  {
    id: 'incoming-delivery-note',
    label: 'Lieferschein Eingang erfassen',
    direction: 'incoming',
    documentType: 'supplier_delivery_note',
    partyRole: 'supplier',
    targetRoute: '/einkauf/lieferschein-erfassung',
    workflowPolicy: 'attach-or-start',
    matchKeys: ['supplierId', 'supplierNumber', 'purchaseOrderId', 'deliveryAdviceId'],
  },
  {
    id: 'incoming-supplier-invoice',
    label: 'Rechnungseingang erfassen',
    direction: 'incoming',
    documentType: 'supplier_invoice',
    partyRole: 'supplier',
    targetRoute: '/einkauf/rechnung-eingang-erfassung',
    workflowPolicy: 'attach-or-start',
    matchKeys: ['supplierId', 'supplierNumber', 'purchaseOrderId', 'goodsReceiptId', 'deliveryNoteId'],
  },
] as const satisfies readonly DocumentEntryPolicy[]

export type DocumentEntryPolicyId = (typeof DOCUMENT_ENTRY_POLICIES)[number]['id']

export function getDocumentEntryPolicy(id: DocumentEntryPolicyId): DocumentEntryPolicy {
  const policy = DOCUMENT_ENTRY_POLICIES.find((entry) => entry.id === id)
  if (!policy) {
    throw new Error(`Unknown document entry policy: ${id}`)
  }
  return policy
}

export function getDocumentEntryPolicies(direction?: DocumentDirection): DocumentEntryPolicy[] {
  return DOCUMENT_ENTRY_POLICIES.filter((entry) => !direction || entry.direction === direction)
}

export function resolveDocumentWorkflowIntent(
  policy: DocumentEntryPolicy,
  matchValues: DocumentMatchValues = {},
): DocumentWorkflowIntent {
  const matchedKeys = policy.matchKeys.filter((key) => {
    const value = matchValues[key]
    return value !== undefined && value !== null && String(value).trim().length > 0
  })

  if (policy.workflowPolicy === 'standalone') {
    return {
      mode: 'standalone',
      matchedKeys,
      targetRoute: policy.targetRoute,
      reason: 'Standalone-Erfassung erzeugt nur die Belegnummer; ein Workflow-Case wird nicht automatisch gestartet.',
    }
  }

  if (matchedKeys.length > 0) {
    return {
      mode: 'attach',
      matchedKeys,
      targetRoute: policy.targetRoute,
      reason: 'Vorhandene Match-Keys erlauben die Zuordnung zu einem bestehenden Kunden-/Lieferanten-Workflow.',
    }
  }

  return {
    mode: 'start',
    matchedKeys,
    targetRoute: policy.targetRoute,
    reason: 'Ohne Match-Key ist der Beleg ein Einstiegspunkt fuer einen neuen Workflow.',
  }
}
