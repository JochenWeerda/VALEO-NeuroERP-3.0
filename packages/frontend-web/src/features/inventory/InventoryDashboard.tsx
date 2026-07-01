import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertTriangle, TrendingUp, Package, Warehouse } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
  type UxTaskItem,
} from '@/components/workflow';

interface InventoryStats {
  total_articles: number;
  total_current_stock: number;
  total_available_stock: number;
  low_stock_count: number;
  out_of_stock_count: number;
  total_value: number;
}

interface AlertItem {
  article_id: string;
  article_number: string;
  name: string;
  current_stock: number;
  min_stock: number;
  deficit: number;
}

interface ReplenishmentSuggestion {
  article_id: string;
  article_number: string;
  name: string;
  current_stock: number;
  suggested_quantity: number;
  estimated_cost?: number;
  priority: number;
}

type InventoryRoleFocus = 'all' | 'warehouse' | 'logistics' | 'scale' | 'procurement' | 'management';

const inventoryRoleProfiles: Array<{ id: InventoryRoleFocus; label: string; description: string }> = [
  { id: 'all', label: 'Alle Rollen', description: 'Zeigt Bestand und Logistikfolge fuer Lager, Logistik, Waage, Einkauf und Leitung.' },
  { id: 'warehouse', label: 'Lager', description: 'Fokus auf Artikelbestand, verfuegbare Menge und Inventur.' },
  { id: 'logistics', label: 'Logistik', description: 'Fokus auf Engpaesse, Nachschub und Bewegungen.' },
  { id: 'scale', label: 'Waage', description: 'Fokus auf Nachweis von Bestand, Bewegungen und Folgeprozessen.' },
  { id: 'procurement', label: 'Einkauf', description: 'Fokus auf Nachschubvorschlaege, Alerts und Bestellfolge.' },
  { id: 'management', label: 'Leitung', description: 'Fokus auf Stopper, Bestandwert und naechste Aktion.' },
];

export function InventoryDashboard() {
  const [roleFocus, setRoleFocus] = useState<InventoryRoleFocus>('all');
  // Fetch inventory statistics
  const { data: stats } = useQuery<InventoryStats>({
    queryKey: ['inventory', 'stats'],
    queryFn: async () => {
      const response = await fetch('/api/v1/inventory/reports/stock-levels');
      return response.json();
    }
  });

  // Fetch low stock alerts
  const { data: alerts } = useQuery<{ alerts: AlertItem[] }>({
    queryKey: ['inventory', 'alerts'],
    queryFn: async () => {
      const response = await fetch('/api/v1/inventory/reports/stock-alerts');
      return response.json();
    }
  });

  // Fetch replenishment suggestions
  const { data: replenishment } = useQuery<{ suggestions: ReplenishmentSuggestion[] }>({
    queryKey: ['inventory', 'replenishment'],
    queryFn: async () => {
      const response = await fetch('/api/v1/inventory/reports/replenishment-suggestions');
      return response.json();
    }
  });
  const alertItems = alerts?.alerts ?? [];
  const replenishmentSuggestions = replenishment?.suggestions ?? [];
  const totalArticles = stats?.total_articles ?? 0;
  const totalStock = stats?.total_current_stock ?? 0;
  const availableStock = stats?.total_available_stock ?? 0;
  const totalValue = stats?.total_value ?? 0;
  const lowStockCount = stats?.low_stock_count ?? alertItems.length;
  const outOfStockCount = stats?.out_of_stock_count ?? 0;
  const hasStockBase = totalArticles > 0 && totalStock > 0;
  const hasCriticalAlerts = outOfStockCount > 0 || alertItems.length > 0;
  const inventoryReady = hasStockBase && !hasCriticalAlerts;
  const inventoryNextAction = outOfStockCount > 0
    ? `${outOfStockCount} Artikel ohne Bestand pruefen.`
    : alertItems.length > 0
      ? `${alertItems.length} Bestandswarnungen priorisieren.`
      : replenishmentSuggestions.length > 0
        ? `${replenishmentSuggestions.length} Nachschubvorschlaege pruefen.`
        : hasStockBase
          ? 'Bestand stabil; Inventur- und Bewegungsnachweis pruefen.'
          : 'Artikel- und Bestandsdaten laden oder ersten Bestand erfassen.';
  const inventoryTaskItems: UxTaskItem[] = [
    { label: 'Bestandsbasis pruefen', done: hasStockBase, hint: hasStockBase ? `${totalArticles} Artikel, ${totalStock.toLocaleString('de-DE')} Bestand.` : 'Artikel- oder Bestandsbasis fehlt.' },
    { label: 'Engpaesse klaeren', done: !hasCriticalAlerts, hint: hasCriticalAlerts ? `${alertItems.length} Warnungen, ${outOfStockCount} ohne Bestand.` : 'Keine kritischen Bestandswarnungen.' },
    { label: 'Nachschub steuern', done: replenishmentSuggestions.length === 0, hint: replenishmentSuggestions.length > 0 ? `${replenishmentSuggestions.length} Nachschubvorschlaege vorhanden.` : 'Kein akuter Nachschubvorschlag.' },
    { label: 'Wert und Nachweis sichern', done: totalValue > 0 || availableStock > 0, hint: `Wert ${new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(totalValue)}, verfuegbar ${availableStock.toLocaleString('de-DE')}.` },
  ];
  const inventoryCrudCapabilities = [
    { key: 'read', label: 'Lesen', available: true, hint: 'Artikel, Bestand, verfuegbarer Bestand, Alerts, Wert und Nachschub sind sichtbar.' },
    { key: 'create', label: 'Artikel/Bewegung anlegen', available: true, hint: 'Neue Artikel und Bewegungen sind als Quick Actions vorgesehen.' },
    { key: 'update', label: 'Inventur/Bestand pflegen', available: hasStockBase, hint: hasStockBase ? 'Inventur und Bestandsbewegungen koennen aus dem Dashboard angestossen werden.' : 'Pflege braucht vorhandene Artikel.' },
    { key: 'approve', label: 'Nachschub freigeben', available: replenishmentSuggestions.length > 0, hint: replenishmentSuggestions.length > 0 ? 'Nachschubvorschlaege koennen priorisiert werden.' : 'Kein Nachschubvorschlag offen.' },
    { key: 'evidence', label: 'Kettennachweis', available: hasStockBase, hint: 'Bestand, Alerts, Nachschub und Wert bilden den Logistiknachweis.' },
    { key: 'audit', label: 'Pruefspur', available: true, hint: 'Dashboarddaten kommen aus den bestehenden Inventory-Report-Endpunkten.' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Bestands- und Logistik-Dashboard</h1>
        <Button>
          <Package className="mr-2 h-4 w-4" />
          New Article
        </Button>
      </div>

      <div className="space-y-4">
        <RoleFocusBar roles={inventoryRoleProfiles} value={roleFocus} onChange={setRoleFocus} visibleCount={roleFocus === 'all' ? 5 : 1} totalCount={5} />
        <ManagementDecisionPanel
          decision={{
            allowed: inventoryReady,
            allowedLabel: 'Arbeitsfaehig',
            blockedLabel: 'Stopper offen',
            summary: inventoryReady ? `Bestandslage ist stabil: ${totalArticles} Artikel, ${totalStock.toLocaleString('de-DE')} Bestand.` : `Vor der Logistikentscheidung ist noch etwas offen: ${inventoryNextAction}`,
            blockerCount: [!hasStockBase, outOfStockCount > 0, alertItems.length > 0].filter(Boolean).length,
            nextFocus: inventoryNextAction,
            template: { label: 'Waage oeffnen', href: '/waage/wiegungen' },
          }}
        />
        <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
          <OperationalTaskPlan title="Bestands-Kettenplan" items={inventoryTaskItems} />
          <div className="space-y-3">
            <NextActionPanel action={inventoryNextAction} tone={inventoryReady ? 'emerald' : hasCriticalAlerts ? 'red' : replenishmentSuggestions.length > 0 ? 'amber' : 'blue'} />
            <EvidenceTemplateLink link={{ label: 'Hofliste pruefen', href: '/waage/hofliste' }} />
            <EvidenceTemplateLink link={{ label: 'Bestellvorschlaege pruefen', href: '/einkauf/bestellvorschlaege' }} />
          </div>
        </div>
        <CrudCapabilityChecklist capabilities={inventoryCrudCapabilities} />
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Articles</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_articles || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Stock</CardTitle>
            <Warehouse className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_current_stock?.toLocaleString() || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Low Stock Alerts</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{alerts?.alerts?.length || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Inventory Value</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">€{stats?.total_value?.toLocaleString() || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Alerts Section */}
      {alerts?.alerts && alerts.alerts.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertTriangle className="mr-2 h-5 w-5 text-orange-500" />
              Low Stock Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {alerts.alerts.slice(0, 5).map((alert) => (
                <div key={alert.article_id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{alert.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {alert.article_number} • Current: {alert.current_stock} • Min: {alert.min_stock}
                    </div>
                  </div>
                  <Badge variant="destructive">
                    Deficit: {alert.deficit}
                  </Badge>
                </div>
              ))}
              {alerts.alerts.length > 5 && (
                <Button variant="outline" className="w-full">
                  View All {alerts.alerts.length} Alerts
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Replenishment Suggestions */}
      {replenishment?.suggestions && replenishment.suggestions.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Replenishment Suggestions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {replenishmentSuggestions.slice(0, 5).map((suggestion) => (
                <div key={suggestion.article_id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">{suggestion.name}</div>
                    <div className="text-sm text-muted-foreground">
                      {suggestion.article_number} • Current: {suggestion.current_stock}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">Order: {suggestion.suggested_quantity}</div>
                    <div className="text-sm text-muted-foreground">
                      €{suggestion.estimated_cost?.toFixed(2) || 'N/A'}
                    </div>
                  </div>
                  <Badge variant={suggestion.priority >= 4 ? "destructive" : "secondary"}>
                    Priority {suggestion.priority}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex-col">
              <Package className="h-6 w-6 mb-2" />
              Stock Movement
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <Warehouse className="h-6 w-6 mb-2" />
              Inventory Count
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <TrendingUp className="h-6 w-6 mb-2" />
              Reports
            </Button>
            <Button variant="outline" className="h-20 flex-col">
              <AlertTriangle className="h-6 w-6 mb-2" />
              Alerts
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
