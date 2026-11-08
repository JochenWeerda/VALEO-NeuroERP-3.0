import { detectDayPart, detectSeason } from './prioritization'
import { getFachaktion } from './registry'
import type { WorkspaceLayer, WorkspaceSignal } from './types'

/** Wanduhr fuer Home-Ranking; Tests ersetzen sie, damit die Schicht nicht kalenderabhaengig flake-t. */
export function workspaceNow(): Date {
  return new Date()
}

/**
 * Signale, die ausschliesslich proactive Fachaktionen anstossen, tragen
 * layer `proactive` inkl. reasonCodes — sonst situational.
 */
function layerForRelatedActions(
  actionIds: readonly string[],
): Extract<WorkspaceLayer, 'situational' | 'proactive'> {
  if (actionIds.length === 0) return 'situational'
  const layers = actionIds.map((id) => getFachaktion(id)?.layer)
  if (layers.every((layer) => layer === 'proactive')) return 'proactive'
  return 'situational'
}

/**
 * Kalender-Fallback fuer die Startseite. Live-Zaehler kommen aus Queue-GETs
 * und SSE; hier keine erfundenen KPI-Zahlen.
 */
export function defaultHomeSignals(now: Date): WorkspaceSignal[] {
  const season = detectSeason(now)
  const dayPart = detectDayPart(now)

  const seasonActions =
    season === 'harvest'
      ? ['harvest.intake-queue', 'agrar.overdue-contracts']
      : season === 'planting'
        ? ['agrar.overdue-contracts']
        : ['workspace.document-inbox']

  const dayActions =
    dayPart === 'morning' || dayPart === 'midday'
      ? ['harvest.intake-queue', 'procurement.goods-receipt-qty-variance']
      : dayPart === 'afternoon'
        ? ['logistics.undispatched-truck-orders']
        : ['finance.invoices-awaiting-my-approval']

  const seasonLayer = layerForRelatedActions(seasonActions)
  const dayLayer = layerForRelatedActions(dayActions)

  return [
    {
      id: 'cal-season',
      kind: 'season',
      layer: seasonLayer,
      relatedActionIds: seasonActions,
      severity: season === 'off-season' ? 1 : 3,
      source: 'calendar',
      season,
      reasonCodes: [`cal:season:${season}`, `layer:${seasonLayer}`],
    },
    {
      id: 'cal-daypart',
      kind: 'time-of-day',
      layer: dayLayer,
      relatedActionIds: dayActions,
      severity: dayLayer === 'proactive' ? 3 : 2,
      source: 'clock',
      dayPart,
      reasonCodes: [`cal:day:${dayPart}`, `layer:${dayLayer}`],
    },
  ]
}

export function rankedLaunchpadTileIds(
  rankedActionIds: Array<{ id: string; launchpadTileId?: string }>,
): string[] {
  const ids: string[] = []
  for (const action of rankedActionIds) {
    if (action.launchpadTileId) {
      ids.push(action.launchpadTileId)
    }
    ids.push(action.id)
  }
  return ids
}
