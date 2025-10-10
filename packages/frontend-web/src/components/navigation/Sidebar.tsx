/**
 * Sidebar - Domänen-Navigation (kein Ribbon!)
 * Zeigt Hauptbereiche des ERP-Systems
 * 
 * Features:
 * - Collapsible (Platz sparen)
 * - Icon + Label (oder nur Icon wenn collapsed)
 * - Aktive Page hervorgehoben
 * - Keyboard-Navigation
 * - MCP-Metadaten
 */

import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';
import {
  ShoppingCart,
  Package,
  Calculator,
  Users,
  FileText,
  Settings,
  BarChart3,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

// Navigation-Items mit MCP-Metadaten
const navItems = [
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
    id: 'finance',
    label: 'Finanzen',
    icon: Calculator,
    path: '/finance',
    mcp: { businessDomain: 'finance', scope: 'finance:read' },
  },
  {
    id: 'customers',
    label: 'Kunden',
    icon: Users,
    path: '/customers',
    mcp: { businessDomain: 'crm', scope: 'crm:read' },
  },
  {
    id: 'analytics',
    label: 'Analytics',
    icon: BarChart3,
    path: '/analytics',
    mcp: { businessDomain: 'analytics', scope: 'analytics:read' },
  },
  {
    id: 'documents',
    label: 'Dokumente',
    icon: FileText,
    path: '/documents',
    mcp: { businessDomain: 'documents', scope: 'docs:read' },
  },
];

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
});

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  return (
    <aside
      className={cn(
        'relative flex flex-col border-r bg-background transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
      role="navigation"
      aria-label="Main navigation"
      data-mcp-component="sidebar"
      data-mcp-collapsed={collapsed}
    >
      {/* Header with Logo */}
      <div className="flex h-16 items-center border-b px-4">
        {!collapsed && (
          <h2 className="text-lg font-semibold">
            VALEO ERP
          </h2>
        )}
        {collapsed && (
          <span className="text-lg font-bold">V</span>
        )}
      </div>

      {/* Navigation Items */}
      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.id}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  'hover:bg-accent hover:text-accent-foreground',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                  isActive
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground'
                )
              }
              title={collapsed ? item.label : undefined}
              data-mcp-nav-item={item.id}
              data-mcp-domain={item.mcp.businessDomain}
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* Footer with Settings + Collapse-Toggle */}
      <div className="border-t p-2">
        {/* Settings */}
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
              'hover:bg-accent hover:text-accent-foreground',
              isActive ? 'bg-accent' : 'text-muted-foreground'
            )
          }
          title={collapsed ? 'Einstellungen' : undefined}
        >
          <Settings className="h-5 w-5" />
          {!collapsed && <span>Einstellungen</span>}
        </NavLink>

        {/* Collapse-Toggle */}
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
  );
}

