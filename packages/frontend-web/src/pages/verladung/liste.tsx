import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useVerladungen, type VerladungItem } from '@/lib/api/betrieb'
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
        <div><Skeleton className="h-8 w-40" /><Skeleton className="h-4 w-28 mt-2" /></div>
        <Skeleton className="h-10 w-40" />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {[1, 2, 3].map((i) => (
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
        {error?.message || 'Die Verladungs-Daten konnten nicht geladen werden.'}
      </p>
      <Button onClick={onRetry} variant="outline" className="gap-2">
        <Truck className="h-4 w-4" />Erneut versuchen
      </Button>
    </div>
  )
}

export default function VerladungenListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: verladungen = [], isLoading, isError, error, refetch } = useVerladungen()

  // Error State: Keine Mock-Daten als Fallback!
  if (isError && !isLoading) {
    return <ErrorState error={error} onRetry={refetch} />
  }

  if (isLoading) return <LoadingSkeleton />

  const filteredVerladungen = useMemo(() => {
    if (!searchTerm) return verladungen
    const term = searchTerm.toLowerCase()
    return verladungen.filter((v) => 
      v.kennzeichen.toLowerCase().includes(term) ||
      v.artikel.toLowerCase().includes(term) ||
      v.lieferscheinNr.toLowerCase().includes(term)
    )
  }, [verladungen, searchTerm])

  const columns = [
    { key: 'kennzeichen' as const, label: 'Kennzeichen', render: (v: VerladungItem) => <span className="font-mono font-bold">{v.kennzeichen}</span> },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'menge' as const, label: 'Menge (t)', render: (v: VerladungItem) => `${v.menge} t` },
    { key: 'lieferscheinNr' as const, label: 'Lieferschein', render: (v: VerladungItem) => <span className="font-mono text-sm">{v.lieferscheinNr}</span> },
    { key: 'datum' as const, label: 'Datum', render: (v: VerladungItem) => new Date(v.datum).toLocaleDateString('de-DE') },
    { key: 'status' as const, label: 'Status', render: (v: VerladungItem) => <Badge variant={v.status === 'verladen' ? 'outline' : v.status === 'in-verladung' ? 'secondary' : 'default'}>{v.status === 'geplant' ? 'Geplant' : v.status === 'in-verladung' ? 'In Verladung' : 'Verladen'}</Badge> },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Verladungen</h1>
          <p className="text-muted-foreground">LKW-Beladungen</p>
        </div>
        <Button onClick={() => navigate('/verladung/lkw-beladung')} className="gap-2">
          <Plus className="h-4 w-4" />Neue Beladung
        </Button>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Verladungen Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Truck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{filteredVerladungen.length}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Verladung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">
              {filteredVerladungen.filter((v) => v.status === 'in-verladung').length}
            </span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Verladen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">
              {filteredVerladungen.filter((v) => v.status === 'verladen').length}
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
          <DataTable data={filteredVerladungen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
