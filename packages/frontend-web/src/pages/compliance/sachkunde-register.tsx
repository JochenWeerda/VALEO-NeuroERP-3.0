import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, Award, FileDown, Plus, Search } from 'lucide-react'

type Sachkundenachweis = {
  id: string
  kunde: string
  kundennr: string
  nachweisNr: string
  ausstellungsdatum: string
  gueltigBis: string
  ausstellendeStelle: string
  status: 'gueltig' | 'ablaufend' | 'abgelaufen'
}

const mockSachkunde: Sachkundenachweis[] = [
  { id: '1', kunde: 'Landwirtschaft Müller', kundennr: 'K-10023', nachweisNr: 'SK-NDS-2022-4567', ausstellungsdatum: '2022-03-15', gueltigBis: '2025-03-15', ausstellendeStelle: 'LWK Niedersachsen', status: 'ablaufend' },
  { id: '2', kunde: 'Hofgut Weber', kundennr: 'K-10045', nachweisNr: 'SK-NDS-2023-8901', ausstellungsdatum: '2023-06-20', gueltigBis: '2026-06-20', ausstellendeStelle: 'LWK Niedersachsen', status: 'gueltig' },
]

export default function SachkundeRegisterPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const ablaufend = mockSachkunde.filter((s) => {
    const ablauf = new Date(s.gueltigBis)
    const warnung = new Date()
    warnung.setMonth(warnung.getMonth() + 3) // 3 Monate Vorlauf
    return ablauf <= warnung && ablauf >= new Date()
  }).length

  const columns = [
    {
      key: 'kunde' as const,
      label: 'Kunde',
      render: (s: Sachkundenachweis) => (
        <button onClick={() => navigate(`/verkauf/kunden-stamm/${s.id}`)} className="font-medium text-blue-600 hover:underline">
          {s.kunde}
        </button>
      ),
    },
    { key: 'kundennr' as const, label: 'Kd-Nr', render: (s: Sachkundenachweis) => <span className="font-mono text-sm">{s.kundennr}</span> },
    { key: 'nachweisNr' as const, label: 'Nachweis-Nr', render: (s: Sachkundenachweis) => <span className="font-mono">{s.nachweisNr}</span> },
    {
      key: 'gueltigBis' as const,
      label: 'Gültig bis',
      render: (s: Sachkundenachweis) => {
        const ablauf = new Date(s.gueltigBis)
        const ablaufend = ablauf <= new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
        return (
          <span className={ablaufend ? 'font-semibold text-orange-600' : ''}>
            {ablauf.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    { key: 'ausstellendeStelle' as const, label: 'Ausgestellt von' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Sachkundenachweis) => (
        <Badge variant={s.status === 'gueltig' ? 'outline' : s.status === 'ablaufend' ? 'secondary' : 'destructive'}>
          {s.status === 'gueltig' ? 'Gültig' : s.status === 'ablaufend' ? 'Läuft ab' : 'Abgelaufen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">PSM-Sachkunde-Register</h1>
          <p className="text-muted-foreground">Sachkundenachweis nach § 9 PflSchG</p>
        </div>
        <Button onClick={() => navigate('/compliance/sachkunde-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Nachweis erfassen
        </Button>
      </div>

      {ablaufend > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ablaufend} Nachweis(e) läuft/laufen in den nächsten 3 Monaten ab!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="rounded-lg bg-orange-50 p-4 text-sm text-orange-900">
        <div className="flex items-center gap-2">
          <Award className="h-4 w-4" />
          <p className="font-semibold">Verkaufsvoraussetzung PSM</p>
        </div>
        <p className="mt-1">
          Sachkundenachweis Pflicht für Anwender • Gültigkeit: 3 Jahre • Bei Verkauf an Privatpersonen/Betriebe prüfen!
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Nachweise Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockSachkunde.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gültig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockSachkunde.filter((s) => s.status === 'gueltig').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Läuft ab (3 Mon.)</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{ablaufend}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgelaufen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{mockSachkunde.filter((s) => s.status === 'abgelaufen').length}</span>
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
              <Input placeholder="Suche Kunde oder Nachweis-Nr..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
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
          <DataTable data={mockSachkunde} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
