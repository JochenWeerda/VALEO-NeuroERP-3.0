import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useQuery } from '@tanstack/react-query';
import { Download, TrendingUp, AlertTriangle, Package, DollarSign } from 'lucide-react';

export default function InventoryReportsPage() {
  const [activeTab, setActiveTab] = useState('overview');

  // Fetch various report data
  const { data: stockLevels } = useQuery({
    queryKey: ['inventory', 'stock-levels'],
    queryFn: async () => {
      const response = await fetch('/api/v1/inventory/reports/stock-levels');
      return response.json();
    }
  });

  const { data: alerts } = useQuery({
    queryKey: ['inventory', 'alerts'],
    queryFn: async () => {
      const response = await fetch('/api/v1/inventory/reports/stock-alerts');
      return response.json();
    }
  });

  const { data: replenishment } = useQuery({
    queryKey: ['inventory', 'replenishment'],
    queryFn: async () => {
      const response = await fetch('/api/v1/inventory/reports/replenishment-suggestions');
      return response.json();
    }
  });

  const { data: turnover } = useQuery({
    queryKey: ['inventory', 'turnover'],
    queryFn: async () => {
      const response = await fetch('/api/v1/inventory/reports/turnover-analysis');
      return response.json();
    }
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Inventory Reports</h1>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="stock-levels">Stock Levels</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="replenishment">Replenishment</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Articles</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stockLevels?.total_articles || 0}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Stock Value</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">€{stockLevels?.total_value?.toLocaleString() || 0}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Low Stock Items</CardTitle>
                <AlertTriangle className="h-4 w-4 text-orange-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">{stockLevels?.low_stock_count || 0}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Out of Stock</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{stockLevels?.out_of_stock_count || 0}</div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Alerts */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Stock Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Article</TableHead>
                    <TableHead>Current Stock</TableHead>
                    <TableHead>Min Stock</TableHead>
                    <TableHead>Deficit</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {alerts?.alerts?.slice(0, 10).map((alert: any) => (
                    <TableRow key={alert.article_id}>
                      <TableCell>{alert.name}</TableCell>
                      <TableCell>{alert.current_stock}</TableCell>
                      <TableCell>{alert.min_stock}</TableCell>
                      <TableCell className="text-red-600">-{alert.deficit}</TableCell>
                      <TableCell>
                        <Badge variant="destructive">Low Stock</Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stock-levels" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Stock Levels by Category</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Articles</TableHead>
                    <TableHead className="text-right">Total Stock</TableHead>
                    <TableHead className="text-right">Total Value</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {stockLevels?.categories && Object.entries(stockLevels.categories).map(([category, data]: [string, any]) => (
                    <TableRow key={category}>
                      <TableCell className="font-medium">{category}</TableCell>
                      <TableCell className="text-right">{data.count}</TableCell>
                      <TableCell className="text-right">{data.total_stock.toLocaleString()}</TableCell>
                      <TableCell className="text-right">€{data.total_value.toLocaleString()}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="alerts" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>All Stock Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {alerts?.alerts?.map((alert: any) => (
                  <div key={alert.article_id} className="flex items-center justify-between p-4 border rounded-lg">
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
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="replenishment" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Replenishment Suggestions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {replenishment?.suggestions?.map((suggestion: any) => (
                  <div key={suggestion.article_id} className="flex items-center justify-between p-4 border rounded-lg">
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
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="mr-2 h-5 w-5" />
                  Inventory Turnover
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Turnover Ratio:</span>
                    <span className="font-medium">{turnover?.turnover_ratio?.toFixed(2) || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Turnover Days:</span>
                    <span className="font-medium">{turnover?.turnover_days?.toFixed(1) || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Inventory Value:</span>
                    <span className="font-medium">€{turnover?.total_inventory_value?.toLocaleString() || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Stock Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Normal Stock:</span>
                    <span className="font-medium text-green-600">
                      {stockLevels?.total_articles - (stockLevels?.low_stock_count + stockLevels?.out_of_stock_count) || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Low Stock:</span>
                    <span className="font-medium text-orange-600">{stockLevels?.low_stock_count || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Out of Stock:</span>
                    <span className="font-medium text-red-600">{stockLevels?.out_of_stock_count || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}