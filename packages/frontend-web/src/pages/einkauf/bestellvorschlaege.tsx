import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle, Clock, Search, ShoppingCart, TrendingUp } from 'lucide-react'

type Bestellvorschlag = {
  id: string
  artikel: string
  aktuellBestand: number
  mindestbestand: number
  vorschlagMenge: number
  lieferant: string
  preis: number
  lieferzeit: number
  prioritaet: 'hoch' | 'mittel' | 'niedrig'
  grund: string
}

const mockVorschlaege: Bestellvorschlag[] = [
  {
    id: '1',
    artikel: 'Weizen Qualität A',
    aktuellBestand: 5,
    mindestbestand: 50,
    vorschlagMenge: 100,
    lieferant: 'Saatgut AG',
    preis: 250.0,
    lieferzeit: 7,
    prioritaet: 'hoch',
    grund: 'Unterschreitung Mindestbestand',
  },
  {
    id: '2',
    artikel: 'NPK-Dünger 15-15-15',
    aktuellBestand: 20,
    mindestbestand: 30,
    vorschlagMenge: 50,
    lieferant: 'Dünger GmbH',
    preis: 185.0,
    lieferzeit: 5,
    prioritaet: 'mittel',
    grund: 'Saisonale Nachfrage',
  },
  {
    id: '3',
    artikel: 'Glyphosat 360g',
    aktuellBestand: 80,
    mindestbestand: 50,
    vorschlagMenge: 30,
    lieferant: 'Agrar-Handel Nord',
    preis: 122.0,
    lieferzeit: 10,
    prioritaet: 'niedrig',
    grund: 'Prognose Absatzsteigerung',
  },
]

const prioritaetVariantMap: Record<Bestellvorschlag['prioritaet'], 'default' | 'secondary' | 'destructive'> = {
  hoch: 'destructive',
  mittel: 'secondary',
  niedrig: 'default',
}

const prioritaetLabelMap: Record<Bestellvorschlag['prioritaet'], string> = {
  hoch: 'Hoch',
  mittel: 'Mittel',
  niedrig: 'Niedrig',
}

export default function BestellvorschlaegePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [prioritaetFilter, setPriorityFilter] = useState<Bestellvorschlag['prioritaet'] | 'alle'>('alle')
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const filteredVorschlaege = mockVorschlaege.filter((vorschlag) => {
    const matchesSearch =
      vorschlag.artikel.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vorschlag.lieferant.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesPriority = prioritaetFilter === 'alle' || vorschlag.prioritaet === prioritaetFilter
    return matchesSearch && matchesPriority
  })

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

  function handleBestellungenErstellen(): void {
    console.log('Erstelle Bestellungen für:', Array.from(selected))
    navigate('/einkauf/bestellung-anlegen')
  }

  const gesamtWert = filteredVorschlaege
    .filter((v) => selected.has(v.id))
    .reduce((sum, v) => sum + v.vorschlagMenge * v.preis, 0)

  const columns = [
    {
      key: 'select' as const,
      label: '',
      render: (vorschlag: Bestellvorschlag) => (
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
      label: 'Priorität',
      render: (vorschlag: Bestellvorschlag) => (
        <Badge variant={prioritaetVariantMap[vorschlag.prioritaet]}>
          {prioritaetLabelMap[vorschlag.prioritaet]}
        </Badge>
      ),
    },
    {
      key: 'artikel' as const,
      label: 'Artikel',
      render: (vorschlag: Bestellvorschlag) => (
        <div>
          <div className="font-medium">{vorschlag.artikel}</div>
          <div className="text-sm text-muted-foreground">{vorschlag.grund}</div>
        </div>
      ),
    },
    {
      key: 'bestand' as const,
      label: 'Bestand',
      render: (vorschlag: Bestellvorschlag) => (
        <div className="text-sm">
          <div className={vorschlag.aktuellBestand < vorschlag.mindestbestand ? 'text-red-600 font-semibold' : ''}>
            Aktuell: {vorschlag.aktuellBestand}
          </div>
          <div className="text-muted-foreground">Mindest: {vorschlag.mindestbestand}</div>
        </div>
      ),
    },
    {
      key: 'vorschlagMenge' as const,
      label: 'Vorschlag',
      render: (vorschlag: Bestellvorschlag) => (
        <span className="font-semibold">{vorschlag.vorschlagMenge} t</span>
      ),
    },
    {
      key: 'lieferant' as const,
      label: 'Lieferant',
    },
    {
      key: 'preis' as const,
      label: 'Preis/Einheit',
      render: (vorschlag: Bestellvorschlag) =>
        new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(vorschlag.preis),
    },
    {
      key: 'gesamtpreis' as const,
      label: 'Gesamtpreis',
      render: (vorschlag: Bestellvorschlag) => (
        <span className="font-semibold">
          {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(
            vorschlag.vorschlagMenge * vorschlag.preis
          )}
        </span>
      ),
    },
    {
      key: 'lieferzeit' as const,
      label: 'Lieferzeit',
      render: (vorschlag: Bestellvorschlag) => (
        <span className="flex items-center gap-1 text-sm">
          <Clock className="h-4 w-4" />
          {vorschlag.lieferzeit} Tage
        </span>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bestellvorschläge</h1>
          <p className="text-muted-foreground">AI-gestützte Bestellempfehlungen</p>
        </div>
        <Button
          onClick={handleBestellungenErstellen}
          disabled={selected.size === 0}
          className="gap-2"
        >
          <ShoppingCart className="h-4 w-4" />
          {selected.size} Bestellung(en) erstellen
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Vorschläge Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{filteredVorschlaege.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Ausgewählt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-2xl font-bold">{selected.size}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Bestellwert (ausgewählt)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtWert)}
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
                placeholder="Suche nach Artikel oder Lieferant..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={prioritaetFilter}
              onChange={(e) => setPriorityFilter(e.target.value as Bestellvorschlag['prioritaet'] | 'alle')}
              className="rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="alle">Alle Prioritäten</option>
              <option value="hoch">Hoch</option>
              <option value="mittel">Mittel</option>
              <option value="niedrig">Niedrig</option>
            </select>
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
