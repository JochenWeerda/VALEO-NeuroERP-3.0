export type DocumentDirection = 'incoming' | 'outgoing'
export type DocumentWorkflowPolicy = 'attach-or-start' | 'capture-then-resolve' | 'standalone'
export type DocumentPartyRole = 'customer' | 'supplier'
export type DocumentWorkflowIntentMode = 'attach' | 'start' | 'standalone'
export type CapturedDocumentWorkflowMode = 'attach' | 'start' | 'manual-review' | 'standalone'
export type DocumentFlowSpineProcessKey = 'order-to-cash' | 'procure-to-pay'
export type DocumentWorkflowCandidateConfidence = 'exact' | 'strong' | 'weak'

export type DocumentFlowSpineBinding = {
  processKey: DocumentFlowSpineProcessKey
  routePath: string
  resumeNodeId?: string
  resumeRoute?: string
}

export type DocumentEntryPolicy = {
  id: string
  label: string
  direction: DocumentDirection
  documentType: string
  partyRole: DocumentPartyRole
  targetRoute: string
  workflowPolicy: DocumentWorkflowPolicy
  matchKeys: readonly string[]
  flowSpine?: DocumentFlowSpineBinding
}

export type DocumentMatchValues = Partial<Record<string, string | number | null | undefined>>

export type DocumentWorkflowIntent = {
  mode: DocumentWorkflowIntentMode
  matchedKeys: string[]
  targetRoute: string
  reason: string
  flowSpine?: DocumentFlowSpineBinding
}

export type DocumentWorkflowCandidate = {
  instanceId: string
  processKey?: string
  label?: string
  matchedKeys?: readonly string[]
  confidence?: DocumentWorkflowCandidateConfidence
}

export type CapturedDocumentWorkflowInput = {
  documentId: string
  documentNumber?: string
  matchValues?: DocumentMatchValues
  candidates?: readonly DocumentWorkflowCandidate[]
  partnerName?: string
  subject?: string
}

export type DocumentFlowSpineCreatePayload = {
  label?: string
  customer_id?: string
  customer_name?: string
  partner_name?: string
  subject?: string
  entry_mode?: string
  linked_document_id?: string
  linked_document_type?: string
}

export type DocumentFlowSpineSavePayload = {
  resume_node_id?: string
  resume_route?: string
  resume_payload: Record<string, unknown>
  business_status?: string
  action_label?: string
}

export type CapturedDocumentWorkflowResolution = {
  mode: CapturedDocumentWorkflowMode
  policyId: string
  matchedKeys: string[]
  targetRoute: string
  reason: string
  flowSpine?: DocumentFlowSpineBinding
  instanceId?: string
  candidate?: DocumentWorkflowCandidate
  candidates?: readonly DocumentWorkflowCandidate[]
  createPayload?: DocumentFlowSpineCreatePayload
  savePayload?: DocumentFlowSpineSavePayload
}

const ORDER_TO_CASH_FLOW: DocumentFlowSpineBinding = {
  processKey: 'order-to-cash',
  routePath: '/workflow/flow-spine-order-to-cash',
}

const PROCURE_TO_PAY_FLOW: DocumentFlowSpineBinding = {
  processKey: 'procure-to-pay',
  routePath: '/workflow/flow-spine-procure-to-pay',
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
    flowSpine: { ...ORDER_TO_CASH_FLOW, resumeNodeId: 'offer', resumeRoute: '/sales/angebot/neu' },
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
    flowSpine: { ...ORDER_TO_CASH_FLOW, resumeNodeId: 'order', resumeRoute: '/sales/order' },
  },
  {
    id: 'outgoing-delivery-note',
    label: 'Sofort-Lieferschein erfassen',
    direction: 'outgoing',
    documentType: 'delivery_note',
    partyRole: 'customer',
    targetRoute: '/verkauf/lieferschein-erfassung',
    workflowPolicy: 'capture-then-resolve',
    matchKeys: ['customerId', 'customerNumber', 'orderId', 'deliveryNoteId'],
    flowSpine: { ...ORDER_TO_CASH_FLOW, resumeNodeId: 'delivery', resumeRoute: '/verkauf/lieferschein-erfassung' },
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
    flowSpine: { ...ORDER_TO_CASH_FLOW, resumeNodeId: 'invoice', resumeRoute: '/sales/invoice' },
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
    flowSpine: { ...ORDER_TO_CASH_FLOW, resumeNodeId: 'invoice', resumeRoute: '/sales/credit-notes' },
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
    flowSpine: { ...PROCURE_TO_PAY_FLOW, resumeNodeId: 'delivery-advice', resumeRoute: '/einkauf/anlieferavis/neu' },
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
    flowSpine: { ...PROCURE_TO_PAY_FLOW, resumeNodeId: 'goods-receipt', resumeRoute: '/einkauf/wareneingang' },
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
    flowSpine: { ...PROCURE_TO_PAY_FLOW, resumeNodeId: 'goods-receipt', resumeRoute: '/einkauf/lieferschein-erfassung' },
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
    flowSpine: { ...PROCURE_TO_PAY_FLOW, resumeNodeId: 'invoice', resumeRoute: '/einkauf/rechnung-eingang-erfassung' },
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

export function getMatchedDocumentKeys(policy: DocumentEntryPolicy, matchValues: DocumentMatchValues = {}): string[] {
  return policy.matchKeys.filter((key) => {
    const value = matchValues[key]
    return value !== undefined && value !== null && String(value).trim().length > 0
  })
}

export function resolveDocumentWorkflowIntent(
  policy: DocumentEntryPolicy,
  matchValues: DocumentMatchValues = {},
): DocumentWorkflowIntent {
  const matchedKeys = getMatchedDocumentKeys(policy, matchValues)

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
      flowSpine: policy.flowSpine,
      reason: 'Vorhandene Match-Keys erlauben die Zuordnung zu einem bestehenden Kunden-/Lieferanten-Workflow.',
    }
  }

  return {
    mode: 'start',
    matchedKeys,
    targetRoute: policy.targetRoute,
    flowSpine: policy.flowSpine,
    reason: 'Ohne Match-Key ist der Beleg ein Einstiegspunkt fuer einen neuen Workflow.',
  }
}

export function resolveCapturedDocumentWorkflow(
  policy: DocumentEntryPolicy,
  input: CapturedDocumentWorkflowInput,
): CapturedDocumentWorkflowResolution {
  const matchValues = input.matchValues ?? {}
  const matchedKeys = getMatchedDocumentKeys(policy, matchValues)

  if (policy.workflowPolicy === 'standalone') {
    return {
      mode: 'standalone',
      policyId: policy.id,
      matchedKeys,
      targetRoute: policy.targetRoute,
      reason: 'Standalone-Erfassung bleibt ohne Flow-Spine-Zuordnung.',
    }
  }

  if (!policy.flowSpine) {
    return {
      mode: 'manual-review',
      policyId: policy.id,
      matchedKeys,
      targetRoute: policy.targetRoute,
      reason: 'Die Belegart hat keinen Flow-Spine-Vertrag und darf deshalb nicht automatisch zugeordnet werden.',
    }
  }

  const candidates = (input.candidates ?? []).filter((candidate) => candidate.instanceId.trim().length > 0)
  const relevantCandidates = candidates.filter(
    (candidate) => !candidate.processKey || candidate.processKey === policy.flowSpine?.processKey,
  )

  if (relevantCandidates.length === 1 && relevantCandidates[0]?.confidence !== 'weak') {
    const candidate = relevantCandidates[0]
    return {
      mode: 'attach',
      policyId: policy.id,
      matchedKeys: candidate.matchedKeys ? [...candidate.matchedKeys] : matchedKeys,
      targetRoute: policy.targetRoute,
      flowSpine: policy.flowSpine,
      instanceId: candidate.instanceId,
      candidate,
      savePayload: buildDocumentFlowSpineSavePayload(policy, input, matchedKeys),
      reason: 'Ein eindeutiger Flow-Spine-Treffer wurde gefunden; der Beleg wird an diesen Vorgang angehaengt.',
    }
  }

  if (relevantCandidates.length > 1 || (relevantCandidates.length === 1 && relevantCandidates[0]?.confidence === 'weak')) {
    return {
      mode: 'manual-review',
      policyId: policy.id,
      matchedKeys,
      targetRoute: policy.targetRoute,
      flowSpine: policy.flowSpine,
      candidates: relevantCandidates,
      reason: 'Mehrere oder unsichere Flow-Spine-Treffer duerfen nicht automatisch zugeordnet werden.',
    }
  }

  return {
    mode: 'start',
    policyId: policy.id,
    matchedKeys,
    targetRoute: policy.targetRoute,
    flowSpine: policy.flowSpine,
    createPayload: buildDocumentFlowSpineCreatePayload(policy, input, matchedKeys),
    savePayload: buildDocumentFlowSpineSavePayload(policy, input, matchedKeys),
    reason: 'Kein bestehender Flow-Spine-Treffer gefunden; der Beleg startet einen neuen Vorgang.',
  }
}

function buildDocumentFlowSpineCreatePayload(
  policy: DocumentEntryPolicy,
  input: CapturedDocumentWorkflowInput,
  matchedKeys: string[],
): DocumentFlowSpineCreatePayload {
  const documentLabel = input.documentNumber?.trim() || input.documentId
  const subject = input.subject?.trim() || `${policy.label}: ${documentLabel}`
  const payload: DocumentFlowSpineCreatePayload = {
    label: subject,
    subject,
    entry_mode: 'quick-document-capture',
    linked_document_id: input.documentId,
    linked_document_type: policy.documentType,
  }

  const partnerName = input.partnerName?.trim()
  if (policy.partyRole === 'customer') {
    const customerId = stringValue(input.matchValues?.customerId)
    if (customerId) payload.customer_id = customerId
    if (partnerName) payload.customer_name = partnerName
  } else if (partnerName) {
    payload.partner_name = partnerName
  }

  if (matchedKeys.length === 0 && !partnerName) {
    payload.subject = `${subject} ohne Partner-Match`
  }

  return payload
}

function buildDocumentFlowSpineSavePayload(
  policy: DocumentEntryPolicy,
  input: CapturedDocumentWorkflowInput,
  matchedKeys: string[],
): DocumentFlowSpineSavePayload {
  return {
    resume_node_id: policy.flowSpine?.resumeNodeId,
    resume_route: policy.flowSpine?.resumeRoute ?? policy.targetRoute,
    business_status: 'document-captured',
    action_label: 'Beleg-Schnellstart zugeordnet',
    resume_payload: {
      documentId: input.documentId,
      documentNumber: input.documentNumber,
      documentType: policy.documentType,
      policyId: policy.id,
      matchedKeys,
      entryMode: 'quick-document-capture',
    },
  }
}

function stringValue(value: string | number | null | undefined): string | undefined {
  if (value === undefined || value === null) return undefined
  const normalized = String(value).trim()
  return normalized || undefined
}
