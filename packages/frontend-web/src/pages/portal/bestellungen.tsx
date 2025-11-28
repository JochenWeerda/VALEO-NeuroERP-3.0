/**
 * Kundenportal - Meine Bestellungen
 * 
 * Übersicht aller Bestellungen des Kunden
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Dialog,
  DialogContent,
  DialogDescription,
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
  Search,
  Package,
  Clock,
  CheckCircle2,
  Truck,
  XCircle,
  Eye,
  Download,
  FileText,
  ChevronRight,
} from 'lucide-react'

interface BestellPosition {
  artikelnummer: string
  name: string
  menge: number
  einheit: string
  einzelpreis: number
  gesamtpreis: number
}

interface Bestellung {
  id: string
  datum: string
  status: 'offen' | 'in_bearbeitung' | 'versendet' | 'abgeschlossen' | 'storniert'
  positionen: BestellPosition[]
  gesamtbetrag: number
  lieferdatum?: string
  trackingnummer?: string
  rechnung?: string
}

const mockBestellungen: Bestellung[] = [
  {
    id: 'B-2024-0147',
    datum: '2024-11-25',
    status: 'in_bearbeitung',
    gesamtbetrag: 1250.00,
    positionen: [
      { artikelnummer: 'SAA-WW-001', name: 'Winterweizen Premium', menge: 15, einheit: 'dt', einzelpreis: 65.00, gesamtpreis: 975.00 },
      { artikelnummer: 'DUE-NPK-001', name: 'NPK 15-15-15', menge: 5, einheit: 'dt', einzelpreis: 39.90, gesamtpreis: 199.50 },
    ],
  },
  {
    id: 'B-2024-0142',
    datum: '2024-11-20',
    status: 'versendet',
    gesamtbetrag: 890.00,
    lieferdatum: '2024-11-28',
    trackingnummer: 'DHL-123456789',
    positionen: [
      { artikelnummer: 'DUE-NPK-001', name: 'NPK 15-15-15', menge: 20, einheit: 'dt', einzelpreis: 39.90, gesamtpreis: 798.00 },
    ],
  },
  {
    id: 'B-2024-0138',
    datum: '2024-11-15',
    status: 'abgeschlossen',
    gesamtbetrag: 2100.00,
    rechnung: 'R-2024-0567',
    positionen: [
      { artikelnummer: 'PSM-GLY-001', name: 'Glyphosat 360', menge: 100, einheit: 'l', einzelpreis: 8.50, gesamtpreis: 850.00 },
      { artikelnummer: 'PSM-OPU-001', name: 'Fungizid Opus Top', menge: 30, einheit: 'l', einzelpreis: 32.50, gesamtpreis: 975.00 },
    ],
  },
  {
    id: 'B-2024-0125',
    datum: '2024-11-01',
    status: 'abgeschlossen',
    gesamtbetrag: 3500.00,
    rechnung: 'R-2024-0542',
    positionen: [
      { artikelnummer: 'FUT-MLF-001', name: 'Milchleistungsfutter 18%', menge: 80, einheit: 'dt', einzelpreis: 38.00, gesamtpreis: 3040.00 },
    ],
  },
  {
    id: 'B-2024-0098',
    datum: '2024-10-15',
    status: 'storniert',
    gesamtbetrag: 500.00,
    positionen: [
      { artikelnummer: 'SAA-WG-002', name: 'Wintergerste Hyvido', menge: 2, einheit: 'Einheit', einzelpreis: 185.00, gesamtpreis: 370.00 },
    ],
  },
]

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  'offen': { label: 'Offen', color: 'bg-gray-100 text-gray-800', icon: <Clock className="h-4 w-4" /> },
  'in_bearbeitung': { label: 'In Bearbeitung', color: 'bg-amber-100 text-amber-800', icon: <Package className="h-4 w-4" /> },
  'versendet': { label: 'Versendet', color: 'bg-blue-100 text-blue-800', icon: <Truck className="h-4 w-4" /> },
  'abgeschlossen': { label: 'Abgeschlossen', color: 'bg-emerald-100 text-emerald-800', icon: <CheckCircle2 className="h-4 w-4" /> },
  'storniert': { label: 'Storniert', color: 'bg-red-100 text-red-800', icon: <XCircle className="h-4 w-4" /> },
}

export default function PortalBestellungen() {
  const [loading, setLoading] = useState(true)
  const [bestellungen, setBestellungen] = useState<Bestellung[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('alle')
  const [selectedBestellung, setSelectedBestellung] = useState<Bestellung | null>(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      setBestellungen(mockBestellungen)
      setLoading(false)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  const filteredBestellungen = bestellungen.filter((b) => {
    const matchesSearch = b.id.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesTab = activeTab === 'alle' || b.status === activeTab
    return matchesSearch && matchesTab
  })

  if (loading) {
    return <BestellungenSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Meine Bestellungen</h1>
        <p className="text-muted-foreground">Übersicht aller Ihrer Bestellungen</p>
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
                  {bestellungen.filter(b => b.status === 'offen' || b.status === 'in_bearbeitung').length}
                </p>
                <p className="text-sm text-muted-foreground">Offene Bestellungen</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-100 p-2 text-blue-600">
                <Truck className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {bestellungen.filter(b => b.status === 'versendet').length}
                </p>
                <p className="text-sm text-muted-foreground">Unterwegs</p>
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
                  {bestellungen.filter(b => b.status === 'abgeschlossen').length}
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
                <Package className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{bestellungen.length}</p>
                <p className="text-sm text-muted-foreground">Gesamt</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filter & Search */}
      <div className="flex flex-col gap-4 md:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Bestellnummer suchen..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      {/* Tabs & Table */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="alle">Alle</TabsTrigger>
          <TabsTrigger value="offen">Offen</TabsTrigger>
          <TabsTrigger value="in_bearbeitung">In Bearbeitung</TabsTrigger>
          <TabsTrigger value="versendet">Versendet</TabsTrigger>
          <TabsTrigger value="abgeschlossen">Abgeschlossen</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-4">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Bestellnummer</TableHead>
                  <TableHead>Datum</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Betrag</TableHead>
                  <TableHead>Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredBestellungen.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground">
                      Keine Bestellungen gefunden
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredBestellungen.map((bestellung) => {
                    const status = statusConfig[bestellung.status]
                    return (
                      <TableRow key={bestellung.id}>
                        <TableCell className="font-medium">{bestellung.id}</TableCell>
                        <TableCell>{bestellung.datum}</TableCell>
                        <TableCell>
                          <Badge className={`${status.color} gap-1`}>
                            {status.icon}
                            {status.label}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          € {bestellung.gesamtbetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedBestellung(bestellung)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {bestellung.rechnung && (
                              <Button variant="ghost" size="sm">
                                <Download className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
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
      <Dialog open={!!selectedBestellung} onOpenChange={() => setSelectedBestellung(null)}>
        <DialogContent className="max-w-2xl">
          {selectedBestellung && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Package className="h-5 w-5" />
                  Bestellung {selectedBestellung.id}
                </DialogTitle>
                <DialogDescription>
                  Vom {selectedBestellung.datum}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4">
                {/* Status */}
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Status:</span>
                  <Badge className={`${statusConfig[selectedBestellung.status].color} gap-1`}>
                    {statusConfig[selectedBestellung.status].icon}
                    {statusConfig[selectedBestellung.status].label}
                  </Badge>
                </div>

                {/* Tracking */}
                {selectedBestellung.trackingnummer && (
                  <div className="rounded-lg bg-muted p-3">
                    <p className="text-sm text-muted-foreground">Sendungsverfolgung</p>
                    <p className="font-medium">{selectedBestellung.trackingnummer}</p>
                    {selectedBestellung.lieferdatum && (
                      <p className="text-sm">Voraussichtliche Lieferung: {selectedBestellung.lieferdatum}</p>
                    )}
                  </div>
                )}

                {/* Positionen */}
                <div>
                  <h4 className="mb-2 font-semibold">Positionen</h4>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Artikel</TableHead>
                        <TableHead className="text-right">Menge</TableHead>
                        <TableHead className="text-right">Einzelpreis</TableHead>
                        <TableHead className="text-right">Gesamt</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {selectedBestellung.positionen.map((pos, idx) => (
                        <TableRow key={idx}>
                          <TableCell>
                            <p className="font-medium">{pos.name}</p>
                            <p className="text-xs text-muted-foreground">{pos.artikelnummer}</p>
                          </TableCell>
                          <TableCell className="text-right">{pos.menge} {pos.einheit}</TableCell>
                          <TableCell className="text-right">€ {pos.einzelpreis.toFixed(2)}</TableCell>
                          <TableCell className="text-right font-medium">€ {pos.gesamtpreis.toFixed(2)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {/* Gesamtbetrag */}
                <div className="flex justify-between border-t pt-4 text-lg font-semibold">
                  <span>Gesamtbetrag (netto)</span>
                  <span>€ {selectedBestellung.gesamtbetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</span>
                </div>

                {/* Rechnung Download */}
                {selectedBestellung.rechnung && (
                  <Button className="w-full gap-2">
                    <Download className="h-4 w-4" />
                    Rechnung {selectedBestellung.rechnung} herunterladen
                  </Button>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

function BestellungenSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-10 w-48" />
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

