import { useParams } from '@/app/routing/typed-router'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { BookMarked, RefreshCw } from 'lucide-react'
import { financeService } from '@/lib/services/finance-service'

const fmt = (n: number) =>
  new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)

export default function SachkontoPage(): JSX.Element {
  const { id } = useParams<{ id: string }>()

  const { data: account, isLoading: loadingAccount, refetch } = useQuery({
    queryKey: ['fibu', 'sachkonto', id],
    queryFn: () => financeService.getAccount(String(id)),
    enabled: !!id && id !== 'neu',
    staleTime: 5 * 60 * 1000,
  })

  const { data: journalData, isLoading: loadingEntries } = useQuery({
    queryKey: ['fibu', 'sachkonto-entries', id],
    queryFn: () => financeService.getJournalEntries({ limit: 50 }),
    enabled: !!id && id !== 'neu',
    staleTime: 2 * 60 * 1000,
  })

  const isLoading = loadingAccount || loadingEntries

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-24" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  if (!account) {
    return (
      <div className="p-6">
        <p className="text-muted-foreground">
          {id === 'neu' ? 'Neues Konto — bitte über Kontenplan anlegen.' : 'Konto nicht gefunden.'}
        </p>
      </div>
    )
  }

  // Filter journal entry lines for this account
  const relevantEntries = (journalData?.items ?? []).flatMap(entry =>
    entry.lines
      .filter(line => line.account_id === account.id)
      .map(line => ({
        id: entry.id,
        belegnr: entry.entry_number,
        datum: entry.posting_date || entry.entry_date,
        text: line.description || entry.description,
        soll: line.debit_amount,
        haben: line.credit_amount,
      }))
  )

  const gesamtSoll = relevantEntries.reduce((s, e) => s + e.soll, 0)
  const gesamtHaben = relevantEntries.reduce((s, e) => s + e.haben, 0)
  const saldo = account.balance

  const typLabel: Record<string, string> = {
    asset: 'Aktiva', liability: 'Passiva', equity: 'Eigenkapital',
    revenue: 'Erlöse', expense: 'Aufwendungen',
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BookMarked className="h-8 w-8" />
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold font-mono">{account.account_number}</h1>
              <Badge variant="outline">{typLabel[account.account_type] ?? account.account_type}</Badge>
              {!account.is_active && <Badge variant="destructive">Gesperrt</Badge>}
            </div>
            <p className="text-muted-foreground">{account.account_name}</p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={() => void refetch()} className="gap-2">
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      <Tabs defaultValue="buchungen" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="buchungen">Buchungen</TabsTrigger>
          <TabsTrigger value="saldo">Saldo & Statistik</TabsTrigger>
        </TabsList>

        <TabsContent value="buchungen" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Kontobuchungen</CardTitle>
            </CardHeader>
            <CardContent>
              {relevantEntries.length === 0 ? (
                <p className="text-sm text-muted-foreground py-4 text-center">
                  Keine Buchungen für dieses Konto vorhanden.
                </p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2">Datum</th>
                        <th className="text-left py-2">Beleg</th>
                        <th className="text-left py-2">Text</th>
                        <th className="text-right py-2">Soll</th>
                        <th className="text-right py-2">Haben</th>
                      </tr>
                    </thead>
                    <tbody>
                      {relevantEntries.map((b, i) => (
                        <tr key={i} className="border-b">
                          <td className="py-3">{new Date(b.datum).toLocaleDateString('de-DE')}</td>
                          <td className="py-3 font-mono">{b.belegnr}</td>
                          <td className="py-3">{b.text}</td>
                          <td className="text-right py-3">{b.soll > 0 ? fmt(b.soll) : '-'}</td>
                          <td className="text-right py-3">{b.haben > 0 ? fmt(b.haben) : '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="saldo" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Saldo & Statistik</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="rounded-lg border p-6 text-center">
                <div className="text-sm text-muted-foreground mb-2">Aktueller Saldo</div>
                <div className={`text-4xl font-bold ${saldo >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {fmt(saldo)}
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-3">
                <div className="rounded-lg border p-4">
                  <div className="text-sm text-muted-foreground mb-1">Buchungen</div>
                  <div className="text-2xl font-bold">{relevantEntries.length}</div>
                </div>
                <div className="rounded-lg border p-4">
                  <div className="text-sm text-muted-foreground mb-1">Soll (gesamt)</div>
                  <div className="text-2xl font-bold text-green-600">{fmt(gesamtSoll)}</div>
                </div>
                <div className="rounded-lg border p-4">
                  <div className="text-sm text-muted-foreground mb-1">Haben (gesamt)</div>
                  <div className="text-2xl font-bold text-red-600">{fmt(gesamtHaben)}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
