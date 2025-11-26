import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { Loader2, CheckCircle2, XCircle, ChevronRight } from 'lucide-react'

const entityType = 'subsidiaryLedgerReconciliation'

export default function NebenbuchAbstimmungPage(): JSX.Element {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [loading, setLoading] = useState(false)
  const [ledgerType, setLedgerType] = useState<string>('AR')
  const [period, setPeriod] = useState<string>(new Date().toISOString().slice(0, 7))
  const [reconciliationData, setReconciliationData] = useState<any>(null)
  const [summary, setSummary] = useState<any>(null)
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null)
  const [details, setDetails] = useState<any[]>([])

  useEffect(() => {
    loadSummary()
  }, [period])

  useEffect(() => {
    if (ledgerType && period) {
      loadReconciliation()
    }
  }, [ledgerType, period])

  const loadSummary = async () => {
    try {
      const response = await fetch(
        `/api/v1/finance/subsidiary-ledger-reconciliation/summary?period=${period}&tenant_id=system`
      )
      if (response.ok) {
        const data = await response.json()
        setSummary(data)
      }
    } catch (error) {
      console.error('Error loading summary:', error)
    }
  }

  const loadReconciliation = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `/api/v1/finance/subsidiary-ledger-reconciliation/${ledgerType.toLowerCase()}?period=${period}&tenant_id=system`
      )
      if (response.ok) {
        const data = await response.json()
        setReconciliationData(data)
      } else {
        toast({
          variant: 'destructive',
          title: t('crud.messages.error'),
          description: t('crud.messages.loadError'),
        })
      }
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.error'),
        description: error.message || t('crud.messages.networkError'),
      })
    } finally {
      setLoading(false)
    }
  }

  const loadDetails = async (accountNumber: string) => {
    setSelectedAccount(accountNumber)
    try {
      const response = await fetch(
        `/api/v1/finance/subsidiary-ledger-reconciliation/${ledgerType.toLowerCase()}/details?account_number=${accountNumber}&period=${period}&tenant_id=system`
      )
      if (response.ok) {
        const data = await response.json()
        setDetails(data)
      }
    } catch (error) {
      console.error('Error loading details:', error)
    }
  }

  const getLedgerTypeLabel = (type: string) => {
    switch (type) {
      case 'AR':
        return t('crud.entities.debtor')
      case 'AP':
        return t('crud.entities.creditor')
      case 'BANK':
        return t('crud.fields.bankAccount')
      default:
        return type
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">{t('crud.fields.subsidiaryLedgerReconciliation')}</h1>
          <p className="text-muted-foreground mt-2">
            {t('crud.tooltips.fields.subsidiaryLedgerReconciliation')}
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>{t('crud.fields.totalAccounts')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summary.total_accounts}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>{t('crud.fields.balancedAccounts')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{summary.balanced_accounts}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>{t('crud.fields.unbalancedAccounts')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{summary.unbalanced_accounts}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>{t('crud.fields.period')}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{period}</div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>{t('crud.fields.filters')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">
                {t('crud.fields.ledgerType')}
              </label>
              <Select value={ledgerType} onValueChange={setLedgerType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="AR">{t('crud.entities.debtor')} (AR)</SelectItem>
                  <SelectItem value="AP">{t('crud.entities.creditor')} (AP)</SelectItem>
                  <SelectItem value="BANK">{t('crud.fields.bankAccount')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">
                {t('crud.fields.period')}
              </label>
              <input
                type="month"
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="w-full px-3 py-2 border rounded-md"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Reconciliation Table */}
      {loading ? (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin" />
          </CardContent>
        </Card>
      ) : reconciliationData ? (
        <Card>
          <CardHeader>
            <CardTitle>
              {getLedgerTypeLabel(ledgerType)} - {t('crud.fields.reconciliation')}
            </CardTitle>
            <CardDescription>
              {t('crud.fields.balancedAccounts')}: {reconciliationData.balanced_accounts} / {reconciliationData.total_accounts}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('crud.fields.accountNumber')}</TableHead>
                  <TableHead>{t('crud.fields.accountName')}</TableHead>
                  <TableHead className="text-right">{t('crud.fields.subsidiaryBalance')}</TableHead>
                  <TableHead className="text-right">{t('crud.fields.generalLedgerBalance')}</TableHead>
                  <TableHead className="text-right">{t('crud.fields.difference')}</TableHead>
                  <TableHead>{t('crud.fields.status')}</TableHead>
                  <TableHead>{t('crud.fields.actions')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reconciliationData.entries.map((entry: any) => (
                  <TableRow key={entry.account_number}>
                    <TableCell className="font-medium">{entry.account_number}</TableCell>
                    <TableCell>{entry.account_name}</TableCell>
                    <TableCell className="text-right">
                      {parseFloat(entry.subsidiary_balance).toFixed(2)} €
                    </TableCell>
                    <TableCell className="text-right">
                      {parseFloat(entry.general_ledger_balance).toFixed(2)} €
                    </TableCell>
                    <TableCell className={`text-right ${Math.abs(parseFloat(entry.difference)) >= 0.01 ? 'text-red-600 font-bold' : ''}`}>
                      {parseFloat(entry.difference).toFixed(2)} €
                    </TableCell>
                    <TableCell>
                      {entry.is_balanced ? (
                        <Badge variant="default" className="bg-green-600">
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          {t('crud.fields.balanced')}
                        </Badge>
                      ) : (
                        <Badge variant="destructive">
                          <XCircle className="h-3 w-3 mr-1" />
                          {t('crud.fields.unbalanced')}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => loadDetails(entry.account_number)}
                      >
                        <ChevronRight className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : null}

      {/* Details Table */}
      {selectedAccount && details.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>
              {t('crud.fields.details')} - {selectedAccount}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>{t('crud.fields.entryNumber')}</TableHead>
                  <TableHead>{t('crud.fields.date')}</TableHead>
                  <TableHead>{t('crud.fields.description')}</TableHead>
                  <TableHead className="text-right">{t('crud.fields.amount')}</TableHead>
                  <TableHead>{t('crud.fields.source')}</TableHead>
                  <TableHead>{t('crud.fields.status')}</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {details.map((detail: any) => (
                  <TableRow key={detail.entry_id}>
                    <TableCell>{detail.entry_number}</TableCell>
                    <TableCell>{detail.entry_date}</TableCell>
                    <TableCell>{detail.description}</TableCell>
                    <TableCell className="text-right">
                      {parseFloat(detail.amount).toFixed(2)} €
                    </TableCell>
                    <TableCell>{detail.source}</TableCell>
                    <TableCell>
                      <Badge variant={detail.matched ? 'default' : 'secondary'}>
                        {detail.matched ? t('crud.fields.matched') : t('crud.fields.unmatched')}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

