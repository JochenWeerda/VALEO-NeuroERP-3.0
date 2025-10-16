import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Search, Edit, ArrowUpDown } from 'lucide-react';

interface Article {
  id: string;
  article_number: string;
  name: string;
  description?: string;
  unit: string;
  category: string;
  current_stock: number;
  available_stock: number;
  reserved_stock: number;
  min_stock?: number;
  max_stock?: number;
  sales_price: number;
  is_active: boolean;
}

interface StockMovementForm {
  article_id: string;
  warehouse_id: string;
  movement_type: 'in' | 'out' | 'transfer' | 'adjustment';
  quantity: number;
  unit_cost?: number;
  reference_number?: string;
  notes?: string;
}

export function StockManagement() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [movementDialogOpen, setMovementDialogOpen] = useState(false);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);
  const queryClient = useQueryClient();

  // Fetch articles
  const { data: articles, isLoading } = useQuery<Article[]>({
    queryKey: ['articles'],
    queryFn: async () => {
      const response = await fetch('/api/v1/inventory/articles');
      const result = await response.json();
      return result.items || [];
    }
  });

  // Fetch warehouses
  const { data: warehouses } = useQuery({
    queryKey: ['warehouses'],
    queryFn: async () => {
      const response = await fetch('/api/v1/inventory/warehouses');
      return response.json();
    }
  });

  // Create stock movement mutation
  const createMovement = useMutation({
    mutationFn: async (movement: StockMovementForm) => {
      const response = await fetch('/api/v1/inventory/stock-movements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(movement)
      });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['articles'] });
      setMovementDialogOpen(false);
      setSelectedArticle(null);
    }
  });

  // Filter articles
  const filteredArticles = articles?.filter(article => {
    const matchesSearch = article.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         article.article_number.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || article.category === selectedCategory;
    return matchesSearch && matchesCategory;
  }) || [];

  // Get unique categories
  const categories = Array.from(new Set(articles?.map(a => a.category) || []));

  const getStockStatus = (article: Article) => {
    if (article.current_stock <= 0) return { status: 'out_of_stock', color: 'destructive' };
    if (article.min_stock && article.current_stock < article.min_stock) return { status: 'low_stock', color: 'secondary' };
    return { status: 'normal', color: 'default' };
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Stock Management</h1>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Article
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search articles..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map(category => (
                  <SelectItem key={category} value={category}>{category}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Articles Table */}
      <Card>
        <CardHeader>
          <CardTitle>Articles ({filteredArticles.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div>Loading...</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Article Number</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead className="text-right">Current Stock</TableHead>
                  <TableHead className="text-right">Available</TableHead>
                  <TableHead className="text-right">Reserved</TableHead>
                  <TableHead className="text-right">Min Stock</TableHead>
                  <TableHead className="text-right">Price</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredArticles.map((article) => {
                  const stockStatus = getStockStatus(article);
                  return (
                    <TableRow key={article.id}>
                      <TableCell className="font-mono">{article.article_number}</TableCell>
                      <TableCell>{article.name}</TableCell>
                      <TableCell>{article.category}</TableCell>
                      <TableCell className="text-right">{article.current_stock}</TableCell>
                      <TableCell className="text-right">{article.available_stock}</TableCell>
                      <TableCell className="text-right">{article.reserved_stock}</TableCell>
                      <TableCell className="text-right">{article.min_stock || '-'}</TableCell>
                      <TableCell className="text-right">€{article.sales_price.toFixed(2)}</TableCell>
                      <TableCell>
                        <Badge variant={stockStatus.color as any}>
                          {stockStatus.status.replace('_', ' ')}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedArticle(article);
                              setMovementDialogOpen(true);
                            }}
                          >
                            <ArrowUpDown className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Stock Movement Dialog */}
      <Dialog open={movementDialogOpen} onOpenChange={setMovementDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Stock Movement - {selectedArticle?.name}</DialogTitle>
          </DialogHeader>
          <StockMovementForm
            article={selectedArticle}
            warehouses={warehouses?.items || []}
            onSubmit={(movement) => createMovement.mutate(movement)}
            isSubmitting={createMovement.isPending}
            onCancel={() => setMovementDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}

interface StockMovementFormProps {
  article: Article | null;
  warehouses: any[];
  onSubmit: (movement: StockMovementForm) => void;
  isSubmitting: boolean;
  onCancel: () => void;
}

function StockMovementForm({ article, warehouses, onSubmit, isSubmitting, onCancel }: StockMovementFormProps) {
  const [formData, setFormData] = useState<StockMovementForm>({
    article_id: article?.id || '',
    warehouse_id: warehouses[0]?.id || '',
    movement_type: 'adjustment',
    quantity: 0,
    unit_cost: undefined,
    reference_number: '',
    notes: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Movement Type</label>
        <Select
          value={formData.movement_type}
          onValueChange={(value: any) => setFormData(prev => ({ ...prev, movement_type: value }))}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="in">Stock In</SelectItem>
            <SelectItem value="out">Stock Out</SelectItem>
            <SelectItem value="transfer">Transfer</SelectItem>
            <SelectItem value="adjustment">Adjustment</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Warehouse</label>
        <Select
          value={formData.warehouse_id}
          onValueChange={(value) => setFormData(prev => ({ ...prev, warehouse_id: value }))}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {warehouses.map(warehouse => (
              <SelectItem key={warehouse.id} value={warehouse.id}>
                {warehouse.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Quantity</label>
        <Input
          type="number"
          step="0.01"
          value={formData.quantity}
          onChange={(e) => setFormData(prev => ({ ...prev, quantity: parseFloat(e.target.value) || 0 }))}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Unit Cost (optional)</label>
        <Input
          type="number"
          step="0.01"
          value={formData.unit_cost || ''}
          onChange={(e) => setFormData(prev => ({ ...prev, unit_cost: parseFloat(e.target.value) || undefined }))}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Reference Number (optional)</label>
        <Input
          value={formData.reference_number}
          onChange={(e) => setFormData(prev => ({ ...prev, reference_number: e.target.value }))}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Notes (optional)</label>
        <Input
          value={formData.notes}
          onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
        />
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Processing...' : 'Create Movement'}
        </Button>
      </div>
    </form>
  );
}