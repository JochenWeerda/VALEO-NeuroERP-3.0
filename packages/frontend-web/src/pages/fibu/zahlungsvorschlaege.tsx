import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Calendar, CheckCircle, Search, TrendingDown } from 'lucide-react'

type Zahlungsvorschlag = {
  id: string
  rechnungsNr: string
  lieferant: string
  betrag: number
  faelligAm: string
  skonto: number
  skontoBis: string
  vorschlag: 'skonto' | 'faellig' | 'spaeter'
  prioritaet: number
}

const mockVorschlaege: Zahlungsvorschlag[] = [
  {
    id: '1',
    rechnungsNr: 'ER-2025-0001',
    lieferant: 'Saatgut AG',
    betrag: 25000.0,
    faelligAm: '2025-11-07',
    skonto: 2,
    skontoBis: '2025-10-18',
    vorschlag: 'skonto',
    prioritaet: 1,
  },
  {
    id: '2',
    rechnungsNr: 'ER-2025-0004',
    lieferant: 'Technik GmbH',
    betrag: 8900.0,
    faelligAm: '2025-10-20',
    skonto: 3,
    skontoBis: '2025-10-15',
    vorschlag: 'skonto',
    prioritaet: 2,
  },
  {
    id: '3',
    rechnungsNr: 'ER-2025-0003',
    lieferant: 'Agrar-Handel Nord',
    betrag: 12200.0,
    faelligAm: '2025-11-09',
    skonto: 0,
    skontoBis: '',
    vorschlag: 'faellig',
    prioritaet: 3,
  },
]

const vorschlagVariantMap: Record<Zahlungsvorschlag['vorschlag'], 'default' | 'secondary' | 'outline'> = {
  skonto: 'default',
  faellig: 'secondary',
  spaeter: 'outline',
}

const vorschlagLabelMap: Record<Zahlungsvorschlag['vorschlag'], string> = {
  skonto: 'Skonto nutzen',
  faellig: 'Fälligkeitstermin',
  spaeter: 'Später zahlen',
}

export default function ZahlungsvorschlaegePage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const filteredVorschlaege = mockVorschlaege.filter((vorschlag) =>
    vorschlag.rechnungsNr.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vorschlag.lieferant.toLowerCase().includes(searchTerm.toLowerCase())
  )

  function toggleSelect(id: string): void {
    setSelected((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const gesamtBetrag = filteredVorschlaege
    .filter((v) => selected.has(v.id))
    .reduce((sum, v) => sum + v.betrag, 0)

  const skontoErsparnis = filteredVorschlaege
    .filter((v) => selected.has(v.id) && v.skonto > 0)
    .reduce((sum, v) => sum + (v.betrag * v.skonto) / 100, 0)

  const columns = [
    {
      key: 'select' as const,
      label: '',
      render: (vorschlag: Zahlungsvorschlag) => (
        <input
          type="checkbox"
          checked={selected.has(vorschlag.id)}
          onChange={() => toggleSelect(vorschlag.id)}
          className="h-4 w-4"
        />
      ),
    },
    {
      key: 'prioritaet' as const,
      label: '#',
      render: (vorschlag: Zahlungsvorschlag) => (
        <span className="text-sm font-semibold">{vorschlag.prioritaet}</span>
      ),
    },
    {
      key: 'rechnungsNr' as const,
      label: 'Rechnung',
      render: (vorschlag: Zahlungsvorschlag) => (
        <div>
          <div className="font-medium">{vorschlag.rechnungsNr}</div>
          <div className="text-sm text-muted-foreground">{vorschlag.lieferant}</div>
        </div>
      ),
    },
    {
      key: 'betrag' as const,
      label: 'Betrag',
      render: (vorschlag: Zahlungsvorschlag) => (
        <span className="font-semibold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(vorschlag.betrag)}
        </span>
      ),
    },
    {
      key: 'skonto' as const,
      label: 'Skonto',
      render: (vorschlag: Zahlungsvorschlag) =>
        vorschlag.skonto > 0 ? (
          <div className="text-sm">
            <div className="font-semibold text-green-600">{vorschlag.skonto}%</div>
            <div className="text-muted-foreground">
              bis {new Date(vorschlag.skontoBis).toLocaleDateString('de-DE')}
            </div>
          </div>
        ) : (
          <span className="text-sm text-muted-foreground">-</span>
        ),
    },
    {
      key: 'ersparnis' as const,
      label: 'Ersparnis',
      render: (vorschlag: Zahlungsvorschlag) =>
        vorschlag.skonto > 0 ? (
          <span className="font-semibold text-green-600">
            {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
              (vorschlag.betrag * vorschlag.skonto) / 100
            )}
          </span>
        ) : (
          <span className="text-sm text-muted-foreground">-</span>
        ),
    },
    {
      key: 'faelligAm' as const,
      label: 'Fällig am',
      render: (vorschlag: Zahlungsvorschlag) => (
        <span className="flex items-center gap-1 text-sm">
          <Calendar className="h-4 w-4" />
          {new Date(vorschlag.faelligAm).toLocaleDateString('de-DE')}
        </span>
      ),
    },
    {
      key: 'vorschlag' as const,
      label: 'Empfehlung',
      render: (vorschlag: Zahlungsvorschlag) => (
        <Badge variant={vorschlagVariantMap[vorschlag.vorschlag]}>
          {vorschlagLabelMap[vorschlag.vorschlag]}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Zahlungsvorschläge</h1>
          <p className="text-muted-foreground">Skonto-optimierte Zahlungsplanung</p>
        </div>
        <Button disabled={selected.size === 0}>
          Zahlungslauf erstellen ({selected.size})
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ausgewählter Betrag</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtBetrag)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Skonto-Ersparnis</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold text-green-600">
                {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
                  skontoErsparnis
                )}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Anzahl Zahlungen</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{selected.size}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Filter & Suche</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Suche nach Rechnung oder Lieferant..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" onClick={() => setSelected(new Set(filteredVorschlaege.map((v) => v.id)))}>
              Alle auswählen
            </Button>
            <Button variant="outline" onClick={() => setSelected(new Set())}>
              Auswahl aufheben
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredVorschlaege} columns={columns} />
          <div className="mt-4 text-sm text-muted-foreground">
            {filteredVorschlaege.length} Vorschlag/Vorschläge • {selected.size} ausgewählt
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
