/**
 * Kundenportal - Anfragen
 * 
 * Übersicht aller Kundenanfragen (Angebotsanfragen, Bestellanfragen, etc.)
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Search,
  Plus,
  Clock,
  CheckCircle2,
  XCircle,
  MessageSquare,
  Eye,
  Send,
  FileQuestion,
  ShoppingCart,
  Wrench,
  HelpCircle,
} from 'lucide-react'

interface Anfrage {
  id: string
  datum: string
  typ: 'angebot' | 'bestellung' | 'dienstleistung' | 'sonstiges'
  betreff: string
  nachricht: string
  status: 'offen' | 'in_bearbeitung' | 'beantwortet' | 'abgeschlossen' | 'abgelehnt'
  antwort?: string
  antwortDatum?: string
}

const mockAnfragen: Anfrage[] = [
  {
    id: 'A-2024-0023',
    datum: '2024-11-25',
    typ: 'angebot',
    betreff: 'Angebotsanfrage Saatgut Winterraps',
    nachricht: 'Bitte um Angebot für ca. 50 Einheiten Winterraps Saatgut für die Aussaat 2025.',
    status: 'in_bearbeitung',
  },
  {
    id: 'A-2024-0022',
    datum: '2024-11-20',
    typ: 'dienstleistung',
    betreff: 'Pflanzenschutzbehandlung Frühjahr',
    nachricht: 'Wir benötigen für Frühjahr 2025 wieder Ihre Unterstützung bei der PSM-Behandlung unserer Wintergetreide-Flächen.',
    status: 'beantwortet',
    antwort: 'Vielen Dank für Ihre Anfrage. Wir werden Sie Anfang März kontaktieren, um die Details zu besprechen. Ihre Flächen sind bereits vorgemerkt.',
    antwortDatum: '2024-11-21',
  },
  {
    id: 'A-2024-0018',
    datum: '2024-11-10',
    typ: 'angebot',
    betreff: 'Preisanfrage Futtermittel Q1/2025',
    nachricht: 'Bitte um aktualisierte Preise für Milchleistungsfutter 18% für Q1 2025. Monatliche Abnahme ca. 30 dt.',
    status: 'abgeschlossen',
    antwort: 'Angebot wurde erstellt und per E-Mail versendet. Vertrag V-2025-001 liegt zur Unterschrift bereit.',
    antwortDatum: '2024-11-12',
  },
  {
    id: 'A-2024-0015',
    datum: '2024-10-28',
    typ: 'sonstiges',
    betreff: 'Frage zu GMP+ Zertifikat',
    nachricht: 'Können Sie mir eine aktuelle Kopie Ihres GMP+ Zertifikats zusenden?',
    status: 'abgeschlossen',
    antwort: 'Das Zertifikat wurde in Ihrem Dokumentenbereich bereitgestellt. Sie können es jederzeit dort herunterladen.',
    antwortDatum: '2024-10-29',
  },
  {
    id: 'A-2024-0012',
    datum: '2024-10-15',
    typ: 'bestellung',
    betreff: 'Eilbestellung Dünger',
    nachricht: 'Wir benötigen kurzfristig 100 dt NPK 15-15-15. Ist eine Lieferung diese Woche möglich?',
    status: 'abgeschlossen',
    antwort: 'Lieferung wurde für den 18.10. bestätigt. Bestellung B-2024-0125 wurde angelegt.',
    antwortDatum: '2024-10-15',
  },
]

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  'offen': { label: 'Offen', color: 'bg-gray-100 text-gray-800', icon: <Clock className="h-4 w-4" /> },
  'in_bearbeitung': { label: 'In Bearbeitung', color: 'bg-amber-100 text-amber-800', icon: <Clock className="h-4 w-4" /> },
  'beantwortet': { label: 'Beantwortet', color: 'bg-blue-100 text-blue-800', icon: <MessageSquare className="h-4 w-4" /> },
  'abgeschlossen': { label: 'Abgeschlossen', color: 'bg-emerald-100 text-emerald-800', icon: <CheckCircle2 className="h-4 w-4" /> },
  'abgelehnt': { label: 'Abgelehnt', color: 'bg-red-100 text-red-800', icon: <XCircle className="h-4 w-4" /> },
}

const typConfig: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  'angebot': { label: 'Angebotsanfrage', icon: <FileQuestion className="h-4 w-4" />, color: 'bg-purple-100 text-purple-800' },
  'bestellung': { label: 'Bestellanfrage', icon: <ShoppingCart className="h-4 w-4" />, color: 'bg-blue-100 text-blue-800' },
  'dienstleistung': { label: 'Dienstleistung', icon: <Wrench className="h-4 w-4" />, color: 'bg-amber-100 text-amber-800' },
  'sonstiges': { label: 'Sonstiges', icon: <HelpCircle className="h-4 w-4" />, color: 'bg-gray-100 text-gray-800' },
}

export default function PortalAnfragen() {
  const [loading, setLoading] = useState(true)
  const [anfragen, setAnfragen] = useState<Anfrage[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('alle')
  const [selectedAnfrage, setSelectedAnfrage] = useState<Anfrage | null>(null)
  const [showNeueAnfrage, setShowNeueAnfrage] = useState(false)
  const [neueAnfrageTyp, setNeueAnfrageTyp] = useState<string>('')
  const [neueAnfrageBetreff, setNeueAnfrageBetreff] = useState('')
  const [neueAnfrageNachricht, setNeueAnfrageNachricht] = useState('')
  const [submitSuccess, setSubmitSuccess] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnfragen(mockAnfragen)
      setLoading(false)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  const filteredAnfragen = anfragen.filter((a) => {
    const matchesSearch = a.betreff.toLowerCase().includes(searchTerm.toLowerCase()) ||
      a.id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesTab = activeTab === 'alle' || a.status === activeTab
    return matchesSearch && matchesTab
  })

  const handleNeueAnfrage = () => {
    // TODO: API Call
    setSubmitSuccess(true)
    setTimeout(() => {
      setShowNeueAnfrage(false)
      setSubmitSuccess(false)
      setNeueAnfrageTyp('')
      setNeueAnfrageBetreff('')
      setNeueAnfrageNachricht('')
    }, 2000)
  }

  if (loading) {
    return <AnfragenSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Anfragen</h1>
          <p className="text-muted-foreground">Ihre Anfragen an uns</p>
        </div>
        <Button onClick={() => setShowNeueAnfrage(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          Neue Anfrage
        </Button>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-amber-100 p-2 text-amber-600">
                <Clock className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {anfragen.filter(a => a.status === 'offen' || a.status === 'in_bearbeitung').length}
                </p>
                <p className="text-sm text-muted-foreground">Offene Anfragen</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-100 p-2 text-blue-600">
                <MessageSquare className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {anfragen.filter(a => a.status === 'beantwortet').length}
                </p>
                <p className="text-sm text-muted-foreground">Beantwortet</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
                <CheckCircle2 className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {anfragen.filter(a => a.status === 'abgeschlossen').length}
                </p>
                <p className="text-sm text-muted-foreground">Abgeschlossen</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-purple-100 p-2 text-purple-600">
                <FileQuestion className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{anfragen.length}</p>
                <p className="text-sm text-muted-foreground">Gesamt</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Anfrage suchen..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Tabs & Table */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="alle">Alle</TabsTrigger>
          <TabsTrigger value="offen">Offen</TabsTrigger>
          <TabsTrigger value="in_bearbeitung">In Bearbeitung</TabsTrigger>
          <TabsTrigger value="beantwortet">Beantwortet</TabsTrigger>
          <TabsTrigger value="abgeschlossen">Abgeschlossen</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-4">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nr.</TableHead>
                  <TableHead>Datum</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Betreff</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAnfragen.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      Keine Anfragen gefunden
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredAnfragen.map((anfrage) => {
                    const status = statusConfig[anfrage.status]
                    const typ = typConfig[anfrage.typ]
                    return (
                      <TableRow key={anfrage.id}>
                        <TableCell className="font-medium">{anfrage.id}</TableCell>
                        <TableCell>{anfrage.datum}</TableCell>
                        <TableCell>
                          <Badge className={`${typ.color} gap-1`}>
                            {typ.icon}
                            {typ.label}
                          </Badge>
                        </TableCell>
                        <TableCell className="max-w-xs truncate">{anfrage.betreff}</TableCell>
                        <TableCell>
                          <Badge className={`${status.color} gap-1`}>
                            {status.icon}
                            {status.label}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedAnfrage(anfrage)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    )
                  })
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Detail Dialog */}
      <Dialog open={!!selectedAnfrage} onOpenChange={() => setSelectedAnfrage(null)}>
        <DialogContent className="max-w-2xl">
          {selectedAnfrage && (
            <>
              <DialogHeader>
                <DialogTitle>{selectedAnfrage.betreff}</DialogTitle>
                <DialogDescription>
                  {selectedAnfrage.id} • {selectedAnfrage.datum}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4">
                {/* Status & Typ */}
                <div className="flex gap-2">
                  <Badge className={`${statusConfig[selectedAnfrage.status].color} gap-1`}>
                    {statusConfig[selectedAnfrage.status].icon}
                    {statusConfig[selectedAnfrage.status].label}
                  </Badge>
                  <Badge className={typConfig[selectedAnfrage.typ].color}>
                    {typConfig[selectedAnfrage.typ].label}
                  </Badge>
                </div>

                {/* Anfrage */}
                <div className="rounded-lg bg-muted p-4">
                  <p className="text-sm font-medium text-muted-foreground mb-1">Ihre Anfrage:</p>
                  <p>{selectedAnfrage.nachricht}</p>
                </div>

                {/* Antwort */}
                {selectedAnfrage.antwort && (
                  <div className="rounded-lg border-2 border-emerald-200 bg-emerald-50 p-4">
                    <p className="text-sm font-medium text-emerald-800 mb-1">
                      Unsere Antwort ({selectedAnfrage.antwortDatum}):
                    </p>
                    <p className="text-emerald-900">{selectedAnfrage.antwort}</p>
                  </div>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>

      {/* Neue Anfrage Dialog */}
      <Dialog open={showNeueAnfrage} onOpenChange={setShowNeueAnfrage}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Plus className="h-5 w-5" />
              Neue Anfrage
            </DialogTitle>
            <DialogDescription>
              Stellen Sie eine Anfrage an unser Team
            </DialogDescription>
          </DialogHeader>

          {submitSuccess ? (
            <div className="flex flex-col items-center gap-4 py-8">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
                <CheckCircle2 className="h-8 w-8 text-emerald-600" />
              </div>
              <div className="text-center">
                <h3 className="text-lg font-semibold">Anfrage gesendet!</h3>
                <p className="text-muted-foreground">Wir werden uns schnellstmöglich bei Ihnen melden.</p>
              </div>
            </div>
          ) : (
            <>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="anfrage-typ">Art der Anfrage</Label>
                  <Select value={neueAnfrageTyp} onValueChange={setNeueAnfrageTyp}>
                    <SelectTrigger id="anfrage-typ">
                      <SelectValue placeholder="Bitte wählen..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="angebot">Angebotsanfrage</SelectItem>
                      <SelectItem value="bestellung">Bestellanfrage</SelectItem>
                      <SelectItem value="dienstleistung">Dienstleistung</SelectItem>
                      <SelectItem value="sonstiges">Sonstiges</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="anfrage-betreff">Betreff</Label>
                  <Input
                    id="anfrage-betreff"
                    placeholder="Worum geht es?"
                    value={neueAnfrageBetreff}
                    onChange={(e) => setNeueAnfrageBetreff(e.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="anfrage-nachricht">Nachricht</Label>
                  <Textarea
                    id="anfrage-nachricht"
                    placeholder="Beschreiben Sie Ihr Anliegen..."
                    value={neueAnfrageNachricht}
                    onChange={(e) => setNeueAnfrageNachricht(e.target.value)}
                    rows={5}
                  />
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNeueAnfrage(false)}>
                  Abbrechen
                </Button>
                <Button
                  onClick={handleNeueAnfrage}
                  disabled={!neueAnfrageTyp || !neueAnfrageBetreff || !neueAnfrageNachricht}
                  className="gap-2"
                >
                  <Send className="h-4 w-4" />
                  Anfrage absenden
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

function AnfragenSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-10 w-32" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-12 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
      <Skeleton className="h-10 w-full" />
      <Card>
        <CardContent className="p-4 space-y-3">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

