/**
 * Maßnahmen-Dokumentation - Mandantenfähiges Spritztagebuch / Feldbuch
 * 
 * Features:
 * - Multi-Tenant: Maßnahmen für verschiedene Kunden dokumentieren
 * - Compliance: PSM-Dokumentation gemäß Pflanzenschutzgesetz
 * - Dienstleister-Modus: Als Dienstleister Maßnahmen für Kunden erfassen
 */

import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  CalendarDays, 
  FileDown, 
  Plus, 
  Search, 
  Building2,
  Droplets,
  Bug,
  Wheat,
  Tractor,
  AlertTriangle,
  CheckCircle,
  Filter,
  Clock,
  User,
  FileText,
  Info
} from 'lucide-react'

// Types
type Kunde = {
  id: string
  name: string
  betriebsnummer: string
}

type MassnahmeTyp = 'Aussaat' | 'Düngung' | 'PSM' | 'Ernte' | 'Bodenbearbeitung' | 'Sonstiges'

type Massnahme = {
  id: string
  datum: string
  uhrzeit?: string
  schlagId: string
  schlagName: string
  kundeId: string
  kundeName: string
  typ: MassnahmeTyp
  mittel: string
  mittelId?: string
  menge: number
  einheit: string
  flaeche: number // behandelte Fläche in ha
  anwender?: string
  geraet?: string
  windgeschwindigkeit?: number // km/h
  temperatur?: number // °C
  anwendungshinweise?: string
  auflagen?: string[]
  compliant: boolean
  exportiert: boolean
}

// Mock-Daten für Kunden
const mockKunden: Kunde[] = [
  { id: 'k1', name: 'Schmidt Landwirtschaft GbR', betriebsnummer: 'DE-NI-030012' },
  { id: 'k2', name: 'Müller Agrar KG', betriebsnummer: 'DE-NI-030045' },
  { id: 'k3', name: 'Bauer Hof Meier', betriebsnummer: 'DE-BY-094015' },
  { id: 'all', name: 'Alle Kunden', betriebsnummer: '' },
]

// Mock-Daten für Maßnahmen mit Mandantenzuordnung
const mockMassnahmen: Massnahme[] = [
  { 
    id: '1', 
    datum: '2025-11-15', 
    uhrzeit: '08:30',
    schlagId: '1',
    schlagName: 'Nordfeld 1', 
    kundeId: 'k1',
    kundeName: 'Schmidt Landwirtschaft GbR',
    typ: 'Düngung', 
    mittel: 'ENTEC 26', 
    menge: 350, 
    einheit: 'kg/ha',
    flaeche: 12.5,
    anwender: 'Max Mustermann',
    geraet: 'Amazone ZA-M 1500',
    compliant: true,
    exportiert: false
  },
  { 
    id: '2', 
    datum: '2025-11-14', 
    uhrzeit: '14:00',
    schlagId: '2',
    schlagName: 'Südacker', 
    kundeId: 'k2',
    kundeName: 'Müller Agrar KG',
    typ: 'PSM', 
    mittel: 'Roundup PowerFlex', 
    mittelId: 'PSM-00456',
    menge: 3.5, 
    einheit: 'l/ha',
    flaeche: 8.3,
    anwender: 'Hans Schmidt',
    geraet: 'Holder 24m Feldspritze',
    windgeschwindigkeit: 12,
    temperatur: 14,
    auflagen: ['NT101', 'NT102', 'NW605'],
    compliant: true,
    exportiert: true
  },
  { 
    id: '3', 
    datum: '2025-11-10', 
    uhrzeit: '07:00',
    schlagId: '1',
    schlagName: 'Nordfeld 1', 
    kundeId: 'k1',
    kundeName: 'Schmidt Landwirtschaft GbR',
    typ: 'Aussaat', 
    mittel: 'Winterweizen Asano', 
    menge: 180, 
    einheit: 'kg/ha',
    flaeche: 12.5,
    anwender: 'Max Mustermann',
    geraet: 'Amazone Cirrus 3001',
    compliant: true,
    exportiert: false
  },
  { 
    id: '4', 
    datum: '2025-11-08', 
    uhrzeit: '09:15',
    schlagId: '4',
    schlagName: 'Bergacker', 
    kundeId: 'k3',
    kundeName: 'Bauer Hof Meier',
    typ: 'PSM', 
    mittel: 'Gladio', 
    mittelId: 'PSM-00789',
    menge: 0.8, 
    einheit: 'l/ha',
    flaeche: 10.5,
    anwender: 'Peter Weber',
    geraet: 'Selbstfahrspritze Horsch',
    windgeschwindigkeit: 8,
    temperatur: 12,
    auflagen: ['NW601', 'NT103'],
    compliant: true,
    exportiert: false
  },
  { 
    id: '5', 
    datum: '2025-11-05', 
    uhrzeit: '10:30',
    schlagId: '3',
    schlagName: 'Wiesengrund', 
    kundeId: 'k1',
    kundeName: 'Schmidt Landwirtschaft GbR',
    typ: 'Bodenbearbeitung', 
    mittel: 'Grubber 3m', 
    menge: 1, 
    einheit: 'Durchgang',
    flaeche: 15.2,
    anwender: 'Max Mustermann',
    geraet: 'Lemken Karat 9',
    compliant: true,
    exportiert: false
  },
]

// API-Funktionen (simuliert)
async function fetchMassnahmen(_kundeId?: string): Promise<Massnahme[]> {
  await new Promise(resolve => setTimeout(resolve, 600))
  return mockMassnahmen
}

// Icon für Maßnahmentyp
function getMassnahmeIcon(typ: MassnahmeTyp) {
  switch (typ) {
    case 'Düngung': return <Droplets className="h-4 w-4 text-blue-600" />
    case 'PSM': return <Bug className="h-4 w-4 text-red-600" />
    case 'Aussaat': return <Wheat className="h-4 w-4 text-amber-600" />
    case 'Ernte': return <Wheat className="h-4 w-4 text-green-600" />
    case 'Bodenbearbeitung': return <Tractor className="h-4 w-4 text-brown-600" />
    default: return <CalendarDays className="h-4 w-4" />
  }
}

// Skeleton-Komponente
function MassnahmenSkeleton() {
  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-48" />
        </div>
        <Skeleton className="h-10 w-36" />
      </div>
      
      <div className="grid gap-4 md:grid-cols-4">
        {[1, 2, 3, 4].map(i => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent className="pt-6">
          {[1, 2, 3, 4, 5].map(i => (
            <Skeleton key={i} className="h-12 w-full mb-2" />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

export default function MassnahmenPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedKundeId, setSelectedKundeId] = useState<string>('all')
  const [filterTyp, setFilterTyp] = useState<string>('alle')
  const [activeTab, setActiveTab] = useState<string>('liste')

  // Daten laden
  const { data: massnahmen, isLoading } = useQuery({
    queryKey: ['massnahmen', selectedKundeId],
    queryFn: () => fetchMassnahmen(selectedKundeId)
  })

  // Gefilterte Maßnahmen
  const filteredMassnahmen = useMemo(() => {
    if (!massnahmen) return []
    
    return massnahmen.filter(m => {
      // Kundenfilter
      if (selectedKundeId !== 'all' && m.kundeId !== selectedKundeId) {
        return false
      }
      
      // Typfilter
      if (filterTyp !== 'alle' && m.typ !== filterTyp) {
        return false
      }
      
      // Suchfilter
      if (searchTerm) {
        const search = searchTerm.toLowerCase()
        return (
          m.schlagName.toLowerCase().includes(search) ||
          m.mittel.toLowerCase().includes(search) ||
          m.kundeName.toLowerCase().includes(search)
        )
      }
      
      return true
    })
  }, [massnahmen, selectedKundeId, filterTyp, searchTerm])

  // Statistiken
  const stats = useMemo(() => {
    const filtered = filteredMassnahmen
    const letzte7Tage = filtered.filter(m => {
      const datum = new Date(m.datum)
      const heute = new Date()
      const diffTage = Math.floor((heute.getTime() - datum.getTime()) / (1000 * 60 * 60 * 24))
      return diffTage <= 7
    })
    
    return {
      gesamt: filtered.length,
      letzte7Tage: letzte7Tage.length,
      duengungen: filtered.filter(m => m.typ === 'Düngung').length,
      psmAnwendungen: filtered.filter(m => m.typ === 'PSM').length,
      compliant: filtered.filter(m => m.compliant).length,
      nichtExportiert: filtered.filter(m => !m.exportiert).length
    }
  }, [filteredMassnahmen])

  // PSM-spezifische Maßnahmen für Spritztagebuch
  const psmMassnahmen = useMemo(() => {
    return filteredMassnahmen.filter(m => m.typ === 'PSM')
  }, [filteredMassnahmen])

  // Spalten-Definition
  const columns = [
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (m: Massnahme) => (
        <div>
          <div className="font-medium">{new Date(m.datum).toLocaleDateString('de-DE')}</div>
          {m.uhrzeit && <div className="text-xs text-muted-foreground">{m.uhrzeit} Uhr</div>}
        </div>
      ),
    },
    { 
      key: 'schlagName' as const, 
      label: 'Schlag',
      render: (m: Massnahme) => (
        <button 
          onClick={() => navigate(`/agrar/feldbuch/schlag/${m.schlagId}`)}
          className="text-blue-600 hover:underline"
        >
          {m.schlagName}
        </button>
      )
    },
    {
      key: 'typ' as const,
      label: 'Typ',
      render: (m: Massnahme) => (
        <div className="flex items-center gap-2">
          {getMassnahmeIcon(m.typ)}
          <Badge variant={m.typ === 'PSM' ? 'destructive' : 'outline'}>
            {m.typ}
          </Badge>
        </div>
      ),
    },
    { key: 'mittel' as const, label: 'Mittel' },
    { 
      key: 'menge' as const, 
      label: 'Menge', 
      render: (m: Massnahme) => `${m.menge} ${m.einheit}` 
    },
    {
      key: 'flaeche' as const,
      label: 'Fläche',
      render: (m: Massnahme) => `${m.flaeche.toFixed(2)} ha`
    },
    {
      key: 'kundeName' as const,
      label: 'Kunde',
      render: (m: Massnahme) => (
        <div className="flex items-center gap-2">
          <Building2 className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm">{m.kundeName}</span>
        </div>
      )
    },
    {
      key: 'compliant' as const,
      label: 'Status',
      render: (m: Massnahme) => (
        <div className="flex items-center gap-2">
          {m.compliant ? (
            <CheckCircle className="h-4 w-4 text-green-600" />
          ) : (
            <AlertTriangle className="h-4 w-4 text-amber-600" />
          )}
          {m.exportiert && <FileText className="h-4 w-4 text-blue-600" title="Exportiert" />}
        </div>
      )
    }
  ]

  // PSM-Spalten für Spritztagebuch
  const psmColumns = [
    {
      key: 'datum' as const,
      label: 'Datum/Zeit',
      render: (m: Massnahme) => (
        <div>
          <div className="font-medium">{new Date(m.datum).toLocaleDateString('de-DE')}</div>
          <div className="text-xs text-muted-foreground">{m.uhrzeit || '-'}</div>
        </div>
      ),
    },
    { key: 'schlagName' as const, label: 'Schlag' },
    { key: 'mittel' as const, label: 'Pflanzenschutzmittel' },
    { 
      key: 'menge' as const, 
      label: 'Aufwandmenge', 
      render: (m: Massnahme) => `${m.menge} ${m.einheit}` 
    },
    {
      key: 'flaeche' as const,
      label: 'Fläche (ha)',
      render: (m: Massnahme) => m.flaeche.toFixed(2)
    },
    {
      key: 'anwender' as const,
      label: 'Anwender',
      render: (m: Massnahme) => (
        <div className="flex items-center gap-1">
          <User className="h-3 w-3" />
          {m.anwender || '-'}
        </div>
      )
    },
    {
      key: 'windgeschwindigkeit' as const,
      label: 'Wetter',
      render: (m: Massnahme) => (
        <div className="text-sm">
          {m.windgeschwindigkeit && <div>{m.windgeschwindigkeit} km/h Wind</div>}
          {m.temperatur && <div>{m.temperatur}°C</div>}
        </div>
      )
    },
    {
      key: 'auflagen' as const,
      label: 'Auflagen',
      render: (m: Massnahme) => (
        <div className="flex flex-wrap gap-1">
          {m.auflagen?.map(a => (
            <Badge key={a} variant="outline" className="text-xs">{a}</Badge>
          ))}
        </div>
      )
    }
  ]

  // Ladezustand
  if (isLoading) {
    return <MassnahmenSkeleton />
  }

  return (
    <div className="space-y-4 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <CalendarDays className="h-8 w-8 text-blue-600" />
            Maßnahmen-Dokumentation
          </h1>
          <p className="text-muted-foreground">
            Spritztagebuch und Feldbuch-Dokumentation für Dienstleister
          </p>
        </div>
        <Button onClick={() => navigate('/agrar/feldbuch/massnahme/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Maßnahme
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-4 lg:grid-cols-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Letzte 7 Tage
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.letzte7Tage}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Droplets className="h-4 w-4 text-blue-600" />
              Düngungen
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.duengungen}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Bug className="h-4 w-4 text-red-600" />
              PSM-Anwendungen
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.psmAnwendungen}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              Compliant
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.compliant}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <FileDown className="h-4 w-4" />
              Nicht exportiert
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-amber-600">{stats.nichtExportiert}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.gesamt}</div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="liste">Alle Maßnahmen</TabsTrigger>
          <TabsTrigger value="spritztagebuch">
            <Bug className="h-4 w-4 mr-1" />
            Spritztagebuch
          </TabsTrigger>
          <TabsTrigger value="duengebilanz">
            <Droplets className="h-4 w-4 mr-1" />
            Düngung
          </TabsTrigger>
        </TabsList>

        <TabsContent value="liste" className="space-y-4">
          {/* Filter */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Filter
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                {/* Kundenauswahl */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Kunde</label>
                  <Select value={selectedKundeId} onValueChange={setSelectedKundeId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Kunde wählen..." />
                    </SelectTrigger>
                    <SelectContent>
                      {mockKunden.map(kunde => (
                        <SelectItem key={kunde.id} value={kunde.id}>
                          {kunde.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Typfilter */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Maßnahmentyp</label>
                  <Select value={filterTyp} onValueChange={setFilterTyp}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="alle">Alle Typen</SelectItem>
                      <SelectItem value="Düngung">Düngung</SelectItem>
                      <SelectItem value="PSM">PSM</SelectItem>
                      <SelectItem value="Aussaat">Aussaat</SelectItem>
                      <SelectItem value="Ernte">Ernte</SelectItem>
                      <SelectItem value="Bodenbearbeitung">Bodenbearbeitung</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Suchfeld */}
                <div className="md:col-span-2">
                  <label className="text-sm font-medium mb-2 block">Suche</label>
                  <div className="flex gap-4">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input 
                        placeholder="Schlag, Mittel, Kunde..." 
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
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Datentabelle */}
          <Card>
            <CardContent className="pt-6">
              {filteredMassnahmen.length === 0 ? (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertTitle>Keine Maßnahmen gefunden</AlertTitle>
                  <AlertDescription>
                    Es wurden keine Maßnahmen mit den aktuellen Filterkriterien gefunden.
                  </AlertDescription>
                </Alert>
              ) : (
                <DataTable data={filteredMassnahmen} columns={columns} />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="spritztagebuch" className="space-y-4">
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Spritztagebuch gemäß § 11 PflSchG</AlertTitle>
            <AlertDescription>
              Dokumentation aller Pflanzenschutzmaßnahmen gemäß Pflanzenschutzgesetz.
              Alle PSM-Anwendungen müssen innerhalb von 30 Tagen dokumentiert werden.
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <CardTitle>PSM-Anwendungen</CardTitle>
              <CardDescription>
                {psmMassnahmen.length} Pflanzenschutzmaßnahmen dokumentiert
              </CardDescription>
            </CardHeader>
            <CardContent>
              {psmMassnahmen.length === 0 ? (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertTitle>Keine PSM-Anwendungen</AlertTitle>
                  <AlertDescription>
                    Es wurden keine Pflanzenschutzmaßnahmen dokumentiert.
                  </AlertDescription>
                </Alert>
              ) : (
                <DataTable data={psmMassnahmen} columns={psmColumns} />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="duengebilanz" className="space-y-4">
          <Alert>
            <Droplets className="h-4 w-4" />
            <AlertTitle>Düngebilanz gemäß DüV</AlertTitle>
            <AlertDescription>
              Dokumentation und Berechnung der Nährstoffbilanz gemäß Düngeverordnung.
              Die Stoffstrombilanz wird in einer zukünftigen Version verfügbar sein.
            </AlertDescription>
          </Alert>

          <Card>
            <CardHeader>
              <CardTitle>Düngungs-Übersicht</CardTitle>
              <CardDescription>
                {stats.duengungen} Düngemaßnahmen dokumentiert
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-gradient-to-br from-blue-100 to-green-100 dark:from-blue-900/30 dark:to-green-900/30 rounded-lg flex items-center justify-center">
                <div className="text-center space-y-4">
                  <Droplets className="h-16 w-16 mx-auto text-blue-600" />
                  <div>
                    <h3 className="text-lg font-semibold">Stoffstrombilanz</h3>
                    <p className="text-sm text-muted-foreground">
                      Die automatische Berechnung der Nährstoffbilanz wird in einer zukünftigen Version verfügbar sein.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
