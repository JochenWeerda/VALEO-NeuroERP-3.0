import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { AlertTriangle, Award, FileDown, Plus, Search } from 'lucide-react'

type Schulung = {
  id: string
  mitarbeiter: string
  personalnr: string
  thema: string
  typ: 'PSM' | 'Gefahrstoffe' | 'Gabelstapler' | 'Erste Hilfe' | 'Brandschutz' | 'Arbeitssicherheit'
  datum: string
  dauer: number
  schulungsleiter: string
  zertifikatNr?: string
  gueltigBis?: string
  status: 'gueltig' | 'ablaufend' | 'abgelaufen'
}

const mockSchulungen: Schulung[] = [
  {
    id: '1',
    mitarbeiter: 'Hans Müller',
    personalnr: 'P-001',
    thema: 'PSM-Sachkunde Fortbildung',
    typ: 'PSM',
    datum: '2024-03-15',
    dauer: 8,
    schulungsleiter: 'LWK Niedersachsen',
    zertifikatNr: 'SK-NDS-2024-123',
    gueltigBis: '2027-03-15',
    status: 'gueltig',
  },
  {
    id: '2',
    mitarbeiter: 'Maria Schmidt',
    personalnr: 'P-002',
    thema: 'Gabelstapler-Führerschein',
    typ: 'Gabelstapler',
    datum: '2023-01-20',
    dauer: 16,
    schulungsleiter: 'TÜV Nord',
    zertifikatNr: 'TÜV-GS-2023-456',
    gueltigBis: '2028-01-20',
    status: 'gueltig',
  },
  {
    id: '3',
    mitarbeiter: 'Thomas Weber',
    personalnr: 'P-003',
    thema: 'Erste Hilfe Grundkurs',
    typ: 'Erste Hilfe',
    datum: '2023-06-10',
    dauer: 8,
    schulungsleiter: 'DRK Rotenburg',
    gueltigBis: '2025-06-10',
    status: 'ablaufend',
  },
]

export default function SchulungenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const ablaufend = mockSchulungen.filter((s) => {
    if (!s.gueltigBis) return false
    const ablauf = new Date(s.gueltigBis)
    const warnung = new Date()
    warnung.setMonth(warnung.getMonth() + 2) // 2 Monate Vorlauf
    return ablauf <= warnung && ablauf >= new Date()
  }).length

  const columns = [
    {
      key: 'mitarbeiter' as const,
      label: 'Mitarbeiter',
      render: (s: Schulung) => (
        <div>
          <button onClick={() => navigate(`/personal/mitarbeiter/${s.id}`)} className="font-medium text-blue-600 hover:underline">
            {s.mitarbeiter}
          </button>
          <div className="text-xs text-muted-foreground font-mono">{s.personalnr}</div>
        </div>
      ),
    },
    { key: 'typ' as const, label: 'Typ', render: (s: Schulung) => <Badge variant="outline">{s.typ}</Badge> },
    { key: 'thema' as const, label: 'Schulungsthema' },
    { key: 'datum' as const, label: 'Datum', render: (s: Schulung) => new Date(s.datum).toLocaleDateString('de-DE') },
    { key: 'dauer' as const, label: 'Dauer', render: (s: Schulung) => `${s.dauer}h` },
    { key: 'schulungsleiter' as const, label: 'Schulungsleiter' },
    {
      key: 'zertifikatNr' as const,
      label: 'Zertifikat',
      render: (s: Schulung) => (s.zertifikatNr ? <span className="font-mono text-sm">{s.zertifikatNr}</span> : <span className="text-muted-foreground">–</span>),
    },
    {
      key: 'gueltigBis' as const,
      label: 'Gültig bis',
      render: (s: Schulung) => {
        if (!s.gueltigBis) return <span className="text-muted-foreground">–</span>
        const ablauf = new Date(s.gueltigBis)
        const ablaufend = ablauf <= new Date(Date.now() + 60 * 24 * 60 * 60 * 1000)
        return (
          <span className={ablaufend ? 'font-semibold text-orange-600' : ''}>
            {ablauf.toLocaleDateString('de-DE')}
          </span>
        )
      },
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Schulung) => (
        <Badge variant={s.status === 'gueltig' ? 'outline' : s.status === 'ablaufend' ? 'secondary' : 'destructive'}>
          {s.status === 'gueltig' ? 'Gültig' : s.status === 'ablaufend' ? 'Läuft ab' : 'Abgelaufen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Award className="h-10 w-10 text-primary" />
          <div>
            <h1 className="text-3xl font-bold">Schulungsnachweise</h1>
            <p className="text-muted-foreground">Mitarbeiter-Qualifikationen & Zertifikate</p>
          </div>
        </div>
        <Button onClick={() => navigate('/personal/schulung-neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Schulung erfassen
        </Button>
      </div>

      {ablaufend > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ablaufend} Schulung(en) laufen in den nächsten 2 Monaten ab!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="rounded-lg bg-blue-50 p-4 text-sm text-blue-900">
        <div className="flex items-center gap-2">
          <Award className="h-4 w-4" />
          <p className="font-semibold">Pflicht-Schulungen Landhandel</p>
        </div>
        <p className="mt-1">
          <strong>PSM:</strong> § 9 PflSchG (Sachkunde) • <strong>Gabelstapler:</strong> DGUV Vorschrift 68 •
          <strong>Erste Hilfe:</strong> DGUV Vorschrift 1 • <strong>Gefahrstoffe:</strong> GefStoffV § 14
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Schulungen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{mockSchulungen.length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gültig</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{mockSchulungen.filter((s) => s.status === 'gueltig').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Laufen ab (60 Tage)</CardTitle>
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
            <span className="text-2xl font-bold text-red-600">{mockSchulungen.filter((s) => s.status === 'abgelaufen').length}</span>
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
              <Input placeholder="Suche Mitarbeiter, Thema..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline">Nur PSM</Button>
            <Button variant="outline">Nur ablaufende</Button>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={mockSchulungen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
