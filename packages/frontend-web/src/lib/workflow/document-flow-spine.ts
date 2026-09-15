/**
 * FSX-012 verallgemeinert: Beleg zuerst speichern, Vorgang danach verknuepfen —
 * fuer **jede** Belegart, nicht nur fuer die Bestellung.
 *
 * Die Logik stammt aus Cursors `purchase-order-flow-spine.ts` und ist hier nur
 * am Policy-Schluessel parametrisiert. Bestellungsspezifisch war daran nichts
 * ausser drei fest verdrahteten Werten: der Policy-ID, dem Resume-Knoten und dem
 * fachlichen Status.
 *
 * Kein zweiter Entscheidungspfad: es bleibt bei
 * `resolveCapturedDocumentWorkflow` (Policy) und FSX-010/011 (Suche und
 * idempotente Anlage).
 */
import { apiClient } from '@/lib/api-client'
import {
  getFlowSpineFetchErrorMessage,
  saveFlowSpineResumeCheckpoint,
  type FlowSpineInstance,
} from '@/lib/api/flow-spines'
import {
  getDocumentEntryPolicy,
  resolveCapturedDocumentWorkflow,
  type DocumentEntryPolicyId,
  type DocumentMatchValues,
  type DocumentWorkflowCandidate,
} from '@/lib/workflow/document-entry-policy'

const CLOSED = new Set(['completed', 'cancelled', 'failed'])

export type DocumentWorkflowHandover = {
  process?: string
  instanceId: string
}

export type LinkDocumentWorkflowInput = {
  documentId: string
  documentNumber?: string
  partnerName?: string
  subject?: string
  matchValues?: DocumentMatchValues
  handover?: DocumentWorkflowHandover | null
  resumeRoute: string
  /** Fachliche Rolle, falls der Beleg als beteiligter angehaengt wird. */
  relation?: string
  /**
   * Eigene Kandidaten statt der Standardsuche ueber die Belegreferenz.
   *
   * Notwendig, weil manche Belege ihren Vorgang **nicht** ueber die eigene
   * Referenz finden: Ein Lieferschein haengt typischerweise an dem Vorgang, den
   * der Auftrag eroeffnet hat — dort steht der Lieferschein noch nirgends. Die
   * Belegsuche aus FSX-010 faende nichts und legte jedes Mal einen neuen Fall an.
   * Die Maske kennt ihre Vorgaengerbelege und sucht besser.
   */
  candidates?: readonly DocumentWorkflowCandidate[]
  /** Fachlicher Status nach der Verknuepfung; sonst der neutrale Vorgabewert. */
  businessStatus?: string
  actionLabel?: string
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

/**
 * Offene Vorgaenge zu einem Beleg in Kandidaten uebersetzen.
 *
 * `matchedKeys` nennt **den Beleg**, nicht den Partner: die Treffer stammen aus
 * einer Abfrage nach `linked_document_id`, ein Partnerabgleich hat gar nicht
 * stattgefunden. (Korrektur an der Vorlage, dort stand `supplierId`.)
 */
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
        matchedKeys: ['linkedDocumentId'],
      } satisfies DocumentWorkflowCandidate
    })
}

async function fetchDocumentCandidates(
  processKey: string,
  documentType: string,
  documentId: string,
): Promise<DocumentWorkflowCandidate[]> {
  const response = await apiClient.get<{ instances?: FlowSpineInstance[] }>(
    `/api/v1/process/flow-spines/${processKey}/instances`,
    { params: { linked_document_id: documentId, linked_document_type: documentType } },
  )
  return candidatesFromDocumentHits(listedInstances(response), documentId, processKey)
}

async function persistResume(
  policyId: DocumentEntryPolicyId,
  processKey: string,
  instanceId: string,
  input: LinkDocumentWorkflowInput,
): Promise<void> {
  const policy = getDocumentEntryPolicy(policyId)
  await saveFlowSpineResumeCheckpoint(processKey, instanceId, {
    resume_node_id: policy.flowSpine?.resumeNodeId,
    resume_route: input.resumeRoute,
    resume_payload: {
      screen: policyId,
      documentId: input.documentId,
      documentType: policy.documentType,
      policyId,
      entryMode: 'quick-document-capture',
    },
    business_status: input.businessStatus ?? 'document-captured',
    action_label: input.actionLabel ?? 'Beleg gespeichert',
  })
}

/**
 * Beleg an den Vorgang haengen — in der **richtigen Rolle**.
 *
 * Das ist die Stelle, an der sich der n:m-Widerspruch aufloest (siehe
 * `docs/design/flow-spine-nm-bindungskonflikt.md`):
 *
 * - Hat der Vorgang **noch keinen** fuehrenden Beleg, wird dieser es. Das ist
 *   der Einstiegsfall, und der Unique-Index aus FSX-011 traegt ihn.
 * - Ist **dieser** Beleg schon der fuehrende, passiert nichts. Idempotent.
 * - Gehoert der Vorgang bereits einem **anderen** Beleg, haengt sich dieser als
 *   **beteiligter** Beleg an (FSX-DOC-LINKS). Das ist der Normalfall der
 *   Belegkette: die Rechnung zum Lieferschein, der Lieferschein zum Auftrag.
 *
 * Ein PATCH waere in diesem dritten Fall ein Umbiegen und wuerde zu Recht mit
 * 409 abgewiesen. Vor FSX-DOC-LINKS gab es dafuer keinen Ausweg — Masken haben
 * die Bindung deshalb ganz weggelassen und den Beleg unverknuepft gelassen.
 */
async function bindOrAttachDocument(
  processKey: string,
  instanceId: string,
  documentType: string,
  documentId: string,
  relation?: string,
): Promise<void> {
  const instance = await apiClient.get<FlowSpineInstance>(
    `/api/v1/process/flow-spines/${processKey}/instances/${instanceId}`,
  )
  const vorhanden = String(instance.linked_document_id ?? '').trim()

  if (!vorhanden) {
    await apiClient.patch(`/api/v1/process/flow-spines/${processKey}/instances/${instanceId}`, {
      linked_document_id: documentId,
      linked_document_type: documentType,
    })
    return
  }

  if (vorhanden === documentId && String(instance.linked_document_type ?? '') === documentType) {
    return
  }

  await apiClient.post(`/api/v1/process/flow-spines/${processKey}/instances/${instanceId}/documents`, {
    document_type: documentType,
    document_id: documentId,
    relation,
  })
}

/**
 * Verknuepft einen **bereits gespeicherten** Beleg mit seinem Prozessvorgang.
 *
 * Wirft bei Teilfehlern. Der Aufrufer darf den Beleg deswegen **nicht**
 * zuruecknehmen — er ist die fuehrende Groesse; die Wiederholung richtet sich
 * ausschliesslich auf diese Verknuepfung. Dank der Idempotenz aus FSX-011 ist
 * sie beliebig oft wiederholbar.
 */
export async function linkDocumentToFlowSpine(
  policyId: DocumentEntryPolicyId,
  input: LinkDocumentWorkflowInput,
): Promise<void> {
  const policy = getDocumentEntryPolicy(policyId)
  const flowSpine = policy.flowSpine
  if (!flowSpine) return

  if (input.handover?.instanceId) {
    // Die Policy legt den Prozess fest; eine URL kann kein anderes Aggregat
    // waehlen. Ein fremder Prozess laeuft an diesem festen Pfad in den 404.
    const instanceId = input.handover.instanceId
    // Der GET in bindOrAttachDocument ist zugleich die Pruefung: ein fremder
    // Mandant oder Prozess laeuft an diesem festen Pfad in den 404.
    await bindOrAttachDocument(
      flowSpine.processKey, instanceId, policy.documentType, input.documentId, input.relation,
    )
    await persistResume(policyId, flowSpine.processKey, instanceId, input)
    return
  }

  const candidates =
    input.candidates ??
    (await fetchDocumentCandidates(flowSpine.processKey, policy.documentType, input.documentId))
  const resolution = resolveCapturedDocumentWorkflow(policy, {
    documentId: input.documentId,
    documentNumber: input.documentNumber,
    partnerName: input.partnerName,
    subject: input.subject,
    matchValues: input.matchValues ?? {},
    candidates,
  })

  if (resolution.mode === 'manual-review') {
    // Mehrere oder unsichere Treffer werden nicht automatisch zugeordnet —
    // lieber eine Rueckfrage als eine falsche Bindung.
    throw new Error('Workflow-Zuordnung unklar: Bitte vorhandenen Vorgang manuell auswaehlen.')
  }
  if (resolution.mode === 'standalone' || !resolution.flowSpine) return

  if (resolution.mode === 'attach' && resolution.instanceId && resolution.savePayload) {
    await bindOrAttachDocument(
      flowSpine.processKey, resolution.instanceId, policy.documentType, input.documentId, input.relation,
    )
    await apiClient.post(
      `/api/v1/process/flow-spines/${flowSpine.processKey}/instances/${resolution.instanceId}/save`,
      resolution.savePayload,
    )
    await persistResume(policyId, flowSpine.processKey, resolution.instanceId, input)
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
      await persistResume(policyId, flowSpine.processKey, createdId, input)
    }
  }
}

export function documentWorkflowLinkErrorMessage(error: unknown): string {
  return getFlowSpineFetchErrorMessage(error)
}
