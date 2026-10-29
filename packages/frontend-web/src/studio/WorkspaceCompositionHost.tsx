/**
 * Host fuer WorkspaceComposition-Slots.
 * Mountet InboxWidget und die registrierte Dispositions-Tafel — keine Duplikate,
 * keine zweite Meridian-Pipeline. Studio-Preview und Home teilen denselben Host.
 * Persönliches View-Pin / Start-Fix via Composition-Overlay (localStorage).
 */

import { useMemo } from 'react'
import { Pin, PinOff } from 'lucide-react'
import {
  InboxWidget,
  inboxOpenHref,
  type InboxQueueItem,
  type InboxQueueSnapshot,
} from '@/components/adaptive-workspace/inbox'
import { useNavigate, type RouteTarget } from '@/app/routing/typed-router'
import { dispositionBoardScreen } from '@/components/mask-builder/specialized/disposition-board-screen'
import { SpecializedComponentHost } from '@/components/mask-builder/specialized/SpecializedComponentHost'
import { Button } from '@/components/ui/button'
import { useWorkspaceCompositionOverlay } from '@/hooks/useWorkspaceCompositionOverlay'
import {
  normalizeWorkspaceComposition,
  type WorkspaceComposition,
} from './workspace-composition'
import {
  applyCompositionPersonalization,
  pinCompositionView,
  setFixedStartView,
  unpinCompositionView,
} from './workspace-composition-overlay'
import {
  DISPOSITION_BOARD_ROUTE,
  resolveWorkspaceCompositionMounts,
  type DispositionBoardSlotMount,
  type InboxSlotMount,
  type WorkspaceCompositionMountPlan,
} from './workspace-composition-runtime'

export type WorkspaceCompositionHostVariant = 'studio' | 'embedded'

export type WorkspaceCompositionHostProps = {
  composition: WorkspaceComposition
  /** Optional: feste Queue fuer Tests / Preview ohne Live-Fetch. */
  inboxQueue?: InboxQueueItem[]
  onOpenMask?: (_item: InboxQueueItem) => void
  /** Home: dieselbe Queue-Projektion wie zuvor am InboxWidget (kein zweiter GET). */
  onQueue?: (_snapshot: InboxQueueSnapshot) => void
  /**
   * `studio`: Titel + Views-Band + Slots (Preview).
   * `embedded`: View-Anpassung + Slots (Home/Start — kein zweites h1).
   */
  variant?: WorkspaceCompositionHostVariant
  className?: string
}

function InboxSlot({
  slot,
  queue,
  onOpenMask,
  onQueue,
  forceCompact,
}: {
  slot: InboxSlotMount
  queue?: InboxQueueItem[]
  onOpenMask?: (_item: InboxQueueItem) => void
  onQueue?: (_snapshot: InboxQueueSnapshot) => void
  forceCompact?: boolean
}): JSX.Element {
  const navigate = useNavigate()

  return (
    <section
      aria-label={slot.label}
      data-testid={`workspace-composition-slot-${slot.id}`}
      data-specialized-kind={slot.kind}
      data-binding-id={slot.bindingId}
      data-host-view-id={slot.hostViewId}
      className="flex flex-col gap-2 rounded-(--radius) border border-border bg-card p-3"
    >
      <h2 className="text-sm font-semibold tracking-tight">{slot.label}</h2>
      <InboxWidget
        queue={queue}
        compact={forceCompact || slot.widget.compact}
        confidenceMin={slot.widget.confidenceMin}
        onQueue={onQueue}
        onOpenMask={(item) => {
          if (onOpenMask) {
            onOpenMask(item)
            return
          }
          const href = inboxOpenHref(item)
          if (!href) return
          navigate(href as RouteTarget)
        }}
      />
    </section>
  )
}

function DispositionBoardSlot({
  slot,
  homeEntryTestId,
}: {
  slot: DispositionBoardSlotMount
  homeEntryTestId?: boolean
}): JSX.Element {
  const contract = dispositionBoardScreen.specialized
  const registered = contract?.type === 'disposition_board' && slot.href === DISPOSITION_BOARD_ROUTE
  const specializedId =
    contract?.type === 'disposition_board' ? contract.id : undefined

  return (
    <section
      aria-label={slot.label}
      data-testid={
        homeEntryTestId ? 'workspace-disposition-entry' : `workspace-composition-slot-${slot.id}`
      }
      data-composition-slot-id={slot.id}
      data-specialized-kind={slot.kind}
      data-specialized-type={slot.kind}
      data-specialized-id={specializedId}
      data-screen-id={slot.screenId ?? dispositionBoardScreen.id}
      data-binding-id={slot.bindingId}
      data-host-view-id={slot.hostViewId}
      data-board-route={slot.href}
      className="flex flex-col gap-2 rounded-(--radius) border border-border bg-card p-3"
    >
      <h2 className="text-sm font-semibold tracking-tight">{slot.label}</h2>
      {registered && contract ? (
        <SpecializedComponentHost specialized={contract} />
      ) : (
        <p role="alert" className="text-sm text-status-error" data-testid={`workspace-composition-disposition-unregistered-${slot.id}`}>
          Dispositions-Tafel ist nicht registriert.
        </p>
      )}
    </section>
  )
}

export function WorkspaceCompositionHost({
  composition,
  inboxQueue,
  onOpenMask,
  onQueue,
  variant = 'studio',
  className,
}: WorkspaceCompositionHostProps): JSX.Element {
  const { overlay, setOverlay } = useWorkspaceCompositionOverlay(composition.personalization)
  const personalized = useMemo(
    () => applyCompositionPersonalization(composition, overlay),
    [composition, overlay],
  )
  const plan: WorkspaceCompositionMountPlan = resolveWorkspaceCompositionMounts(personalized)
  const views = normalizeWorkspaceComposition(personalized).views
  const embedded = variant === 'embedded'

  return (
    <div
      data-testid="workspace-composition-host"
      data-composition-id={plan.compositionId}
      data-studio-version={plan.studioVersion}
      data-host-variant={variant}
      data-default-view-id={plan.defaultViewId ?? ''}
      className={className ?? 'flex flex-col gap-4'}
    >
      {!embedded ? (
        <header className="flex flex-col gap-1">
          <h1 className="text-lg font-semibold tracking-tight">{plan.title}</h1>
          <p className="text-xs text-muted-foreground">
            Composition {plan.compositionId} · Studio {plan.studioVersion}
          </p>
        </header>
      ) : null}

      <ol
        className="flex flex-col gap-1 rounded-(--radius) border border-border bg-muted/30 p-3"
        data-testid={embedded ? 'workspace-composition-view-pins' : 'workspace-composition-views'}
        aria-label={embedded ? 'Views anpassen' : 'Views in Composition-Reihenfolge'}
      >
        {views.map((view, index) => {
          const pinned = overlay.pinnedViewIds.includes(view.id)
          const fixed = overlay.fixedStartViewId === view.id
          return (
            <li
              key={view.id}
              data-testid={`workspace-composition-view-${view.id}`}
              data-view-order={view.order ?? (index + 1) * 10}
              data-view-pinned={pinned ? 'true' : 'false'}
              data-view-fixed-start={fixed ? 'true' : 'false'}
              className="flex flex-wrap items-center justify-between gap-2 text-sm text-foreground"
            >
              <div className="min-w-0">
                <span className="text-2xs tracking-wide uppercase text-muted-foreground">
                  {String(index + 1).padStart(2, '0')}
                </span>{' '}
                {view.label}
                {fixed ? (
                  <span className="ml-2 text-2xs tracking-wide uppercase text-muted-foreground">
                    Start
                  </span>
                ) : null}
              </div>
              <div className="flex items-center gap-1">
                <Button
                  type="button"
                  variant="ghost"
                  className="h-11"
                  aria-pressed={pinned}
                  aria-label={pinned ? `${view.label} lösen` : `${view.label} pinnen`}
                  onClick={() => {
                    setOverlay((current) =>
                      pinned
                        ? unpinCompositionView(current, view.id)
                        : pinCompositionView(current, view.id),
                    )
                  }}
                >
                  {pinned ? <PinOff className="h-4 w-4" /> : <Pin className="h-4 w-4" />}
                </Button>
                <Button
                  type="button"
                  variant={fixed ? 'default' : 'outline'}
                  className="h-11"
                  aria-pressed={fixed}
                  aria-label={
                    fixed ? `${view.label} als Start gelöst` : `${view.label} als Start fixieren`
                  }
                  onClick={() => {
                    setOverlay((current) => setFixedStartView(current, fixed ? null : view.id))
                  }}
                >
                  {fixed ? 'Start fixiert' : 'Als Start'}
                </Button>
              </div>
            </li>
          )
        })}
      </ol>

      <div
        className="grid gap-4 lg:grid-cols-2"
        data-testid={embedded ? 'workspace-specialist-slots' : 'workspace-composition-slots'}
        aria-label="Spezialkomponenten"
      >
        {plan.slots.map((slot) => {
          if (slot.kind === 'inbox') {
            return (
              <InboxSlot
                key={slot.id}
                slot={slot}
                queue={inboxQueue}
                onOpenMask={onOpenMask}
                onQueue={onQueue}
                forceCompact={embedded}
              />
            )
          }
          return (
            <DispositionBoardSlot
              key={slot.id}
              slot={slot}
              homeEntryTestId={embedded}
            />
          )
        })}
      </div>
    </div>
  )
}
