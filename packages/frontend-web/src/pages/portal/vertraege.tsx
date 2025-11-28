/**
 * Kundenportal - Verträge
 * 
 * Übersicht aller Verträge und Kontrakte des Kunden
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
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
  FileText,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Clock,
  Eye,
  Download,
  ChevronRight,
  TrendingUp,
  Package,
} from 'lucide-react'

interface Vertrag {
  id: string
  bezeichnung: string
  typ: 'liefervertrag' | 'rahmenvertrag' | 'preiskontrakt'
  produkt: string
  startdatum: string
  enddatum: string
  status: 'aktiv' | 'abgelaufen' | 'auslaufend'
  gesamtmenge: number
  gelieferteMenge: number
  einheit: string
  preis: number
  dokument?: string
}

const mockVertraege: Vertrag[] = [
  {
    id: 'V-2024-001',
    bezeichnung: 'Futtermittel-Rahmenvertrag 2024',
    typ: 'rahmenvertrag',
    produkt: 'Milchleistungsfutter 18%',
    startdatum: '2024-01-01',
    enddatum: '2024-12-31',
    status: 'aktiv',
    gesamtmenge: 500,
    gelieferteMenge: 380,
    einheit: 'dt',
    preis: 36.50,
    dokument: 'vertrag-v-2024-001.pdf',
  },
  {
    id: 'V-2024-002',
    bezeichnung: 'PSM-Preiskontrakt Q4',
    typ: 'preiskontrakt',
    produkt: 'Glyphosat 360',
    startdatum: '2024-10-01',
    enddatum: '2024-12-31',
    status: 'auslaufend',
    gesamtmenge: 200,
    gelieferteMenge: 120,
    einheit: 'l',
    preis: 7.80,
    dokument: 'vertrag-v-2024-002.pdf',
  },
  {
    id: 'V-2024-003',
    bezeichnung: 'Saatgut-Liefervertrag Winterweizen',
    typ: 'liefervertrag',
    produkt: 'Winterweizen Premium',
    startdatum: '2024-08-01',
    enddatum: '2024-10-31',
    status: 'abgelaufen',
    gesamtmenge: 100,
    gelieferteMenge: 100,
    einheit: 'dt',
    preis: 62.00,
    dokument: 'vertrag-v-2024-003.pdf',
  },
  {
    id: 'V-2024-004',
    bezeichnung: 'Düngemittel-Jahresvertrag',
    typ: 'rahmenvertrag',
    produkt: 'NPK 15-15-15',
    startdatum: '2024-01-01',
    enddatum: '2024-12-31',
    status: 'aktiv',
    gesamtmenge: 300,
    gelieferteMenge: 180,
    einheit: 'dt',
    preis: 38.00,
    dokument: 'vertrag-v-2024-004.pdf',
  },
]

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  'aktiv': { label: 'Aktiv', color: 'bg-emerald-100 text-emerald-800', icon: <CheckCircle2 className="h-4 w-4" /> },
  'auslaufend': { label: 'Läuft bald aus', color: 'bg-amber-100 text-amber-800', icon: <AlertCircle className="h-4 w-4" /> },
  'abgelaufen': { label: 'Abgelaufen', color: 'bg-gray-100 text-gray-800', icon: <Clock className="h-4 w-4" /> },
}

const typConfig: Record<string, { label: string; color: string }> = {
  'liefervertrag': { label: 'Liefervertrag', color: 'bg-blue-100 text-blue-800' },
  'rahmenvertrag': { label: 'Rahmenvertrag', color: 'bg-purple-100 text-purple-800' },
  'preiskontrakt': { label: 'Preiskontrakt', color: 'bg-amber-100 text-amber-800' },
}

export default function PortalVertraege() {
  const [loading, setLoading] = useState(true)
  const [vertraege, setVertraege] = useState<Vertrag[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedVertrag, setSelectedVertrag] = useState<Vertrag | null>(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      setVertraege(mockVertraege)
      setLoading(false)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  const filteredVertraege = vertraege.filter((v) =>
    v.bezeichnung.toLowerCase().includes(searchTerm.toLowerCase()) ||
    v.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    v.produkt.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const aktiveVertraege = vertraege.filter(v => v.status === 'aktiv').length
  const auslaufendeVertraege = vertraege.filter(v => v.status === 'auslaufend').length
  const gesamtVolumen = vertraege
    .filter(v => v.status !== 'abgelaufen')
    .reduce((sum, v) => sum + v.gesamtmenge * v.preis, 0)

  if (loading) {
    return <VertrageSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Verträge & Kontrakte</h1>
        <p className="text-muted-foreground">Übersicht aller Ihrer Verträge</p>
      </div>

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
                <CheckCircle2 className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{aktiveVertraege}</p>
                <p className="text-sm text-muted-foreground">Aktive Verträge</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-amber-100 p-2 text-amber-600">
                <AlertCircle className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{auslaufendeVertraege}</p>
                <p className="text-sm text-muted-foreground">Laufen bald aus</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-purple-100 p-2 text-purple-600">
                <TrendingUp className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  € {(gesamtVolumen / 1000).toFixed(1)}k
                </p>
                <p className="text-sm text-muted-foreground">Vertragsvolumen</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-100 p-2 text-blue-600">
                <FileText className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{vertraege.length}</p>
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
          placeholder="Vertrag suchen..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Verträge Grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {filteredVertraege.map((vertrag) => {
          const status = statusConfig[vertrag.status]
          const typ = typConfig[vertrag.typ]
          const erfuellung = Math.round((vertrag.gelieferteMenge / vertrag.gesamtmenge) * 100)

          return (
            <Card key={vertrag.id} className="transition-all hover:shadow-md">
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-base">{vertrag.bezeichnung}</CardTitle>
                    <CardDescription>{vertrag.id}</CardDescription>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <Badge className={`${status.color} gap-1`}>
                      {status.icon}
                      {status.label}
                    </Badge>
                    <Badge className={typ.color}>{typ.label}</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="rounded-lg bg-muted p-3">
                  <p className="text-sm text-muted-foreground">Produkt</p>
                  <p className="font-medium">{vertrag.produkt}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Vertragspreis: € {vertrag.preis.toFixed(2)} / {vertrag.einheit}
                  </p>
                </div>

                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-muted-foreground">Erfüllung</span>
                    <span className="font-medium">{erfuellung}%</span>
                  </div>
                  <Progress value={erfuellung} className="h-2" />
                  <p className="text-xs text-muted-foreground mt-1">
                    {vertrag.gelieferteMenge} von {vertrag.gesamtmenge} {vertrag.einheit} geliefert
                  </p>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-1 text-muted-foreground">
                    <Calendar className="h-4 w-4" />
                    {vertrag.startdatum} - {vertrag.enddatum}
                  </div>
                  <div className="flex gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedVertrag(vertrag)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    {vertrag.dokument && (
                      <Button variant="ghost" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Detail Dialog */}
      <Dialog open={!!selectedVertrag} onOpenChange={() => setSelectedVertrag(null)}>
        <DialogContent className="max-w-2xl">
          {selectedVertrag && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  {selectedVertrag.bezeichnung}
                </DialogTitle>
                <DialogDescription>
                  Vertragsnummer: {selectedVertrag.id}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4">
                {/* Status Badges */}
                <div className="flex gap-2">
                  <Badge className={`${statusConfig[selectedVertrag.status].color} gap-1`}>
                    {statusConfig[selectedVertrag.status].icon}
                    {statusConfig[selectedVertrag.status].label}
                  </Badge>
                  <Badge className={typConfig[selectedVertrag.typ].color}>
                    {typConfig[selectedVertrag.typ].label}
                  </Badge>
                </div>

                {/* Vertragsdetails */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="rounded-lg bg-muted p-3">
                    <p className="text-sm text-muted-foreground">Produkt</p>
                    <p className="font-medium">{selectedVertrag.produkt}</p>
                  </div>
                  <div className="rounded-lg bg-muted p-3">
                    <p className="text-sm text-muted-foreground">Vertragspreis</p>
                    <p className="font-medium">€ {selectedVertrag.preis.toFixed(2)} / {selectedVertrag.einheit}</p>
                  </div>
                  <div className="rounded-lg bg-muted p-3">
                    <p className="text-sm text-muted-foreground">Laufzeit</p>
                    <p className="font-medium">{selectedVertrag.startdatum} - {selectedVertrag.enddatum}</p>
                  </div>
                  <div className="rounded-lg bg-muted p-3">
                    <p className="text-sm text-muted-foreground">Vertragsvolumen</p>
                    <p className="font-medium">
                      € {(selectedVertrag.gesamtmenge * selectedVertrag.preis).toLocaleString('de-DE', { minimumFractionDigits: 2 })}
                    </p>
                  </div>
                </div>

                {/* Erfüllung */}
                <div>
                  <h4 className="font-semibold mb-2">Vertragserfüllung</h4>
                  <Progress 
                    value={Math.round((selectedVertrag.gelieferteMenge / selectedVertrag.gesamtmenge) * 100)} 
                    className="h-3" 
                  />
                  <div className="flex justify-between mt-2 text-sm">
                    <span>Geliefert: {selectedVertrag.gelieferteMenge} {selectedVertrag.einheit}</span>
                    <span>Offen: {selectedVertrag.gesamtmenge - selectedVertrag.gelieferteMenge} {selectedVertrag.einheit}</span>
                  </div>
                </div>

                {/* Download Button */}
                {selectedVertrag.dokument && (
                  <Button className="w-full gap-2">
                    <Download className="h-4 w-4" />
                    Vertragsdokument herunterladen
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

function VertrageSkeleton() {
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
      <div className="grid gap-4 md:grid-cols-2">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-24" />
            </CardHeader>
            <CardContent className="space-y-4">
              <Skeleton className="h-20 w-full" />
              <Skeleton className="h-8 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

