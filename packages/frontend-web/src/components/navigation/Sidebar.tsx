import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  BarChart3,
  Calculator,
  ChevronLeft,
  ChevronRight,
  FileText,
  LayoutDashboard,
  Package,
  Scale,
  ScrollText,
  Settings,
  ShieldCheck,
  ShoppingCart,
  Sprout,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'
import { useFeature } from '@/hooks/useFeature'

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

type NavigationItem = {
  id: string
  label: string
  icon: typeof LayoutDashboard
  path: string
  mcp: { businessDomain: string; scope: string }
  featureKey?: 'agrar'
}

const navItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/',
    mcp: { businessDomain: 'core', scope: 'core:read' },
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3,
    path: '/analytics',
    mcp: { businessDomain: 'analytics', scope: 'analytics:read' },
  },
  {
    id: 'sales',
    label: 'Verkauf',
    icon: ShoppingCart,
    path: '/sales',
    mcp: { businessDomain: 'sales', scope: 'sales:read' },
  },
  {
    id: 'inventory',
    label: 'Lager',
    icon: Package,
    path: '/inventory',
    mcp: { businessDomain: 'inventory', scope: 'inventory:read' },
  },
  {
    id: 'agrar',
    label: 'Agrar',
    icon: Sprout,
    path: '/agrar/saatgut',
    mcp: { businessDomain: 'agrar', scope: 'agrar:read' },
    featureKey: 'agrar',
  },
  {
    id: 'weighing',
    label: 'Waagen & Annahme',
    icon: Scale,
    path: '/weighing',
    mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
  },
  {
    id: 'contracts',
    label: 'Kontrakte',
    icon: ScrollText,
    path: '/contracts',
    mcp: { businessDomain: 'procurement', scope: 'procurement:read' },
  },
  {
    id: 'pricing',
    label: 'Pricing',
    icon: Calculator,
    path: '/pricing',
    mcp: { businessDomain: 'pricing', scope: 'pricing:read' },
  },
  {
    id: 'documents',
    label: 'Dokumente',
    icon: FileText,
    path: '/document',
    mcp: { businessDomain: 'documents', scope: 'docs:read' },
  },
  {
    id: 'policies',
    label: 'Policies',
    icon: ShieldCheck,
    path: '/policies',
    mcp: { businessDomain: 'compliance', scope: 'compliance:read' },
  },
]

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

      <nav className="flex-1 space-y-1 p-2">
        {navItems
          .filter((item) => (item.featureKey === 'agrar' ? agrarEnabled : true))
          .map((item) => {
            const Icon = item.icon
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
          })}
      </nav>

      <div className="border-t p-2">
        <NavLink
          to="/settings"
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
