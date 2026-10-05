import { describe, expect, it, vi, beforeEach } from 'vitest'
import { linkDocumentToFlowSpine, candidatesFromDocumentHits } from '@/lib/workflow/document-flow-spine'
import type { FlowSpineInstance } from '@/lib/api/flow-spines'

/**
 * FSX-013-LINKER — die Verknuepfung ist nicht mehr bestellungsspezifisch.
 *
 * Der Nachweis, auf den es ankommt: derselbe Ablauf traegt eine **zweite**
 * Belegart, und zwar ohne dass irgendwo ein Beleg- oder Prozessname fest
 * verdrahtet ist. Cursors Bestelltests laufen unveraendert gegen den
 * delegierenden Wrapper — das ist die andere Haelfte des Nachweises.
 */

const getMock = vi.hoisted(() => vi.fn())
const postMock = vi.hoisted(() => vi.fn())
const patchMock = vi.hoisted(() => vi.fn())
const saveMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: { get: getMock, post: postMock, patch: patchMock },
}))

vi.mock('@/lib/api/flow-spines', () => ({
  saveFlowSpineResumeCheckpoint: saveMock,
  getFlowSpineFetchErrorMessage: (error: unknown) =>
    error instanceof Error ? error.message : 'Fehler',
}))

describe('document-flow-spine (FSX-013-LINKER)', () => {
  beforeEach(() => {
    getMock.mockReset()
    postMock.mockReset()
    patchMock.mockReset()
    saveMock.mockReset().mockResolvedValue(undefined)
  })

  it('legt fuer den Lieferschein einen Fall im richtigen Prozess an', async () => {
    getMock.mockResolvedValue({ data: { instances: [] } })
    postMock.mockResolvedValue({ instance_id: 'wf-ls' })

    await linkDocumentToFlowSpine('outgoing-delivery-note', {
      documentId: 'LS-1',
      documentNumber: 'LS-2026-001',
      partnerName: 'Agrarhandel Nord',
      matchValues: { customerId: 'K-1' },
      resumeRoute: '/verkauf/lieferschein-erfassung',
    })

    // Der Lieferschein haengt an order-to-cash, nicht an procure-to-pay — die
    // Policy bestimmt den Prozess, nicht der Aufrufer.
    expect(getMock).toHaveBeenCalledWith(
      '/api/v1/process/flow-spines/order-to-cash/instances',
      { params: { linked_document_id: 'LS-1', linked_document_type: 'delivery_note' } },
    )
    expect(postMock).toHaveBeenCalledWith(
      '/api/v1/process/flow-spines/order-to-cash/instances',
      expect.objectContaining({ linked_document_type: 'delivery_note', linked_document_id: 'LS-1' }),
    )
  })

  it('nimmt den Resume-Knoten aus der Policy, nicht aus einer festen Zeichenkette', async () => {
    getMock.mockResolvedValue({ data: { instances: [] } })
    postMock.mockResolvedValue({ instance_id: 'wf-ls' })

    await linkDocumentToFlowSpine('outgoing-delivery-note', {
      documentId: 'LS-1',
      resumeRoute: '/verkauf/lieferschein-erfassung',
    })

    expect(saveMock).toHaveBeenCalledWith(
      'order-to-cash',
      'wf-ls',
      expect.objectContaining({ resume_node_id: 'delivery' }),
    )
  })

  it('haengt an einen gefundenen offenen Fall an, statt einen zweiten anzulegen', async () => {
    getMock
      .mockResolvedValueOnce({
        data: {
          instances: [
            {
              instance_id: 'wf-vorhanden',
              process_key: 'order-to-cash',
              lifecycle_status: 'in_progress',
              linked_document_id: 'LS-1',
            },
          ],
        },
      })
      // Der Vorgang hat noch keinen fuehrenden Beleg -> dieser wird es.
      .mockResolvedValueOnce({ instance_id: 'wf-vorhanden', linked_document_id: null })

    await linkDocumentToFlowSpine('outgoing-delivery-note', {
      documentId: 'LS-1',
      resumeRoute: '/verkauf/lieferschein-erfassung',
    })

    expect(patchMock).toHaveBeenCalledWith(
      '/api/v1/process/flow-spines/order-to-cash/instances/wf-vorhanden',
      expect.objectContaining({ linked_document_id: 'LS-1' }),
    )
    expect(postMock).not.toHaveBeenCalledWith(
      '/api/v1/process/flow-spines/order-to-cash/instances',
      expect.anything(),
    )
  })

  it('haengt sich als beteiligter Beleg an, wenn der Vorgang schon einem anderen gehoert', async () => {
    // Der Normalfall der Belegkette: Der Vorgang wurde vom Auftrag eroeffnet,
    // der Lieferschein gehoert dazu — ist aber nicht der Einstiegsbeleg.
    getMock
      .mockResolvedValueOnce({
        data: {
          instances: [
            {
              instance_id: 'wf-auftrag',
              process_key: 'order-to-cash',
              lifecycle_status: 'in_progress',
              linked_document_id: 'SO-7',
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        instance_id: 'wf-auftrag',
        linked_document_id: 'SO-7',
        linked_document_type: 'sales_order',
      })

    await linkDocumentToFlowSpine('outgoing-delivery-note', {
      documentId: 'LS-1',
      relation: 'lieferschein',
      resumeRoute: '/verkauf/lieferschein-erfassung',
    })

    // Kein PATCH — das waere ein Umbiegen und wuerde zu Recht 409 liefern.
    expect(patchMock).not.toHaveBeenCalled()
    expect(postMock).toHaveBeenCalledWith(
      '/api/v1/process/flow-spines/order-to-cash/instances/wf-auftrag/documents',
      { document_type: 'delivery_note', document_id: 'LS-1', relation: 'lieferschein' },
    )
  })

  it('tut nichts, wenn der Beleg bereits der fuehrende des Vorgangs ist', async () => {
    getMock
      .mockResolvedValueOnce({
        data: {
          instances: [
            {
              instance_id: 'wf-1',
              process_key: 'order-to-cash',
              lifecycle_status: 'in_progress',
              linked_document_id: 'LS-1',
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        instance_id: 'wf-1',
        linked_document_id: 'LS-1',
        linked_document_type: 'delivery_note',
      })

    await linkDocumentToFlowSpine('outgoing-delivery-note', {
      documentId: 'LS-1',
      resumeRoute: '/verkauf/lieferschein-erfassung',
    })

    expect(patchMock).not.toHaveBeenCalled()
    expect(postMock).not.toHaveBeenCalledWith(
      expect.stringContaining('/documents'),
      expect.anything(),
    )
  })

  it('haengt bei mehreren Treffern nichts an, sondern verlangt eine Entscheidung', async () => {
    getMock.mockResolvedValue({
      data: {
        instances: [
          { instance_id: 'wf-a', process_key: 'order-to-cash', lifecycle_status: 'in_progress', linked_document_id: 'LS-1' },
          { instance_id: 'wf-b', process_key: 'order-to-cash', lifecycle_status: 'in_progress', linked_document_id: 'LS-1' },
        ],
      },
    })

    await expect(
      linkDocumentToFlowSpine('outgoing-delivery-note', {
        documentId: 'LS-1',
        resumeRoute: '/verkauf/lieferschein-erfassung',
      }),
    ).rejects.toThrow(/manuell auswaehlen/)

    expect(patchMock).not.toHaveBeenCalled()
    expect(postMock).not.toHaveBeenCalled()
  })

  it('prueft eine URL-Fall-ID am Prozess der Policy, nicht am behaupteten', async () => {
    getMock.mockRejectedValue({ response: { status: 404 } })
    // Der GET ist zugleich die Pruefung; er laeuft gegen den Policy-Prozess.

    await expect(
      linkDocumentToFlowSpine('outgoing-delivery-note', {
        documentId: 'LS-1',
        handover: { process: 'procure-to-pay', instanceId: 'fremder-fall' },
        resumeRoute: '/verkauf/lieferschein-erfassung',
      }),
    ).rejects.toEqual({ response: { status: 404 } })

    // Die URL behauptet procure-to-pay; geprueft wird gegen order-to-cash.
    expect(getMock).toHaveBeenCalledWith(
      '/api/v1/process/flow-spines/order-to-cash/instances/fremder-fall',
    )
    expect(patchMock).not.toHaveBeenCalled()
  })

  it('nennt den Beleg als Treffergrund, nicht den Partner', () => {
    const instances = [
      {
        instance_id: 'wf-1',
        process_key: 'order-to-cash',
        lifecycle_status: 'in_progress',
        linked_document_id: 'LS-1',
      },
    ] as FlowSpineInstance[]

    // Die Kandidaten stammen aus einer Abfrage nach linked_document_id; ein
    // Partnerabgleich hat gar nicht stattgefunden.
    expect(candidatesFromDocumentHits(instances, 'LS-1', 'order-to-cash')).toEqual([
      expect.objectContaining({ confidence: 'exact', matchedKeys: ['linkedDocumentId'] }),
    ])
  })
})
