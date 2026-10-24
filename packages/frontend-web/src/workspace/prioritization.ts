import type {
  DayPart,
  RankedWorkItem,
  RankingAdvisor,
  SeasonId,
  TypedFachaktion,
  UserContext,
  WorkspaceSignal,
} from './types'
import { hasRequiredScope } from './user-context'

export const noopRankingAdvisor: RankingAdvisor = (items) => items

export function detectSeason(now: Date): SeasonId {
  const month = now.getMonth() + 1
  if (month >= 7 && month <= 10) {
    return 'harvest'
  }
  if (month >= 3 && month <= 5) {
    return 'planting'
  }
  return 'off-season'
}

export function detectDayPart(now: Date): DayPart {
  const hour = now.getHours()
  if (hour >= 5 && hour < 11) {
    return 'morning'
  }
  if (hour >= 11 && hour < 14) {
    return 'midday'
  }
  if (hour >= 14 && hour < 18) {
    return 'afternoon'
  }
  return 'evening'
}

function startOfDay(isoDate: string): number {
  return Date.parse(`${isoDate.slice(0, 10)}T00:00:00`)
}

function daysUntil(dueAt: string, now: Date): number {
  const due = startOfDay(dueAt)
  const today = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())
  return Math.round((due - today) / 86_400_000)
}

function domainMatchesRole(domain: string, roles: string[]): boolean {
  const aliases: Record<string, string[]> = {
    logistics: ['disponent', 'lagerist'],
    agrar: ['landwirt', 'disponent'],
    sales: ['aussendienst', 'sachbearbeiter'],
    procurement: ['sachbearbeiter'],
    finance: ['buchhalter', 'geschaeftsfuehrung'],
    documents: ['sachbearbeiter', 'buchhalter'],
  }
  const accepted = aliases[domain] ?? []
  return roles.some((role) => accepted.includes(role) || role === 'admin')
}

function layerBonus(layer: TypedFachaktion['layer']): number {
  if (layer === 'proactive') return 15
  if (layer === 'situational') return 10
  if (layer === 'personal') return 5
  return 2
}

/**
 * Deterministische Rangfolge fuer situativ/proaktiv.
 * KI darf danach nur umordnen, nie Score oder Reason-Codes loeschen.
 */
export function rankWorkspaceItems(input: {
  actions: TypedFachaktion[]
  context: UserContext
  signals: WorkspaceSignal[]
  now: Date
  advisor?: RankingAdvisor
}): RankedWorkItem[] {
  const season = detectSeason(input.now)
  const dayPart = detectDayPart(input.now)
  const advisor = input.advisor ?? noopRankingAdvisor

  const ranked: RankedWorkItem[] = []
  for (const action of input.actions) {
    if (!hasRequiredScope(action.requiredScopes, input.context.scopes)) {
      continue
    }

    const related = input.signals.filter((signal) => signal.relatedActionIds.includes(action.id))
    let score = layerBonus(action.layer)
    const reasonCodes: string[] = [`layer:${action.layer}`]

    if (
      input.context.pinned.includes(action.id) ||
      (action.launchpadTileId !== undefined && input.context.pinned.includes(action.launchpadTileId))
    ) {
      score += 1000
      reasonCodes.push('pinned')
    }
    if (input.context.favorites.includes(action.id)) {
      score += 12
      reasonCodes.push('favorite')
    }
    if (domainMatchesRole(action.businessDomain, input.context.roles)) {
      score += 10
      reasonCodes.push(`role:${action.businessDomain}`)
    }

    for (const signal of related) {
      score += signal.severity * 20
      reasonCodes.push(`signal:${signal.kind}`, `severity:${signal.severity}`)
      if (typeof signal.count === 'number' && signal.count > 0) {
        score += Math.min(signal.count, 20)
        reasonCodes.push(`count:${signal.count}`)
      }
      if (signal.dueAt) {
        const remaining = daysUntil(signal.dueAt, input.now)
        if (remaining < 0) {
          score += 80
          reasonCodes.push('overdue')
        } else if (remaining === 0) {
          score += 50
          reasonCodes.push('due-today')
        } else if (remaining <= 7) {
          score += 25
          reasonCodes.push('due-soon')
        }
      }
      if (signal.season === season && season !== 'off-season') {
        score += 8
        reasonCodes.push(`season:${season}`)
      }
      if (signal.dayPart === dayPart) {
        score += 5
        reasonCodes.push(`day:${dayPart}`)
      }
      for (const code of signal.reasonCodes ?? []) {
        if (code !== '') reasonCodes.push(code)
      }
    }

    ranked.push({ action, score, reasonCodes: [...new Set(reasonCodes)] })
  }

  ranked.sort((left, right) => {
    if (right.score !== left.score) {
      return right.score - left.score
    }
    return left.action.id.localeCompare(right.action.id)
  })

  return advisor(ranked)
}

/**
 * Kachel-Reihenfolge fuer das Launchpad. Fixierte Oberflaeche behaelt
 * die Katalog-/Overlay-Ordnung; Pins stehen trotzdem vorn.
 */
export function orderLaunchpadTileIds(
  tileIds: string[],
  rankedActionIds: string[],
  context: Pick<UserContext, 'pinned' | 'surfaceLocked'>,
): string[] {
  const pinned = context.pinned.filter((id) => tileIds.includes(id))
  if (context.surfaceLocked) {
    const rest = tileIds.filter((id) => !pinned.includes(id))
    return [...pinned, ...rest]
  }

  const seen = new Set<string>()
  const next: string[] = []
  const push = (id: string): void => {
    if (!tileIds.includes(id) || seen.has(id)) {
      return
    }
    seen.add(id)
    next.push(id)
  }

  for (const id of pinned) {
    push(id)
  }
  for (const id of rankedActionIds) {
    push(id)
  }
  for (const id of tileIds) {
    push(id)
  }
  return next
}
