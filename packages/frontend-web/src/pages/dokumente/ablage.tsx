import { useState, useMemo } from 'react'
import { useDokumenteAblage, type Dokument } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, FileDown, FileText, Search, Upload } from 'lucide-react'

function LoadingSkeleton(): JSX.Element {
  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div><Skeleton className="h-8 w-56" /><Skeleton className="h-4 w-32 mt-2" /></div>
        <Skeleton className="h-10 w-32" />
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {[1, 2, 3].map((i) => (
          <Card key={i}><CardHeader className="pb-2"><Skeleton className="h-4 w-28" /></CardHeader><CardContent><Skeleton className="h-8 w-20" /></CardContent></Card>
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
        {error?.message || 'Die Dokumenten-Daten konnten nicht geladen werden.'}
      </p>
      <Button onClick={onRetry} variant="outline" className="gap-2">
        <FileText className="h-4 w-4" />Erneut versuchen
      </Button>
    </div>
  )
}

export default function DokumentenAblagePage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const { data: dokumente = [], isLoading, isError, error, refetch } = useDokumenteAblage()

  const filteredDokumente = useMemo(() => {
    if (!searchTerm) return dokumente
    const term = searchTerm.toLowerCase()
    return dokumente.filter((d) => 
      d.name.toLowerCase().includes(term) ||
      d.kategorie.toLowerCase().includes(term)
    )
  }, [dokumente, searchTerm])

  // Error State: Keine Mock-Daten als Fallback!
  if (isError && !isLoading) {
    return <ErrorState error={error} onRetry={refetch} />
  }

  if (isLoading) return <LoadingSkeleton />

  const columns = [
    { key: 'name' as const, label: 'Dokument', render: (d: Dokument) => <div><div className="font-medium">{d.name}</div><Badge variant="outline" className="mt-1">{d.typ}</Badge></div> },
    { key: 'kategorie' as const, label: 'Kategorie' },
    { key: 'groesse' as const, label: 'Groesse', render: (d: Dokument) => `${d.groesse} KB` },
    { key: 'hochgeladen' as const, label: 'Hochgeladen', render: (d: Dokument) => <div><div>{new Date(d.hochgeladen).toLocaleDateString('de-DE')}</div><div className="text-sm text-muted-foreground">{d.benutzer}</div></div> },
    { key: 'actions' as const, label: 'Aktionen', render: () => <div className="flex gap-2"><Button size="sm" variant="outline">Download</Button></div> },
  ]

  const gesamtGroesse = filteredDokumente.reduce((sum, d) => sum + d.groesse, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dokumenten-Ablage</h1>
          <p className="text-muted-foreground">Digitales Archiv</p>
        </div>
        <Button className="gap-2">
          <Upload className="h-4 w-4" />Hochladen
        </Button>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Dokumente Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{filteredDokumente.length}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Speicherplatz</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{gesamtGroesse} KB</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Heute hochgeladen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {filteredDokumente.filter((d) => d.hochgeladen === new Date().toISOString().split('T')[0]).length}
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
          <DataTable data={filteredDokumente} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
