import { useState, useEffect } from 'react'
import { useSearchParams } from '@/app/routing/typed-router'
import { useTranslation } from 'react-i18next'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { NativeSelect } from '@/components/ui/native-select'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { Loader2, CheckCircle2, XCircle, ChevronRight, Download } from 'lucide-react'
import { normalizeOperationalStatus } from '@/lib/operational-status'

export default function NebenbuchAbstimmungPage(): JSX.Element {
  const { t } = useTranslation()
  const { toast } = useToast()
  const [searchParams] = useSearchParams()
  const workflowInstanceId = searchParams.get('workflowInstanceId')
  const workflowProcess = searchParams.get('workflowProcess')
  const workflowCase = searchParams.get('workflowCase')
  const [loading, setLoading] = useState(false)
  const [ledgerType, setLedgerType] = useState<string>('AR')
  const [period, setPeriod] = useState<string>(new Date().toISOString().slice(0, 7))
  const [reconciliationData, setReconciliationData] = useState<Record<string, unknown> | null>(null)
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null)
  const [selectedAccount, setSelectedAccount] = useState<string | null>(null)
  const [details, setDetails] = useState<Record<string, unknown>[]>([])
  const [exporting, setExporting] = useState(false)
  const [matchingInProgress, setMatchingInProgress] = useState(false)

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
      const { data } = await apiClient.get(
        `/api/v1/finance/subsidiary-ledger-reconciliation/summary`,
        { params: { period } },
      )
      setSummary(data)
    } catch {
      // Zusammenfassung ist sekundär; Hauptabstimmung hat eigene Fehlerbehandlung
    }
  }

  const loadReconciliation = async () => {
    setLoading(true)
    try {
      const { data } = await apiClient.get(
        `/api/v1/finance/subsidiary-ledger-reconciliation/${ledgerType.toLowerCase()}`,
        { params: { period } },
      )
      setReconciliationData(data)
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.error'),
        description: error?.response?.data?.detail || error.message || t('crud.messages.networkError'),
      })
    } finally {
      setLoading(false)
    }
  }

  const loadDetails = async (accountNumber: string) => {
    setSelectedAccount(accountNumber)
    try {
      const { data } = await apiClient.get<Record<string, unknown>[]>(
        `/api/v1/finance/subsidiary-ledger-reconciliation/${ledgerType.toLowerCase()}/details`,
        { params: { account_number: accountNumber, period } },
      )
      setDetails(Array.isArray(data) ? data : [])
    } catch {
      // Details-Anfrage schlägt still fehl; Tab bleibt leer
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

  const matchEntries = async (entryIds: string[]) => {
    if (!entryIds.length) return
    setMatchingInProgress(true)
    try {
      await apiClient.post(
        `/api/v1/finance/subsidiary-ledger-reconciliation/${ledgerType.toLowerCase()}/match`,
        { entry_ids: entryIds, period, account_number: selectedAccount },
      )
      toast({ title: 'Abstimmung erfolgreich', description: `${entryIds.length} Posten abgestimmt.` })
      if (selectedAccount) await loadDetails(selectedAccount)
      await loadReconciliation()
      await loadSummary()
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.error'),
        description: error?.response?.data?.detail || error.message || 'Abstimmung fehlgeschlagen',
      })
    } finally {
      setMatchingInProgress(false)
    }
  }

  const exportCsv = async () => {
    setExporting(true)
    try {
      const response = await apiClient.get(
        `/api/v1/finance/subsidiary-ledger-reconciliation/${ledgerType.toLowerCase()}/export?period=${encodeURIComponent(period)}`,
        { responseType: 'blob' }
      )

      const blob = response.data as Blob
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `nebenbuch-abstimmung-${ledgerType.toLowerCase()}-${period}.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)

      toast({
        title: 'Export erstellt',
        description: 'CSV wurde erfolgreich heruntergeladen.',
      })
    } catch (error: any) {
      toast({
        variant: 'destructive',
        title: t('crud.messages.error'),
        description: error?.message || t('crud.messages.networkError'),
      })
    } finally {
      setExporting(false)
    }
  }
  const ledgerTypeOptions = [
    { value: 'AR', label: `${t('crud.entities.debtor')} (AR)` },
    { value: 'AP', label: `${t('crud.entities.creditor')} (AP)` },
    { value: 'BANK', label: t('crud.fields.bankAccount') },
  ]
  const unbalancedAccounts = Number(summary?.unbalanced_accounts ?? reconciliationData?.entries?.filter(entry => !entry.is_balanced).length ?? 0)
  const operationalStatus = normalizeOperationalStatus(
    unbalancedAccounts > 0 ? 'eskaliert' : reconciliationData ? 'in_pruefung' : 'offen'
  )
  const contextSections = [
    {
      title: 'Abstimmung',
      items: [
        { label: 'Ledger-Typ', value: ledgerType },
        { label: 'Periode', value: period },
        { label: 'Unbalanciert', value: String(unbalancedAccounts) },
      ],
    },
    {
      title: 'Klaerungslage',
      items: [
        { label: 'Konten gesamt', value: String(summary?.total_accounts ?? reconciliationData?.total_accounts ?? 0) },
        { label: 'Ausgeglichen', value: String(summary?.balanced_accounts ?? reconciliationData?.balanced_accounts ?? 0) },
        { label: 'Detailkonto', value: selectedAccount || 'Keins geoeffnet' },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: unbalancedAccounts > 0 ? 'Differenzkonten klaeren' : 'Export oder Abschlussfreigabe' },
        { label: 'Blocker', value: unbalancedAccounts > 0 ? 'Es bestehen unausgeglichene Konten.' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Abstimmungsraum geladen', detail: `${ledgerType} fuer ${period}` },
    selectedAccount ? { label: 'Detailkonto geoeffnet', detail: selectedAccount } : null,
    unbalancedAccounts > 0 ? { label: 'Differenzen erkannt', detail: `${unbalancedAccounts} Konto/Konten nicht ausgeglichen` } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

  return (
    <div className="container mx-auto p-6 space-y-6">
      <OperationalCaseHeader
        title={t('crud.fields.subsidiaryLedgerReconciliation')}
        description="Abgleich zwischen Nebenbuch und Hauptbuch mit Fokus auf Differenzen und Folgeklaerung."
        status={operationalStatus}
        owner="Finanzbuchhaltung"
        blocker={unbalancedAccounts > 0 ? 'Es liegen unausgeglichene Konten im aktuellen Abstimmungsraum vor.' : null}
        nextAction={unbalancedAccounts > 0 ? 'Differenzkonten und Einzelposten klaeren' : 'Abgleich exportieren oder Periode freigeben'}
        caseLabel={`${ledgerType} ${period}`}
        tags={['FIBU', 'Abstimmung']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Abstimmungsverlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      {workflowInstanceId && (
        <div className="mb-4 rounded-md border border-indigo-500/30 bg-indigo-500/10 px-4 py-2 text-sm text-indigo-200">
          Flow-Spine: {workflowCase || workflowProcess} (Instanz {workflowInstanceId.slice(0, 8)}...)
        </div>
      )}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">{t('crud.fields.subsidiaryLedgerReconciliation')}</h1>
          <p className="text-muted-foreground mt-2">
            {t('crud.tooltips.fields.subsidiaryLedgerReconciliation')}
          </p>
        </div>
        <Button variant="outline" onClick={exportCsv} disabled={exporting}>
          {exporting ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
          Export CSV
        </Button>
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
              <NativeSelect
                value={ledgerType}
                onValueChange={setLedgerType}
                options={ledgerTypeOptions}
              />
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
                {reconciliationData.entries.map(entry => (
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
            <div className="flex justify-between items-center">
              <CardTitle>
                {t('crud.fields.details')} - {selectedAccount}
              </CardTitle>
              <Button
                size="sm"
                disabled={matchingInProgress || !details.some(d => !d.matched)}
                onClick={() => {
                  const unmatchedIds = details
                    .filter(d => !d.matched && d.entry_id)
                    .map(d => d.entry_id)
                  matchEntries(unmatchedIds)
                }}
              >
                {matchingInProgress ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <CheckCircle2 className="h-4 w-4 mr-2" />}
                Offene Posten abstimmen
              </Button>
            </div>
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
                {details.map(detail => (
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

