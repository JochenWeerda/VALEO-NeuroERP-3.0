import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Calendar, Mail, Phone, Plus, Search, Users } from 'lucide-react'

type Aktivitaet = {
  id: string
  typ: 'termin' | 'anruf' | 'email' | 'notiz'
  titel: string
  kunde: string
  ansprechpartner: string
  datum: string
  status: 'geplant' | 'abgeschlossen' | 'ueberfaellig'
  zustaendig: string
}

const mockAktivitaeten: Aktivitaet[] = [
  { id: '1', typ: 'termin', titel: 'Jahresgespräch Düngeplanung', kunde: 'Landwirtschaft Müller', ansprechpartner: 'Hans Müller', datum: '2025-10-15', status: 'geplant', zustaendig: 'Max Mustermann' },
  { id: '2', typ: 'anruf', titel: 'Rückruf zu PSM-Bestellung', kunde: 'Hofgut Weber', ansprechpartner: 'Maria Weber', datum: '2025-10-10', status: 'ueberfaellig', zustaendig: 'Anna Schmidt' },
  { id: '3', typ: 'email', titel: 'Angebot Saatgut 2026', kunde: 'Agrar Schmidt GmbH', ansprechpartner: 'Thomas Schmidt', datum: '2025-10-12', status: 'abgeschlossen', zustaendig: 'Max Mustermann' },
]

export default function AktivitaetenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const columns = [
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (a: Aktivitaet) => {
        const icons = { termin: Calendar, anruf: Phone, email: Mail, notiz: Users }
        const Icon = icons[a.typ]
        return (
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4" />
            <span className="capitalize">{a.typ}</span>
          </div>
        )
      },
    },
    {
      key: 'titel' as const,
      label: 'Titel',
      render: (a: Aktivitaet) => (
        <button onClick={() => navigate(`/crm/aktivitaet/${a.id}`)} className="font-medium text-blue-600 hover:underline">
          {a.titel}
        </button>
      ),
    },
    { key: 'kunde' as const, label: 'Kunde' },
    { key: 'ansprechpartner' as const, label: 'Ansprechpartner' },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (a: Aktivitaet) => {
        const ueberfaellig = new Date(a.datum) < new Date() && a.status !== 'abgeschlossen'
        return (
          <span className={ueberfaellig ? 'font-semibold text-red-600' : ''}>
            {new Date(a.datum).toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    { key: 'zustaendig' as const, label: 'Zuständig' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (a: Aktivitaet) => (
        <Badge variant={a.status === 'abgeschlossen' ? 'outline' : a.status === 'ueberfaellig' ? 'destructive' : 'secondary'}>
          {a.status === 'abgeschlossen' ? 'Abgeschlossen' : a.status === 'ueberfaellig' ? 'Überfällig' : 'Geplant'}
        </Badge>
      ),
    },
  ]

  const ueberfaellig = mockAktivitaeten.filter((a) => a.status === 'ueberfaellig').length

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">CRM-Aktivitäten</h1>
          <p className="text-muted-foreground">Termine, Anrufe, E-Mails & Notizen</p>
        </div>
        <Button onClick={() => navigate('/crm/aktivitaet-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Aktivität
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Aktivitäten Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockAktivitaeten.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Geplant</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-blue-600">{mockAktivitaeten.filter((a) => a.status === 'geplant').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Überfällig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{ueberfaellig}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockAktivitaeten.filter((a) => a.status === 'abgeschlossen').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche Aktivität, Kunde..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline">Nur Meine</Button>
            <Button variant="outline">Nur Überfällige</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockAktivitaeten} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
