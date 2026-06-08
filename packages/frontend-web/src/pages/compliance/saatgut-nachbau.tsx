import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useSaatgutNachbau, type SaatgutNachbau } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

export default function SaatgutNachbauPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: nachbau = [], isError, error, refetch } = useSaatgutNachbau()

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const columns = [
    {
      key: 'betrieb' as const,
      label: 'Betrieb',
      render: (n: SaatgutNachbau) => (
        <button onClick={() => navigate(`/crm/betrieb/${n.id}`)} className="font-medium text-blue-600 hover:underline">
          {n.betrieb}
        </button>
      ),
    },
    { key: 'sorte' as const, label: 'Sorte' },
    { key: 'kultur' as const, label: 'Kultur', render: (n: SaatgutNachbau) => <Badge variant="outline">{n.kultur}</Badge> },
    {
      key: 'flaeche' as const,
      label: 'Flaeche (ha)',
      render: (n: SaatgutNachbau) => <span className="font-mono">{n.flaeche.toLocaleString('de-DE', { minimumFractionDigits: 1 })}</span>,
    },
    { key: 'erntejahr' as const, label: 'Erntejahr' },
    {
      key: 'gebuehr' as const,
      label: 'Nachbaugebuehr',
      render: (n: SaatgutNachbau) => (
        <span className="font-semibold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n.gebuehr)}</span>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (n: SaatgutNachbau) => (
        <Badge variant={n.status === 'bezahlt' ? 'outline' : n.status === 'befreit' ? 'secondary' : 'default'}>
          {n.status === 'bezahlt' ? 'Bezahlt' : n.status === 'befreit' ? 'Befreit' : 'Offen'}
        </Badge>
      ),
    },
  ]

  const gesamtFlaeche = nachbau.reduce((sum, n) => sum + n.flaeche, 0)
  const gesamtGebuehr = nachbau.reduce((sum, n) => sum + n.gebuehr, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Saatgut-Nachbau Meldungen</h1>
          <p className="text-muted-foreground">Saatgut-Treuhandverwaltung (STV)</p>
        </div>
        <Button onClick={() => navigate('/compliance/saatgut-nachbau-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Nachbau erfassen
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Meldungen Gesamt</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{nachbau.length}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Flaeche Gesamt</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{gesamtFlaeche.toLocaleString('de-DE', { minimumFractionDigits: 1 })} ha</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gebuehr Gesamt</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold">{new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtGebuehr)}</span></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Bezahlt</CardTitle></CardHeader>
          <CardContent><span className="text-2xl font-bold text-green-600">{nachbau.filter((n) => n.status === 'bezahlt').length}</span></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Suche & Filter</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Betrieb oder Sorte..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2"><FileDown className="h-4 w-4" />STV-Export</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6"><DataTable data={nachbau} columns={columns} /></CardContent>
      </Card>
    </div>
  )
}


