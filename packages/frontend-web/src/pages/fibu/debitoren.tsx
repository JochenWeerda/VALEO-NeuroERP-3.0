import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { BackButton } from '@/components/BackButton'
import { AlertTriangle, Euro, FileDown, Search } from 'lucide-react'
import { useDebitorenOP, type DebitOP } from '@/lib/api/fibu'
import { ErrorState } from '@/components/ErrorState'

export default function DebitorenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: items, isLoading, isError, error, refetch } = useDebitorenOP()

  if (isLoading) return (
    <div className="p-3 md:p-6 space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-[400px] w-full" />
    </div>
  )

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const list = items ?? []

  const columns = [
    {
      key: 'rechnungsnr' as const,
      label: 'Rechnung',
      render: (op: DebitOP) => (
        <button onClick={() => navigate(`/sales/invoice/${op.id}`)} className="font-medium text-blue-600 hover:underline font-mono">
          {op.rechnungsnr}
        </button>
      ),
    },
    { key: 'kunde' as const, label: 'Kunde' },
    { key: 'kundennr' as const, label: 'Kd-Nr', render: (op: DebitOP) => <span className="font-mono text-sm">{op.kundennr}</span> },
    { key: 'datum' as const, label: 'Re-Datum', render: (op: DebitOP) => new Date(op.datum).toLocaleDateString('de-DE') },
    {
      key: 'faelligkeit' as const,
      label: 'Fälligkeit',
      render: (op: DebitOP) => {
        const faellig = new Date(op.faelligkeit)
        const ueberfaellig = faellig < new Date()
        return (
          <span className={ueberfaellig ? 'font-semibold text-status-error' : ''}>
            {faellig.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (op: DebitOP) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(op.betrag),
    },
    {
      key: 'offen' as const,
      label: 'Offen',
      render: (op: DebitOP) => (
        <span className="font-bold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(op.offen)}
        </span>
      ),
    },
    {
      key: 'mahnStufe' as const,
      label: 'Status',
      render: (op: DebitOP) => {
        if (op.mahnStufe > 0) {
          return <Badge variant="destructive">Mahnstufe {op.mahnStufe}</Badge>
        }
        if (op.ueberfaellig) {
          return <Badge variant="secondary">Überfällig</Badge>
        }
        return <Badge variant="outline">Offen</Badge>
      },
    },
  ]

  const gesamtOffen = list.reduce((sum, op) => sum + op.offen, 0)
  const ueberfaellig = list.filter((op) => op.ueberfaellig).length
  const mahnungen = list.filter((op) => op.mahnStufe > 0).length

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Debitorenbuchhaltung</h1>
          <p className="text-muted-foreground">Offene Posten Kunden</p>
        </div>
        <BackButton to="/fibu/op-verwaltung" label="Zurück zur OP-Verwaltung" />
      </div>

      {ueberfaellig > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ueberfaellig} überfällige Rechnung(en)!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offene Posten</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{list.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Euro className="h-5 w-5 text-status-warning" />
              <span className="text-2xl font-bold text-status-warning">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtOffen)}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Überfällig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-error">{ueberfaellig}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Mahnung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-error">{mahnungen}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              DATEV Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={list} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
