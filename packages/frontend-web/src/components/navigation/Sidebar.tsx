import { Link, NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Settings,
} from 'lucide-react'
import { useFeature } from '@/hooks/useFeature'
import { usePinnedTiles } from '@/hooks/usePinnedTiles'
import { useMemo, useState } from 'react'
import { NAV_LINKS, NAV_SECTIONS, type NavItem } from '@/app/navigation/manifest'
import { resolveRoutePathFromModule } from '@/app/navigation/route-paths'

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
  onNavigate?: () => void
}


export function Sidebar({ collapsed, onToggle, onNavigate }: SidebarProps): JSX.Element {
  const agrarEnabled = useFeature('agrar')
  const { pinnedTileIds } = usePinnedTiles()
  const navItems: NavItem[] = NAV_SECTIONS
  const filteredNavItems = navItems.filter((item) => (item.featureKey === 'agrar' ? agrarEnabled : true))
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(
    new Set(), // Standardmäßig alle Gruppen eingeklappt
  )
  const settingsPath = useMemo(
    () =>
      NAV_LINKS.find((entry) => entry.id === 'system-einstellungen')?.path ??
      resolveRoutePathFromModule('@/pages/einstellungen/system', 'einstellungen/system'),
    [],
  )
  const favoriteLinks = useMemo(() => {
    if (pinnedTileIds.length === 0) {
      return []
    }

    const navById = new Map<string, NavItem>()
    const stack = [...filteredNavItems]
    while (stack.length > 0) {
      const current = stack.pop()
      if (!current) {
        continue
      }
      navById.set(current.id, current)
      if (current.children && current.children.length > 0) {
        stack.push(...current.children)
      }
    }

    return pinnedTileIds
      .map((id) => navById.get(id))
      .filter((item): item is NavItem => Boolean(item))
      .map((item) => ({ item, path: resolveEffectivePath(item) }))
      .filter((entry): entry is { item: NavItem; path: string } => Boolean(entry.path))
      .slice(0, 6)
  }, [filteredNavItems, pinnedTileIds])

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
      <div className="flex h-16 items-center justify-between border-b px-4">
        <Link to="/" className="flex items-center focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded" aria-label="Zur Startseite">
          {collapsed ? (
            <img
              src="/branding/valeo-erp-logo.png"
              alt="VALEO ERP Logo"
              className="h-8 w-8 rounded object-cover"
            />
          ) : (
            <img
              src="/branding/valeo-erp-logo.png"
              alt="VALEO ERP Logo"
              className="h-9 w-auto max-w-[170px] object-contain"
            />
          )}
        </Link>
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="h-8 w-8"
          aria-label={collapsed ? 'Sidebar erweitern' : 'Sidebar einklappen'}
          title={collapsed ? 'Erweitern (Strg+B)' : 'Einklappen (Strg+B)'}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-2">
        {filteredNavItems.map((item) => renderNavItem(item, 0))}
      </nav>

      <div className="border-t p-2">
        {!collapsed && favoriteLinks.length > 0 && (
          <div className="mb-3 rounded-md border bg-muted/30 p-2">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Favoriten</p>
            <div className="space-y-1">
              {favoriteLinks.map((favorite) => {
                const FavoriteIcon = favorite.item.icon
                return (
                  <NavLink
                    key={`fav-${favorite.item.id}`}
                    to={favorite.path}
                    onClick={onNavigate}
                    className={({ isActive }) =>
                      cn(
                        'flex items-center gap-2 rounded-md px-2 py-1.5 text-xs font-medium transition-colors',
                        'hover:bg-accent hover:text-accent-foreground',
                        isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground',
                      )
                    }
                  >
                    <FavoriteIcon className="h-3.5 w-3.5 flex-shrink-0" />
                    <span className="truncate">{favorite.item.label}</span>
                  </NavLink>
                )
              })}
            </div>
          </div>
        )}

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
      </div>
    </aside>
  )

  function renderNavItem(item: NavItem, depth: number): JSX.Element {
    const Icon = item.icon
    const hasChildren = Boolean(item.children && item.children.length > 0)
    const isExpanded = expandedGroups.has(item.id)
    const canNavigate = Boolean(item.path)

    if (!hasChildren && canNavigate) {
      return (
        <NavLink
          key={item.id}
          to={item.path ?? '/'}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              depth > 0 && 'ml-2 text-xs',
              'hover:bg-accent hover:text-accent-foreground',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
              isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground',
            )
          }
          title={collapsed ? item.label : undefined}
          data-mcp-nav-item={item.id}
          data-mcp-domain={item.mcp.businessDomain}
        >
          <Icon className={cn('h-5 w-5 flex-shrink-0', depth > 0 && 'h-4 w-4')} />
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
            depth > 0 && 'ml-2 text-xs',
            'hover:bg-accent hover:text-accent-foreground',
            'text-muted-foreground',
          )}
          title={collapsed ? item.label : undefined}
        >
          <Icon className={cn('h-5 w-5 flex-shrink-0', depth > 0 && 'h-4 w-4')} />
          {!collapsed && (
            <>
              <span className="flex-1 text-left">{item.label}</span>
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </>
          )}
        </button>

        {!collapsed && isExpanded && item.children && (
          <div className={cn('ml-4 mt-1 space-y-1 border-l pl-2', depth > 0 && 'ml-6')}>
            {item.children.map((child) => renderNavItem(child, depth + 1))}
            {canNavigate && (
              <NavLink
                to={item.path ?? '/'}
                onClick={onNavigate}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2 rounded-md px-2 py-1.5 text-xs font-medium transition-colors',
                    'hover:bg-accent hover:text-accent-foreground',
                    isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground',
                  )
                }
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                <span>{item.label} oeffnen</span>
              </NavLink>
            )}
          </div>
        )}
      </div>
    )
  }

  function resolveEffectivePath(item: NavItem): string | null {
    if (item.path && !item.path.includes(':')) {
      return item.path
    }
    if (!item.children || item.children.length === 0) {
      return null
    }
    for (const child of item.children) {
      const found = resolveEffectivePath(child)
      if (found) {
        return found
      }
    }
    return null
  }
}

