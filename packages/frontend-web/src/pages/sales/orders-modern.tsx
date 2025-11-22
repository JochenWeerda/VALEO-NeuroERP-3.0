/**
 * Sales Orders Page - Mit moderner Navigation (KEIN RIBBON!)
 * Zeigt Best-Practice für Page-Layout mit:
 * - AppShell (Sidebar + TopBar)
 * - PageToolbar (kontextuelle Aktionen)
 * - Command Palette (Ctrl+K)
 * 
 * MCP-ready für Phase 3
 */

import { useTranslation } from 'react-i18next'
import { PageToolbar, ToolbarAction } from '@/components/navigation/PageToolbar';
import { Archive, Download, Filter, Plus, Sparkles, Upload } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { getEntityTypeLabel, getListTitle } from '@/features/crud/utils/i18n-helpers';

export default function SalesOrdersModernPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate();
  const entityType = 'salesOrder'
  const entityTypeLabel = getEntityTypeLabel(t, entityType, 'Verkaufsauftrag')
  const pageTitle = getListTitle(t, entityTypeLabel)

  // Primäraktionen (max 3-4) - direkt sichtbar
  const primaryActions: ToolbarAction[] = [
    {
      id: 'new-order',
      label: `${t('crud.actions.new')} ${entityTypeLabel}`,
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
      label: t('crud.actions.export'),
      icon: <Download className="h-4 w-4" />,
      onClick: () => console.info('Export requested'),
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
      label: t('crud.actions.import'),
      icon: <Upload className="h-4 w-4" />,
      onClick: () => console.info('Import requested'),
      mcp: {
        intent: 'import-data',
      },
    },
    {
      id: 'filter',
      label: t('crud.actions.filter'),
      icon: <Filter className="h-4 w-4" />,
      onClick: () => console.info('Advanced filter requested'),
      mcp: {
        intent: 'filter-data',
      },
    },
    {
      id: 'archive',
      label: t('crud.actions.archive'),
      icon: <Archive className="h-4 w-4" />,
      onClick: () => console.info('Archive requested'),
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
        title={pageTitle}
        subtitle={t('crud.list.overview', { entityType: entityTypeLabel })}
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
          <h3 className="text-lg font-semibold mb-4">{pageTitle}</h3>
          
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              {t('crud.list.modernNavigationPattern')}
            </p>
            
            <ul className="list-disc list-inside space-y-2 text-sm">
              <li>✅ <strong>{t('crud.list.sidebarLeft')}</strong> - {t('crud.list.domainNavigation')}</li>
              <li>✅ <strong>{t('crud.list.topBar')}</strong> - {t('crud.list.searchAndUserMenu')}</li>
              <li>✅ <strong>{t('crud.list.pageToolbar')}</strong> - {t('crud.list.relevantActionsOnly')}</li>
              <li>✅ <strong>{t('crud.list.commandPalette')}</strong> - {t('crud.list.pressCtrlK')}</li>
              <li>✅ <strong>{t('crud.list.noRibbon')}</strong> - {t('crud.list.savesSpace')}</li>
              <li>✅ <strong>{t('crud.list.responsive')}</strong> - {t('crud.list.mobileReady')}</li>
              <li>✅ <strong>{t('crud.list.mcpMetadata')}</strong> - {t('crud.list.preparedForAI')}</li>
            </ul>

            <div className="mt-6 p-4 bg-muted rounded-md">
              <h4 className="font-semibold mb-2">💡 {t('crud.list.testNavigation')}</h4>
              <ul className="space-y-1 text-sm">
                <li>→ <kbd className="px-2 py-1 bg-background rounded">Ctrl+K</kbd> - {t('crud.list.commandPalette')}</li>
                <li>→ <kbd className="px-2 py-1 bg-background rounded">Ctrl+B</kbd> - {t('crud.list.sidebarToggle')}</li>
                <li>→ <kbd className="px-2 py-1 bg-background rounded">Ctrl+N</kbd> - {t('crud.actions.new')} {entityTypeLabel}</li>
                <li>→ {t('crud.list.clickOn')} <strong>⋯</strong> - {t('crud.list.overflowMenu')}</li>
              </ul>
            </div>

            <div className="mt-4 p-4 bg-primary/10 rounded-md">
              <h4 className="font-semibold mb-2 flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                {t('crud.list.mcpIntegration')}
              </h4>
              <p className="text-sm text-muted-foreground">
                {t('crud.list.allActionsHaveMCP')}
              </p>
              <ul className="mt-2 space-y-1 text-sm">
                <li>• {t('crud.list.aiExplainsActions')}</li>
                <li>• {t('crud.list.aiSuggestsActions')}</li>
                <li>• {t('crud.list.contextAware')}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

