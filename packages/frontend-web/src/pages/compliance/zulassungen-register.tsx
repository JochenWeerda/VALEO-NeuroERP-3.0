import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, FileDown, Search, ShieldCheck } from 'lucide-react'

type Zulassung = {
  id: string
  produkt: string
  typ: 'PSM' | 'Saatgut' | 'Dünger'
  nummer: string
  behoerde: string
  gueltigBis: string
  status: 'aktiv' | 'auslaufend' | 'abgelaufen'
}

const mockZulassungen: Zulassung[] = [
  { id: '1', produkt: 'Roundup PowerFlex', typ: 'PSM', nummer: '024567-00', behoerde: 'BVL', gueltigBis: '2026-12-31', status: 'aktiv' },
  { id: '2', produkt: 'Weizen Sorte Asano', typ: 'Saatgut', nummer: 'BSA-2021-045', behoerde: 'BSA', gueltigBis: '2025-12-31', status: 'auslaufend' },
]

export default function ZulassungenRegisterPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')

  const auslaufend = mockZulassungen.filter((z) => z.status === 'auslaufend').length

  const columns = [
    {
      key: 'produkt' as const,
      label: 'Produkt',
      render: (z: Zulassung) => (
        <div>
          <div className="font-medium">{z.produkt}</div>
          <Badge variant="outline" className="mt-1">{z.typ}</Badge>
        </div>
      ),
    },
    { key: 'nummer' as const, label: 'Zulassungsnummer', render: (z: Zulassung) => <span className="font-mono text-sm">{z.nummer}</span> },
    { key: 'behoerde' as const, label: 'Behörde' },
    {
      key: 'gueltigBis' as const,
      label: 'Gültig bis',
      render: (z: Zulassung) => new Date(z.gueltigBis).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (z: Zulassung) => (
        <Badge variant={z.status === 'aktiv' ? 'outline' : z.status === 'auslaufend' ? 'secondary' : 'destructive'}>
          {z.status === 'aktiv' ? 'Aktiv' : z.status === 'auslaufend' ? 'Auslaufend' : 'Abgelaufen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Zulassungsregister</h1>
          <p className="text-muted-foreground">PSM, Saatgut & Dünger</p>
        </div>
      </div>

      {auslaufend > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{auslaufend} Zulassung(en) laufen bald ab!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Zulassungen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockZulassungen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktiv</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockZulassungen.filter((z) => z.status === 'aktiv').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Auslaufend</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{auslaufend}</span>
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
          <DataTable data={mockZulassungen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
