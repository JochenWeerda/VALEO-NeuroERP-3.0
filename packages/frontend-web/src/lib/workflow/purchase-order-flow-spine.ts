/**
 * FSX-012 — Bestellung zuerst, Fall danach. Kein zweiter Entscheidungspfad:
 * nutzt resolveCapturedDocumentWorkflow und FSX-010/011.
 */
import { apiClient } from '@/lib/api-client'
import {
  FlowSpineInstance,
  getFlowSpineFetchErrorMessage,
  saveFlowSpineResumeCheckpoint,
} from '@/lib/api/flow-spines'
import {
  getDocumentEntryPolicy,
  resolveCapturedDocumentWorkflow,
  type DocumentWorkflowCandidate,
} from '@/lib/workflow/document-entry-policy'

const CLOSED = new Set(['completed', 'cancelled', 'failed'])

export const PURCHASE_ORDER_DOCUMENT_TYPE = 'purchase_order'

export type PurchaseOrderWorkflowHandover = {
  process?: string
  instanceId: string
}

export type LinkPurchaseOrderWorkflowInput = {
  documentId: string
  documentNumber?: string
  supplierId?: string
  supplierName?: string
  subject?: string
  requisitionId?: string
  contractId?: string
  rfqId?: string
  handover?: PurchaseOrderWorkflowHandover | null
  resumeRoute: string
}

function instanceIdOf(value: { instance_id?: string; id?: string }): string {
  return String(value.instance_id ?? value.id ?? '').trim()
}

function listedInstances(response: unknown): FlowSpineInstance[] {
  if (!response || typeof response !== 'object') return []
  const obj = response as { instances?: FlowSpineInstance[]; data?: { instances?: FlowSpineInstance[] } }
  if (Array.isArray(obj.instances)) return obj.instances
  if (Array.isArray(obj.data?.instances)) return obj.data.instances
  return []
}

export function candidatesFromDocumentHits(
  instances: readonly FlowSpineInstance[],
  documentId: string,
  processKey: string,
): DocumentWorkflowCandidate[] {
  return instances
    .filter((instance) => instanceIdOf(instance).length > 0)
    .filter((instance) => !CLOSED.has(String(instance.lifecycle_status ?? '')))
    .map((instance) => {
      const linked = String(instance.linked_document_id ?? '').trim()
      return {
        instanceId: instanceIdOf(instance),
        processKey: instance.process_key ?? processKey,
        label: instance.label,
        confidence: linked === documentId ? 'exact' : 'strong',
        matchedKeys: ['supplierId'],
      } satisfies DocumentWorkflowCandidate
    })
}

async function fetchDocumentCandidates(processKey: string, documentId: string): Promise<DocumentWorkflowCandidate[]> {
  const response = await apiClient.get<{ instances?: FlowSpineInstance[] }>(
    `/api/v1/process/flow-spines/${processKey}/instances`,
    {
      params: {
        linked_document_id: documentId,
        linked_document_type: PURCHASE_ORDER_DOCUMENT_TYPE,
      },
    },
  )
  return candidatesFromDocumentHits(listedInstances(response), documentId, processKey)
}

async function persistResume(processKey: string, instanceId: string, resumeRoute: string, documentId: string): Promise<void> {
  await saveFlowSpineResumeCheckpoint(processKey, instanceId, {
    resume_node_id: 'purchase-order',
    resume_route: resumeRoute,
    resume_payload: {
      screen: 'purchase-order-create',
      purchaseOrderId: documentId,
      documentType: PURCHASE_ORDER_DOCUMENT_TYPE,
      policyId: 'outgoing-purchase-order',
      entryMode: 'quick-document-capture',
    },
    business_status: 'bestellung_erfasst',
    action_label: 'Bestellung gespeichert',
  })
}

async function attachHandover(
  processKey: string,
  input: LinkPurchaseOrderWorkflowInput,
): Promise<void> {
  const instanceId = input.handover?.instanceId
  if (!instanceId) return
  // 404 wenn Mandant oder process_key nicht passen — keine Existenz fremder Faelle.
  await apiClient.get(`/api/v1/process/flow-spines/${processKey}/instances/${instanceId}`)
  await apiClient.patch(`/api/v1/process/flow-spines/${processKey}/instances/${instanceId}`, {
    linked_document_id: input.documentId,
    linked_document_type: PURCHASE_ORDER_DOCUMENT_TYPE,
  })
  await persistResume(processKey, instanceId, input.resumeRoute, input.documentId)
}

/**
 * Verknuepft eine bereits gespeicherte Bestellung mit dem Procure-to-Pay-Fall.
 * Wirft bei Teilfehlern — der Aufrufer darf die Bestellung nicht zurueckrollen.
 */
export async function linkPurchaseOrderToFlowSpine(input: LinkPurchaseOrderWorkflowInput): Promise<void> {
  const policy = getDocumentEntryPolicy('outgoing-purchase-order')
  const flowSpine = policy.flowSpine
  if (!flowSpine) return

  if (input.handover?.instanceId) {
    // The policy fixes the process; URL data cannot select another aggregate.
    // A foreign-process instance is rejected by the server at this fixed path.
    await attachHandover(flowSpine.processKey, input)
    return
  }

  const candidates = await fetchDocumentCandidates(flowSpine.processKey, input.documentId)
  const resolution = resolveCapturedDocumentWorkflow(policy, {
    documentId: input.documentId,
    documentNumber: input.documentNumber,
    partnerName: input.supplierName,
    subject: input.subject,
    matchValues: {
      supplierId: input.supplierId,
      requisitionId: input.requisitionId,
      contractId: input.contractId,
      rfqId: input.rfqId,
    },
    candidates,
  })

  if (resolution.mode === 'manual-review') {
    throw new Error('Workflow-Zuordnung unklar: Bitte vorhandenen Vorgang manuell auswaehlen.')
  }
  if (resolution.mode === 'standalone' || !resolution.flowSpine) return

  if (resolution.mode === 'attach' && resolution.instanceId && resolution.savePayload) {
    await apiClient.patch(
      `/api/v1/process/flow-spines/${flowSpine.processKey}/instances/${resolution.instanceId}`,
      {
        linked_document_id: input.documentId,
        linked_document_type: PURCHASE_ORDER_DOCUMENT_TYPE,
      },
    )
    await apiClient.post(
      `/api/v1/process/flow-spines/${flowSpine.processKey}/instances/${resolution.instanceId}/save`,
      resolution.savePayload,
    )
    await persistResume(flowSpine.processKey, resolution.instanceId, input.resumeRoute, input.documentId)
    return
  }

  if (resolution.mode === 'start' && resolution.createPayload) {
    const created = await apiClient.post<FlowSpineInstance>(
      `/api/v1/process/flow-spines/${flowSpine.processKey}/instances`,
      resolution.createPayload,
    )
    const createdId = instanceIdOf(created)
    if (createdId && resolution.savePayload) {
      await apiClient.post(
        `/api/v1/process/flow-spines/${flowSpine.processKey}/instances/${createdId}/save`,
        resolution.savePayload,
      )
      await persistResume(flowSpine.processKey, createdId, input.resumeRoute, input.documentId)
    }
  }
}

export function purchaseOrderWorkflowLinkErrorMessage(error: unknown): string {
  return getFlowSpineFetchErrorMessage(error)
}
