import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Settings,
} from 'lucide-react'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'
import { useFeature } from '@/hooks/useFeature'
import { useMemo, useState } from 'react'
import { NAV_LINKS, NAV_SECTIONS, type NavItem } from '@/app/navigation/manifest'
import { resolveRoutePathFromModule } from '@/app/navigation/route-paths'

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

export const sidebarMCP = createMCPMetadata('Sidebar', 'navigation', {
  accessibility: {
    role: 'navigation',
    ariaLabel: 'Main navigation',
    focusable: true,
  },
  intent: {
    purpose: 'Navigate between ERP domains',
    userActions: ['navigate', 'collapse', 'expand'],
    businessDomain: 'core',
  },
  mcpHints: {
    explainable: true,
    contextAware: true,
  },
})

export function Sidebar({ collapsed, onToggle }: SidebarProps): JSX.Element {
  const agrarEnabled = useFeature('agrar')
  const navItems: NavItem[] = NAV_SECTIONS
  const filteredNavItems = navItems.filter((item) => (item.featureKey === 'agrar' ? agrarEnabled : true))
  const allGroupIds = filteredNavItems
    .filter((item) => item.children && item.children.length > 0)
    .map((item) => item.id)
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(
    new Set(allGroupIds),
  )
  const settingsPath = useMemo(
    () =>
      NAV_LINKS.find((entry) => entry.id === 'system-einstellungen')?.path ??
      resolveRoutePathFromModule('@/pages/einstellungen/system', 'einstellungen/system'),
    [],
  )

  function toggleGroup(id: string): void {
    setExpandedGroups((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  return (
    <aside
      className={cn(
        'relative flex flex-col border-r bg-background transition-all duration-300',
        collapsed ? 'w-16' : 'w-64',
      )}
      role="navigation"
      aria-label="Main navigation"
      data-mcp-component="sidebar"
      data-mcp-collapsed={collapsed}
    >
      <div className="flex h-16 items-center border-b px-4">
        {collapsed ? <span className="text-lg font-bold">V</span> : <h2 className="text-lg font-semibold">VALEO ERP</h2>}
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-2">
        {filteredNavItems.map((item) => {
            const Icon = item.icon
            const isExpanded = expandedGroups.has(item.id)
            const hasChildren = item.children && item.children.length > 0

            if (!hasChildren && item.path) {
              return (
                <NavLink
                  key={item.id}
                  to={item.path}
                  className={({ isActive }) =>
                    cn(
                      'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                      'hover:bg-accent hover:text-accent-foreground',
                      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                      isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground',
                    )
                  }
                  title={collapsed ? item.label : undefined}
                  data-mcp-nav-item={item.id}
                  data-mcp-domain={item.mcp.businessDomain}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  {!collapsed && <span>{item.label}</span>}
                </NavLink>
              )
            }

            return (
              <div key={item.id}>
                <button
                  onClick={() => toggleGroup(item.id)}
                  className={cn(
                    'flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                    'hover:bg-accent hover:text-accent-foreground',
                    'text-muted-foreground',
                  )}
                  title={collapsed ? item.label : undefined}
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  {!collapsed && (
                    <>
                      <span className="flex-1 text-left">{item.label}</span>
                      {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </>
                  )}
                </button>

                {!collapsed && isExpanded && item.children && (
                  <div className="ml-6 mt-1 space-y-1 border-l pl-2">
                    {item.children.map((child) => {
                      const ChildIcon = child.icon
                      return (
                        <NavLink
                          key={child.id}
                          to={child.path ?? '#'}
                          className={({ isActive }) =>
                            cn(
                              'flex items-center gap-2 rounded-md px-2 py-1.5 text-xs font-medium transition-colors',
                              'hover:bg-accent hover:text-accent-foreground',
                              isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground',
                            )
                          }
                          data-mcp-nav-item={child.id}
                        >
                          <ChildIcon className="h-4 w-4 flex-shrink-0" />
                          <span>{child.label}</span>
                        </NavLink>
                      )
                    })}
                  </div>
                )}
              </div>
            )
          })}
      </nav>

      <div className="border-t p-2">
        <NavLink
          to={settingsPath}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              'hover:bg-accent hover:text-accent-foreground',
              isActive ? 'bg-accent' : 'text-muted-foreground',
            )
          }
          title={collapsed ? 'Einstellungen' : undefined}
        >
          <Settings className="h-5 w-5" />
          {!collapsed && <span>Einstellungen</span>}
        </NavLink>

        <Button
          variant="ghost"
          size={collapsed ? 'icon' : 'sm'}
          onClick={onToggle}
          className="mt-2 w-full"
          aria-label={collapsed ? 'Sidebar erweitern' : 'Sidebar einklappen'}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4" />
              <span className="ml-2">Einklappen</span>
            </>
          )}
        </Button>
      </div>
    </aside>
  )
}
