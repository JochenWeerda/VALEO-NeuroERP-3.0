import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Plus, Search } from 'lucide-react'

type PSM = {
  id: string
  mittel: string
  wirkstoff: string
  kulturen: string[]
  zulassungBis: string
  status: 'aktiv' | 'auslaufend' | 'widerrufen'
  erklaerungLandwirtStatus: string | null
}

const mockPSM: PSM[] = [
  {
    id: '1',
    mittel: 'Roundup PowerFlex',
    wirkstoff: 'Glyphosat 480 g/l',
    kulturen: ['Getreide', 'Mais', 'Raps'],
    zulassungBis: '2026-12-31',
    status: 'aktiv',
    erklaerungLandwirtStatus: null,
  },
  {
    id: '2',
    mittel: 'Fungisan Pro',
    wirkstoff: 'Tebuconazol 250 g/l',
    kulturen: ['Getreide', 'Raps'],
    zulassungBis: '2025-06-30',
    status: 'auslaufend',
    erklaerungLandwirtStatus: null,
  },
]

export default function PSMListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'mittel' as const,
      label: 'Mittel',
      render: (psm: PSM) => (
        <button
          onClick={() => navigate(`/agrar/psm/stamm/${psm.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {psm.mittel}
        </button>
      ),
    },
    {
      key: 'wirkstoff' as const,
      label: 'Wirkstoff',
    },
    {
      key: 'kulturen' as const,
      label: 'Kulturen',
      render: (psm: PSM) => (
        <div className="flex flex-wrap gap-1">
          {psm.kulturen.slice(0, 2).map((k, i) => (
            <Badge key={i} variant="outline">{k}</Badge>
          ))}
          {psm.kulturen.length > 2 && <Badge variant="secondary">+{psm.kulturen.length - 2}</Badge>}
        </div>
      ),
    },
    {
      key: 'zulassungBis' as const,
      label: 'Zulassung bis',
      render: (psm: PSM) => new Date(psm.zulassungBis).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (psm: PSM) => (
        <Badge variant={psm.status === 'aktiv' ? 'outline' : 'destructive'}>
          {psm.status === 'aktiv' ? 'Aktiv' : psm.status === 'auslaufend' ? 'Auslaufend' : 'Widerrufen'}
        </Badge>
      ),
    },
    {
      key: 'erklaerungLandwirtStatus' as const,
      label: 'Erklärung Landwirt',
      render: (psm: PSM) => {
        if (!psm.erklaerungLandwirtStatus) return <span className="text-muted-foreground">-</span>
        const statusColors = {
          'eingegangen': 'bg-yellow-100 text-yellow-800',
          'geprueft': 'bg-green-100 text-green-800',
          'abgelehnt': 'bg-red-100 text-red-800',
        }
        return (
          <Badge className={statusColors[psm.erklaerungLandwirtStatus as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'}>
            {psm.erklaerungLandwirtStatus === 'eingegangen' ? 'Eingegangen' :
             psm.erklaerungLandwirtStatus === 'geprueft' ? 'Geprüft' : 'Abgelehnt'}
          </Badge>
        )
      },
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Pflanzenschutzmittel</h1>
          <p className="text-muted-foreground">PSM-Stammdaten</p>
        </div>
        <Button onClick={() => navigate('/agrar/psm/stamm/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues PSM
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
              <Input
                placeholder="Suche nach Mittel oder Wirkstoff..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
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
          <DataTable data={mockPSM} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
