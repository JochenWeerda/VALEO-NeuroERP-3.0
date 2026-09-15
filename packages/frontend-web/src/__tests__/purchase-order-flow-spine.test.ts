import { describe, expect, it, vi, beforeEach } from 'vitest'
import {
  candidatesFromDocumentHits,
  linkPurchaseOrderToFlowSpine,
} from '@/lib/workflow/purchase-order-flow-spine'
import type { FlowSpineInstance } from '@/lib/api/flow-spines'

const getMock = vi.hoisted(() => vi.fn())
const postMock = vi.hoisted(() => vi.fn())
const patchMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: getMock,
    post: postMock,
    patch: patchMock,
  },
}))

describe('purchase-order flow spine (FSX-012)', () => {
  beforeEach(() => {
    getMock.mockReset()
    postMock.mockReset()
    patchMock.mockReset()
  })

  it('treats a matching open document hit as exact and ignores completed cases', () => {
    const instances = [
      {
        instance_id: 'wf-open',
        process_key: 'procure-to-pay',
        label: 'Offen',
        lifecycle_status: 'in_progress',
        linked_document_id: 'PO-1',
      },
      {
        instance_id: 'wf-done',
        process_key: 'procure-to-pay',
        lifecycle_status: 'completed',
        linked_document_id: 'PO-1',
      },
    ] as FlowSpineInstance[]

    const candidates = candidatesFromDocumentHits(instances, 'PO-1', 'procure-to-pay')
    expect(candidates).toEqual([
      expect.objectContaining({ instanceId: 'wf-open', confidence: 'exact' }),
    ])
  })

  it('starts a new case after save when FSX-010 finds nothing', async () => {
    getMock.mockResolvedValue({ instances: [] })
    postMock
      .mockResolvedValueOnce({ instance_id: 'wf-new' })
      .mockResolvedValue({})

    await linkPurchaseOrderToFlowSpine({
      documentId: 'PO-1',
      supplierId: 'S-1',
      supplierName: 'Nordhafen',
      resumeRoute: '/einkauf/bestellungen/PO-1',
    })

    expect(getMock).toHaveBeenCalledWith(
      '/api/v1/process/flow-spines/procure-to-pay/instances',
      expect.objectContaining({
        params: { linked_document_id: 'PO-1', linked_document_type: 'purchase_order' },
      }),
    )
    expect(postMock.mock.calls[0]?.[0]).toBe('/api/v1/process/flow-spines/procure-to-pay/instances')
    expect(postMock.mock.calls[0]?.[1]).toEqual(
      expect.objectContaining({
        linked_document_id: 'PO-1',
        linked_document_type: 'purchase_order',
      }),
    )
    expect(postMock.mock.calls.some((call) => String(call[0]).endsWith('/save'))).toBe(true)
  })

  it('binds a URL handover via PATCH and does not create a second case', async () => {
    getMock.mockResolvedValue({ instance_id: 'wf-1', linked_document_id: null })
    patchMock.mockResolvedValue({ instance_id: 'wf-1' })
    postMock.mockResolvedValue({})

    await linkPurchaseOrderToFlowSpine({
      documentId: 'PO-2',
      handover: { process: 'procure-to-pay', instanceId: 'wf-1' },
      resumeRoute: '/einkauf/bestellungen/PO-2',
    })

    expect(getMock).toHaveBeenCalledWith('/api/v1/process/flow-spines/procure-to-pay/instances/wf-1')
    expect(patchMock).toHaveBeenCalledWith(
      '/api/v1/process/flow-spines/procure-to-pay/instances/wf-1',
      expect.objectContaining({
        linked_document_id: 'PO-2',
        linked_document_type: 'purchase_order',
      }),
    )
    const createCalls = postMock.mock.calls.filter((call) => String(call[0]).endsWith('/instances'))
    expect(createCalls).toHaveLength(0)
  })
})


it('checks a foreign-process URL instance only against the purchase-order policy', async () => {
  getMock.mockReset().mockRejectedValue({ response: { status: 404 } })
  patchMock.mockReset()
  postMock.mockReset()
  await expect(linkPurchaseOrderToFlowSpine({
    documentId: 'PO-1',
    handover: { process: 'order-to-cash', instanceId: 'sales-case' },
    resumeRoute: '/einkauf/bestellungen/PO-1',
  })).rejects.toEqual({ response: { status: 404 } })
  expect(getMock).toHaveBeenCalledWith('/api/v1/process/flow-spines/procure-to-pay/instances/sales-case')
  expect(patchMock).not.toHaveBeenCalled()
  expect(postMock).not.toHaveBeenCalled()
})
