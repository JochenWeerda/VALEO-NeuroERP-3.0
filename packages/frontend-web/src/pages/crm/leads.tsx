import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search, Target } from 'lucide-react'

type Lead = {
  id: string
  unternehmen: string
  ansprechpartner: string
  quelle: string
  potenzial: number
  prioritaet: 'hoch' | 'mittel' | 'niedrig'
  status: 'neu' | 'kontaktiert' | 'qualifiziert' | 'verloren'
}

const mockLeads: Lead[] = [
  { id: '1', unternehmen: 'Agrar Ost GmbH', ansprechpartner: 'Thomas Weber', quelle: 'Messe', potenzial: 50000, prioritaet: 'hoch', status: 'qualifiziert' },
  { id: '2', unternehmen: 'Müller Landwirtschaft', ansprechpartner: 'Anna Müller', quelle: 'Website', potenzial: 25000, prioritaet: 'mittel', status: 'kontaktiert' },
  { id: '3', unternehmen: 'Hof Meier', ansprechpartner: 'Karl Meier', quelle: 'Empfehlung', potenzial: 15000, prioritaet: 'niedrig', status: 'neu' },
]

export default function LeadsPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'unternehmen' as const,
      label: 'Unternehmen',
      render: (l: Lead) => (
        <div>
          <button onClick={() => navigate(`/crm/lead/${l.id}`)} className="font-medium text-blue-600 hover:underline">
            {l.unternehmen}
          </button>
          <div className="text-sm text-muted-foreground">{l.ansprechpartner}</div>
        </div>
      ),
    },
    { key: 'quelle' as const, label: 'Quelle' },
    {
      key: 'potenzial' as const,
      label: 'Potenzial',
      render: (l: Lead) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(l.potenzial),
    },
    {
      key: 'prioritaet' as const,
      label: 'Priorität',
      render: (l: Lead) => (
        <Badge variant={l.prioritaet === 'hoch' ? 'destructive' : l.prioritaet === 'mittel' ? 'secondary' : 'outline'}>
          {l.prioritaet === 'hoch' ? 'Hoch' : l.prioritaet === 'mittel' ? 'Mittel' : 'Niedrig'}
        </Badge>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (l: Lead) => (
        <Badge variant={l.status === 'qualifiziert' ? 'default' : 'outline'}>
          {l.status === 'neu' ? 'Neu' : l.status === 'kontaktiert' ? 'Kontaktiert' : l.status === 'qualifiziert' ? 'Qualifiziert' : 'Verloren'}
        </Badge>
      ),
    },
  ]

  const gesamtPotenzial = mockLeads.reduce((sum, l) => sum + l.potenzial, 0)

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Leads</h1>
          <p className="text-muted-foreground">Verkaufschancen</p>
        </div>
        <Button onClick={() => navigate('/crm/lead/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Lead
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Leads Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{mockLeads.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamtpotenzial</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(gesamtPotenzial)}
            </span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Qualifiziert</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockLeads.filter((l) => l.status === 'qualifiziert').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Hohe Priorität</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{mockLeads.filter((l) => l.prioritaet === 'hoch').length}</span>
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
          <DataTable data={mockLeads} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
