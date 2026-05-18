import type { ProfessionalDocumentRecord } from '@/lib/professional-workspaces'
import type { SupplyChainOverview } from '@/lib/api/supply-chain'

export type DomainAlertLevel = 'niedrig' | 'mittel' | 'hoch'

export function summarizeSupplyTransfer(chain: SupplyChainOverview | null | undefined): {
  transferPressure: DomainAlertLevel
  handoverRisk: number
  nextAction: string
} {
  if (!chain) return { transferPressure: 'niedrig', handoverRisk: 0, nextAction: 'Daten werden geladen' }
  const handoverRisk = chain.waitingInbound + chain.openWeighingTickets + chain.blockedCharges
  const transferPressure: DomainAlertLevel =
    handoverRisk >= 18 || chain.freightInTransit >= 10
      ? 'hoch'
      : handoverRisk >= 8 || chain.freightInTransit >= 4
        ? 'mittel'
        : 'niedrig'

  let nextAction = 'Kette stabil halten und Uebergaben beobachten'
  if (chain.blockedCharges > 0) nextAction = 'Gesperrte Chargen zuerst mit Waage, Annahme und Fracht aufloesen'
  else if (chain.openWeighingTickets > chain.waitingInbound) nextAction = 'Wiegeuebergaben bereinigen und offene Tickets schliessen'
  else if (chain.waitingInbound > 0) nextAction = 'Wartende Annahmen schneller in Wiegung und Charge ueberfuehren'
  else if (chain.freightInTransit > 0) nextAction = 'Unterwegs-Frachten und Dokumentruecklauf eng begleiten'

  return { transferPressure, handoverRisk, nextAction }
}

export function summarizeDocumentEvidence(records: ProfessionalDocumentRecord[]): {
  unassignedCount: number
  evidenceRisk: DomainAlertLevel
  nextAction: string
} {
  const unassignedCount = records.filter((record) => record.objectRef === 'nicht zugeordnet').length
  const expiringOrFollowUps = records.filter((record) => record.status === 'wiedervorlage').length
  const evidenceRelevant = records.filter((record) => record.status === 'nachweisrelevant').length
  const evidenceRisk: DomainAlertLevel =
    expiringOrFollowUps >= 8 || unassignedCount >= 8
      ? 'hoch'
      : expiringOrFollowUps >= 3 || unassignedCount >= 3 || evidenceRelevant >= 10
        ? 'mittel'
        : 'niedrig'

  let nextAction = 'Nachweislage stabil'
  if (unassignedCount > 0) nextAction = 'Objektbezug fuer unzugeordnete Dokumente nachziehen'
  else if (expiringOrFollowUps > 0) nextAction = 'Wiedervorlagen und Ablaufnachweise priorisieren'
  else if (evidenceRelevant > 0) nextAction = 'Nachweisrelevante Dokumente gegen Vorgaenge und Meldepfade pruefen'

  return { unassignedCount, evidenceRisk, nextAction }
}

export function summarizeContractOperations(input: Array<{
  hedgeQuotePct?: number | null
  marketValuationEur?: number | null
  dunningLevel?: number | null
  writeoffCandidate?: boolean | null
  printReady?: boolean | null
}>): {
  operatorPressure: DomainAlertLevel
  unhedgedCount: number
  dunningCount: number
  nextAction: string
} {
  const unhedgedCount = input.filter((item) => (item.hedgeQuotePct ?? 0) < 100).length
  const dunningCount = input.filter((item) => (item.dunningLevel ?? 0) > 0).length
  const negativeMarket = input.filter((item) => (item.marketValuationEur ?? 0) < 0).length
  const writeoffCandidates = input.filter((item) => Boolean(item.writeoffCandidate)).length
  const operatorPressure: DomainAlertLevel =
    unhedgedCount + dunningCount + negativeMarket + writeoffCandidates >= 8
      ? 'hoch'
      : unhedgedCount + dunningCount + negativeMarket + writeoffCandidates >= 3
        ? 'mittel'
        : 'niedrig'

  let nextAction = 'Fixierungs- und Mahnlage stabil'
  if (unhedgedCount > 0) nextAction = 'Fixierungsluecken und offene Mengen zuerst bearbeiten'
  else if (negativeMarket > 0) nextAction = 'Negative Marktwerte gegen Fristen und Engagement pruefen'
  else if (dunningCount > 0) nextAction = 'Mahnstufen in Vertragsabwicklung rueckkoppeln'
  else if (writeoffCandidates > 0) nextAction = 'Abschreibungskandidaten und Washout-Pfade pruefen'

  return { operatorPressure, unhedgedCount, dunningCount, nextAction }
}

export function summarizeCustomerOperations(input: {
  duplicateCount: number
  hasOwner: boolean
  hasReachableContact: boolean
  nextActions: number
}): {
  ownershipRisk: DomainAlertLevel
  nextAction: string
} {
  const score = (input.duplicateCount > 0 ? 2 : 0) + (input.hasOwner ? 0 : 1) + (input.hasReachableContact ? 0 : 1)
  const ownershipRisk: DomainAlertLevel = score >= 3 ? 'hoch' : score >= 1 ? 'mittel' : 'niedrig'

  let nextAction = 'Kundenstamm fuer Folgeobjekte stabil'
  if (input.duplicateCount > 0) nextAction = 'Dubletten vor Folgeprozess klaeren'
  else if (!input.hasOwner) nextAction = 'Owner und Verantwortung im Stamm festziehen'
  else if (!input.hasReachableContact) nextAction = 'Belastbaren Kontaktkanal vervollstaendigen'
  else if (input.nextActions > 0) nextAction = 'Folgeobjekte und Dokumentpfad bewusst anstossen'

  return { ownershipRisk, nextAction }
}

export function summarizeProcurementMatch(input: {
  exceptionsCount: number
  variancePercentage: number
  autoApprovalEligible: boolean
  hasGoodsReceipt: boolean
}): {
  exceptionPressure: DomainAlertLevel
  nextAction: string
} {
  const exceptionPressure: DomainAlertLevel =
    input.exceptionsCount >= 4 || input.variancePercentage > 10
      ? 'hoch'
      : input.exceptionsCount > 0 || input.variancePercentage > 3
        ? 'mittel'
        : 'niedrig'

  let nextAction = 'Abgleich kann in den Freigabepfad uebergehen'
  if (!input.hasGoodsReceipt) nextAction = 'Wareneingang oder Nachweis vor Freigabe klaeren'
  else if (!input.autoApprovalEligible) nextAction = 'Ausnahmen begruenden und Lieferanten-/Freigabefall bilden'
  else if (input.exceptionsCount > 0) nextAction = 'Teilabweichungen dokumentieren und kontrolliert freigeben'

  return { exceptionPressure, nextAction }
}

export function summarizeFibuConnectorOperations(input: {
  connectorProfiles: number
  exportRuns: number
  openPeriods: number
  adjustingPeriods: number
  dunningReady: boolean
  interestReady: boolean
  taxReady: boolean
}): {
  readinessRisk: DomainAlertLevel
  nextAction: string
} {
  const score =
    (input.connectorProfiles === 0 ? 2 : 0) +
    (input.adjustingPeriods > 0 ? 2 : 0) +
    (input.openPeriods > 3 ? 1 : 0) +
    (!input.dunningReady ? 1 : 0) +
    (!input.interestReady ? 1 : 0) +
    (!input.taxReady ? 1 : 0)
  const readinessRisk: DomainAlertLevel = score >= 4 ? 'hoch' : score >= 2 ? 'mittel' : 'niedrig'

  let nextAction = 'Connector- und Revisionslage stabil'
  if (input.connectorProfiles === 0) nextAction = 'Mindestens ein belastbares Connector-Profil fuer den Operatorpfad hinterlegen'
  else if (input.adjustingPeriods > 0) nextAction = 'Adjusting-Perioden bereinigen, bevor neue Exportlaeufe gestartet werden'
  else if (!input.dunningReady || !input.interestReady) nextAction = 'Mahn- und Zinsparameter fuer die Operatorpfade vervollstaendigen'
  else if (!input.taxReady) nextAction = 'Steuer- und Rueckmeldepfad vor dem naechsten Exportlauf schliessen'
  else if (input.exportRuns === 0) nextAction = 'Ersten revisionsfaehigen Exportlauf gegen das aktive Profil fahren'

  return { readinessRisk, nextAction }
}

export function summarizeOpportunityOperations(input: {
  probability?: number | null
  status?: string | null
  hasOwner: boolean
  hasCustomer: boolean
  quoteCount: number
  expectedCloseDate?: string | null
}): {
  dealRisk: DomainAlertLevel
  nextAction: string
} {
  const closed = input.status === 'closed_won' || input.status === 'closed_lost'
  const score =
    (!input.hasOwner ? 1 : 0) +
    (!input.hasCustomer ? 1 : 0) +
    ((input.probability ?? 0) < 30 && !closed ? 1 : 0) +
    (input.quoteCount === 0 && !closed ? 1 : 0)
  const dealRisk: DomainAlertLevel = score >= 3 ? 'hoch' : score >= 1 ? 'mittel' : 'niedrig'

  let nextAction = 'Deal sauber nachhalten'
  if (!input.hasCustomer) nextAction = 'Kundenbezug festziehen, bevor der Deal weiterqualifiziert wird'
  else if (!input.hasOwner) nextAction = 'Ownership klar zuweisen und Folgeaktion terminieren'
  else if ((input.probability ?? 0) < 30 && !closed) nextAction = 'Deal neu qualifizieren oder kontrolliert schliessen'
  else if (input.quoteCount === 0 && !closed) nextAction = 'Angebotspfad anstossen oder den Bedarf belastbar absichern'
  else if (input.expectedCloseDate) nextAction = 'Abschlussdatum und Folgeobjekte eng gegen den Deal steuern'

  return { dealRisk, nextAction }
}

export function summarizeMeldewesenFeedback(input: {
  failedJobs: number
  runningJobs: number
  artifactCount: number
  queueCount: number
  weighingCount: number
  freightCount: number
  documentCount: number
}): {
  feedbackRisk: DomainAlertLevel
  nextAction: string
} {
  const score = (input.failedJobs > 0 ? 2 : 0) + (input.runningJobs > 0 ? 1 : 0) + (input.artifactCount === 0 ? 1 : 0)
  const feedbackRisk: DomainAlertLevel = score >= 3 ? 'hoch' : score >= 1 ? 'mittel' : 'niedrig'

  let nextAction = 'Rueckmeldelage stabil halten'
  if (input.failedJobs > 0) nextAction = 'Fehlgeschlagene Laeufe mit Artefakt- und Bescheidpfad aufarbeiten'
  else if (input.artifactCount === 0) nextAction = 'Artefakt- und Nachweisfluss fuer letzte Meldung sichern'
  else if (input.queueCount + input.weighingCount + input.freightCount > 0) nextAction = 'Physische Objektkette gegen Meldefaelle rueckkoppeln'
  else if (input.documentCount > 0) nextAction = 'Bescheide und Nachweise den Dokumentpfaden zuordnen'

  return { feedbackRisk, nextAction }
}
