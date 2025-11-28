/**
 * Schlagkartei (Feldbuch) - Mandantenfähige Ackerschlagverwaltung
 * 
 * Features:
 * - Multi-Tenant: Schläge können Kunden (Landwirten) zugeordnet werden
 * - Feldblockfinder-Integration: Schlagdaten aus offiziellen Quellen übernehmen
 * - Dienstleister-Modus: Dokumentation von Maßnahmen für Kunden
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
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { 
  FileDown, 
  MapPin, 
  Plus, 
  Search, 
  Users, 
  Leaf, 
  Map, 
  Info,
  Filter,
  Building2,
  Calendar
} from 'lucide-react'
import { FeldblockfinderIntegration, SchlagData } from '@/components/agrar/FeldblockfinderIntegration'

// Types
type Kunde = {
  id: string
  name: string
  betriebsnummer: string
  bundesland: string
  schlagCount: number
  gesamtflaeche: number
}

type Schlag = {
  id: string
  name: string
  flik?: string
  flaeche: number
  kultur: string
  vorkultur?: string
  kundeId: string
  kundeName: string
  gemeinde: string
  gemarkung?: string
  bodenart?: string
  ackerzahl?: number
  status: 'aktiv' | 'stillgelegt' | 'brache'
  letzteMassnahme?: {
    datum: string
    typ: string
  }
}

// Mock-Daten für Kunden (Landwirte/Tenants)
const mockKunden: Kunde[] = [
  { id: 'k1', name: 'Schmidt Landwirtschaft GbR', betriebsnummer: 'DE-NI-030012', bundesland: 'niedersachsen', schlagCount: 12, gesamtflaeche: 145.8 },
  { id: 'k2', name: 'Müller Agrar KG', betriebsnummer: 'DE-NI-030045', bundesland: 'niedersachsen', schlagCount: 8, gesamtflaeche: 89.3 },
  { id: 'k3', name: 'Bauer Hof Meier', betriebsnummer: 'DE-BY-094015', bundesland: 'bayern', schlagCount: 5, gesamtflaeche: 52.1 },
  { id: 'all', name: 'Alle Kunden', betriebsnummer: '', bundesland: '', schlagCount: 25, gesamtflaeche: 287.2 },
]

// Mock-Daten für Schläge mit Kundenzuordnung
const mockSchlaege: Schlag[] = [
  { 
    id: '1', 
    name: 'Nordfeld 1', 
    flik: 'DENILI0000012345',
    flaeche: 12.5, 
    kultur: 'Winterweizen', 
    vorkultur: 'Winterraps',
    kundeId: 'k1', 
    kundeName: 'Schmidt Landwirtschaft GbR',
    gemeinde: 'Nordhausen',
    gemarkung: 'Nordheim',
    bodenart: 'Lehm',
    ackerzahl: 65,
    status: 'aktiv',
    letzteMassnahme: { datum: '2025-11-15', typ: 'Düngung' }
  },
  { 
    id: '2', 
    name: 'Südacker', 
    flik: 'DENILI0000012346',
    flaeche: 8.3, 
    kultur: 'Winterraps', 
    vorkultur: 'Winterweizen',
    kundeId: 'k2', 
    kundeName: 'Müller Agrar KG',
    gemeinde: 'Südhausen',
    gemarkung: 'Südfeld',
    bodenart: 'Sandig-Lehm',
    ackerzahl: 55,
    status: 'aktiv',
    letzteMassnahme: { datum: '2025-11-10', typ: 'PSM-Behandlung' }
  },
  { 
    id: '3', 
    name: 'Wiesengrund', 
    flik: 'DENILI0000012347',
    flaeche: 15.2, 
    kultur: 'Silomais', 
    vorkultur: 'Wintergerste',
    kundeId: 'k1', 
    kundeName: 'Schmidt Landwirtschaft GbR',
    gemeinde: 'Nordhausen',
    gemarkung: 'Wiesenau',
    bodenart: 'Lehm-Ton',
    ackerzahl: 70,
    status: 'aktiv'
  },
  { 
    id: '4', 
    name: 'Bergacker', 
    flik: 'DEBYLI0000098765',
    flaeche: 10.5, 
    kultur: 'Wintergerste', 
    vorkultur: 'Kartoffeln',
    kundeId: 'k3', 
    kundeName: 'Bauer Hof Meier',
    gemeinde: 'Bergdorf',
    gemarkung: 'Am Berg',
    bodenart: 'Sandig',
    ackerzahl: 45,
    status: 'aktiv'
  },
  { 
    id: '5', 
    name: 'Stilllegungsfläche', 
    flaeche: 3.2, 
    kultur: 'Brache', 
    kundeId: 'k1', 
    kundeName: 'Schmidt Landwirtschaft GbR',
    gemeinde: 'Nordhausen',
    status: 'stillgelegt'
  },
]

// API-Funktionen (simuliert)
async function fetchKunden(): Promise<Kunde[]> {
  // Simuliere API-Aufruf
  await new Promise(resolve => setTimeout(resolve, 500))
  return mockKunden
}

async function fetchSchlaege(_kundeId?: string): Promise<Schlag[]> {
  // Simuliere API-Aufruf
  await new Promise(resolve => setTimeout(resolve, 700))
  return mockSchlaege
}

// Skeleton-Komponente für Ladezustand
function SchlagkarteiSkeleton() {
  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div className="space-y-2">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-4 w-64" />
        </div>
        <Skeleton className="h-10 w-32" />
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
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-10 w-full" />
            {[1, 2, 3, 4, 5].map(i => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default function SchlagkarteiPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedKundeId, setSelectedKundeId] = useState<string>('all')
  const [activeTab, setActiveTab] = useState<string>('liste')
  const [feldblockDialogOpen, setFeldblockDialogOpen] = useState(false)
  const [filterStatus, setFilterStatus] = useState<string>('alle')

  // Daten laden mit React Query
  const { data: kunden, isLoading: kundenLoading } = useQuery({
    queryKey: ['kunden'],
    queryFn: fetchKunden
  })

  const { data: schlaege, isLoading: schlaegeLoading } = useQuery({
    queryKey: ['schlaege', selectedKundeId],
    queryFn: () => fetchSchlaege(selectedKundeId)
  })

  // Gefilterte Schläge
  const filteredSchlaege = useMemo(() => {
    if (!schlaege) return []
    
    return schlaege.filter(schlag => {
      // Kundenfilter
      if (selectedKundeId !== 'all' && schlag.kundeId !== selectedKundeId) {
        return false
      }
      
      // Statusfilter
      if (filterStatus !== 'alle' && schlag.status !== filterStatus) {
        return false
      }
      
      // Suchfilter
      if (searchTerm) {
        const search = searchTerm.toLowerCase()
        return (
          schlag.name.toLowerCase().includes(search) ||
          schlag.kultur.toLowerCase().includes(search) ||
          schlag.gemeinde.toLowerCase().includes(search) ||
          schlag.flik?.toLowerCase().includes(search)
        )
      }
      
      return true
    })
  }, [schlaege, selectedKundeId, filterStatus, searchTerm])

  // Statistiken
  const stats = useMemo(() => {
    const filtered = filteredSchlaege
    return {
      schlagCount: filtered.length,
      gesamtflaeche: filtered.reduce((sum, s) => sum + s.flaeche, 0),
      kulturen: new Set(filtered.map(s => s.kultur)).size,
      kundenCount: new Set(filtered.map(s => s.kundeId)).size
    }
  }, [filteredSchlaege])

  // Ausgewählter Kunde
  const selectedKunde = useMemo(() => {
    return kunden?.find(k => k.id === selectedKundeId)
  }, [kunden, selectedKundeId])

  // Feldblockfinder Schlag-Übernahme
  const handleSchlagFromFeldblockfinder = (schlagData: SchlagData) => {
    // Hier würde der neue Schlag erstellt werden
    setFeldblockDialogOpen(false)
    // Navigation zum Schlag-Anlegen mit vorausgefüllten Daten
    navigate('/agrar/feldbuch/schlag/neu', { 
      state: { 
        flik: schlagData.flik,
        flaeche: schlagData.flaeche,
        bundesland: schlagData.bundesland,
        kundeId: selectedKundeId !== 'all' ? selectedKundeId : undefined
      }
    })
  }

  // Spalten-Definition
  const columns = [
    {
      key: 'name' as const,
      label: 'Schlag',
      render: (s: Schlag) => (
        <div>
          <button 
            onClick={() => navigate(`/agrar/feldbuch/schlag/${s.id}`)} 
            className="font-medium text-blue-600 hover:underline"
          >
            {s.name}
          </button>
          {s.flik && (
            <div className="text-xs text-muted-foreground">{s.flik}</div>
          )}
        </div>
      ),
    },
    { 
      key: 'flaeche' as const, 
      label: 'Fläche', 
      render: (s: Schlag) => `${s.flaeche.toFixed(2)} ha` 
    },
    { 
      key: 'kultur' as const, 
      label: 'Kultur', 
      render: (s: Schlag) => (
        <div className="flex items-center gap-2">
          <Leaf className="h-4 w-4 text-green-600" />
          <Badge variant="outline">{s.kultur}</Badge>
        </div>
      )
    },
    { 
      key: 'kundeName' as const, 
      label: 'Kunde/Landwirt',
      render: (s: Schlag) => (
        <div className="flex items-center gap-2">
          <Building2 className="h-4 w-4 text-muted-foreground" />
          <span>{s.kundeName}</span>
        </div>
      )
    },
    { 
      key: 'gemeinde' as const, 
      label: 'Gemeinde' 
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Schlag) => (
        <Badge variant={s.status === 'aktiv' ? 'default' : s.status === 'stillgelegt' ? 'secondary' : 'outline'}>
          {s.status === 'aktiv' ? 'Aktiv' : s.status === 'stillgelegt' ? 'Stillgelegt' : 'Brache'}
        </Badge>
      )
    },
    {
      key: 'letzteMassnahme' as const,
      label: 'Letzte Maßnahme',
      render: (s: Schlag) => s.letzteMassnahme ? (
        <div className="text-sm">
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {new Date(s.letzteMassnahme.datum).toLocaleDateString('de-DE')}
          </div>
          <div className="text-muted-foreground">{s.letzteMassnahme.typ}</div>
        </div>
      ) : '-'
    },
  ]

  // Ladezustand
  if (kundenLoading || schlaegeLoading) {
    return <SchlagkarteiSkeleton />
  }

  return (
    <div className="space-y-4 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <MapPin className="h-8 w-8 text-green-600" />
            Schlagkartei
          </h1>
          <p className="text-muted-foreground">
            Mandantenfähige Ackerschlagverwaltung für Dienstleister
          </p>
        </div>
        <div className="flex gap-2">
          <Dialog open={feldblockDialogOpen} onOpenChange={setFeldblockDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="gap-2">
                <Map className="h-4 w-4" />
                Feldblockfinder
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Feldblockfinder</DialogTitle>
                <DialogDescription>
                  Suchen Sie Feldblöcke und übernehmen Sie die Daten in Ihre Schlagkartei
                </DialogDescription>
              </DialogHeader>
              <FeldblockfinderIntegration
                defaultBundesland={selectedKunde?.bundesland}
                onSchlagSelected={handleSchlagFromFeldblockfinder}
                height="500px"
              />
            </DialogContent>
          </Dialog>
          <Button onClick={() => navigate('/agrar/feldbuch/schlag/neu')} className="gap-2">
            <Plus className="h-4 w-4" />
            Neuer Schlag
          </Button>
        </div>
      </div>

      {/* Mandanten-Info */}
      {selectedKundeId !== 'all' && selectedKunde && (
        <Alert>
          <Building2 className="h-4 w-4" />
          <AlertTitle>Kundenansicht: {selectedKunde.name}</AlertTitle>
          <AlertDescription>
            Betriebsnummer: {selectedKunde.betriebsnummer} | 
            {selectedKunde.schlagCount} Schläge | 
            {selectedKunde.gesamtflaeche.toFixed(1)} ha Gesamtfläche
          </AlertDescription>
        </Alert>
      )}

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <MapPin className="h-4 w-4 text-blue-600" />
              Schläge
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.schlagCount}</div>
            <p className="text-xs text-muted-foreground">
              {selectedKundeId === 'all' ? 'Alle Kunden' : 'Ausgewählter Kunde'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Map className="h-4 w-4 text-green-600" />
              Gesamtfläche
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.gesamtflaeche.toFixed(1)} ha</div>
            <p className="text-xs text-muted-foreground">Bewirtschaftete Fläche</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Leaf className="h-4 w-4 text-amber-600" />
              Kulturen
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.kulturen}</div>
            <p className="text-xs text-muted-foreground">Verschiedene Kulturen</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <Users className="h-4 w-4 text-purple-600" />
              Kunden
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{selectedKundeId === 'all' ? stats.kundenCount : 1}</div>
            <p className="text-xs text-muted-foreground">Betriebe</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="liste">Schlagliste</TabsTrigger>
          <TabsTrigger value="karte">Kartenansicht</TabsTrigger>
          <TabsTrigger value="kulturen">Kulturübersicht</TabsTrigger>
        </TabsList>

        <TabsContent value="liste" className="space-y-4">
          {/* Filter */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Filter & Suche
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-4">
                {/* Kundenauswahl (Multi-Tenant) */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Kunde/Landwirt</label>
                  <Select value={selectedKundeId} onValueChange={setSelectedKundeId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Kunde auswählen..." />
                    </SelectTrigger>
                    <SelectContent>
                      {kunden?.map(kunde => (
                        <SelectItem key={kunde.id} value={kunde.id}>
                          {kunde.name}
                          {kunde.id !== 'all' && ` (${kunde.schlagCount} Schläge)`}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Statusfilter */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Status</label>
                  <Select value={filterStatus} onValueChange={setFilterStatus}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="alle">Alle Status</SelectItem>
                      <SelectItem value="aktiv">Aktiv</SelectItem>
                      <SelectItem value="stillgelegt">Stillgelegt</SelectItem>
                      <SelectItem value="brache">Brache</SelectItem>
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
                        placeholder="Schlag, Kultur, FLIK, Gemeinde..." 
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
              {filteredSchlaege.length === 0 ? (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertTitle>Keine Schläge gefunden</AlertTitle>
                  <AlertDescription>
                    Es wurden keine Schläge mit den aktuellen Filterkriterien gefunden.
                    {selectedKundeId !== 'all' && ' Wählen Sie einen anderen Kunden oder zeigen Sie alle Kunden an.'}
                  </AlertDescription>
                </Alert>
              ) : (
                <DataTable 
                  data={filteredSchlaege} 
                  columns={columns}
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="karte">
          <Card>
            <CardHeader>
              <CardTitle>Kartenansicht</CardTitle>
              <CardDescription>
                Visualisierung der Schläge auf einer interaktiven Karte (in Entwicklung)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-96 bg-gradient-to-br from-green-100 to-blue-100 dark:from-green-900/30 dark:to-blue-900/30 rounded-lg flex items-center justify-center">
                <div className="text-center space-y-4">
                  <Map className="h-16 w-16 mx-auto text-green-600" />
                  <div>
                    <h3 className="text-lg font-semibold">Kartenintegration</h3>
                    <p className="text-sm text-muted-foreground">
                      GIS-Kartenansicht mit OpenStreetMap/Leaflet wird in einer zukünftigen Version verfügbar sein.
                    </p>
                  </div>
                  <Button variant="outline" onClick={() => setFeldblockDialogOpen(true)}>
                    <Map className="h-4 w-4 mr-2" />
                    Feldblockfinder öffnen
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="kulturen">
          <Card>
            <CardHeader>
              <CardTitle>Kulturübersicht</CardTitle>
              <CardDescription>
                Anbauflächen nach Kulturen aufgeschlüsselt
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Array.from(new Set(filteredSchlaege.map(s => s.kultur))).map(kultur => {
                  const kulturSchlaege = filteredSchlaege.filter(s => s.kultur === kultur)
                  const kulturFlaeche = kulturSchlaege.reduce((sum, s) => sum + s.flaeche, 0)
                  const prozent = (kulturFlaeche / stats.gesamtflaeche * 100).toFixed(1)
                  
                  return (
                    <div key={kultur} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Leaf className="h-5 w-5 text-green-600" />
                        <div>
                          <div className="font-medium">{kultur}</div>
                          <div className="text-sm text-muted-foreground">
                            {kulturSchlaege.length} Schläge
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">{kulturFlaeche.toFixed(1)} ha</div>
                        <div className="text-sm text-muted-foreground">{prozent}%</div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
