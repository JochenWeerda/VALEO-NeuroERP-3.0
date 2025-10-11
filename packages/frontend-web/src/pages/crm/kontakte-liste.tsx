import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search } from 'lucide-react'

type Kontakt = {
  id: string
  name: string
  unternehmen: string
  email: string
  telefon: string
  typ: 'kunde' | 'lieferant' | 'landwirt'
}

const mockKontakte: Kontakt[] = [
  { id: '1', name: 'Max Mustermann', unternehmen: 'Landhandel Nord', email: 'max@landhandel.de', telefon: '+49 123 456', typ: 'kunde' },
  { id: '2', name: 'Anna Schmidt', unternehmen: 'Saatgut AG', email: 'schmidt@saatgut.de', telefon: '+49 987 654', typ: 'lieferant' },
]

export default function KontakteListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Name',
      render: (k: Kontakt) => (
        <button onClick={() => navigate(`/crm/kontakt/${k.id}`)} className="font-medium text-blue-600 hover:underline">
          {k.name}
        </button>
      ),
    },
    { key: 'unternehmen' as const, label: 'Unternehmen' },
    { key: 'email' as const, label: 'E-Mail' },
    { key: 'telefon' as const, label: 'Telefon' },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (k: Kontakt) => <Badge variant="outline">{k.typ === 'kunde' ? 'Kunde' : k.typ === 'lieferant' ? 'Lieferant' : 'Landwirt'}</Badge>,
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Kontakte</h1>
          <p className="text-muted-foreground">CRM-Kontakte</p>
        </div>
        <Button onClick={() => navigate('/crm/kontakt/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Kontakt
        </Button>
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
          <DataTable data={mockKontakte} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
