import { ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { MoreHorizontal } from 'lucide-react'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'

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
  mcpContext,
}: PageToolbarProps): JSX.Element {
  const hasSubtitle = typeof subtitle === 'string' && subtitle.length > 0
  const hasRightSlot = rightSlot !== undefined && rightSlot !== null

  return (
    <div
      className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
      role="toolbar"
      aria-label={`${title} toolbar`}
      data-mcp-component="page-toolbar"
      data-mcp-page-domain={mcpContext?.pageDomain}
    >
      <div className="flex h-16 items-center gap-4 px-6">
        <div className="flex-1">
          <h1 className="text-xl font-semibold tracking-tight">{title}</h1>
          {hasSubtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
        </div>

        {primaryActions.length > 0 && (
          <div className="flex items-center gap-2">
            {primaryActions.map((action) => {
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

        {overflowActions.length > 0 && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="More actions">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              {overflowActions.map((action, idx) => {
                const hasShortcut = typeof action.shortcut === 'string' && action.shortcut.length > 0
                const iconNode = action.icon ?? null
                const iconMargin = iconNode !== null ? 'ml-2' : undefined

                return (
                  <div key={action.id}>
                    {idx > 0 && action.variant === 'destructive' && <DropdownMenuSeparator />}
                    <DropdownMenuItem
                      onClick={action.onClick}
                      disabled={action.disabled === true}
                      className={action.variant === 'destructive' ? 'text-destructive' : ''}
                      data-mcp-action={action.id}
                      data-mcp-intent={action.mcp?.intent}
                    >
                      {iconNode}
                      <span className={iconMargin}>{action.label}</span>
                      {hasShortcut && <kbd className="ml-auto text-xs">{action.shortcut}</kbd>}
                    </DropdownMenuItem>
                  </div>
                )
              })}
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        {hasRightSlot && <div className="flex items-center">{rightSlot}</div>}
      </div>
    </div>
  )
}
