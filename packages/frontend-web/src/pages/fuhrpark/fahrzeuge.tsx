import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, FileDown, Plus, Search, Truck } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { listFuhrparkFahrzeuge, type FuhrparkFahrzeug } from '@/lib/api/fuhrpark'

function LoadingSkeleton(): JSX.Element {
  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div><Skeleton className="h-8 w-32" /><Skeleton className="mt-2 h-4 w-48" /></div>
        <Skeleton className="h-10 w-40" />
      </div>
      <Card className="border-orange-500 bg-orange-50"><CardContent className="pt-4"><Skeleton className="h-5 w-64" /></CardContent></Card>
      <Card><CardContent className="pt-6"><Skeleton className="h-64 w-full" /></CardContent></Card>
    </div>
  )
}

function ErrorState({ error, onRetry }: { error: Error | null; onRetry: () => void }): JSX.Element {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <AlertTriangle className="mb-4 h-12 w-12 text-red-500" />
      <h2 className="mb-2 text-xl font-semibold text-red-600">Backend nicht erreichbar</h2>
      <p className="mb-4 text-muted-foreground">{error?.message || 'Die Fahrzeug-Daten konnten nicht geladen werden.'}</p>
      <Button onClick={onRetry} variant="outline" className="gap-2"><Truck className="h-4 w-4" />Erneut versuchen</Button>
    </div>
  )
}

export default function FahrzeugePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const { data: fahrzeuge = [], isLoading, isError, error, refetch } = useQuery({
    queryKey: ['fuhrpark', 'fahrzeuge'],
    queryFn: listFuhrparkFahrzeuge,
  })

  const filteredFahrzeuge = useMemo(() => {
    if (!searchTerm) return fahrzeuge
    const term = searchTerm.toLowerCase()
    return fahrzeuge.filter((f) =>
      f.kennzeichen.toLowerCase().includes(term) ||
      f.typ.toLowerCase().includes(term) ||
      (f.ro_nummer ?? '').toLowerCase().includes(term),
    )
  }, [fahrzeuge, searchTerm])

  const inspektionFaellig = filteredFahrzeuge.filter((f) => {
    if (!f.naechste_inspektion) return false
    return new Date(f.naechste_inspektion) < new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
  }).length

  if (isError && !isLoading) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  if (isLoading) return <LoadingSkeleton />

  const columns = [
    {
      key: 'kennzeichen' as const,
      label: 'Kennzeichen',
      render: (f: FuhrparkFahrzeug) => (
        <button onClick={() => navigate(`/fuhrpark/fahrzeug/${f.id}`)} className="font-mono font-medium text-blue-600 hover:underline">{f.kennzeichen}</button>
      ),
    },
    { key: 'ro_nummer' as const, label: 'RO-Nr.' },
    { key: 'typ' as const, label: 'Typ' },
    { key: 'kilometerstand' as const, label: 'km-Stand', render: (f: FuhrparkFahrzeug) => Number(f.kilometerstand ?? 0).toLocaleString('de-DE') },
    {
      key: 'naechste_inspektion' as const,
      label: 'Inspektion',
      render: (f: FuhrparkFahrzeug) => {
        if (!f.naechste_inspektion) return '-'
        const datum = new Date(f.naechste_inspektion)
        const faellig = datum < new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)
        return <span className={faellig ? 'font-semibold text-orange-600' : ''}>{datum.toLocaleDateString('de-DE')}</span>
      },
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (f: FuhrparkFahrzeug) => (
        <Badge variant={f.status === 'verfuegbar' ? 'outline' : f.status === 'unterwegs' ? 'secondary' : 'destructive'}>
          {f.status === 'verfuegbar' ? 'Verfuegbar' : f.status === 'unterwegs' ? 'Unterwegs' : 'Werkstatt'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fuhrpark</h1>
          <p className="text-muted-foreground">Fahrzeug-Verwaltung</p>
        </div>
        <Button onClick={() => navigate('/fuhrpark/fahrzeug/neu')} className="gap-2"><Plus className="h-4 w-4" />Neues Fahrzeug</Button>
      </div>

      {inspektionFaellig > 0 && (
        <Card className="border-orange-500 bg-orange-50"><CardContent className="pt-4"><div className="flex items-center gap-2 text-orange-900"><AlertTriangle className="h-5 w-5" /><span className="font-semibold">{inspektionFaellig} Inspektion(en) in den naechsten 14 Tagen faellig!</span></div></CardContent></Card>
      )}

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div>
            <Button variant="outline" className="gap-2"><FileDown className="h-4 w-4" />Export</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6"><DataTable data={filteredFahrzeuge} columns={columns} /></CardContent>
      </Card>
    </div>
  )
}
