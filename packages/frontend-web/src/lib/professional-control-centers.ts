import type { FibuCockpitReadModel } from '@/lib/api/fibu'
import type { SupplyChainOverview } from '@/lib/api/supply-chain'

export type ContractHedgeSummary = {
  hedgeGapCount: number
  marketPressureCount: number
  dunningPressureCount: number
  nextAction: string
}

export type FibuOpsSummary = {
  reorgRisk: 'niedrig' | 'mittel' | 'hoch'
  interestPressure: 'niedrig' | 'mittel' | 'hoch'
  nextAction: string
}

export type SupplyOpsSummary = {
  bottleneck: 'annahme' | 'waage' | 'charge' | 'fracht' | 'stabil'
  pressure: 'niedrig' | 'mittel' | 'hoch'
  nextAction: string
}

export function summarizeContractHedge(items: Array<{
  hedgeQuotePct?: number | null
  marketValuationEur?: number | null
  dunningLevel?: number | null
}>): ContractHedgeSummary {
  const hedgeGapCount = items.filter((item) => (item.hedgeQuotePct ?? 0) < 100).length
  const marketPressureCount = items.filter((item) => (item.marketValuationEur ?? 0) < 0).length
  const dunningPressureCount = items.filter((item) => (item.dunningLevel ?? 0) > 0).length
  let nextAction = 'Hedge- und Fixierungsbild stabil'
  if (hedgeGapCount > 0) nextAction = 'Hedge-Luecken priorisieren und Fixierungsbedarf pruefen'
  else if (marketPressureCount > 0) nextAction = 'Negative Marktwerte gegen offene Mengen absichern'
  else if (dunningPressureCount > 0) nextAction = 'Mahnstufen in Vertragssteuerung rueckkoppeln'
  return { hedgeGapCount, marketPressureCount, dunningPressureCount, nextAction }
}

export function summarizeFibuOps(fibuCockpit: FibuCockpitReadModel, adjustingPeriods: number): FibuOpsSummary {
  const openRisks = [
    fibuCockpit.interest.candidate_count > 0,
    !fibuCockpit.master_data.interest_groups_ready,
    adjustingPeriods > 0,
    !fibuCockpit.annual_close.ready_for_year_close,
  ].filter(Boolean).length
  const reorgRisk: FibuOpsSummary['reorgRisk'] = openRisks >= 3 ? 'hoch' : openRisks >= 1 ? 'mittel' : 'niedrig'
  const interestPressure: FibuOpsSummary['interestPressure'] =
    fibuCockpit.interest.candidate_count > 20 || !fibuCockpit.master_data.interest_groups_ready
      ? 'hoch'
      : fibuCockpit.interest.candidate_count > 0
        ? 'mittel'
        : 'niedrig'
  let nextAction = 'Abschluss- und Revisionslage stabil'
  if (!fibuCockpit.master_data.interest_groups_ready) nextAction = 'Zinsgruppen und Mahnparameter vervollstaendigen'
  else if (adjustingPeriods > 0) nextAction = 'Adjusting-Perioden und Reorganisator-Faelle bereinigen'
  else if (!fibuCockpit.annual_close.ready_for_year_close) nextAction = 'Jahreswechsel-Readiness gegen offene OP und VAT-Lage schliessen'
  else if (fibuCockpit.interest.candidate_count > 0) nextAction = 'Zinskandidaten bewerten und Mahn-/Zinslauf vorbereiten'
  return { reorgRisk, interestPressure, nextAction }
}

export function summarizeSupplyOps(chain: SupplyChainOverview | null | undefined): SupplyOpsSummary {
  if (!chain) return { bottleneck: 'stabil', pressure: 'niedrig', nextAction: 'Daten werden geladen' }
  const maxValue = Math.max(chain.waitingInbound, chain.openWeighingTickets, chain.blockedCharges, chain.freightInTransit)
  let bottleneck: SupplyOpsSummary['bottleneck'] = 'stabil'
  if (maxValue === chain.waitingInbound && maxValue > 0) bottleneck = 'annahme'
  else if (maxValue === chain.openWeighingTickets && maxValue > 0) bottleneck = 'waage'
  else if (maxValue === chain.blockedCharges && maxValue > 0) bottleneck = 'charge'
  else if (maxValue === chain.freightInTransit && maxValue > 0) bottleneck = 'fracht'

  const pressure: SupplyOpsSummary['pressure'] =
    maxValue >= 10 ? 'hoch' : maxValue >= 4 ? 'mittel' : 'niedrig'

  let nextAction = 'Physische Kette stabil'
  if (bottleneck === 'annahme') nextAction = 'Warteschlange abbauen und Rohware schneller in die Wiegung ziehen'
  else if (bottleneck === 'waage') nextAction = 'Offene Wiegetickets und Eich-/Operatorlage an der Waage priorisieren'
  else if (bottleneck === 'charge') nextAction = 'Gesperrte oder ungepruefte Chargen fuer Lager/Fracht freibekommen'
  else if (bottleneck === 'fracht') nextAction = 'Unterwegs-Stau und Dokumentruecklauf in der Fracht disponieren'

  return { bottleneck, pressure, nextAction }
}
