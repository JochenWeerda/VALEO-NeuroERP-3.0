/**
 * FSX-012 — Bestellung zuerst, Fall danach.
 *
 * Die Ablauflogik liegt seit FSX-013-LINKER in `document-flow-spine.ts` und ist
 * dort am Policy-Schluessel parametrisiert. Bestellungsspezifisch war daran
 * nichts ausser drei Werten: der Policy-ID, dem Resume-Knoten (kommt jetzt aus
 * der Policy) und den beiden fachlichen Texten fuer die Timeline.
 *
 * Diese Datei haelt nur noch die Schnittstelle, mit der die Bestellmasken
 * arbeiten. Ein zweiter Entscheidungspfad ist sie ausdruecklich nicht.
 */
import {
  candidatesFromDocumentHits,
  documentWorkflowLinkErrorMessage,
  linkDocumentToFlowSpine,
  type DocumentWorkflowHandover,
} from '@/lib/workflow/document-flow-spine'

export const PURCHASE_ORDER_DOCUMENT_TYPE = 'purchase_order'

export type PurchaseOrderWorkflowHandover = DocumentWorkflowHandover

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

export { candidatesFromDocumentHits }

export async function linkPurchaseOrderToFlowSpine(input: LinkPurchaseOrderWorkflowInput): Promise<void> {
  await linkDocumentToFlowSpine('outgoing-purchase-order', {
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
    handover: input.handover,
    resumeRoute: input.resumeRoute,
    // Diese beiden Texte bleiben bestellungsspezifisch: sie stehen in der
    // Timeline und sollen dort die Bestellung benennen, nicht "Beleg".
    businessStatus: 'bestellung_erfasst',
    actionLabel: 'Bestellung gespeichert',
  })
}

export function purchaseOrderWorkflowLinkErrorMessage(error: unknown): string {
  return documentWorkflowLinkErrorMessage(error)
}
