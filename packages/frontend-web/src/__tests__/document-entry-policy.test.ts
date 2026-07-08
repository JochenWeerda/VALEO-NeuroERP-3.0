import { describe, expect, it } from 'vitest'
import {
  DOCUMENT_ENTRY_POLICIES,
  getDocumentEntryPolicies,
  getDocumentEntryPolicy,
  resolveCapturedDocumentWorkflow,
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
      if (policy.workflowPolicy !== 'standalone') {
        expect(policy.flowSpine?.processKey).toMatch(/^(order-to-cash|procure-to-pay)$/)
      }
    }
  })

  it('uses capture-then-resolve for immediate outgoing delivery notes', () => {
    const policy = getDocumentEntryPolicy('outgoing-delivery-note')
    const intent = resolveDocumentWorkflowIntent(policy, {
      customerId: 'C-1000',
      orderId: 'SO-42',
    })

    expect(policy.workflowPolicy).toBe('capture-then-resolve')
    expect(policy.flowSpine).toMatchObject({
      processKey: 'order-to-cash',
      resumeNodeId: 'delivery',
      resumeRoute: '/verkauf/lieferschein-erfassung',
    })
    expect(intent.mode).toBe('attach')
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

  it('starts a new flow spine after quick capture when no candidate matches', () => {
    const policy = getDocumentEntryPolicy('outgoing-delivery-note')
    const resolution = resolveCapturedDocumentWorkflow(policy, {
      documentId: 'DN-UUID-1',
      documentNumber: 'LS-2026-42',
      partnerName: 'Musterkunde GmbH',
      matchValues: {
        customerId: 'C-1000',
        customerNumber: '1000',
      },
      candidates: [],
    })

    expect(resolution.mode).toBe('start')
    expect(resolution.flowSpine?.processKey).toBe('order-to-cash')
    expect(resolution.createPayload).toMatchObject({
      customer_id: 'C-1000',
      customer_name: 'Musterkunde GmbH',
      entry_mode: 'quick-document-capture',
      linked_document_id: 'DN-UUID-1',
      linked_document_type: 'delivery_note',
    })
    expect(resolution.savePayload).toMatchObject({
      resume_node_id: 'delivery',
      resume_route: '/verkauf/lieferschein-erfassung',
      business_status: 'document-captured',
    })
  })

  it('attaches a captured document to one confident existing flow spine candidate', () => {
    const policy = getDocumentEntryPolicy('outgoing-delivery-note')
    const resolution = resolveCapturedDocumentWorkflow(policy, {
      documentId: 'DN-UUID-1',
      documentNumber: 'LS-2026-42',
      matchValues: {
        customerId: 'C-1000',
        orderId: 'SO-42',
      },
      candidates: [
        {
          instanceId: 'WF-1',
          processKey: 'order-to-cash',
          confidence: 'exact',
          matchedKeys: ['customerId', 'orderId'],
        },
      ],
    })

    expect(resolution.mode).toBe('attach')
    expect(resolution.instanceId).toBe('WF-1')
    expect(resolution.matchedKeys).toEqual(['customerId', 'orderId'])
    expect(resolution.createPayload).toBeUndefined()
    expect(resolution.savePayload?.resume_payload).toMatchObject({
      documentId: 'DN-UUID-1',
      documentType: 'delivery_note',
      entryMode: 'quick-document-capture',
    })
  })

  it('requires manual review for ambiguous captured document candidates', () => {
    const policy = getDocumentEntryPolicy('outgoing-delivery-note')
    const resolution = resolveCapturedDocumentWorkflow(policy, {
      documentId: 'DN-UUID-1',
      matchValues: {
        customerId: 'C-1000',
      },
      candidates: [
        { instanceId: 'WF-1', processKey: 'order-to-cash', confidence: 'strong' },
        { instanceId: 'WF-2', processKey: 'order-to-cash', confidence: 'strong' },
      ],
    })

    expect(resolution.mode).toBe('manual-review')
    expect(resolution.instanceId).toBeUndefined()
    expect(resolution.createPayload).toBeUndefined()
    expect(resolution.candidates).toHaveLength(2)
  })

  it('requires manual review for weak single candidates', () => {
    const policy = getDocumentEntryPolicy('incoming-supplier-invoice')
    const resolution = resolveCapturedDocumentWorkflow(policy, {
      documentId: 'SI-UUID-1',
      documentNumber: 'ER-2026-42',
      partnerName: 'Lieferant KG',
      candidates: [{ instanceId: 'WF-P2P-1', processKey: 'procure-to-pay', confidence: 'weak' }],
    })

    expect(resolution.mode).toBe('manual-review')
    expect(resolution.flowSpine?.processKey).toBe('procure-to-pay')
    expect(resolution.createPayload).toBeUndefined()
  })
})
