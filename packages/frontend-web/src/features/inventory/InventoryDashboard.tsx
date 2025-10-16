// React import removed - not needed with new JSX transform
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertTriangle, TrendingUp, Package, Warehouse } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';

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

export function InventoryDashboard() {
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
  const { data: replenishment } = useQuery({
    queryKey: ['inventory', 'replenishment'],
    queryFn: async () => {
      const response = await fetch('/api/v1/inventory/reports/replenishment-suggestions');
      return response.json();
    }
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Inventory Dashboard</h1>
        <Button>
          <Package className="mr-2 h-4 w-4" />
          New Article
        </Button>
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
              {replenishment.suggestions.slice(0, 5).map((suggestion: any) => (
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