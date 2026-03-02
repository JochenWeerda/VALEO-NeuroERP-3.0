import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { TrendingUp, RefreshCw, Download } from 'lucide-react'
import { financeService, type BalanceSheetItem } from '@/lib/services/finance-service'
import { exportToCSV } from '@/lib/export-utils'
import { useToast } from '@/hooks/use-toast'

const fmt = (n: number) =>
  new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(n)

function ItemGroup({ title, items, total, colorClass }: {
  title: string; items: BalanceSheetItem[]; total: number; colorClass: string
}) {
  return (
    <div className="rounded-lg border p-4">
      <div className="font-semibold text-lg mb-3">{title}</div>
      {items.map((item, i) => (
        <div key={i} className={`flex justify-between py-2 border-b last:border-0 pl-${item.level * 4}`}>
          <span className="text-sm">{item.account_name}</span>
          <span className="font-semibold">{fmt(Number(item.balance))}</span>
        </div>
      ))}
      <div className="flex justify-between pt-3 mt-3 border-t-2 font-bold">
        <span>Summe {title}</span>
        <span className={colorClass}>{fmt(Number(total))}</span>
      </div>
    </div>
  )
}

export default function BilanzPage(): JSX.Element {
  const currentPeriod = new Date().toISOString().substring(0, 7) // YYYY-MM
  const [period, setPeriod] = useState(currentPeriod)

  const { data: bilanz, isLoading, isError, refetch } = useQuery({
    queryKey: ['fibu', 'bilanz', period],
    queryFn: () => financeService.getBilanz({ period }),
    staleTime: 5 * 60 * 1000,
  })

  if (isLoading) {
    return (
      <div className="space-y-6 p-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 md:grid-cols-3">
          {[...Array(3)].map((_, i) => <Skeleton key={i} className="h-24" />)}
        </div>
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-80" />
          <Skeleton className="h-80" />
        </div>
      </div>
    )
  }

  if (isError || !bilanz) {
    return (
      <div className="space-y-6 p-6">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Bilanz</h1>
            <p className="text-muted-foreground">Bilanzstichtag auswählen</p>
          </div>
          <Input
            type="month"
            value={period}
            onChange={e => setPeriod(e.target.value)}
            className="w-40"
          />
          <Button variant="outline" onClick={() => void refetch()} className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Laden
          </Button>
        </div>
        {isError && (
          <Card className="border-amber-200 bg-amber-50">
            <CardContent className="p-4 text-amber-800 text-sm">
              Keine Bilanzdaten für Periode {period} vorhanden. Bitte Buchungen erfassen oder andere Periode wählen.
            </CardContent>
          </Card>
        )}
      </div>
    )
  }

  const bilanzsumme = Number(bilanz.total_assets)
  const eigenkapital = Number(bilanz.total_equity)
  const fremdkapital = Number(bilanz.total_liabilities)
  const ekQuote = bilanzsumme > 0 ? ((eigenkapital / bilanzsumme) * 100).toFixed(1) : '0.0'

  // Assets nach Typ gruppieren
  const anlagevermoegen = bilanz.assets.filter(a => a.account_type === 'ASSET' && a.level === 0)
  const umlaufvermoegen = bilanz.assets.filter(a => a.account_type === 'ASSET' && a.level > 0)

  const { toast } = useToast()
  const handleExport = (): void => {
    const rows = [
      ...bilanz.assets.map((a) => ({ typ: 'Aktiva', konto: a.account_name, saldo: a.balance })),
      ...bilanz.equity.map((e) => ({ typ: 'Eigenkapital', konto: e.account_name, saldo: e.balance })),
      ...bilanz.liabilities.map((l) => ({ typ: 'Passiva', konto: l.account_name, saldo: l.balance })),
    ]
    try {
      exportToCSV(rows, `bilanz-${period}-${new Date().toISOString().slice(0, 10)}.csv`, [
        { key: 'typ', label: 'Typ' },
        { key: 'konto', label: 'Konto' },
        { key: 'saldo', label: 'Saldo' },
      ])
      toast({ title: 'Export', description: 'Bilanz exportiert.' })
    } catch (e) {
      toast({ title: 'Export fehlgeschlagen', description: String(e), variant: 'destructive' })
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold">Bilanz</h1>
            <p className="text-muted-foreground">Stichtag: {bilanz.as_of_date}</p>
          </div>
          <Input
            type="month"
            value={period}
            onChange={e => setPeriod(e.target.value)}
            className="w-40"
          />
          <Button variant="outline" size="sm" onClick={() => void refetch()} className="gap-2">
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex items-center gap-2">
          {!bilanz.is_balanced && (
            <Badge variant="destructive">Nicht ausgeglichen!</Badge>
          )}
          <Badge variant="outline" className="text-lg px-4 py-2">
            EK-Quote: {ekQuote}%
          </Badge>
          <Button variant="outline" size="sm" className="gap-2" onClick={handleExport}>
            <Download className="h-4 w-4" />
            Export CSV
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bilanzsumme</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{fmt(bilanzsumme)}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eigenkapital</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{fmt(eigenkapital)}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fremdkapital</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{fmt(fremdkapital)}</span>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* AKTIVA */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">AKTIVA</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {bilanz.assets.length > 0 ? (
              <>
                {anlagevermoegen.length > 0 && (
                  <ItemGroup title="Anlagevermögen" items={anlagevermoegen}
                    total={anlagevermoegen.reduce((s, a) => s + Number(a.balance), 0)} colorClass="" />
                )}
                {umlaufvermoegen.length > 0 && (
                  <ItemGroup title="Umlaufvermögen" items={umlaufvermoegen}
                    total={umlaufvermoegen.reduce((s, a) => s + Number(a.balance), 0)} colorClass="" />
                )}
                {anlagevermoegen.length === 0 && umlaufvermoegen.length === 0 && (
                  bilanz.assets.map((a, i) => (
                    <div key={i} className="flex justify-between py-2 border-b last:border-0">
                      <span className="text-sm">{a.account_name}</span>
                      <span className="font-semibold">{fmt(Number(a.balance))}</span>
                    </div>
                  ))
                )}
              </>
            ) : (
              <p className="text-sm text-muted-foreground">Keine Aktivposten vorhanden</p>
            )}
            <div className="rounded-lg bg-blue-50 p-4">
              <div className="flex justify-between text-xl font-bold text-blue-900">
                <span>SUMME AKTIVA</span>
                <span>{fmt(bilanzsumme)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* PASSIVA */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">PASSIVA</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {bilanz.equity.length > 0 && (
              <ItemGroup title="Eigenkapital" items={bilanz.equity}
                total={eigenkapital} colorClass="text-green-600" />
            )}
            {bilanz.liabilities.length > 0 && (
              <ItemGroup title="Fremdkapital" items={bilanz.liabilities}
                total={fremdkapital} colorClass="" />
            )}
            {bilanz.equity.length === 0 && bilanz.liabilities.length === 0 && (
              <p className="text-sm text-muted-foreground">Keine Passivposten vorhanden</p>
            )}
            <div className="rounded-lg bg-blue-50 p-4">
              <div className="flex justify-between text-xl font-bold text-blue-900">
                <span>SUMME PASSIVA</span>
                <span>{fmt(bilanzsumme)}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
