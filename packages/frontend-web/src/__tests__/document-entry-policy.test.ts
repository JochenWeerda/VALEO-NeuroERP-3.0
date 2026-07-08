import { describe, expect, it } from 'vitest'
import {
  DOCUMENT_ENTRY_POLICIES,
  getDocumentEntryPolicies,
  getDocumentEntryPolicy,
  resolveDocumentWorkflowIntent,
} from '@/lib/workflow/document-entry-policy'

describe('document entry policy', () => {
  it('models incoming and outgoing entry routes with party role and match keys', () => {
    expect(getDocumentEntryPolicies('incoming')).toHaveLength(4)
    expect(getDocumentEntryPolicies('outgoing')).toHaveLength(5)

    for (const policy of DOCUMENT_ENTRY_POLICIES) {
      expect(policy.targetRoute).toMatch(/^\//)
      expect(policy.matchKeys.length).toBeGreaterThan(0)
      expect(['customer', 'supplier']).toContain(policy.partyRole)
    }
  })

  it('keeps immediate outgoing delivery notes standalone by default', () => {
    const policy = getDocumentEntryPolicy('outgoing-delivery-note')
    const intent = resolveDocumentWorkflowIntent(policy, {
      customerId: 'C-1000',
      orderId: 'SO-42',
    })

    expect(intent.mode).toBe('standalone')
    expect(intent.matchedKeys).toEqual(['customerId', 'orderId'])
    expect(intent.targetRoute).toBe('/verkauf/lieferschein-erfassung')
  })

  it('attaches attach-or-start documents when match keys are present', () => {
    const policy = getDocumentEntryPolicy('incoming-supplier-invoice')
    const intent = resolveDocumentWorkflowIntent(policy, {
      supplierId: 'S-1000',
      purchaseOrderId: 'PO-42',
    })

    expect(intent.mode).toBe('attach')
    expect(intent.matchedKeys).toEqual(['supplierId', 'purchaseOrderId'])
  })

  it('starts a new workflow when attach-or-start documents have no match keys', () => {
    const policy = getDocumentEntryPolicy('outgoing-invoice')
    const intent = resolveDocumentWorkflowIntent(policy)

    expect(intent.mode).toBe('start')
    expect(intent.matchedKeys).toEqual([])
  })
})
