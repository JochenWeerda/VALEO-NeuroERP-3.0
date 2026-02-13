import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWaagen, type Waage } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, FileDown, Plus, Scale, Search, WifiOff } from 'lucide-react'

function LoadingSkeleton(): JSX.Element {
  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div><Skeleton className="h-8 w-48" /><Skeleton className="h-4 w-32 mt-2" /></div>
        <Skeleton className="h-10 w-36" />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Card key={i}><CardHeader className="pb-2"><Skeleton className="h-4 w-24" /></CardHeader><CardContent><Skeleton className="h-8 w-16" /></CardContent></Card>
        ))}
      </div>
      <Card><CardHeader><Skeleton className="h-5 w-32" /></CardHeader><CardContent><div className="flex gap-4"><Skeleton className="h-10 w-full" /><Skeleton className="h-10 w-32" /></div></CardContent></Card>
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
        {error?.message || 'Die Waagen-Daten konnten nicht geladen werden.'}
      </p>
      <Button onClick={onRetry} variant="outline" className="gap-2">
        <Scale className="h-4 w-4" />Erneut versuchen
      </Button>
    </div>
  )
}

export default function WaageListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: waagen = [], isLoading, isError, error, refetch } = useWaagen()

  // Error State: Keine Mock-Daten als Fallback!
  if (isError && !isLoading) {
    return <ErrorState error={error} onRetry={refetch} />
  }

  if (isLoading) return <LoadingSkeleton />

  const filteredWaagen = useMemo(() => {
    if (!searchTerm) return waagen
    const term = searchTerm.toLowerCase()
    return waagen.filter((w) => 
      w.standort.toLowerCase().includes(term) || 
      w.id.toLowerCase().includes(term) ||
      w.typ.toLowerCase().includes(term)
    )
  }, [waagen, searchTerm])

  const columns = [
    { key: 'standort' as const, label: 'Standort', render: (w: Waage) => <div><div className="font-medium">{w.standort}</div><div className="text-sm text-muted-foreground">{w.id}</div></div> },
    { key: 'typ' as const, label: 'Typ' },
    { key: 'maxKapazitaet' as const, label: 'Max. Kapazitaet (t)' },
    { key: 'naechsteEichung' as const, label: 'Naechste Eichung', render: (w: Waage) => new Date(w.naechsteEichung).toLocaleDateString('de-DE') },
    { key: 'status' as const, label: 'Status', render: (w: Waage) => <Badge variant={w.status === 'aktiv' || w.status === 'geeicht' ? 'outline' : 'secondary'}>{w.status === 'aktiv' ? 'Aktiv' : w.status === 'wartung' ? 'Wartung' : 'Geeicht'}</Badge> },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Waagen</h1>
          <p className="text-muted-foreground">Waagen-Management</p>
        </div>
        <Button onClick={() => navigate('/waage/neu')} className="gap-2">
          <Plus className="h-4 w-4" />Neue Waage
        </Button>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Waagen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Scale className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{filteredWaagen.length}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {filteredWaagen.filter((w) => w.status === 'aktiv').length}
            </span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eichung faellig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {filteredWaagen.filter((w) => new Date(w.naechsteEichung) <= new Date()).length}
            </span>
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
          <DataTable data={filteredWaagen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
