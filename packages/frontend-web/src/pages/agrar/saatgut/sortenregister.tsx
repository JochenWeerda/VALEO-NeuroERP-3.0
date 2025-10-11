import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search } from 'lucide-react'

type Sorte = {
  id: string
  name: string
  art: string
  zuechter: string
  zulassung: string
  eigenschaft: string[]
  status: 'aktiv' | 'auslaufend'
}

const mockSorten: Sorte[] = [
  { id: '1', name: 'Asano', art: 'Weizen', zuechter: 'KWS', zulassung: '2020', eigenschaft: ['Winterhart', 'Ertragsstark'], status: 'aktiv' },
  { id: '2', name: 'Elixer', art: 'Weizen', zuechter: 'Saaten-Union', zulassung: '2019', eigenschaft: ['Frühreife', 'Standfest'], status: 'aktiv' },
]

export default function SortenregisterPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'name' as const,
      label: 'Sorte',
      render: (s: Sorte) => (
        <button onClick={() => navigate(`/agrar/saatgut/sorte/${s.id}`)} className="font-medium text-blue-600 hover:underline">
          {s.name}
        </button>
      ),
    },
    { key: 'art' as const, label: 'Art' },
    { key: 'zuechter' as const, label: 'Züchter' },
    { key: 'zulassung' as const, label: 'Zulassung' },
    {
      key: 'eigenschaft' as const,
      label: 'Eigenschaften',
      render: (s: Sorte) => (
        <div className="flex flex-wrap gap-1">
          {s.eigenschaft.slice(0, 2).map((e, i) => (
            <Badge key={i} variant="outline">{e}</Badge>
          ))}
          {s.eigenschaft.length > 2 && <Badge variant="secondary">+{s.eigenschaft.length - 2}</Badge>}
        </div>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Sorte) => (
        <Badge variant={s.status === 'aktiv' ? 'outline' : 'secondary'}>
          {s.status === 'aktiv' ? 'Aktiv' : 'Auslaufend'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Sortenregister</h1>
          <p className="text-muted-foreground">Saatgut-Sorten</p>
        </div>
        <Button onClick={() => navigate('/agrar/saatgut/sorte/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Sorte
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
          <DataTable data={mockSorten} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
