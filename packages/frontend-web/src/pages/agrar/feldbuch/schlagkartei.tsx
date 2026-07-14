/**
 * Schlagkartei (Feldbuch) - Mandantenfähige Ackerschlagverwaltung
 * 
 * Features:
 * - Multi-Tenant: Schläge können Kunden (Landwirten) zugeordnet werden
 * - Feldblockfinder-Integration: Schlagdaten aus offiziellen Quellen übernehmen
 * - Dienstleister-Modus: Dokumentation von Maßnahmen für Kunden
 */

import { useState, useMemo } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
// useQuery is used via hooks from @/lib/api/agrar
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'
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
  Calendar,
  Pencil,
  Trash2
} from 'lucide-react'
import { FeldblockfinderIntegration, SchlagData } from '@/components/agrar/FeldblockfinderIntegration'
import { SchlagKarte } from '@/components/agrar/SchlagKarte'

// Types
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

type AgrarRole = 'dienstleister' | 'landwirt' | 'beratung' | 'leitung'

const agrarRoles = [
  { id: 'dienstleister', label: 'Dienstleister', description: 'Schlaege je Kunde sauber verwalten und Massnahmen vorbereiten.' },
  { id: 'landwirt', label: 'Landwirt', description: 'Eigene Flaechen, Kulturen und letzte Massnahmen schnell verstehen.' },
  { id: 'beratung', label: 'Beratung', description: 'Kultur, Flaeche, Status und naechste fachliche Aktion pruefen.' },
  { id: 'leitung', label: 'Leitung', description: 'Flaechenumfang, Kundenlage und Pflegebedarf verdichtet bewerten.' },
] satisfies Array<{ id: AgrarRole; label: string; description: string }>

// API hooks from centralized agrar module
import { useAgrarKunden, useSchlaege, useDeleteSchlag } from '@/lib/api/agrar'
import { useToast } from '@/hooks/use-toast'

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
  const { toast } = useToast()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedKundeId, setSelectedKundeId] = useState<string>('all')
  const [activeTab, setActiveTab] = useState<string>('liste')
  const [feldblockDialogOpen, setFeldblockDialogOpen] = useState(false)
  const [filterStatus, setFilterStatus] = useState<string>('alle')
  const [roleFocus, setRoleFocus] = useState<AgrarRole>('dienstleister')

  // Daten laden mit API-Hooks
  const { data: kunden, isLoading: kundenLoading } = useAgrarKunden()

  const { data: schlaege, isLoading: schlaegeLoading } = useSchlaege(selectedKundeId)
  const deleteSchlag = useDeleteSchlag()

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
      kundenCount: new Set(filtered.map(s => s.kundeId)).size,
      aktiv: filtered.filter(s => s.status === 'aktiv').length,
      ohneMassnahme: filtered.filter(s => !s.letzteMassnahme).length,
    }
  }, [filteredSchlaege])

  // Ausgewählter Kunde
  const selectedKunde = useMemo(() => {
    return kunden?.find(k => k.id === selectedKundeId)
  }, [kunden, selectedKundeId])
  const schlagReady = stats.schlagCount > 0 && stats.ohneMassnahme === 0
  const nextSchlagAction = stats.schlagCount === 0
    ? 'Ersten Schlag anlegen oder per Feldblockfinder uebernehmen.'
    : stats.ohneMassnahme > 0
      ? `${stats.ohneMassnahme} Schlag/Schlaege ohne letzte Massnahme pruefen und dokumentieren.`
      : 'Schlagliste exportieren oder naechste Massnahme planen.'

  const handleExport = () => {
    const header = 'Schlag;FLIK;Flaeche_ha;Kultur;Vorkultur;Kunde;Gemeinde;Status\n'
    const rows = filteredSchlaege.map((s) =>
      [s.name, s.flik ?? '', s.flaeche, s.kultur, s.vorkultur ?? '', s.kundeName, s.gemeinde, s.status].map((v) => `"${String(v).replace(/"/g, '""')}"`).join(';')
    )
    const blob = new Blob([header + rows.join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Schlagkartei_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast({ title: 'Export', description: `${filteredSchlaege.length} Schläge exportiert.` })
  }

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
          <Leaf className="h-4 w-4 text-status-success" />
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
    {
      key: 'aktionen' as const,
      label: 'Aktionen',
      render: (s: Schlag) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" onClick={() => navigate(`/agrar/feldbuch/schlag/${s.id}`)} title="Bearbeiten">
            <Pencil className="h-4 w-4" />
          </Button>
          {s.status === 'aktiv' && (
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                if (confirm('Schlag stilllegen? (Status wird auf „stillgelegt“ gesetzt)')) {
                  deleteSchlag.mutate(s.id, {
                    onSuccess: () => toast({ title: 'Schlag stillgelegt' }),
                    onError: () => toast({ variant: 'destructive', title: 'Stilllegen fehlgeschlagen' })
                  })
                }
              }}
              disabled={deleteSchlag.isPending}
              title="Stilllegen"
            >
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          )}
        </div>
      )
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
            <MapPin className="h-8 w-8 text-status-success" />
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

      <RoleFocusBar
        roles={agrarRoles}
        value={roleFocus}
        onChange={setRoleFocus}
        visibleCount={filteredSchlaege.length}
        totalCount={schlaege?.length ?? 0}
        title="Arbeitsrolle fuer Schlagkartei"
      />

      <ManagementDecisionPanel
        decision={{
          allowed: schlagReady,
          allowedLabel: 'Feldlage gepflegt',
          blockedLabel: 'Feldlage pruefen',
          summary: schlagReady
            ? 'Alle sichtbaren Schlaege haben eine letzte Massnahme. Die Schlagkartei ist fuer Planung, Export und Nachweis nutzbar.'
            : 'Schlaege ohne Massnahmenbezug oder fehlende Flaechen verhindern eine belastbare Feldbuchlage. Bitte zuerst Anlage oder letzte Massnahme klaeren.',
          blockerCount: schlagReady ? 0 : Math.max(stats.ohneMassnahme, stats.schlagCount === 0 ? 1 : 0),
          nextFocus: nextSchlagAction,
          template: {
            label: 'Schlagkartei-Nachweis',
            href: '/docs/agrar/schlagkartei-nachweis.md',
          },
        }}
      />

      <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr_1fr]">
        <OperationalTaskPlan
          title="Feldplan"
          items={[
            { label: 'Schlaege erfassen', done: stats.schlagCount > 0, hint: `${stats.schlagCount} Schlag/Schlaege im aktuellen Filter.` },
            { label: 'Aktive Flaechen pruefen', done: stats.aktiv > 0, hint: `${stats.aktiv} aktive Flaeche(n).` },
            { label: 'Massnahmenbezug halten', done: stats.ohneMassnahme === 0, hint: stats.ohneMassnahme > 0 ? `${stats.ohneMassnahme} Schlag/Schlaege ohne letzte Massnahme.` : 'Alle sichtbaren Schlaege haben eine letzte Massnahme.' },
            { label: 'Export/Nachweis sichern', done: filteredSchlaege.length > 0, hint: 'CSV-Export dokumentiert die aktuelle Schlagliste.' },
          ]}
        />
        <NextActionPanel action={nextSchlagAction} tone={schlagReady ? 'emerald' : stats.schlagCount === 0 ? 'blue' : 'amber'} />
        <div className="space-y-3">
          <EvidenceTemplateLink link={{ label: 'Feldblock- und Schlagnachweis', href: '/docs/agrar/feldblock-schlagnachweis.md' }} />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'create', label: 'Anlegen', available: true, hint: 'Neuer Schlag oder Feldblockfinder-Uebernahme.' },
              { key: 'read', label: 'Lesen', available: true, hint: 'Flaeche, Kultur, Kunde, Status und letzte Massnahme sind sichtbar.' },
              { key: 'update', label: 'Bearbeiten', available: true, hint: 'Bearbeiten fuehrt in die Schlag-Detailroute.' },
              { key: 'delete', label: 'Stilllegen', available: true, hint: 'Aktive Schlaege werden kontrolliert stillgelegt.' },
              { key: 'export', label: 'Export', available: true, hint: 'CSV-Export dient als einfacher Flaechennachweis.' },
              { key: 'evidence', label: 'Nachweis', available: filteredSchlaege.length > 0, hint: 'FLIK, Flaeche und Kunde bilden die Nachweisbasis.' },
            ]}
          />
        </div>
      </div>

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
              <Map className="h-4 w-4 text-status-success" />
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
              <Leaf className="h-4 w-4 text-status-warning" />
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
                  <NativeSelect
                    value={selectedKundeId}
                    onValueChange={setSelectedKundeId}
                    options={(kunden ?? []).map((kunde) => ({
                      value: kunde.id,
                      label: kunde.id !== 'all' ? `${kunde.name} (${kunde.schlagCount} Schlaege)` : kunde.name,
                    }))}
                  />
                </div>

                {/* Statusfilter */}
                <div>
                  <label className="text-sm font-medium mb-2 block">Status</label>
                  <NativeSelect
                    value={filterStatus}
                    onValueChange={setFilterStatus}
                    options={[
                      { value: 'alle', label: 'Alle Status' },
                      { value: 'aktiv', label: 'Aktiv' },
                      { value: 'stillgelegt', label: 'Stillgelegt' },
                      { value: 'brache', label: 'Brache' },
                    ]}
                  />
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
                    <Button variant="outline" className="gap-2" onClick={handleExport}>
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
                Ackerschlaege als GeoJSON-Polygone auf OpenStreetMap - RFC 7946 GIS-Integration
              </CardDescription>
            </CardHeader>
            <CardContent className="p-0 overflow-hidden rounded-b-lg">
              <SchlagKarte height="520px" />
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
                        <Leaf className="h-5 w-5 text-status-success" />
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
