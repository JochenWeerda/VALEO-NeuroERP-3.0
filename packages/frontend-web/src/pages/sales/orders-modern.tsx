/**
 * Sales Orders Page - Mit moderner Navigation (KEIN RIBBON!)
 * Zeigt Best-Practice für Page-Layout mit:
 * - AppShell (Sidebar + TopBar)
 * - PageToolbar (kontextuelle Aktionen)
 * - Command Palette (Ctrl+K)
 * 
 * MCP-ready für Phase 3
 */

import { PageToolbar, ToolbarAction } from '@/components/navigation/PageToolbar';
import { Plus, Download, Upload, Filter, Archive } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function SalesOrdersModernPage() {
  const navigate = useNavigate();

  // Primäraktionen (max 3-4) - direkt sichtbar
  const primaryActions: ToolbarAction[] = [
    {
      id: 'new-order',
      label: 'Neuer Auftrag',
      icon: <Plus className="h-4 w-4" />,
      onClick: () => navigate('/sales/orders/new'),
      variant: 'default',
      shortcut: 'Ctrl+N',
      mcp: {
        intent: 'create-sales-order',
        requiredData: ['customer', 'articles'],
      },
    },
    {
      id: 'export',
      label: 'Export',
      icon: <Download className="h-4 w-4" />,
      onClick: () => console.log('Export'),
      variant: 'outline',
      mcp: {
        intent: 'export-data',
        requiredData: ['selection'],
      },
    },
  ];

  // Overflow-Aktionen - im ⋯-Menu
  const overflowActions: ToolbarAction[] = [
    {
      id: 'import',
      label: 'Importieren',
      icon: <Upload className="h-4 w-4" />,
      onClick: () => console.log('Import'),
      mcp: {
        intent: 'import-data',
      },
    },
    {
      id: 'filter',
      label: 'Erweiterte Filter',
      icon: <Filter className="h-4 w-4" />,
      onClick: () => console.log('Filter'),
      mcp: {
        intent: 'filter-data',
      },
    },
    {
      id: 'archive',
      label: 'Archivieren',
      icon: <Archive className="h-4 w-4" />,
      onClick: () => console.log('Archive'),
      variant: 'destructive',
      mcp: {
        intent: 'archive-data',
        requiresConfirmation: true,
        requiredData: ['selection'],
      },
    },
  ];

  return (
    <>
      {/* Kontextuelle Page-Toolbar (KEIN Ribbon!) */}
      <PageToolbar
        title="Verkaufsaufträge"
        subtitle="Alle offenen Aufträge verwalten"
        primaryActions={primaryActions}
        overflowActions={overflowActions}
        mcpContext={{
          pageDomain: 'sales',
          currentDocument: undefined,
          availableActions: ['create', 'export', 'import', 'filter', 'archive'],
        }}
      />

      {/* Page Content */}
      <div className="p-6">
        <div className="rounded-lg border bg-card p-6">
          <h3 className="text-lg font-semibold mb-4">Sales Orders Liste</h3>
          
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Diese Seite zeigt das moderne Navigation-Pattern:
            </p>
            
            <ul className="list-disc list-inside space-y-2 text-sm">
              <li>✅ <strong>Sidebar links</strong> - Domänen-Navigation</li>
              <li>✅ <strong>TopBar oben</strong> - Suche + User-Menu</li>
              <li>✅ <strong>PageToolbar</strong> - Nur relevante Aktionen</li>
              <li>✅ <strong>Command Palette</strong> - Drücke Ctrl+K!</li>
              <li>✅ <strong>Kein Ribbon</strong> - Spart Platz, bessere UX</li>
              <li>✅ <strong>Responsive</strong> - Mobile-ready</li>
              <li>✅ <strong>MCP-Metadaten</strong> - Vorbereitet für AI (Phase 3)</li>
            </ul>

            <div className="mt-6 p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">💡 Teste die Navigation:</h4>
              <ul className="space-y-1 text-sm">
                <li>→ <kbd className="px-2 py-1 bg-background rounded">Ctrl+K</kbd> - Command Palette</li>
                <li>→ <kbd className="px-2 py-1 bg-background rounded">Ctrl+B</kbd> - Sidebar Toggle</li>
                <li>→ <kbd className="px-2 py-1 bg-background rounded">Ctrl+N</kbd> - Neuer Auftrag</li>
                <li>→ Klick auf <strong>⋯</strong> - Overflow-Menu</li>
              </ul>
            </div>

            <div className="mt-4 p-4 bg-primary/10 rounded-md">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                MCP-Integration (Phase 3)
              </h4>
              <p className="text-sm text-muted-foreground">
                Alle Actions haben MCP-Metadaten. In Phase 3:
              </p>
              <ul className="mt-2 space-y-1 text-sm">
                <li>• AI erklärt Aktionen: "Was macht 'Archivieren'?"</li>
                <li>• AI schlägt Aktionen vor: "Zeige mir Export-Optionen"</li>
                <li>• Kontext-aware: "Erstelle Auftrag für letzten Kunden"</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

