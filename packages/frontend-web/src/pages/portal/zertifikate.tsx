/**
 * Kundenportal - Zertifikate
 * 
 * GMP+, VLOG, QS und andere Zertifikate zum Download
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Search,
  Download,
  Award,
  Shield,
  CheckCircle2,
  AlertCircle,
  Calendar,
  Clock,
  ExternalLink,
  FileCheck,
  Leaf,
} from 'lucide-react'

interface Zertifikat {
  id: string
  name: string
  typ: string
  aussteller: string
  gueltigVon: string
  gueltigBis: string
  status: 'gueltig' | 'auslaufend' | 'abgelaufen'
  beschreibung: string
  dokument: string
  logo?: string
}

const mockZertifikate: Zertifikat[] = [
  {
    id: '1',
    name: 'GMP+ B3 Zertifikat',
    typ: 'GMP+',
    aussteller: 'TÜV SÜD',
    gueltigVon: '2024-01-15',
    gueltigBis: '2027-01-14',
    status: 'gueltig',
    beschreibung: 'Qualitätssicherung für Handel und Lagerung von Futtermitteln',
    dokument: 'gmp-b3-2024.pdf',
  },
  {
    id: '2',
    name: 'VLOG Zertifikat',
    typ: 'VLOG',
    aussteller: 'Verband Lebensmittel ohne Gentechnik',
    gueltigVon: '2024-03-01',
    gueltigBis: '2025-02-28',
    status: 'gueltig',
    beschreibung: 'Ohne Gentechnik - Futtermittel nach VLOG Standard',
    dokument: 'vlog-2024.pdf',
  },
  {
    id: '3',
    name: 'QS-Zertifikat Futtermittel',
    typ: 'QS',
    aussteller: 'QS Qualität und Sicherheit GmbH',
    gueltigVon: '2024-06-01',
    gueltigBis: '2025-05-31',
    status: 'gueltig',
    beschreibung: 'QS-System Futtermittelwirtschaft',
    dokument: 'qs-futtermittel-2024.pdf',
  },
  {
    id: '4',
    name: 'Bio-Zertifikat DE-ÖKO-006',
    typ: 'Bio',
    aussteller: 'ABCERT AG',
    gueltigVon: '2024-01-01',
    gueltigBis: '2024-12-31',
    status: 'auslaufend',
    beschreibung: 'Ökologischer Landbau nach EU-Öko-Verordnung',
    dokument: 'bio-2024.pdf',
  },
  {
    id: '5',
    name: 'ISO 9001:2015',
    typ: 'ISO',
    aussteller: 'DQS GmbH',
    gueltigVon: '2023-04-01',
    gueltigBis: '2026-03-31',
    status: 'gueltig',
    beschreibung: 'Qualitätsmanagementsystem',
    dokument: 'iso-9001-2023.pdf',
  },
  {
    id: '6',
    name: 'AMA Gütesiegel',
    typ: 'AMA',
    aussteller: 'Agrarmarkt Austria',
    gueltigVon: '2023-08-01',
    gueltigBis: '2024-07-31',
    status: 'abgelaufen',
    beschreibung: 'AMA-Gütesiegel für landwirtschaftliche Produkte',
    dokument: 'ama-2023.pdf',
  },
  {
    id: '7',
    name: 'GLOBALG.A.P.',
    typ: 'GLOBALG.A.P.',
    aussteller: 'GLOBALG.A.P. c/o FoodPLUS GmbH',
    gueltigVon: '2024-02-15',
    gueltigBis: '2025-02-14',
    status: 'gueltig',
    beschreibung: 'Good Agricultural Practice - Primärproduktion',
    dokument: 'globalgap-2024.pdf',
  },
]

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode; bgColor: string }> = {
  'gueltig': { 
    label: 'Gültig', 
    color: 'bg-emerald-100 text-emerald-800', 
    icon: <CheckCircle2 className="h-4 w-4" />,
    bgColor: 'border-l-emerald-500',
  },
  'auslaufend': { 
    label: 'Läuft bald aus', 
    color: 'bg-amber-100 text-amber-800', 
    icon: <AlertCircle className="h-4 w-4" />,
    bgColor: 'border-l-amber-500',
  },
  'abgelaufen': { 
    label: 'Abgelaufen', 
    color: 'bg-red-100 text-red-800', 
    icon: <Clock className="h-4 w-4" />,
    bgColor: 'border-l-red-500',
  },
}

const typColors: Record<string, string> = {
  'GMP+': 'bg-blue-600 text-white',
  'VLOG': 'bg-green-600 text-white',
  'QS': 'bg-orange-500 text-white',
  'Bio': 'bg-emerald-600 text-white',
  'ISO': 'bg-purple-600 text-white',
  'AMA': 'bg-red-600 text-white',
  'GLOBALG.A.P.': 'bg-teal-600 text-white',
}

export default function PortalZertifikate() {
  const [loading, setLoading] = useState(true)
  const [zertifikate, setZertifikate] = useState<Zertifikat[]>([])
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    const timer = setTimeout(() => {
      setZertifikate(mockZertifikate)
      setLoading(false)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  const filteredZertifikate = zertifikate.filter((z) =>
    z.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    z.typ.toLowerCase().includes(searchTerm.toLowerCase()) ||
    z.aussteller.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const gueltigeZertifikate = zertifikate.filter(z => z.status === 'gueltig').length
  const auslaufendeZertifikate = zertifikate.filter(z => z.status === 'auslaufend').length
  const abgelaufeneZertifikate = zertifikate.filter(z => z.status === 'abgelaufen').length

  if (loading) {
    return <ZertifikateSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Zertifikate</h1>
        <p className="text-muted-foreground">Alle Zertifikate und Qualitätsnachweise zum Download</p>
      </div>

      {/* Warnung bei auslaufenden Zertifikaten */}
      {auslaufendeZertifikate > 0 && (
        <Alert className="border-amber-200 bg-amber-50">
          <AlertCircle className="h-4 w-4 text-amber-600" />
          <AlertTitle className="text-amber-800">Zertifikate laufen bald aus</AlertTitle>
          <AlertDescription className="text-amber-700">
            {auslaufendeZertifikate} Zertifikat(e) laufen in den nächsten Wochen aus.
            Bitte kontaktieren Sie uns für eine Verlängerung.
          </AlertDescription>
        </Alert>
      )}

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
                <CheckCircle2 className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{gueltigeZertifikate}</p>
                <p className="text-sm text-muted-foreground">Gültige Zertifikate</p>
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
                <p className="text-2xl font-bold">{auslaufendeZertifikate}</p>
                <p className="text-sm text-muted-foreground">Laufen bald aus</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-purple-100 p-2 text-purple-600">
                <Award className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{zertifikate.length}</p>
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
          placeholder="Zertifikat suchen..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Zertifikate Grid */}
      <div className="grid gap-4 md:grid-cols-2">
        {filteredZertifikate.map((zertifikat) => {
          const status = statusConfig[zertifikat.status]
          return (
            <Card 
              key={zertifikat.id} 
              className={`border-l-4 transition-all hover:shadow-md ${status.bgColor}`}
            >
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                      <Award className="h-6 w-6 text-muted-foreground" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{zertifikat.name}</CardTitle>
                      <CardDescription>{zertifikat.aussteller}</CardDescription>
                    </div>
                  </div>
                  <Badge className={typColors[zertifikat.typ] || 'bg-gray-600 text-white'}>
                    {zertifikat.typ}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">{zertifikat.beschreibung}</p>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">
                      {zertifikat.gueltigVon} - {zertifikat.gueltigBis}
                    </span>
                  </div>
                  <Badge className={`${status.color} gap-1`}>
                    {status.icon}
                    {status.label}
                  </Badge>
                </div>

                <Button className="w-full gap-2">
                  <Download className="h-4 w-4" />
                  Zertifikat herunterladen
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {filteredZertifikate.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Award className="h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Keine Zertifikate gefunden</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function ZertifikateSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-10 w-48" />
      <div className="grid gap-4 sm:grid-cols-3">
        {[...Array(3)].map((_, i) => (
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
              <Skeleton className="h-12 w-full" />
            </CardHeader>
            <CardContent className="space-y-3">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-10 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

