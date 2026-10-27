import { useMemo } from 'react'
import { noopRankingAdvisor } from './prioritization'
import type { RankingAdvisor } from './types'

/**
 * Optionaler KI-Hook fuer die Handlungsbedarf-Liste.
 * Default ist Identitaet (`noopRankingAdvisor`) — Regel-Priorisierung bleibt.
 * Kein LLM; ein spaeterer Client darf nur umordnen, nie Scores/Reason-Codes loeschen.
 */
export function useRankingAdvisor(override?: RankingAdvisor): RankingAdvisor {
  return useMemo(() => override ?? noopRankingAdvisor, [override])
}
