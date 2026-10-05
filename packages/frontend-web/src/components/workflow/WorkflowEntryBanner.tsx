/**
 * FSX-013: Die Komponente `WorkflowEntryBanner` ist entfallen.
 *
 * Sie war ein Hinweiskasten, der erklaerte, dass hinter der Maske ein
 * Prozessvorgang steht — mit Titel, Absatz und vier Merkmalschips. Seit dem
 * Rollout zeigt `WorkflowProcessBand` denselben Sachverhalt in einer Zeile:
 * Phasen, Stand, naechster Schritt. Was die Maske zeigt, muss sie nicht sagen.
 *
 * Geblieben sind der Kontexttyp und der Leser der Handover-Parameter — sie
 * beschreiben den Einstieg aus dem Leitstand und werden von 18 Masken genutzt.
 * Der Dateiname bleibt, damit deren Importe nicht ohne Grund wandern.
 */


export type WorkflowEntryContext = {
  process: string
  instanceId: string
  caseNumber: string
  label: string
  partnerName: string
  subject: string
  entryMode: string
}

export function readWorkflowEntryContext(searchParams: URLSearchParams): WorkflowEntryContext | null {
  const process = searchParams.get('workflowProcess') || ''
  const instanceId = searchParams.get('workflowInstanceId') || ''
  const caseNumber = searchParams.get('workflowCase') || ''
  const label = searchParams.get('workflowLabel') || ''
  const partnerName = searchParams.get('partnerName') || searchParams.get('customerName') || ''
  const subject = searchParams.get('subject') || ''
  const entryMode = searchParams.get('entryMode') || ''

  if (!process && !instanceId && !caseNumber) {
    return null
  }

  return {
    process,
    instanceId,
    caseNumber,
    label,
    partnerName,
    subject,
    entryMode,
  }
}
