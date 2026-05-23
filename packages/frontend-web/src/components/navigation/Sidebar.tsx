import { Suspense, lazy, useEffect, useMemo, useRef, useState } from 'react'
import { clsx } from 'clsx'
import { Link, NavLink } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { ChevronDown, ChevronLeft, ChevronRight, ChevronUp } from 'lucide-react'
import { useFeature } from '@/hooks/useFeature'
import { usePinnedTiles } from '@/hooks/usePinnedTiles'
import { useUserRole } from '@/hooks/useUserRole'
import { useNavSections } from '@/app/navigation/nav-runtime'
import type { NavItem } from '@/app/navigation/types'
import { resolveRoutePathFromModule } from '@/app/navigation/route-paths'

const SidebarFavorites = lazy(() =>
  import('./SidebarFavorites').then((module) => ({ default: module.default })),
)

const SidebarSettingsLink = lazy(() =>
  import('./SidebarSettingsLink').then((module) => ({ default: module.default })),
)

const SETTINGS_PATH = resolveRoutePathFromModule('@/pages/einstellungen/system', 'einstellungen/system')

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
  onNavigate?: () => void
}

export function Sidebar({ collapsed, onToggle, onNavigate }: SidebarProps): JSX.Element {
  const agrarEnabled = useFeature('agrar')
  const { pinnedTileIds } = usePinnedTiles()
  const navSections = useNavSections()
  const userRoles = useUserRole()
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set())
  const hoverTimers = useRef<Map<string, ReturnType<typeof setTimeout>>>(new Map())

  const filteredNavItems = useMemo(() => {
    function isVisible(item: NavItem): boolean {
      if (item.featureKey === 'agrar' && !agrarEnabled) return false
      if (item.visibleToRoles && item.visibleToRoles.length > 0 && userRoles.length > 0) {
        if (!item.visibleToRoles.some((r) => userRoles.includes(r))) return false
      }
      return true
    }
    return navSections.filter(isVisible)
  }, [agrarEnabled, navSections, userRoles])

  const visiblePrefetchItems = useMemo(() => {
    const visibleItems: NavItem[] = []

    const collectVisibleItems = (items: NavItem[]): void => {
      for (const item of items) {
        visibleItems.push(item)
        if (!collapsed && expandedGroups.has(item.id) && item.children) {
          collectVisibleItems(item.children)
        }
      }
    }

    collectVisibleItems(filteredNavItems)
    return visibleItems
  }, [collapsed, expandedGroups, filteredNavItems])

  useEffect(() => {
    void import('./sidebar-prefetch').then((module) => {
      module.prefetchVisibleModules(visiblePrefetchItems)
    })
  }, [visiblePrefetchItems])

  const navById = useMemo(() => {
    const index = new Map<string, NavItem>()
    const stack = [...filteredNavItems]
    while (stack.length > 0) {
      const current = stack.pop()
      if (!current) continue
      index.set(current.id, current)
      if (current.children && current.children.length > 0) {
        stack.push(...current.children)
      }
    }
    return index
  }, [filteredNavItems])

  const favoriteLinks = useMemo(() => {
    return pinnedTileIds
      .map((id) => navById.get(id))
      .filter((item): item is NavItem => Boolean(item))
      .map((item) => ({ item, path: resolveEffectivePath(item) }))
      .filter((entry): entry is { item: NavItem; path: string } => Boolean(entry.path))
      .slice(0, 6)
  }, [navById, pinnedTileIds])

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

  function handleGroupMouseEnter(id: string): void {
    const existing = hoverTimers.current.get(id)
    if (existing) clearTimeout(existing)
    const timer = setTimeout(() => {
      setExpandedGroups((prev) => new Set([...prev, id]))
      hoverTimers.current.delete(id)
    }, 220)
    hoverTimers.current.set(id, timer)
  }

  function handleGroupMouseLeave(id: string): void {
    const existing = hoverTimers.current.get(id)
    if (existing) {
      clearTimeout(existing)
      hoverTimers.current.delete(id)
    }
    const closeTimer = setTimeout(() => {
      setExpandedGroups((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }, 350)
    hoverTimers.current.set(`close:${id}`, closeTimer)
  }

  function handleGroupMouseEnterCancel(id: string): void {
    const closeTimer = hoverTimers.current.get(`close:${id}`)
    if (closeTimer) {
      clearTimeout(closeTimer)
      hoverTimers.current.delete(`close:${id}`)
    }
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
            clsx(
              'flex min-h-11 items-center gap-3 rounded-[8px] px-3 py-2 text-sm font-medium transition-colors',
              depth > 0 && 'ml-2 text-xs',
              'hover:bg-[var(--sidebar-item-hover-bg)] hover:text-white',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20',
              isActive
                ? 'border-l-[3px] border-l-[var(--sidebar-item-active-indicator)] bg-[var(--sidebar-item-active-bg)] text-white'
                : 'text-[hsl(210,20%,70%)]',
            )
          }
          title={collapsed ? item.label : undefined}
          data-mcp-nav-item={item.id}
          data-mcp-domain={item.mcp.businessDomain}
        >
          <Icon className={clsx('h-5 w-5 flex-shrink-0', depth > 0 && 'h-4 w-4')} />
          {!collapsed && <span>{item.label}</span>}
        </NavLink>
      )
    }

    return (
      <div
        key={item.id}
        onMouseEnter={() => { handleGroupMouseEnterCancel(item.id); handleGroupMouseEnter(item.id) }}
        onMouseLeave={() => handleGroupMouseLeave(item.id)}
      >
        <button
          onClick={() => toggleGroup(item.id)}
          className={clsx(
            'flex min-h-11 w-full items-center gap-3 rounded-[8px] px-3 py-2 text-sm font-medium transition-colors',
            depth > 0 && 'ml-2 text-xs',
            'hover:bg-[var(--sidebar-item-hover-bg)] hover:text-white',
            'text-[hsl(210,20%,70%)]',
          )}
          title={collapsed ? item.label : undefined}
        >
          <Icon className={clsx('h-5 w-5 flex-shrink-0', depth > 0 && 'h-4 w-4')} />
          {!collapsed && (
            <>
              <span className="flex-1 text-left">{item.label}</span>
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </>
          )}
        </button>

        {!collapsed && isExpanded && item.children ? (
          <div className={clsx('ml-4 mt-1 space-y-1 border-l pl-2', depth > 0 && 'ml-6')}>
            {item.children.map((child) => renderNavItem(child, depth + 1))}
            {canNavigate ? (
              <NavLink
                to={item.path ?? '/'}
                onClick={onNavigate}
                className={({ isActive }) =>
                  clsx(
                    'flex min-h-11 items-center gap-2 rounded-md px-2 py-1.5 text-xs font-medium transition-colors',
                    'hover:bg-accent hover:text-accent-foreground',
                    isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground',
                  )
                }
              >
                <Icon className="h-4 w-4 flex-shrink-0" />
                <span>{item.label} oeffnen</span>
              </NavLink>
            ) : null}
          </div>
        ) : null}
      </div>
    )
  }

  return (
    <aside
      className={clsx(
        'relative flex flex-col border-r transition-all',
        'bg-[var(--sidebar-bg)] text-[var(--sidebar-fg)]',
        'border-[var(--sidebar-border)]',
        collapsed ? 'w-[var(--sidebar-width-collapsed,64px)]' : 'w-[var(--sidebar-width-expanded,240px)]',
      )}
      style={{ transitionProperty: 'width', transitionDuration: 'var(--duration-normal,250ms)', transitionTimingFunction: 'var(--ease-spring)' }}
      role="navigation"
      aria-label="Main navigation"
      data-mcp-component="sidebar"
      data-mcp-collapsed={collapsed}
    >
      <div className="flex h-16 items-center justify-between border-b border-[var(--sidebar-border)] px-4">
        <Link
          to="/"
          className="flex min-h-11 min-w-11 items-center rounded focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
          aria-label="Zur Startseite"
        >
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
          className="h-11 w-11 text-[hsl(210,20%,70%)] hover:bg-[var(--sidebar-item-hover-bg)] hover:text-white"
          aria-label={collapsed ? 'Sidebar erweitern' : 'Sidebar einklappen'}
          title={collapsed ? 'Erweitern (Strg+B)' : 'Einklappen (Strg+B)'}
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-2">
        {filteredNavItems.map((item) => renderNavItem(item, 0))}
      </nav>

      <div className="border-t border-[var(--sidebar-border)] p-2">
        {!collapsed ? (
          <Suspense fallback={null}>
            <SidebarFavorites favorites={favoriteLinks} onNavigate={onNavigate} />
          </Suspense>
        ) : null}

        <Suspense fallback={null}>
          <SidebarSettingsLink collapsed={collapsed} path={SETTINGS_PATH} />
        </Suspense>
      </div>
    </aside>
  )
}
