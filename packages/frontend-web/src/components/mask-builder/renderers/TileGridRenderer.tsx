import { memo } from 'react'
import { ChevronRight } from 'lucide-react'
import { useNavigate } from '@/app/routing/typed-router'
import type { RenderTilePlan } from '../render-plan/types'

/**
 * TileGridRenderer (UIX-061): rendert die Worklist-Kacheln eines cockpit-
 * Workspaces als navigierbare Karten. Jede Kachel springt in ihre Ziel-Maske
 * (targetPath inkl. Filter). Ton (neutral|warning|danger) steuert die Akzent-
 * farbe; ein optionaler Live-Zaehler (count) wird angezeigt, wenn vorhanden.
 */
const TONE_ACCENT: Record<RenderTilePlan['tone'], string> = {
  neutral: 'border-l-border',
  warning: 'border-l-amber-500',
  danger: 'border-l-destructive',
}

export const TileGridRenderer = memo(function TileGridRenderer({
  tiles,
  counts,
}: {
  tiles: RenderTilePlan[]
  /** Optionale Live-Zaehler je Kachel-Key (Nachtrag, sobald count_only existiert). */
  counts?: Record<string, number>
}): JSX.Element | null {
  const navigate = useNavigate()
  if (tiles.length === 0) return null

  return (
    <div
      data-testid="tile-grid"
      className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3"
    >
      {tiles.map((tile) => {
        const count = counts?.[tile.key]
        return (
          <button
            key={tile.key}
            type="button"
            data-testid={`tile-${tile.key}`}
            data-tone={tile.tone}
            onClick={() => navigate(tile.targetPath)}
            className={`group flex items-center justify-between rounded-md border border-l-4 ${TONE_ACCENT[tile.tone]} bg-card px-4 py-3 text-left shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring`}
          >
            <span className="flex flex-col">
              <span className="text-sm font-medium">{tile.label}</span>
              {typeof count === 'number' && (
                <span className="text-xs text-muted-foreground group-hover:text-accent-foreground">
                  {count} offen
                </span>
              )}
            </span>
            <ChevronRight className="h-4 w-4 shrink-0 opacity-60" />
          </button>
        )
      })}
    </div>
  )
})
