/**
 * Kundenportal - Rechnungen
 * 
 * Übersicht aller Rechnungen des Kunden
 */

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
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
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Search,
  Receipt,
  Euro,
  CheckCircle2,
  AlertCircle,
  Clock,
  Eye,
  Download,
  Calendar,
  CreditCard,
  AlertTriangle,
} from 'lucide-react'

interface Rechnung {
  id: string
  rechnungsnummer: string
  datum: string
  faelligkeitsdatum: string
  status: 'bezahlt' | 'offen' | 'ueberfaellig' | 'teilzahlung'
  nettobetrag: number
  mwst: number
  bruttobetrag: number
  bezahltBetrag: number
  bestellung?: string
  dokument: string
}

const mockRechnungen: Rechnung[] = [
  {
    id: '1',
    rechnungsnummer: 'R-2024-0567',
    datum: '2024-11-15',
    faelligkeitsdatum: '2024-12-15',
    status: 'offen',
    nettobetrag: 2100.00,
    mwst: 399.00,
    bruttobetrag: 2499.00,
    bezahltBetrag: 0,
    bestellung: 'B-2024-0138',
    dokument: 'rechnung-r-2024-0567.pdf',
  },
  {
    id: '2',
    rechnungsnummer: 'R-2024-0542',
    datum: '2024-11-01',
    faelligkeitsdatum: '2024-12-01',
    status: 'teilzahlung',
    nettobetrag: 3500.00,
    mwst: 665.00,
    bruttobetrag: 4165.00,
    bezahltBetrag: 2000.00,
    bestellung: 'B-2024-0125',
    dokument: 'rechnung-r-2024-0542.pdf',
  },
  {
    id: '3',
    rechnungsnummer: 'R-2024-0498',
    datum: '2024-10-15',
    faelligkeitsdatum: '2024-11-15',
    status: 'bezahlt',
    nettobetrag: 1580.00,
    mwst: 300.20,
    bruttobetrag: 1880.20,
    bezahltBetrag: 1880.20,
    dokument: 'rechnung-r-2024-0498.pdf',
  },
  {
    id: '4',
    rechnungsnummer: 'R-2024-0445',
    datum: '2024-09-20',
    faelligkeitsdatum: '2024-10-20',
    status: 'bezahlt',
    nettobetrag: 4200.00,
    mwst: 798.00,
    bruttobetrag: 4998.00,
    bezahltBetrag: 4998.00,
    dokument: 'rechnung-r-2024-0445.pdf',
  },
  {
    id: '5',
    rechnungsnummer: 'R-2024-0412',
    datum: '2024-09-01',
    faelligkeitsdatum: '2024-10-01',
    status: 'ueberfaellig',
    nettobetrag: 890.00,
    mwst: 169.10,
    bruttobetrag: 1059.10,
    bezahltBetrag: 0,
    dokument: 'rechnung-r-2024-0412.pdf',
  },
]

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  'bezahlt': { label: 'Bezahlt', color: 'bg-emerald-100 text-emerald-800', icon: <CheckCircle2 className="h-4 w-4" /> },
  'offen': { label: 'Offen', color: 'bg-amber-100 text-amber-800', icon: <Clock className="h-4 w-4" /> },
  'ueberfaellig': { label: 'Überfällig', color: 'bg-red-100 text-red-800', icon: <AlertTriangle className="h-4 w-4" /> },
  'teilzahlung': { label: 'Teilzahlung', color: 'bg-blue-100 text-blue-800', icon: <CreditCard className="h-4 w-4" /> },
}

export default function PortalRechnungen() {
  const [loading, setLoading] = useState(true)
  const [rechnungen, setRechnungen] = useState<Rechnung[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('alle')
  const [selectedRechnung, setSelectedRechnung] = useState<Rechnung | null>(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      setRechnungen(mockRechnungen)
      setLoading(false)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  const filteredRechnungen = rechnungen.filter((r) => {
    const matchesSearch = r.rechnungsnummer.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesTab = activeTab === 'alle' || r.status === activeTab
    return matchesSearch && matchesTab
  })

  const offenerBetrag = rechnungen
    .filter(r => r.status === 'offen' || r.status === 'ueberfaellig' || r.status === 'teilzahlung')
    .reduce((sum, r) => sum + (r.bruttobetrag - r.bezahltBetrag), 0)
  
  const ueberfaelligerBetrag = rechnungen
    .filter(r => r.status === 'ueberfaellig')
    .reduce((sum, r) => sum + r.bruttobetrag, 0)

  if (loading) {
    return <RechnungenSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Rechnungen</h1>
        <p className="text-muted-foreground">Übersicht aller Ihrer Rechnungen</p>
      </div>

      {/* Warnung bei überfälligen Rechnungen */}
      {ueberfaelligerBetrag > 0 && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Überfällige Rechnungen</AlertTitle>
          <AlertDescription>
            Sie haben offene Rechnungen im Wert von € {ueberfaelligerBetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}, 
            die das Zahlungsziel überschritten haben.
          </AlertDescription>
        </Alert>
      )}

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-amber-100 p-2 text-amber-600">
                <Euro className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  € {offenerBetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                </p>
                <p className="text-sm text-muted-foreground">Offener Betrag</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-red-100 p-2 text-red-600">
                <AlertTriangle className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {rechnungen.filter(r => r.status === 'ueberfaellig').length}
                </p>
                <p className="text-sm text-muted-foreground">Überfällig</p>
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
                  {rechnungen.filter(r => r.status === 'bezahlt').length}
                </p>
                <p className="text-sm text-muted-foreground">Bezahlt</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-purple-100 p-2 text-purple-600">
                <Receipt className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{rechnungen.length}</p>
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
          placeholder="Rechnungsnummer suchen..."
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
          <TabsTrigger value="ueberfaellig">Überfällig</TabsTrigger>
          <TabsTrigger value="bezahlt">Bezahlt</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-4">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Rechnungsnr.</TableHead>
                  <TableHead>Datum</TableHead>
                  <TableHead>Fällig bis</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Brutto</TableHead>
                  <TableHead className="text-right">Offen</TableHead>
                  <TableHead>Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRechnungen.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground">
                      Keine Rechnungen gefunden
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredRechnungen.map((rechnung) => {
                    const status = statusConfig[rechnung.status]
                    const offenBetrag = rechnung.bruttobetrag - rechnung.bezahltBetrag
                    return (
                      <TableRow key={rechnung.id}>
                        <TableCell className="font-medium">{rechnung.rechnungsnummer}</TableCell>
                        <TableCell>{rechnung.datum}</TableCell>
                        <TableCell>{rechnung.faelligkeitsdatum}</TableCell>
                        <TableCell>
                          <Badge className={`${status.color} gap-1`}>
                            {status.icon}
                            {status.label}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          € {rechnung.bruttobetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          {offenBetrag > 0 
                            ? `€ ${offenBetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}`
                            : '-'
                          }
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedRechnung(rechnung)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Download className="h-4 w-4" />
                            </Button>
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
      <Dialog open={!!selectedRechnung} onOpenChange={() => setSelectedRechnung(null)}>
        <DialogContent className="max-w-lg">
          {selectedRechnung && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <Receipt className="h-5 w-5" />
                  Rechnung {selectedRechnung.rechnungsnummer}
                </DialogTitle>
                <DialogDescription>
                  Vom {selectedRechnung.datum}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4">
                {/* Status */}
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Status:</span>
                  <Badge className={`${statusConfig[selectedRechnung.status].color} gap-1`}>
                    {statusConfig[selectedRechnung.status].icon}
                    {statusConfig[selectedRechnung.status].label}
                  </Badge>
                </div>

                {/* Beträge */}
                <div className="space-y-2 rounded-lg border p-4">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Nettobetrag</span>
                    <span>€ {selectedRechnung.nettobetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">MwSt. (19%)</span>
                    <span>€ {selectedRechnung.mwst.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</span>
                  </div>
                  <div className="flex justify-between border-t pt-2 font-semibold">
                    <span>Bruttobetrag</span>
                    <span>€ {selectedRechnung.bruttobetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</span>
                  </div>
                  {selectedRechnung.bezahltBetrag > 0 && (
                    <>
                      <div className="flex justify-between text-emerald-600">
                        <span>Bezahlt</span>
                        <span>- € {selectedRechnung.bezahltBetrag.toLocaleString('de-DE', { minimumFractionDigits: 2 })}</span>
                      </div>
                      <div className="flex justify-between border-t pt-2 font-semibold text-amber-600">
                        <span>Noch offen</span>
                        <span>€ {(selectedRechnung.bruttobetrag - selectedRechnung.bezahltBetrag).toLocaleString('de-DE', { minimumFractionDigits: 2 })}</span>
                      </div>
                    </>
                  )}
                </div>

                {/* Fälligkeit */}
                <div className="flex items-center gap-2 rounded-lg bg-muted p-3">
                  <Calendar className="h-5 w-5 text-muted-foreground" />
                  <div>
                    <p className="text-sm text-muted-foreground">Zahlungsziel</p>
                    <p className="font-medium">{selectedRechnung.faelligkeitsdatum}</p>
                  </div>
                </div>

                {/* Bestellung */}
                {selectedRechnung.bestellung && (
                  <div className="flex items-center gap-2 rounded-lg bg-muted p-3">
                    <Receipt className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm text-muted-foreground">Bestellung</p>
                      <p className="font-medium">{selectedRechnung.bestellung}</p>
                    </div>
                  </div>
                )}

                {/* Download */}
                <Button className="w-full gap-2">
                  <Download className="h-4 w-4" />
                  Rechnung herunterladen
                </Button>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

function RechnungenSkeleton() {
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

