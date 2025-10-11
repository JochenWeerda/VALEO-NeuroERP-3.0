import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { AlertTriangle, Plus } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

type ENNIMeldung = {
  id: string
  typ: 'DBE' | 'DdD' | '170-N'
  betrieb: string
  vvvo: string
  datum: string
  status: 'entwurf' | 'eingereicht' | 'bestaetigt'
  naehrstoffe: {
    n: number
    p: number
    k: number
  }
}

const mockENNI: ENNIMeldung[] = [
  { id: '1', typ: 'DBE', betrieb: 'Landwirtschaft Müller', vvvo: '03-276-1234', datum: '2025-10-01', status: 'bestaetigt', naehrstoffe: { n: 180, p: 60, k: 120 } },
  { id: '2', typ: 'DdD', betrieb: 'Hofgut Weber', vvvo: '03-276-5678', datum: '2025-09-15', status: 'eingereicht', naehrstoffe: { n: 220, p: 80, k: 150 } },
]

export default function ENNIMeldungenPage(): JSX.Element {
  const navigate = useNavigate()

  const columns = [
    { key: 'typ' as const, label: 'Typ', render: (m: ENNIMeldung) => <Badge variant="outline">{m.typ}</Badge> },
    { key: 'betrieb' as const, label: 'Betrieb' },
    { key: 'vvvo' as const, label: 'VVVO-Nr', render: (m: ENNIMeldung) => <span className="font-mono">{m.vvvo}</span> },
    { key: 'datum' as const, label: 'Datum', render: (m: ENNIMeldung) => new Date(m.datum).toLocaleDateString('de-DE') },
    {
      key: 'naehrstoffe' as const,
      label: 'N-P-K (kg/ha)',
      render: (m: ENNIMeldung) => (
        <div className="flex gap-2 font-mono text-xs">
          <span className="text-blue-600">{m.naehrstoffe.n}</span> -
          <span className="text-orange-600">{m.naehrstoffe.p}</span> -
          <span className="text-green-600">{m.naehrstoffe.k}</span>
        </div>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (m: ENNIMeldung) => (
        <Badge variant={m.status === 'bestaetigt' ? 'outline' : m.status === 'eingereicht' ? 'secondary' : 'default'}>
          {m.status === 'bestaetigt' ? 'Bestätigt' : m.status === 'eingereicht' ? 'Eingereicht' : 'Entwurf'}
        </Badge>
      ),
    },
  ]

  const offen = mockENNI.filter((m) => m.status === 'entwurf').length

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">ENNI-Meldungen</h1>
          <p className="text-muted-foreground">Niedersachsen Wirtschaftsdünger (DBE/DdD/170-N)</p>
        </div>
        <Button onClick={() => navigate('/compliance/enni-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Meldung
        </Button>
      </div>

      {offen > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{offen} Meldung(en) noch nicht eingereicht!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Meldungen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockENNI.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bestätigt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockENNI.filter((m) => m.status === 'bestaetigt').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Eingereicht</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{mockENNI.filter((m) => m.status === 'eingereicht').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Entwurf</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{offen}</span>
          </CardContent>
        </Card>
      </div>

      <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
        <p className="font-semibold">📋 ENNI-Portal Niedersachsen</p>
        <p className="mt-1">Elektronische Erfassung von Nährstoffströmen • Meldepflicht für Händler und Betriebe</p>
        <p className="mt-1">Fristen: DBE (30.04.), DdD (31.05.), 170-N (31.12.)</p>
      </div>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockENNI} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
