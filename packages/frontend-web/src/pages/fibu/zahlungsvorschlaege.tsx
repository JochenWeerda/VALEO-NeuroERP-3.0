import { useState } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { DataTable } from '@/components/ui/data-table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Calendar, CheckCircle, Search, TrendingDown } from 'lucide-react'
import { useZahlungsvorschlaege, type Zahlungsvorschlag } from '@/lib/api/fibu'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { normalizeOperationalStatus } from '@/lib/operational-status'

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
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const { data: items, isLoading } = useZahlungsvorschlaege()

  const handleZahlungslaufErstellen = () => {
    if (selected.size === 0) return
    navigate('/fibu/zahlungslaeufe')
  }

  if (isLoading) return (
    <div className="p-3 md:p-6 space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-[400px] w-full" />
    </div>
  )

  const list = items ?? []

  const filteredVorschlaege = list.filter((vorschlag) =>
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
  const skontoFaelle = filteredVorschlaege.filter((item) => item.skonto > 0).length
  const operationalStatus = normalizeOperationalStatus(selected.size > 0 ? 'wartet_auf_mensch' : skontoFaelle > 0 ? 'in_pruefung' : 'offen')
  const contextSections = [
    {
      title: 'Vorgang',
      items: [
        { label: 'Vorschlaege gesamt', value: String(list.length) },
        { label: 'Gefiltert', value: String(filteredVorschlaege.length) },
        { label: 'Skonto-Faelle', value: String(skontoFaelle) },
      ],
    },
    {
      title: 'Wirtschaftslage',
      items: [
        {
          label: 'Ausgewaehlter Betrag',
          value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(gesamtBetrag),
        },
        {
          label: 'Skonto-Ersparnis',
          value: new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(skontoErsparnis),
        },
      ],
    },
    {
      title: 'Governance',
      items: [
        { label: 'Naechste Aktion', value: selected.size > 0 ? 'Zahlungslauf erstellen' : 'Skonto- und Faelligkeitslogik pruefen' },
        { label: 'Blocker', value: selected.size > 0 ? 'Auswahl wartet auf Zahlungsfreigabe' : 'Kein akuter Blocker' },
      ],
    },
  ]
  const timelineItems = [
    { label: 'Vorschlagsliste geladen', detail: `${list.length} Zahlungsvorschlaege verfuegbar` },
    skontoFaelle > 0 ? { label: 'Skonto-Potenzial erkannt', detail: `${skontoFaelle} Faelle mit Einsparung` } : null,
    selected.size > 0 ? { label: 'Selektion aktiv', detail: `${selected.size} Position(en) fuer Zahlungslauf markiert` } : null,
  ].filter((item): item is { label: string; detail: string } => item !== null)

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
    <div className="space-y-4 p-3 md:p-6">
      <OperationalCaseHeader
        title="Zahlungsvorschlaege"
        description="Skonto- und faelligkeitsorientierte Zahlungsplanung fuer Kreditoren."
        status={operationalStatus}
        owner="Kreditorenbuchhaltung"
        blocker={selected.size > 0 ? 'Auswahl ist noch nicht in einen Zahlungslauf ueberfuehrt.' : null}
        nextAction={selected.size > 0 ? 'Zahlungslauf erstellen' : 'Faellige und skontofaehige Rechnungen selektieren'}
        caseLabel="Zahlungsplanung"
        tags={['FIBU', 'Kreditoren']}
      />
      <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
        <OperationalTimeline title="Verlauf" items={timelineItems} />
        <OperationalContextPanel sections={contextSections} />
      </div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Zahlungsvorschläge</h1>
          <p className="text-muted-foreground">Skonto-optimierte Zahlungsplanung</p>
        </div>
        <Button disabled={selected.size === 0} onClick={handleZahlungslaufErstellen}>
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
