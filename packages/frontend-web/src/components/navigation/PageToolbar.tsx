/**
 * PageToolbar - Kontextuelle Toolbar (kein Ribbon!)
 * Zeigt nur relevante Aktionen für aktuelle Seite
 * 
 * Features:
 * - Primäraktionen (2-4) direkt sichtbar
 * - Rest im Overflow-Menu (⋯)
 * - Responsive (stacked auf Mobile)
 * - Keyboard-Shortcuts
 * - MCP-Metadaten für AI-Assistenz
 */

import { ReactNode } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { MoreHorizontal } from 'lucide-react';
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata';

export interface ToolbarAction {
  id: string;
  label: string;
  icon?: ReactNode;
  onClick: () => void;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary';
  disabled?: boolean;
  shortcut?: string;
  // MCP-Metadaten
  mcp?: {
    intent: string;
    requiresConfirmation?: boolean;
    requiredData?: string[];
  };
}

interface PageToolbarProps {
  title: string;
  subtitle?: string;
  // Primäraktionen (max 3-4)
  primaryActions?: ToolbarAction[];
  // Overflow-Aktionen (⋯-Menu)
  overflowActions?: ToolbarAction[];
  // Rechts-Slot (z.B. Status-Badge)
  rightSlot?: ReactNode;
  // MCP-Context für Page
  mcpContext?: {
    pageDomain: string;
    currentDocument?: string;
    availableActions: string[];
  };
}

// MCP-Metadaten für PageToolbar
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
});

export function PageToolbar({
  title,
  subtitle,
  primaryActions = [],
  overflowActions = [],
  rightSlot,
  mcpContext,
}: PageToolbarProps) {
  return (
    <div 
      className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60"
      role="toolbar"
      aria-label={`${title} toolbar`}
      data-mcp-component="page-toolbar"
      data-mcp-page-domain={mcpContext?.pageDomain}
    >
      <div className="flex h-16 items-center gap-4 px-6">
        {/* Titel & Subtitle */}
        <div className="flex-1">
          <h1 className="text-xl font-semibold tracking-tight">
            {title}
          </h1>
          {subtitle && (
            <p className="text-sm text-muted-foreground">
              {subtitle}
            </p>
          )}
        </div>

        {/* Primäraktionen (2-4 Buttons) */}
        {primaryActions.length > 0 && (
          <div className="flex items-center gap-2">
            {primaryActions.map((action) => (
              <Button
                key={action.id}
                variant={action.variant || 'default'}
                onClick={action.onClick}
                disabled={action.disabled}
                size="sm"
                // MCP-Metadaten
                data-mcp-action={action.id}
                data-mcp-intent={action.mcp?.intent}
                aria-label={action.label}
                title={action.shortcut ? `${action.label} (${action.shortcut})` : action.label}
              >
                {action.icon}
                <span className="ml-2">{action.label}</span>
                {action.shortcut && (
                  <kbd className="ml-2 hidden rounded bg-muted px-1 text-xs lg:inline">
                    {action.shortcut}
                  </kbd>
                )}
              </Button>
            ))}
          </div>
        )}

        {/* Overflow-Menu (⋯) */}
        {overflowActions.length > 0 && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="icon"
                aria-label="More actions"
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              {overflowActions.map((action, idx) => (
                <div key={action.id}>
                  {idx > 0 && action.variant === 'destructive' && (
                    <DropdownMenuSeparator />
                  )}
                  <DropdownMenuItem
                    onClick={action.onClick}
                    disabled={action.disabled}
                    className={action.variant === 'destructive' ? 'text-destructive' : ''}
                    // MCP-Metadaten
                    data-mcp-action={action.id}
                    data-mcp-intent={action.mcp?.intent}
                  >
                    {action.icon}
                    <span className="ml-2">{action.label}</span>
                    {action.shortcut && (
                      <kbd className="ml-auto text-xs">
                        {action.shortcut}
                      </kbd>
                    )}
                  </DropdownMenuItem>
                </div>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        {/* Rechts-Slot (z.B. Status-Badge) */}
        {rightSlot && (
          <div className="flex items-center">
            {rightSlot}
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Beispiel-Usage:
 * 
 * <PageToolbar
 *   title="Verkaufsaufträge"
 *   subtitle="Alle offenen Aufträge"
 *   primaryActions={[
 *     {
 *       id: 'new-order',
 *       label: 'Neuer Auftrag',
 *       icon: <Plus />,
 *       onClick: () => navigate('/sales/orders/new'),
 *       variant: 'default',
 *       shortcut: 'Ctrl+N',
 *       mcp: {
 *         intent: 'create-sales-order',
 *       },
 *     },
 *     {
 *       id: 'export',
 *       label: 'Exportieren',
 *       icon: <Download />,
 *       onClick: handleExport,
 *       variant: 'outline',
 *       mcp: {
 *         intent: 'export-data',
 *         requiredData: ['selection'],
 *       },
 *     },
 *   ]}
 *   overflowActions={[
 *     {
 *       id: 'import',
 *       label: 'Importieren',
 *       onClick: handleImport,
 *     },
 *     {
 *       id: 'archive',
 *       label: 'Archivieren',
 *       onClick: handleArchive,
 *       variant: 'destructive',
 *     },
 *   ]}
 *   mcpContext={{
 *     pageDomain: 'sales',
 *     availableActions: ['create', 'export', 'import'],
 *   }}
 * />
 */

