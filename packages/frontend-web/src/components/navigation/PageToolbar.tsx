import { ReactNode, useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { MoreHorizontal } from 'lucide-react'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'
import { useActionDispatchOptional } from '@/features/ki-usability'
import { auth } from '@/lib/auth'
import { mergeToolbarActionsForDensity, resolveRoleDensityProfile } from '@/features/role-density'
import { useTenant } from '@/hooks/useTenant'

export interface ToolbarAction {
  id: string
  label: string
  icon?: ReactNode
  onClick: () => void
  variant?: 'default' | 'destructive' | 'outline' | 'secondary'
  disabled?: boolean
  shortcut?: string
  mcp?: {
    intent: string
    requiresConfirmation?: boolean
    requiredData?: string[]
  }
}

interface PageToolbarProps {
  title: string
  subtitle?: string
  primaryActions?: ToolbarAction[]
  overflowActions?: ToolbarAction[]
  rightSlot?: ReactNode
  densityProfileOverride?: import('@/features/role-density').RoleDensityProfile
  mcpContext?: {
    pageDomain: string
    currentDocument?: string
    availableActions: string[]
  }
}

export const pageToolbarMCP = createMCPMetadata('PageToolbar', 'navigation', {
  accessibility: {
    role: 'toolbar',
    ariaLabel: 'Page actions toolbar',
    focusable: true,
  },
  intent: {
    purpose: 'Provide contextual actions for current page',
    userActions: ['click-action', 'open-overflow'],
    dataContext: ['current-page', 'user-permissions'],
  },
  mcpHints: {
    autoFillable: false,
    explainable: true,
    testable: true,
    contextAware: true,
  },
})

export function PageToolbar({
  title,
  subtitle,
  primaryActions = [],
  overflowActions = [],
  rightSlot,
  densityProfileOverride,
  mcpContext,
}: PageToolbarProps): JSX.Element {
  const dispatchContext = useActionDispatchOptional()
  const { tenantId } = useTenant()
  const [overflowOpen, setOverflowOpen] = useState(false)
  const overflowRef = useRef<HTMLDivElement>(null)
  const hasSubtitle = typeof subtitle === 'string' && subtitle.length > 0
  const hasRightSlot = rightSlot !== undefined && rightSlot !== null
  const roleDensityProfile = densityProfileOverride ?? resolveRoleDensityProfile(auth.getUser()?.roles, {
    tenantId,
    pageDomain: mcpContext?.pageDomain,
    availableActionIds: [...primaryActions.map((action) => action.id), ...overflowActions.map((action) => action.id)],
  })
  const densityScopedActions = mergeToolbarActionsForDensity(primaryActions, overflowActions, roleDensityProfile)
  const scopedPrimaryActions = densityScopedActions.primaryActions
  const scopedOverflowActions = densityScopedActions.overflowActions
  const allActions = [...scopedPrimaryActions, ...scopedOverflowActions]

  useEffect(() => {
    const handleOutsideClick = (event: MouseEvent): void => {
      if (overflowRef.current && !overflowRef.current.contains(event.target as Node)) {
        setOverflowOpen(false)
      }
    }

    document.addEventListener('mousedown', handleOutsideClick)
    return () => document.removeEventListener('mousedown', handleOutsideClick)
  }, [])

  useEffect(() => {
    if (!dispatchContext || allActions.length === 0) {
      return
    }

    const unregisterHandlers = allActions.map((action) =>
      dispatchContext.registerHandler(action.id, async () => {
        await action.onClick()
      })
    )

    return () => {
      unregisterHandlers.forEach((unregister) => unregister())
    }
  }, [allActions, dispatchContext])

  return (
    <div
      className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
      role="toolbar"
      aria-label={`${title} toolbar`}
      data-mcp-component="page-toolbar"
      data-mcp-page-domain={mcpContext?.pageDomain}
    >
      <div className="flex min-h-[4.5rem] items-center gap-4 px-4 py-3 sm:px-6">
        <div className="flex-1">
          <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
          {hasSubtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
        </div>

        {scopedPrimaryActions.length > 0 && (
          <div className="flex items-center gap-2">
            {scopedPrimaryActions.map((action) => {
              const hasShortcut = typeof action.shortcut === 'string' && action.shortcut.length > 0
              const iconNode = action.icon ?? null
              const iconMargin = iconNode !== null ? 'ml-2' : undefined
              const titleText = hasShortcut ? `${action.label} (${action.shortcut})` : action.label

              return (
                <Button
                  key={action.id}
                  variant={action.variant ?? 'default'}
                  onClick={action.onClick}
                  disabled={action.disabled === true}
                  size="sm"
                  className="min-h-touch min-w-touch touch-manipulation"
                  data-mcp-action={action.id}
                  data-mcp-intent={action.mcp?.intent}
                  aria-label={action.label}
                  title={titleText}
                >
                  {iconNode}
                  <span className={iconMargin}>{action.label}</span>
                  {hasShortcut && (
                    <kbd className="ml-2 hidden rounded bg-muted px-1 text-xs lg:inline">{action.shortcut}</kbd>
                  )}
                </Button>
              )
            })}
          </div>
        )}

        {scopedOverflowActions.length > 0 && (
          <div className="relative" ref={overflowRef}>
            <Button
              variant="ghost"
              size="icon"
              className="min-h-touch min-w-touch touch-manipulation"
              aria-label="More actions"
              onClick={() => setOverflowOpen((current) => !current)}
            >
              <MoreHorizontal className="h-4 w-4" />
            </Button>
            {overflowOpen && (
              <div className="absolute right-0 top-full z-50 mt-2 w-56 rounded-lg border bg-popover p-1 shadow-lg">
                {scopedOverflowActions.map((action, idx) => {
                  const hasShortcut = typeof action.shortcut === 'string' && action.shortcut.length > 0
                  const iconNode = action.icon ?? null
                  const destructive = action.variant === 'destructive'

                  return (
                    <div key={action.id}>
                      {idx > 0 && destructive && <div className="my-1 h-px bg-border" />}
                      <button
                        type="button"
                        onClick={() => {
                          action.onClick()
                          setOverflowOpen(false)
                        }}
                        disabled={action.disabled === true}
                        className={`flex min-h-touch w-full items-center gap-2 rounded-md px-3 py-2 text-left text-sm hover:bg-accent disabled:pointer-events-none disabled:opacity-50 ${destructive ? 'text-destructive' : ''}`}
                        data-mcp-action={action.id}
                        data-mcp-intent={action.mcp?.intent}
                      >
                        {iconNode}
                        <span className="flex-1">{action.label}</span>
                        {hasShortcut && <kbd className="text-xs">{action.shortcut}</kbd>}
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {hasRightSlot && <div className="flex items-center">{rightSlot}</div>}
      </div>
    </div>
  )
}
