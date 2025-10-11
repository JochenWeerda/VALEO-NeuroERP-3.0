import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, FileText, Search, Upload } from 'lucide-react'

type Dokument = {
  id: string
  name: string
  typ: string
  kategorie: string
  groesse: number
  hochgeladen: string
  benutzer: string
}

const mockDokumente: Dokument[] = [
  { id: '1', name: 'Lieferschein LS-042.pdf', typ: 'PDF', kategorie: 'Lieferscheine', groesse: 125, hochgeladen: '2025-10-11', benutzer: 'admin@valeo.de' },
  { id: '2', name: 'Rechnung RE-042.pdf', typ: 'PDF', kategorie: 'Rechnungen', groesse: 88, hochgeladen: '2025-10-11', benutzer: 'fibu@valeo.de' },
  { id: '3', name: 'Analyse-Bericht.xlsx', typ: 'Excel', kategorie: 'Labor', groesse: 45, hochgeladen: '2025-10-10', benutzer: 'labor@valeo.de' },
]

export default function DokumentenAblagePage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Dokument',
      render: (d: Dokument) => (
        <div>
          <div className="font-medium">{d.name}</div>
          <Badge variant="outline" className="mt-1">{d.typ}</Badge>
        </div>
      ),
    },
    { key: 'kategorie' as const, label: 'Kategorie' },
    { key: 'groesse' as const, label: 'Größe', render: (d: Dokument) => `${d.groesse} KB` },
    {
      key: 'hochgeladen' as const,
      label: 'Hochgeladen',
      render: (d: Dokument) => (
        <div>
          <div>{new Date(d.hochgeladen).toLocaleDateString('de-DE')}</div>
          <div className="text-sm text-muted-foreground">{d.benutzer}</div>
        </div>
      ),
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: () => (
        <div className="flex gap-2">
          <Button size="sm" variant="outline">Download</Button>
        </div>
      ),
    },
  ]

  const gesamtGroesse = mockDokumente.reduce((sum, d) => sum + d.groesse, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dokumenten-Ablage</h1>
          <p className="text-muted-foreground">Digitales Archiv</p>
        </div>
        <Button className="gap-2">
          <Upload className="h-4 w-4" />
          Hochladen
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
              <span className="text-2xl font-bold">{mockDokumente.length}</span>
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
            <span className="text-2xl font-bold">{mockDokumente.filter((d) => d.hochgeladen === '2025-10-11').length}</span>
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
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockDokumente} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
