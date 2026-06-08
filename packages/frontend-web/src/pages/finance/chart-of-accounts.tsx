import { useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { FileDown, Plus, Search, Edit, Trash2, Loader2, Building2, TrendingUp, TrendingDown, DollarSign, ListTree } from 'lucide-react'
import { queryKeys } from '@/lib/query'
import { financeService, type Account, type AccountHierarchy } from '@/lib/services/finance-service'
import { toast } from 'sonner'
import { TreeView, type TreeNode } from '@/components/ui/tree-view'
import { useTenant } from '@/hooks/useTenant'

type AccountCreateForm = {
  account_number: string
  account_name: string
  account_type: Account['account_type']
  category: string
  currency: string
  allow_manual_entries: boolean
}

type AccountUpdateForm = {
  account_name: string
  account_type: Account['account_type']
  category: string
  currency: string
  allow_manual_entries: boolean
}

type AccountFormErrors = Partial<Record<'account_number' | 'account_name' | 'account_type' | 'category' | 'currency', string>>

const ACCOUNT_TYPE_OPTIONS = [
  { value: 'asset', labelKey: 'crud.fields.accountTypeAsset' },
  { value: 'liability', labelKey: 'crud.fields.accountTypeLiability' },
  { value: 'equity', labelKey: 'crud.fields.accountTypeEquity' },
  { value: 'revenue', labelKey: 'crud.fields.accountTypeRevenue' },
  { value: 'expense', labelKey: 'crud.fields.accountTypeExpense' },
] as const satisfies ReadonlyArray<{ value: Account['account_type']; labelKey: string }>

const CATEGORY_KEYS = [
  'current_assets',
  'fixed_assets',
  'current_liabilities',
  'long_term_liabilities',
  'equity',
  'revenue',
  'cost_of_goods_sold',
  'operating_expenses',
  'other_expenses',
] as const

const DEFAULT_CREATE_FORM: AccountCreateForm = {
  account_number: '',
  account_name: '',
  account_type: 'asset',
  category: 'current_assets',
  currency: 'EUR',
  allow_manual_entries: true,
}

const EMPTY_UPDATE_FORM: AccountUpdateForm = {
  account_name: '',
  account_type: 'asset',
  category: 'current_assets',
  currency: 'EUR',
  allow_manual_entries: true,
}

const validateCreateForm = (form: AccountCreateForm): AccountFormErrors => {
  const errors: AccountFormErrors = {}
  if (!form.account_number.trim()) {
    errors.account_number = 'Kontonummer ist erforderlich'
  } else if (form.account_number.trim().length > 20) {
    errors.account_number = 'Kontonummer darf maximal 20 Zeichen haben'
  }
  if (!form.account_name.trim()) {
    errors.account_name = 'Kontoname ist erforderlich'
  } else if (form.account_name.trim().length > 100) {
    errors.account_name = 'Kontoname darf maximal 100 Zeichen haben'
  }
  if (!form.category.trim()) {
    errors.category = 'Kategorie ist erforderlich'
  }
  if (!form.currency.trim() || form.currency.trim().length !== 3) {
    errors.currency = 'Waehrung muss 3 Zeichen haben'
  }
  return errors
}

const validateUpdateForm = (form: AccountUpdateForm): AccountFormErrors => {
  const errors: AccountFormErrors = {}
  if (!form.account_name.trim()) {
    errors.account_name = 'Kontoname ist erforderlich'
  } else if (form.account_name.trim().length > 100) {
    errors.account_name = 'Kontoname darf maximal 100 Zeichen haben'
  }
  if (!form.category.trim()) {
    errors.category = 'Kategorie ist erforderlich'
  }
  if (!form.currency.trim() || form.currency.trim().length !== 3) {
    errors.currency = 'Waehrung muss 3 Zeichen haben'
  }
  return errors
}

export default function ChartOfAccountsPage(): JSX.Element {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { tenantId } = useTenant()
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingAccount, setEditingAccount] = useState<Account | null>(null)
  const [createForm, setCreateForm] = useState<AccountCreateForm>(DEFAULT_CREATE_FORM)
  const [createErrors, setCreateErrors] = useState<AccountFormErrors>({})
  const [updateForm, setUpdateForm] = useState<AccountUpdateForm>(EMPTY_UPDATE_FORM)
  const [updateErrors, setUpdateErrors] = useState<AccountFormErrors>({})

  const categoryLabels: Record<(typeof CATEGORY_KEYS)[number], string> = {
    current_assets: t('crud.fields.accountCategoryCurrentAssets'),
    fixed_assets: t('crud.fields.accountCategoryFixedAssets'),
    current_liabilities: t('crud.fields.accountCategoryCurrentLiabilities'),
    long_term_liabilities: t('crud.fields.accountCategoryLongTermLiabilities'),
    equity: t('crud.fields.accountCategoryEquity'),
    revenue: t('crud.fields.accountCategoryRevenue'),
    cost_of_goods_sold: t('crud.fields.accountCategoryCostOfGoodsSold'),
    operating_expenses: t('crud.fields.accountCategoryOperatingExpenses'),
    other_expenses: t('crud.fields.accountCategoryOtherExpenses'),
  }

  const accountTypeOptions = ACCOUNT_TYPE_OPTIONS.map((option) => ({
    value: option.value,
    label: t(option.labelKey),
  }))
  const typeFilterOptions = [{ value: 'all', label: t('crud.fields.allTypes') }, ...accountTypeOptions]
  const categoryOptions = CATEGORY_KEYS.map((value) => ({ value, label: categoryLabels[value] }))
  const categoryFilterOptions = [{ value: 'all', label: t('crud.fields.allCategories') }, ...categoryOptions]

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
    queryFn: () =>
      financeService.getAccountsHierarchy({
        account_type: typeFilter !== 'all' ? typeFilter : undefined,
      }),
    enabled: true,
  })

  const accounts = accountsData?.items || []
  const totalAccounts = accountsData?.total || 0

  const filteredAccounts = accounts.filter((account) => {
    if (typeFilter !== 'all' && account.account_type !== typeFilter) return false
    if (categoryFilter !== 'all' && account.category !== categoryFilter) return false
    return true
  })

  const stats = {
    total: totalAccounts,
    assets: accounts.filter((a) => a.account_type === 'asset').length,
    liabilities: accounts.filter((a) => a.account_type === 'liability').length,
    equity: accounts.filter((a) => a.account_type === 'equity').length,
    revenue: accounts.filter((a) => a.account_type === 'revenue').length,
    expenses: accounts.filter((a) => a.account_type === 'expense').length,
  }

  const createMutation = useMutation({
    mutationFn: (data: AccountCreateForm) =>
      financeService.createAccount({
        ...data,
        tenant_id: tenantId,
      }),
    onSuccess: () => {
      toast.success('Konto erfolgreich erstellt')
      queryClient.invalidateQueries({ queryKey: queryKeys.finance.chartOfAccounts.all })
      setIsCreateDialogOpen(false)
      setCreateForm(DEFAULT_CREATE_FORM)
      setCreateErrors({})
    },
    onError: (mutationError) => {
      toast.error('Fehler beim Erstellen des Kontos')
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: AccountUpdateForm }) => financeService.updateAccount(id, data),
    onSuccess: () => {
      toast.success('Konto erfolgreich aktualisiert')
      queryClient.invalidateQueries({ queryKey: queryKeys.finance.chartOfAccounts.all })
      setEditingAccount(null)
      setUpdateForm(EMPTY_UPDATE_FORM)
      setUpdateErrors({})
    },
    onError: (mutationError) => {
      toast.error('Fehler beim Aktualisieren des Kontos')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => financeService.deleteAccount(id),
    onSuccess: () => {
      toast.success('Konto erfolgreich deaktiviert')
      queryClient.invalidateQueries({ queryKey: queryKeys.finance.chartOfAccounts.all })
    },
    onError: (mutationError) => {
      toast.error('Fehler beim Deaktivieren des Kontos')
    },
  })

  const handleCreateField = <K extends keyof AccountCreateForm>(field: K, value: AccountCreateForm[K]): void => {
    setCreateForm((prev) => ({ ...prev, [field]: value }))
    if (createErrors[field as keyof AccountFormErrors]) {
      setCreateErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  const handleUpdateField = <K extends keyof AccountUpdateForm>(field: K, value: AccountUpdateForm[K]): void => {
    setUpdateForm((prev) => ({ ...prev, [field]: value }))
    if (updateErrors[field as keyof AccountFormErrors]) {
      setUpdateErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  const onCreateSubmit = (): void => {
    const errors = validateCreateForm(createForm)
    setCreateErrors(errors)
    if (Object.keys(errors).length > 0) {
      return
    }
    createMutation.mutate({
      ...createForm,
      account_number: createForm.account_number.trim(),
      account_name: createForm.account_name.trim(),
      currency: createForm.currency.trim().toUpperCase(),
    })
  }

  const onUpdateSubmit = (): void => {
    if (!editingAccount) {
      return
    }
    const errors = validateUpdateForm(updateForm)
    setUpdateErrors(errors)
    if (Object.keys(errors).length > 0) {
      return
    }
    updateMutation.mutate({
      id: editingAccount.id,
      data: {
        ...updateForm,
        account_name: updateForm.account_name.trim(),
        currency: updateForm.currency.trim().toUpperCase(),
      },
    })
  }

  const handleEdit = (account: Account): void => {
    setEditingAccount(account)
    setUpdateErrors({})
    setUpdateForm({
      account_name: account.account_name,
      account_type: account.account_type,
      category: account.category,
      currency: account.currency || 'EUR',
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
      render: (account: Account) => (
        <div>
          <div className="font-medium">{account.account_name}</div>
          <div className="text-sm text-muted-foreground">{categoryLabels[account.category as keyof typeof categoryLabels] || account.category}</div>
        </div>
      ),
    },
    {
      key: 'account_type' as const,
      label: 'Typ',
      render: (account: Account) => (
        <Badge
          variant={
            account.account_type === 'asset'
              ? 'default'
              : account.account_type === 'liability'
                ? 'secondary'
                : account.account_type === 'equity'
                  ? 'outline'
                  : account.account_type === 'revenue'
                    ? 'default'
                    : 'destructive'
          }
        >
          {financeService.getAccountTypeLabel(account.account_type)}
        </Badge>
      ),
    },
    {
      key: 'balance' as const,
      label: 'Saldo',
      render: (account: Account) => (
        <div className={`font-mono text-right ${account.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: account.currency || 'EUR' }).format(account.balance)}
        </div>
      ),
    },
    {
      key: 'currency' as const,
      label: 'Waehrung',
      render: (account: Account) => account.currency,
    },
    {
      key: 'allow_manual_entries' as const,
      label: 'Manuell',
      render: (account: Account) => <Badge variant={account.allow_manual_entries ? 'default' : 'secondary'}>{account.allow_manual_entries ? 'Ja' : 'Nein'}</Badge>,
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (account: Account) => (
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => handleEdit(account)}>
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
                  Sind Sie sicher, dass Sie das Konto "{account.account_name}" deaktivieren moechten?
                  Das Konto wird nicht geloescht, sondern nur deaktiviert.
                </AlertDialogDescription>
              </AlertDialogHeader>
              <AlertDialogFooter>
                <AlertDialogCancel>Abbrechen</AlertDialogCancel>
                <AlertDialogAction onClick={() => deleteMutation.mutate(account.id)} className="bg-red-600 hover:bg-red-700">
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
          <p className="text-muted-foreground">{error instanceof Error ? error.message : 'Unbekannter Fehler'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kontenplan</h1>
          <p className="text-muted-foreground">{isLoading ? 'Lade Konten...' : `${totalAccounts} Konten im System`}</p>
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
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="create-account-number">{t('crud.fields.accountNumber')} *</Label>
                <Input
                  id="create-account-number"
                  placeholder="z.B. 1000"
                  value={createForm.account_number}
                  onChange={(event) => handleCreateField('account_number', event.target.value)}
                />
                {createErrors.account_number ? <p className="text-sm text-red-500">{createErrors.account_number}</p> : null}
              </div>
              <div className="space-y-2">
                <Label htmlFor="create-account-name">{t('crud.fields.accountName')} *</Label>
                <Input
                  id="create-account-name"
                  placeholder="z.B. Kasse"
                  value={createForm.account_name}
                  onChange={(event) => handleCreateField('account_name', event.target.value)}
                />
                {createErrors.account_name ? <p className="text-sm text-red-500">{createErrors.account_name}</p> : null}
              </div>
              <div className="space-y-2">
                <Label htmlFor="create-account-type">{t('crud.fields.accountType')} *</Label>
                <NativeSelect id="create-account-type" value={createForm.account_type} onValueChange={(value) => handleCreateField('account_type', value as Account['account_type'])} options={accountTypeOptions} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="create-account-category">{t('crud.fields.accountCategory')} *</Label>
                <NativeSelect id="create-account-category" value={createForm.category} onValueChange={(value) => handleCreateField('category', value)} options={categoryOptions} />
                {createErrors.category ? <p className="text-sm text-red-500">{createErrors.category}</p> : null}
              </div>
              <div className="space-y-2">
                <Label htmlFor="create-account-currency">Waehrung</Label>
                <Input
                  id="create-account-currency"
                  maxLength={3}
                  value={createForm.currency}
                  onChange={(event) => handleCreateField('currency', event.target.value.toUpperCase())}
                />
                {createErrors.currency ? <p className="text-sm text-red-500">{createErrors.currency}</p> : null}
              </div>
              <div className="flex items-center justify-between rounded-md border p-3">
                <div>
                  <p className="text-sm font-medium">Manuelle Buchungen erlauben</p>
                  <p className="text-xs text-muted-foreground">Fuer dieses Konto direkte Buchungen zulassen</p>
                </div>
                <input
                  type="checkbox"
                  checked={createForm.allow_manual_entries}
                  onChange={(event) => handleCreateField('allow_manual_entries', event.target.checked)}
                  className="h-4 w-4 rounded border"
                />
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Abbrechen
                </Button>
                <Button type="button" disabled={createMutation.isPending} onClick={onCreateSubmit}>
                  {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Erstellen
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-6">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Building2 className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{stats.total}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">{t('crud.fields.accountTypeAsset')}</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><TrendingUp className="h-5 w-5 text-green-600" /><span className="text-2xl font-bold">{stats.assets}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">{t('crud.fields.accountTypeLiability')}</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><TrendingDown className="h-5 w-5 text-red-600" /><span className="text-2xl font-bold">{stats.liabilities}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Eigenkapital</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><DollarSign className="h-5 w-5 text-purple-600" /><span className="text-2xl font-bold">{stats.equity}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Erloese</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><TrendingUp className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{stats.revenue}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aufwendungen</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><TrendingDown className="h-5 w-5 text-orange-600" /><span className="text-2xl font-bold">{stats.expenses}</span></div></CardContent></Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <div className="relative min-w-64 flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder={t('crud.fields.searchAccountPlaceholder')} value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} className="pl-10" />
            </div>
            <NativeSelect value={typeFilter} onValueChange={setTypeFilter} options={typeFilterOptions} className="w-48" />
            <NativeSelect value={categoryFilter} onValueChange={setCategoryFilter} options={categoryFilterOptions} className="w-48" />
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <Tabs defaultValue="table" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="table">Tabellenansicht</TabsTrigger>
              <TabsTrigger value="hierarchy" className="gap-2"><ListTree className="h-4 w-4" />Hierarchie</TabsTrigger>
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
                    return <TreeView key={rootAccount.id} nodes={[convertToTreeNode(rootAccount)]} onNodeClick={(node) => { const account = node.data as AccountHierarchy; if (account) handleEdit(account as unknown as Account) }} defaultExpanded={[rootAccount.id]} className="rounded-lg border p-4" />
                  })}
                </div>
              ) : (
                <div className="py-8 text-center text-muted-foreground">Keine Konten gefunden. Erstellen Sie ein neues Konto, um zu beginnen.</div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <Dialog open={!!editingAccount} onOpenChange={() => setEditingAccount(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Konto bearbeiten</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="update-account-name">{t('crud.fields.accountName')} *</Label>
              <Input id="update-account-name" value={updateForm.account_name} onChange={(event) => handleUpdateField('account_name', event.target.value)} />
              {updateErrors.account_name ? <p className="text-sm text-red-500">{updateErrors.account_name}</p> : null}
            </div>
            <div className="space-y-2">
              <Label htmlFor="update-account-type">{t('crud.fields.accountType')} *</Label>
              <NativeSelect id="update-account-type" value={updateForm.account_type} onValueChange={(value) => handleUpdateField('account_type', value as Account['account_type'])} options={accountTypeOptions} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="update-account-category">{t('crud.fields.accountCategory')} *</Label>
              <NativeSelect id="update-account-category" value={updateForm.category} onValueChange={(value) => handleUpdateField('category', value)} options={categoryOptions} />
              {updateErrors.category ? <p className="text-sm text-red-500">{updateErrors.category}</p> : null}
            </div>
            <div className="space-y-2">
              <Label htmlFor="update-account-currency">Waehrung</Label>
              <Input id="update-account-currency" maxLength={3} value={updateForm.currency} onChange={(event) => handleUpdateField('currency', event.target.value.toUpperCase())} />
              {updateErrors.currency ? <p className="text-sm text-red-500">{updateErrors.currency}</p> : null}
            </div>
            <div className="flex items-center justify-between rounded-md border p-3">
              <div>
                <p className="text-sm font-medium">Manuelle Buchungen erlauben</p>
                <p className="text-xs text-muted-foreground">Direkte Buchungen fuer dieses Konto zulassen</p>
              </div>
              <input type="checkbox" checked={updateForm.allow_manual_entries} onChange={(event) => handleUpdateField('allow_manual_entries', event.target.checked)} className="h-4 w-4 rounded border" />
            </div>
            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setEditingAccount(null)}>Abbrechen</Button>
              <Button type="button" disabled={updateMutation.isPending} onClick={onUpdateSubmit}>
                {updateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Speichern
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
