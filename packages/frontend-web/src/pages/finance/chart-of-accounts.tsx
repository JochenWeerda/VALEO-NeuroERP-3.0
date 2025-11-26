import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { FileDown, Plus, Search, Edit, Trash2, Loader2, Building2, TrendingUp, TrendingDown, DollarSign, ListTree } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { queryKeys } from '@/lib/query'
import { financeService, type Account, type AccountHierarchy } from '@/lib/services/finance-service'
import { toast } from 'sonner'
import { TreeView, type TreeNode } from '@/components/ui/tree-view'

// Form schemas
const accountCreateSchema = z.object({
  account_number: z.string().min(1).max(20),
  account_name: z.string().min(1).max(100),
  account_type: z.enum(['asset', 'liability', 'equity', 'revenue', 'expense']),
  category: z.string().min(1),
  currency: z.string().length(3, 'Währung muss 3 Zeichen haben').default('EUR'),
  allow_manual_entries: z.boolean().default(true),
})

const accountUpdateSchema = z.object({
  account_name: z.string().min(1).max(100).optional(),
  account_type: z.enum(['asset', 'liability', 'equity', 'revenue', 'expense']).optional(),
  category: z.string().min(1).optional(),
  currency: z.string().length(3, 'Währung muss 3 Zeichen haben').optional(),
  allow_manual_entries: z.boolean().optional(),
})

type AccountCreateForm = z.infer<typeof accountCreateSchema>
type AccountUpdateForm = z.infer<typeof accountUpdateSchema>

export default function ChartOfAccountsPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingAccount, setEditingAccount] = useState<Account | null>(null)

  const { data: accountsData, isLoading, error } = useQuery({
    queryKey: queryKeys.finance.chartOfAccounts.listFiltered({
      search: searchTerm || undefined,
    }),
    queryFn: () => financeService.getAccounts({
      search: searchTerm || undefined,
      limit: 100,
    }),
  })

  const { data: hierarchyData, isLoading: isLoadingHierarchy } = useQuery({
    queryKey: ['accounts', 'hierarchy', typeFilter],
    queryFn: () => financeService.getAccountsHierarchy({
      account_type: typeFilter !== 'all' ? typeFilter : undefined,
    }),
    enabled: true, // Always load hierarchy
  })

  const accounts = accountsData?.items || []
  const totalAccounts = accountsData?.total || 0

  // Filter accounts
  const filteredAccounts = accounts.filter(account => {
    if (typeFilter !== 'all' && account.account_type !== typeFilter) return false
    if (categoryFilter !== 'all' && account.category !== categoryFilter) return false
    return true
  })

  // Statistics
  const stats = {
    total: totalAccounts,
    assets: accounts.filter(a => a.account_type === 'asset').length,
    liabilities: accounts.filter(a => a.account_type === 'liability').length,
    equity: accounts.filter(a => a.account_type === 'equity').length,
    revenue: accounts.filter(a => a.account_type === 'revenue').length,
    expenses: accounts.filter(a => a.account_type === 'expense').length,
  }

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: AccountCreateForm) => financeService.createAccount({
      ...data,
      tenant_id: 'system', // TODO: Get from context
    }),
    onSuccess: () => {
      toast.success('Konto erfolgreich erstellt')
      queryClient.invalidateQueries({ queryKey: queryKeys.finance.chartOfAccounts.all })
      setIsCreateDialogOpen(false)
      createForm.reset()
    },
    onError: (error) => {
      toast.error('Fehler beim Erstellen des Kontos')
      console.error('Create error:', error)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: AccountUpdateForm }) =>
      financeService.updateAccount(id, data),
    onSuccess: () => {
      toast.success('Konto erfolgreich aktualisiert')
      queryClient.invalidateQueries({ queryKey: queryKeys.finance.chartOfAccounts.all })
      setEditingAccount(null)
      updateForm.reset()
    },
    onError: (error) => {
      toast.error('Fehler beim Aktualisieren des Kontos')
      console.error('Update error:', error)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => financeService.deleteAccount(id),
    onSuccess: () => {
      toast.success('Konto erfolgreich deaktiviert')
      queryClient.invalidateQueries({ queryKey: queryKeys.finance.chartOfAccounts.all })
    },
    onError: (error) => {
      toast.error('Fehler beim Deaktivieren des Kontos')
      console.error('Delete error:', error)
    },
  })

  // Forms
  const createForm = useForm<AccountCreateForm>({
    resolver: zodResolver(accountCreateSchema) as any,
    defaultValues: {
      account_number: '',
      account_name: '',
      account_type: 'asset',
      category: 'current_assets',
      currency: 'EUR',
      allow_manual_entries: true,
    },
  })

  const updateForm = useForm<AccountUpdateForm>({
    resolver: zodResolver(accountUpdateSchema),
  })

  const onCreateSubmit = (data: AccountCreateForm) => {
    createMutation.mutate(data)
  }

  const onUpdateSubmit = (data: AccountUpdateForm) => {
    if (editingAccount) {
      updateMutation.mutate({ id: editingAccount.id, data })
    }
  }

  const handleEdit = (account: Account) => {
    setEditingAccount(account)
    updateForm.reset({
      account_name: account.account_name,
      account_type: account.account_type,
      category: account.category,
      currency: account.currency,
      allow_manual_entries: account.allow_manual_entries,
    })
  }

  const columns = [
    {
      key: 'account_number' as const,
      label: t('crud.fields.accountNumber'),
      render: (account: Account) => (
        <button
          onClick={() => navigate(`/finance/accounts/${account.id}`)}
          className="font-mono font-medium text-blue-600 hover:underline"
        >
          {account.account_number}
        </button>
      ),
    },
    {
      key: 'account_name' as const,
      label: t('crud.fields.accountName'),
      render: (account: Account) => {
        const getCategoryLabel = (cat: string) => {
          const categoryMap: Record<string, string> = {
            'current_assets': t('crud.fields.accountCategoryCurrentAssets'),
            'fixed_assets': t('crud.fields.accountCategoryFixedAssets'),
            'current_liabilities': t('crud.fields.accountCategoryCurrentLiabilities'),
            'long_term_liabilities': t('crud.fields.accountCategoryLongTermLiabilities'),
            'equity': t('crud.fields.accountCategoryEquity'),
            'revenue': t('crud.fields.accountCategoryRevenue'),
            'cost_of_goods_sold': t('crud.fields.accountCategoryCostOfGoodsSold'),
            'operating_expenses': t('crud.fields.accountCategoryOperatingExpenses'),
            'other_expenses': t('crud.fields.accountCategoryOtherExpenses')
          }
          return categoryMap[cat] || cat
        }
        return (
          <div>
            <div className="font-medium">{account.account_name}</div>
            <div className="text-sm text-muted-foreground">
              {getCategoryLabel(account.category)}
            </div>
          </div>
        )
      },
    },
    {
      key: 'account_type' as const,
      label: 'Typ',
      render: (account: Account) => (
        <Badge variant={
          account.account_type === 'asset' ? 'default' :
          account.account_type === 'liability' ? 'secondary' :
          account.account_type === 'equity' ? 'outline' :
          account.account_type === 'revenue' ? 'default' : 'destructive'
        }>
          {financeService.getAccountTypeLabel(account.account_type)}
        </Badge>
      ),
    },
    {
      key: 'balance' as const,
      label: 'Saldo',
      render: (account: Account) => (
        <div className={`font-mono text-right ${
          account.balance >= 0 ? 'text-green-600' : 'text-red-600'
        }`}>
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: account.currency || 'EUR' }).format(account.balance)}
        </div>
      ),
    },
    {
      key: 'currency' as const,
      label: 'Währung',
      render: (account: Account) => account.currency,
    },
    {
      key: 'allow_manual_entries' as const,
      label: 'Manuell',
      render: (account: Account) => (
        <Badge variant={account.allow_manual_entries ? 'default' : 'secondary'}>
          {account.allow_manual_entries ? 'Ja' : 'Nein'}
        </Badge>
      ),
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (account: Account) => (
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleEdit(account)}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <AlertDialog>
            <AlertDialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Trash2 className="h-4 w-4" />
              </Button>
            </AlertDialogTrigger>
            <AlertDialogContent>
              <AlertDialogHeader>
                <AlertDialogTitle>Konto deaktivieren</AlertDialogTitle>
                <AlertDialogDescription>
                  Sind Sie sicher, dass Sie das Konto "{account.account_name}" deaktivieren möchten?
                  Das Konto wird nicht gelöscht, sondern nur deaktiviert.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Abbrechen</AlertDialogCancel>
                <AlertDialogAction
                  onClick={() => deleteMutation.mutate(account.id)}
                  className="bg-red-600 hover:bg-red-700"
                >
                  Deaktivieren
                </AlertDialogAction>
              </AlertDialogFooter>
            </AlertDialogContent>
          </AlertDialog>
        </div>
      ),
    },
  ]

  if (error) {
    return (
      <div className="space-y-4 p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Fehler beim Laden der Konten</h1>
          <p className="text-muted-foreground">
            {error instanceof Error ? error.message : 'Unbekannter Fehler'}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kontenplan</h1>
          <p className="text-muted-foreground">
            {isLoading ? 'Lade Konten...' : `${totalAccounts} Konten im System`}
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              Neues Konto
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Neues Konto erstellen</DialogTitle>
            </DialogHeader>
            <Form {...createForm}>
              <form onSubmit={createForm.handleSubmit(onCreateSubmit as any)} className="space-y-4">
                <FormField
                  control={createForm.control}
                  name="account_number"
                  render={({ field }: any) => (
                    <FormItem>
                      <FormLabel>{t('crud.fields.accountNumber')} *</FormLabel>
                      <FormControl>
                        <Input placeholder="z.B. 1000" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={createForm.control}
                  name="account_name"
                  render={({ field }: any) => (
                    <FormItem>
                      <FormLabel>{t('crud.fields.accountName')} *</FormLabel>
                      <FormControl>
                        <Input placeholder="z.B. Kasse" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={createForm.control}
                  name="account_type"
                  render={({ field }: any) => (
                    <FormItem>
                      <FormLabel>{t('crud.fields.accountType')} *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder={t('crud.fields.selectType')} />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="asset">{t('crud.fields.accountTypeAsset')}</SelectItem>
                          <SelectItem value="liability">{t('crud.fields.accountTypeLiability')}</SelectItem>
                          <SelectItem value="equity">{t('crud.fields.accountTypeEquity')}</SelectItem>
                          <SelectItem value="revenue">{t('crud.fields.accountTypeRevenue')}</SelectItem>
                          <SelectItem value="expense">{t('crud.fields.accountTypeExpense')}</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={createForm.control}
                  name="category"
                  render={({ field }: any) => (
                    <FormItem>
                      <FormLabel>{t('crud.fields.accountCategory')} *</FormLabel>
                      <Select onValueChange={field.onChange} defaultValue={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder={t('crud.fields.selectCategory')} />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value="current_assets">{t('crud.fields.accountCategoryCurrentAssets')}</SelectItem>
                          <SelectItem value="fixed_assets">{t('crud.fields.accountCategoryFixedAssets')}</SelectItem>
                          <SelectItem value="current_liabilities">{t('crud.fields.accountCategoryCurrentLiabilities')}</SelectItem>
                          <SelectItem value="long_term_liabilities">{t('crud.fields.accountCategoryLongTermLiabilities')}</SelectItem>
                          <SelectItem value="equity">{t('crud.fields.accountCategoryEquity')}</SelectItem>
                          <SelectItem value="revenue">{t('crud.fields.accountCategoryRevenue')}</SelectItem>
                          <SelectItem value="cost_of_goods_sold">{t('crud.fields.accountCategoryCostOfGoodsSold')}</SelectItem>
                          <SelectItem value="operating_expenses">{t('crud.fields.accountCategoryOperatingExpenses')}</SelectItem>
                          <SelectItem value="other_expenses">{t('crud.fields.accountCategoryOtherExpenses')}</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                {/* @ts-ignore - Form component temporary workaround */}
                <div className="flex justify-end gap-2 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsCreateDialogOpen(false)}
                  >
                    Abbrechen
                  </Button>
                  <Button
                    type="submit"
                    disabled={createMutation.isPending}
                  >
                    {createMutation.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                    Erstellen
                  </Button>
                </div>
              </form>
            </Form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Building2 className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{stats.total}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.fields.accountTypeAsset')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{stats.assets}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">{t('crud.fields.accountTypeLiability')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-red-600" />
              <span className="text-2xl font-bold">{stats.liabilities}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eigenkapital</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-purple-600" />
              <span className="text-2xl font-bold">{stats.equity}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erlöse</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{stats.revenue}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aufwendungen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-orange-600" />
              <span className="text-2xl font-bold">{stats.expenses}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <div className="relative flex-1 min-w-64">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder={t('crud.fields.searchAccountPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder={t('crud.fields.allTypes')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('crud.fields.allTypes')}</SelectItem>
                <SelectItem value="asset">{t('crud.fields.accountTypeAsset')}</SelectItem>
                <SelectItem value="liability">{t('crud.fields.accountTypeLiability')}</SelectItem>
                <SelectItem value="equity">{t('crud.fields.accountTypeEquity')}</SelectItem>
                <SelectItem value="revenue">{t('crud.fields.accountTypeRevenue')}</SelectItem>
                <SelectItem value="expense">{t('crud.fields.accountTypeExpense')}</SelectItem>
              </SelectContent>
            </Select>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder={t('crud.fields.allCategories')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">{t('crud.fields.allCategories')}</SelectItem>
                <SelectItem value="current_assets">{t('crud.fields.accountCategoryCurrentAssets')}</SelectItem>
                <SelectItem value="fixed_assets">{t('crud.fields.accountCategoryFixedAssets')}</SelectItem>
                <SelectItem value="current_liabilities">{t('crud.fields.accountCategoryCurrentLiabilities')}</SelectItem>
                <SelectItem value="long_term_liabilities">{t('crud.fields.accountCategoryLongTermLiabilities')}</SelectItem>
                <SelectItem value="equity">Eigenkapital</SelectItem>
                <SelectItem value="revenue">Erlöse</SelectItem>
                <SelectItem value="cost_of_goods_sold">Wareneinsatz</SelectItem>
                <SelectItem value="operating_expenses">Betriebliche Aufwendungen</SelectItem>
                <SelectItem value="other_expenses">Sonstige Aufwendungen</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Accounts Table / Hierarchy View */}
      <Card>
        <CardContent className="pt-6">
          <Tabs defaultValue="table" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="table">Tabellenansicht</TabsTrigger>
              <TabsTrigger value="hierarchy" className="gap-2">
                <ListTree className="h-4 w-4" />
                Hierarchie
              </TabsTrigger>
            </TabsList>
            <TabsContent value="table">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin" />
                  <span className="ml-2">Lade Konten...</span>
                </div>
              ) : (
                <DataTable data={filteredAccounts} columns={columns} />
              )}
            </TabsContent>
            <TabsContent value="hierarchy">
              {isLoadingHierarchy ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin" />
                  <span className="ml-2">Lade Hierarchie...</span>
                </div>
              ) : hierarchyData && hierarchyData.length > 0 ? (
                <div className="space-y-4">
                  {hierarchyData.map((rootAccount) => {
                    const convertToTreeNode = (acc: AccountHierarchy): TreeNode => ({
                      id: acc.id,
                      label: `${acc.account_number} - ${acc.account_name} (${new Intl.NumberFormat('de-DE', { style: 'currency', currency: acc.currency || 'EUR' }).format(acc.balance)})`,
                      children: acc.children.map(convertToTreeNode),
                      data: acc,
                    })
                    return (
                      <TreeView
                        key={rootAccount.id}
                        nodes={[convertToTreeNode(rootAccount)]}
                        onNodeClick={(node) => {
                          const account = node.data as AccountHierarchy
                          if (account) {
                            handleEdit(account as any)
                          }
                        }}
                        defaultExpanded={[rootAccount.id]}
                        className="border rounded-lg p-4"
                      />
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Keine Konten gefunden. Erstellen Sie ein neues Konto, um zu beginnen.
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={!!editingAccount} onOpenChange={() => setEditingAccount(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Konto bearbeiten</DialogTitle>
          </DialogHeader>
          <Form {...updateForm}>
            <form onSubmit={updateForm.handleSubmit(onUpdateSubmit)} className="space-y-4">
              <FormField
                control={updateForm.control}
                name="account_name"
                render={({ field }: any) => (
                  <FormItem>
                    <FormLabel>{t('crud.fields.accountName')} *</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={updateForm.control}
                name="account_type"
                render={({ field }: any) => (
                  <FormItem>
                    <FormLabel>{t('crud.fields.accountType')} *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder={t('crud.fields.selectType')} />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="asset">{t('crud.fields.accountTypeAsset')}</SelectItem>
                        <SelectItem value="liability">{t('crud.fields.accountTypeLiability')}</SelectItem>
                        <SelectItem value="equity">{t('crud.fields.accountTypeEquity')}</SelectItem>
                        <SelectItem value="revenue">{t('crud.fields.accountTypeRevenue')}</SelectItem>
                        <SelectItem value="expense">{t('crud.fields.accountTypeExpense')}</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
                <FormField
                  control={updateForm.control}
                  name="category"
                  render={({ field }: any) => (
                    <FormItem>
                    <FormLabel>{t('crud.fields.accountCategory')} *</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder={t('crud.fields.selectCategory')} />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="current_assets">{t('crud.fields.accountCategoryCurrentAssets')}</SelectItem>
                        <SelectItem value="fixed_assets">{t('crud.fields.accountCategoryFixedAssets')}</SelectItem>
                        <SelectItem value="current_liabilities">{t('crud.fields.accountCategoryCurrentLiabilities')}</SelectItem>
                        <SelectItem value="long_term_liabilities">{t('crud.fields.accountCategoryLongTermLiabilities')}</SelectItem>
                        <SelectItem value="equity">{t('crud.fields.accountCategoryEquity')}</SelectItem>
                        <SelectItem value="revenue">{t('crud.fields.accountCategoryRevenue')}</SelectItem>
                        <SelectItem value="cost_of_goods_sold">{t('crud.fields.accountCategoryCostOfGoodsSold')}</SelectItem>
                        <SelectItem value="operating_expenses">{t('crud.fields.accountCategoryOperatingExpenses')}</SelectItem>
                        <SelectItem value="other_expenses">{t('crud.fields.accountCategoryOtherExpenses')}</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <div className="flex justify-end gap-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setEditingAccount(null)}
                >
                  Abbrechen
                </Button>
                <Button
                  type="submit"
                  disabled={updateMutation.isPending}
                >
                  {updateMutation.isPending && <Loader2 className="h-4 w-4 animate-spin mr-2" />}
                  Speichern
                </Button>
              </div>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  )
}