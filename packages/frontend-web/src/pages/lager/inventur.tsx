import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { CheckCircle, ClipboardList, Search } from 'lucide-react'

type InventurPosition = {
  id: string
  artikel: string
  lagerort: string
  sollBestand: number
  istBestand: number
  differenz: number
  status: 'offen' | 'gezaehlt' | 'abgeschlossen'
}

const mockPositionen: InventurPosition[] = [
  { id: '1', artikel: 'Weizen Premium', lagerort: 'Silo 1', sollBestand: 450, istBestand: 0, differenz: 0, status: 'offen' },
  { id: '2', artikel: 'Sojaschrot 44%', lagerort: 'Halle A', sollBestand: 280, istBestand: 278, differenz: -2, status: 'gezaehlt' },
]

export default function InventurPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const columns = [
    {
      key: 'select' as const,
      label: '',
      render: (pos: InventurPosition) => (
        <input type="checkbox" checked={selected.has(pos.id)} onChange={() => {
          const newSet = new Set(selected)
          if (newSet.has(pos.id)) newSet.delete(pos.id)
          else newSet.add(pos.id)
          setSelected(newSet)
        }} className="h-4 w-4" />
      ),
    },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'lagerort' as const, label: 'Lagerort' },
    { key: 'sollBestand' as const, label: 'Soll (t)' },
    { key: 'istBestand' as const, label: 'Ist (t)' },
    {
      key: 'differenz' as const,
      label: 'Differenz',
      render: (pos: InventurPosition) => (
        <span className={pos.differenz !== 0 ? 'font-semibold text-orange-600' : ''}>
          {pos.differenz > 0 ? '+' : ''}{pos.differenz} t
        </span>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (pos: InventurPosition) => (
        <Badge variant={pos.status === 'abgeschlossen' ? 'outline' : 'default'}>
          {pos.status === 'offen' ? 'Offen' : pos.status === 'gezaehlt' ? 'Gezählt' : 'Abgeschlossen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Inventur</h1>
          <p className="text-muted-foreground">Stichtagsinventur 2025</p>
        </div>
        <Button disabled={selected.size === 0}>
          <CheckCircle className="h-4 w-4 mr-2" />
          {selected.size} Position(en) abschließen
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Positionen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ClipboardList className="h-5 w-5" />
              <span className="text-2xl font-bold">{mockPositionen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockPositionen.filter((p) => p.status === 'offen').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockPositionen.filter((p) => p.status === 'abgeschlossen').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockPositionen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
