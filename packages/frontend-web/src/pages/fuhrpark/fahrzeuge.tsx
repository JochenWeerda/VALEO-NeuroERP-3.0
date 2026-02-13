import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useFahrzeuge, type Fahrzeug } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, FileDown, Plus, Search, Truck } from 'lucide-react'

function LoadingSkeleton(): JSX.Element {
  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div><Skeleton className="h-8 w-32" /><Skeleton className="h-4 w-48 mt-2" /></div>
        <Skeleton className="h-10 w-40" />
      </div>
      <Card className="border-orange-500 bg-orange-50"><CardContent className="pt-4"><Skeleton className="h-5 w-64" /></CardContent></Card>
      <div className="grid gap-4 md:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}><CardHeader className="pb-2"><Skeleton className="h-4 w-24" /></CardHeader><CardContent><Skeleton className="h-8 w-16" /></CardContent></Card>
        ))}
      </div>
      <Card><CardHeader><Skeleton className="h-5 w-24" /></CardHeader><CardContent><div className="flex gap-4"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-24" /></div></CardContent></Card>
      <Card><CardContent className="pt-6"><Skeleton className="h-64 w-full" /></CardContent></Card>
    </div>
  )
}

function ErrorState({ error, onRetry }: { error: Error | null; onRetry: () => void }): JSX.Element {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
      <h2 className="text-xl font-semibold text-red-600 mb-2">Backend nicht erreichbar</h2>
      <p className="text-muted-foreground mb-4">
        {error?.message || 'Die Fahrzeug-Daten konnten nicht geladen werden.'}
      </p>
      <Button onClick={onRetry} variant="outline" className="gap-2">
        <Truck className="h-4 w-4" />Erneut versuchen
      </Button>
    </div>
  )
}

export default function FahrzeugePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: fahrzeuge = [], isLoading, isError, error, refetch } = useFahrzeuge()

  // Error State: Keine Mock-Daten als Fallback!
  if (isError && !isLoading) {
    return <ErrorState error={error} onRetry={refetch} />
  }

  if (isLoading) return <LoadingSkeleton />

  const filteredFahrzeuge = useMemo(() => {
    if (!searchTerm) return fahrzeuge
    const term = searchTerm.toLowerCase()
    return fahrzeuge.filter((f) => 
      f.kennzeichen.toLowerCase().includes(term) ||
      f.typ.toLowerCase().includes(term)
    )
  }, [fahrzeuge, searchTerm])

  const inspektionFaellig = filteredFahrzeuge.filter((f) => new Date(f.naechsteInspektion) < new Date(Date.now() + 14 * 24 * 60 * 60 * 1000)).length

  const columns = [
    { key: 'kennzeichen' as const, label: 'Kennzeichen', render: (f: Fahrzeug) => <button onClick={() => navigate(`/fuhrpark/fahrzeug/${f.id}`)} className="font-medium text-blue-600 hover:underline font-mono">{f.kennzeichen}</button> },
    { key: 'typ' as const, label: 'Typ' },
    { key: 'kilometerstand' as const, label: 'km-Stand', render: (f: Fahrzeug) => f.kilometerstand.toLocaleString('de-DE') },
    { key: 'naechsteInspektion' as const, label: 'Inspektion', render: (f: Fahrzeug) => { const datum = new Date(f.naechsteInspektion); const faellig = datum < new Date(Date.now() + 14 * 24 * 60 * 60 * 1000); return <span className={faellig ? 'font-semibold text-orange-600' : ''}>{datum.toLocaleDateString('de-DE')}</span> } },
    { key: 'status' as const, label: 'Status', render: (f: Fahrzeug) => <Badge variant={f.status === 'verfuegbar' ? 'outline' : f.status === 'unterwegs' ? 'secondary' : 'destructive'}>{f.status === 'verfuegbar' ? 'Verfuegbar' : f.status === 'unterwegs' ? 'Unterwegs' : 'Werkstatt'}</Badge> },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fuhrpark</h1>
          <p className="text-muted-foreground">Fahrzeug-Verwaltung</p>
        </div>
        <Button onClick={() => navigate('/fuhrpark/fahrzeug/neu')} className="gap-2">
          <Plus className="h-4 w-4" />Neues Fahrzeug
        </Button>
      </div>
      {inspektionFaellig > 0 && <Card className="border-orange-500 bg-orange-50"><CardContent className="pt-4"><div className="flex items-center gap-2 text-orange-900"><AlertTriangle className="h-5 w-5" /><span className="font-semibold">{inspektionFaellig} Inspektion(en) in den naechsten 14 Tagen faellig!</span></div></CardContent></Card>}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fahrzeuge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{filteredFahrzeuge.length}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Verfuegbar</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {filteredFahrzeuge.filter((f) => f.status === 'verfuegbar').length}
            </span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Unterwegs</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">
              {filteredFahrzeuge.filter((f) => f.status === 'unterwegs').length}
            </span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Inspektion faellig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{inspektionFaellig}</span>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input 
                placeholder="Suche..." 
                value={searchTerm} 
                onChange={(e) => setSearchTerm(e.target.value)} 
                className="pl-10" 
              />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />Export
            </Button>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredFahrzeuge} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
