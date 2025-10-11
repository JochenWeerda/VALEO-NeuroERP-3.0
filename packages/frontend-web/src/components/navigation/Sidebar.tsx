import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  BarChart3,
  Calculator,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  FileText,
  LayoutDashboard,
  Package,
  Scale,
  Settings,
  ShieldCheck,
  ShoppingCart,
  Sprout,
  Users,
  Euro,
  Truck,
  Building2,
  Leaf,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'
import { useFeature } from '@/hooks/useFeature'
import { useState } from 'react'

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

type NavItem = {
  id: string
  label: string
  icon: typeof LayoutDashboard
  path?: string
  children?: NavItem[]
  mcp: { businessDomain: string; scope: string }
  featureKey?: 'agrar'
}

const navItems: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/',
    mcp: { businessDomain: 'core', scope: 'core:read' },
  },
  {
    id: 'verkauf',
    label: 'Verkauf',
    icon: ShoppingCart,
    mcp: { businessDomain: 'sales', scope: 'sales:read' },
    children: [
      { id: 'sales-dashboard', label: 'Dashboard', icon: BarChart3, path: '/dashboard/sales', mcp: { businessDomain: 'sales', scope: 'sales:read' } },
      { id: 'angebot', label: 'Angebote', icon: FileText, path: '/sales', mcp: { businessDomain: 'sales', scope: 'sales:read' } },
      { id: 'auftrag', label: 'Aufträge', icon: FileText, path: '/sales/order', mcp: { businessDomain: 'sales', scope: 'sales:read' } },
      { id: 'lieferung', label: 'Lieferungen', icon: Truck, path: '/sales/delivery', mcp: { businessDomain: 'sales', scope: 'sales:read' } },
      { id: 'rechnung', label: 'Rechnungen', icon: FileText, path: '/sales/invoice', mcp: { businessDomain: 'sales', scope: 'sales:read' } },
      { id: 'kunden', label: 'Kunden', icon: Users, path: '/verkauf/kunden-liste', mcp: { businessDomain: 'sales', scope: 'sales:read' } },
    ],
  },
  {
    id: 'einkauf',
    label: 'Einkauf',
    icon: ShoppingCart,
    mcp: { businessDomain: 'procurement', scope: 'procurement:read' },
    children: [
      { id: 'einkauf-dashboard', label: 'Dashboard', icon: BarChart3, path: '/dashboard/einkauf', mcp: { businessDomain: 'procurement', scope: 'procurement:read' } },
      { id: 'bestellvorschlaege', label: 'Bestellvorschläge', icon: AlertCircle, path: '/einkauf/bestellvorschlaege', mcp: { businessDomain: 'procurement', scope: 'procurement:read' } },
      { id: 'bestellungen', label: 'Bestellungen', icon: FileText, path: '/contracts', mcp: { businessDomain: 'procurement', scope: 'procurement:read' } },
      { id: 'wareneingang', label: 'Wareneingang', icon: Package, path: '/charge/wareneingang', mcp: { businessDomain: 'procurement', scope: 'procurement:read' } },
      { id: 'lieferanten', label: 'Lieferanten', icon: Users, path: '/einkauf/lieferanten-liste', mcp: { businessDomain: 'procurement', scope: 'procurement:read' } },
      { id: 'warengruppen', label: 'Warengruppen', icon: Package, path: '/einkauf/warengruppen', mcp: { businessDomain: 'procurement', scope: 'procurement:read' } },
      { id: 'disposition', label: 'Disposition', icon: Calculator, path: '/disposition/liste', mcp: { businessDomain: 'procurement', scope: 'procurement:read' } },
    ],
  },
  {
    id: 'fibu',
    label: 'Finanzbuchhaltung',
    icon: Euro,
    mcp: { businessDomain: 'finance', scope: 'finance:read' },
    children: [
      { id: 'hauptbuch', label: 'Hauptbuch', icon: FileText, path: '/fibu/hauptbuch', mcp: { businessDomain: 'finance', scope: 'finance:read' } },
      { id: 'debitoren', label: 'Debitoren', icon: Euro, path: '/fibu/debitoren', mcp: { businessDomain: 'finance', scope: 'finance:read' } },
      { id: 'kreditoren', label: 'Kreditoren', icon: Euro, path: '/fibu/kreditoren', mcp: { businessDomain: 'finance', scope: 'finance:read' } },
      { id: 'buchungsjournal', label: 'Buchungsjournal', icon: FileText, path: '/fibu/buchungsjournal', mcp: { businessDomain: 'finance', scope: 'finance:read' } },
      { id: 'kontenplan', label: 'Kontenplan', icon: FileText, path: '/fibu/kontenplan', mcp: { businessDomain: 'finance', scope: 'finance:read' } },
      { id: 'bilanz', label: 'Bilanz', icon: BarChart3, path: '/fibu/bilanz', mcp: { businessDomain: 'finance', scope: 'finance:read' } },
      { id: 'guv', label: 'GuV', icon: BarChart3, path: '/fibu/guv', mcp: { businessDomain: 'finance', scope: 'finance:read' } },
      { id: 'bwa', label: 'BWA', icon: BarChart3, path: '/fibu/bwa', mcp: { businessDomain: 'finance', scope: 'finance:read' } },
      { id: 'anlagen', label: 'Anlagenbuchhaltung', icon: Building2, path: '/fibu/anlagen', mcp: { businessDomain: 'finance', scope: 'finance:read' } },
      { id: 'op-verwaltung', label: 'OP-Verwaltung', icon: Euro, path: '/fibu/op-verwaltung', mcp: { businessDomain: 'finance', scope: 'finance:read' } },
    ],
  },
  {
    id: 'lager',
    label: 'Lager & Logistik',
    icon: Package,
    mcp: { businessDomain: 'inventory', scope: 'inventory:read' },
    children: [
      { id: 'bestandsuebersicht', label: 'Bestandsübersicht', icon: BarChart3, path: '/lager/bestandsuebersicht', mcp: { businessDomain: 'inventory', scope: 'inventory:read' } },
      { id: 'einlagerung', label: 'Einlagerung', icon: Package, path: '/lager/einlagerung', mcp: { businessDomain: 'inventory', scope: 'inventory:read' } },
      { id: 'auslagerung', label: 'Auslagerung', icon: Package, path: '/lager/auslagerung', mcp: { businessDomain: 'inventory', scope: 'inventory:read' } },
      { id: 'inventur', label: 'Inventur', icon: FileText, path: '/lager/inventur', mcp: { businessDomain: 'inventory', scope: 'inventory:read' } },
      { id: 'tourenplanung', label: 'Tourenplanung', icon: Truck, path: '/logistik/tourenplanung', mcp: { businessDomain: 'logistics', scope: 'logistics:read' } },
      { id: 'verladung', label: 'Verladung', icon: Truck, path: '/verladung/liste', mcp: { businessDomain: 'logistics', scope: 'logistics:read' } },
    ],
  },
  {
    id: 'agrar',
    label: 'Agrar',
    icon: Sprout,
    mcp: { businessDomain: 'agrar', scope: 'agrar:read' },
    featureKey: 'agrar',
    children: [
      { id: 'psm', label: 'Pflanzenschutzmittel', icon: Leaf, path: '/agrar/psm', mcp: { businessDomain: 'agrar', scope: 'agrar:read' } },
      { id: 'saatgut', label: 'Saatgut', icon: Sprout, path: '/agrar/saatgut', mcp: { businessDomain: 'agrar', scope: 'agrar:read' } },
      { id: 'duenger', label: 'Dünger', icon: Leaf, path: '/agrar/duenger', mcp: { businessDomain: 'agrar', scope: 'agrar:read' } },
      { id: 'feldbuch', label: 'Feldbuch', icon: FileText, path: '/agrar/feldbuch/schlagkartei', mcp: { businessDomain: 'agrar', scope: 'agrar:read' } },
      { id: 'futter', label: 'Futtermittel', icon: Package, path: '/futter/einzel/liste', mcp: { businessDomain: 'agrar', scope: 'agrar:read' } },
    ],
  },
  {
    id: 'annahme',
    label: 'Waage & Annahme',
    icon: Scale,
    mcp: { businessDomain: 'logistics', scope: 'logistics:read' },
    children: [
      { id: 'warteschlange', label: 'Warteschlange', icon: Truck, path: '/annahme/warteschlange', mcp: { businessDomain: 'logistics', scope: 'logistics:read' } },
      { id: 'waage-liste', label: 'Waagen', icon: Scale, path: '/waage/liste', mcp: { businessDomain: 'logistics', scope: 'logistics:read' } },
      { id: 'wiegungen', label: 'Wiegungen', icon: FileText, path: '/waage/wiegungen', mcp: { businessDomain: 'logistics', scope: 'logistics:read' } },
    ],
  },
  {
    id: 'compliance',
    label: 'Compliance & QS',
    icon: ShieldCheck,
    mcp: { businessDomain: 'compliance', scope: 'compliance:read' },
    children: [
      { id: 'policies', label: 'Policies', icon: ShieldCheck, path: '/policies', mcp: { businessDomain: 'compliance', scope: 'compliance:read' } },
      { id: 'zulassungen', label: 'Zulassungen', icon: FileText, path: '/compliance/zulassungen-register', mcp: { businessDomain: 'compliance', scope: 'compliance:read' } },
      { id: 'eudr', label: 'EUDR-Compliance', icon: Leaf, path: '/nachhaltigkeit/eudr-compliance', mcp: { businessDomain: 'compliance', scope: 'compliance:read' } },
      { id: 'labor', label: 'Labor', icon: FileText, path: '/qualitaet/labor-liste', mcp: { businessDomain: 'quality', scope: 'quality:read' } },
      { id: 'zertifikate', label: 'Zertifikate', icon: ShieldCheck, path: '/zertifikate/liste', mcp: { businessDomain: 'compliance', scope: 'compliance:read' } },
    ],
  },
  {
    id: 'admin',
    label: 'Administration',
    icon: Settings,
    mcp: { businessDomain: 'admin', scope: 'admin:read' },
    children: [
      { id: 'benutzer', label: 'Benutzer', icon: Users, path: '/admin/benutzer-liste', mcp: { businessDomain: 'admin', scope: 'admin:read' } },
      { id: 'monitoring', label: 'Monitoring', icon: AlertCircle, path: '/monitoring/alerts', mcp: { businessDomain: 'admin', scope: 'admin:read' } },
    ],
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
  const [expandedGroups, setExpandedGroups] = useState<Set<string>>(new Set(['verkauf', 'fibu']))

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
        {navItems
          .filter((item) => (item.featureKey === 'agrar' ? agrarEnabled : true))
          .map((item) => {
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
          to="/einstellungen/system"
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
