import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useCharges, type Charge } from '@/lib/api/charges'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, FileDown, Package, Search } from 'lucide-react'
import { useTouchDevice } from '@/hooks/useTouchDevice'

export default function ChargenListePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: chargen = [], isLoading } = useCharges()

  const filteredChargen = useMemo(() => {
    if (!searchTerm) return chargen
    const term = searchTerm.toLowerCase()
    return chargen.filter(c => 
      c.chargenId?.toLowerCase().includes(term) ||
      c.artikel?.toLowerCase().includes(term) ||
      c.lagerort?.toLowerCase().includes(term)
    )
  }, [chargen, searchTerm])

  const inPruefung = filteredChargen.filter((c) => c.status === 'in-pruefung').length

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <Skeleton className="h-8 w-48" />
            <Skeleton className="h-4 w-32 mt-2" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid gap-4 md:grid-cols-4">
          {[1,2,3,4].map(i => (
            <Card key={i}><CardContent className="pt-4"><Skeleton className="h-16 w-full" /></CardContent></Card>
          ))}
        </div>
        <Card><CardContent className="pt-4"><Skeleton className="h-64 w-full" /></CardContent></Card>
      </div>
    )
  }

  const columns = [
    {
      key: 'chargenId' as const,
      label: 'Chargen-ID',
      render: (c: Charge) => (
        <button
          type="button"
          onClick={() => navigate(`/charge/stamm/${c.id}`)}
          className="min-h-11 font-medium font-mono text-primary touch-manipulation"
        >
          {c.chargenId}
        </button>
      ),
    },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'menge' as const, label: 'Menge (t)', render: (c: Charge) => `${c.menge} t` },
    { key: 'lagerort' as const, label: 'Lagerort' },
    {
      key: 'eingang' as const,
      label: 'Eingang',
      render: (c: Charge) => new Date(c.eingang).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (c: Charge) => (
        <Badge variant={c.status === 'freigegeben' ? 'outline' : c.status === 'gesperrt' ? 'destructive' : c.status === 'erfasst' ? 'default' : 'secondary'}>
          {c.status === 'freigegeben' ? 'Freigegeben' : c.status === 'gesperrt' ? 'Gesperrt' : c.status === 'erfasst' ? 'Erfasst' : 'In Pruefung'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Chargen</h1>
          <p className="text-muted-foreground">Chargen suchen und oeffnen</p>
        </div>
        <Button onClick={() => navigate('/charge/wareneingang')} className="min-h-touch touch-manipulation">Wareneingang</Button>
      </div>

      {inPruefung > 0 && (
        <Card className="border-status-warning/40 bg-status-warning/10">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-status-warning">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{inPruefung} Charge(n) in Qualitaetspruefung</span>
            </div>
          </CardContent>
        </Card>
      )}

      {!isTouch ? (
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Chargen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-muted-foreground" />
              <span className="text-2xl font-bold">{chargen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Freigegeben</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-success">{chargen.filter((c) => c.status === 'freigegeben').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">In Pruefung</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-status-warning">{inPruefung}</span>
          </CardContent>
        </Card>
      </div>
      ) : null}

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Suche Chargen"
                placeholder="Chargen-ID oder Artikel"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button
              variant="outline"
              className="min-h-touch gap-2 touch-manipulation"
              onClick={() => {
                const header = 'Chargen-ID;Artikel;Menge;Lagerort;Eingang;Status\n'
                const esc = (v: unknown) => `"${String(v ?? '').replace(/"/g, '""')}"`
                const rows = filteredChargen
                  .map((c) => [c.chargenId, c.artikel, c.menge, c.lagerort, c.eingang, c.status].map(esc).join(';'))
                  .join('\n')
                const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8' })
                const url = URL.createObjectURL(blob)
                const a = document.createElement('a')
                a.href = url
                a.download = `chargen-${new Date().toISOString().slice(0, 10)}.csv`
                a.click()
                URL.revokeObjectURL(url)
              }}
            >
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredChargen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}


