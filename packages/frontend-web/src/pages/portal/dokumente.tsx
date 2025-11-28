/**
 * Kundenportal - Dokumente
 * 
 * Download-Center für alle Kundendokumente
 * Nährstoffbilanzen, Analysen, Deklarationen etc.
 */

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Search,
  Download,
  FileText,
  FileSpreadsheet,
  File,
  Calendar,
  Filter,
  FolderOpen,
  BarChart3,
  Award,
  Beaker,
  ScrollText,
  Wheat,
  ChevronRight,
  Eye,
} from 'lucide-react'

interface Dokument {
  id: string
  name: string
  typ: 'naehrstoff' | 'analyse' | 'deklaration' | 'rechnung' | 'vertrag' | 'lieferschein' | 'sonstiges'
  kategorie: string
  datum: string
  dateigroesse: string
  dateiformat: 'pdf' | 'csv' | 'xlsx'
  jahr?: number
  produkt?: string
}

const mockDokumente: Dokument[] = [
  // Nährstoffbilanzen
  { id: '1', name: 'Nährstoffbilanz 2024', typ: 'naehrstoff', kategorie: 'Jahresübersicht', datum: '2024-11-20', dateigroesse: '245 KB', dateiformat: 'pdf', jahr: 2024 },
  { id: '2', name: 'Nährstoffbilanz 2023', typ: 'naehrstoff', kategorie: 'Jahresübersicht', datum: '2024-01-15', dateigroesse: '238 KB', dateiformat: 'pdf', jahr: 2023 },
  { id: '3', name: 'Stoffstrombilanz 2024', typ: 'naehrstoff', kategorie: 'Stoffstrom', datum: '2024-11-15', dateigroesse: '312 KB', dateiformat: 'pdf', jahr: 2024 },
  
  // Analysen
  { id: '4', name: 'Bodenprobe Schlag 1 - Herbst 2024', typ: 'analyse', kategorie: 'Bodenanalyse', datum: '2024-10-20', dateigroesse: '156 KB', dateiformat: 'pdf', produkt: 'Winterweizen' },
  { id: '5', name: 'Futtermittelanalyse MLF 18%', typ: 'analyse', kategorie: 'Futtermittel', datum: '2024-09-15', dateigroesse: '189 KB', dateiformat: 'pdf', produkt: 'Milchleistungsfutter' },
  { id: '6', name: 'Silageanalyse Grassilage 2024', typ: 'analyse', kategorie: 'Futtermittel', datum: '2024-08-01', dateigroesse: '142 KB', dateiformat: 'pdf' },
  
  // Deklarationen
  { id: '7', name: 'Produktdeklaration NPK 15-15-15', typ: 'deklaration', kategorie: 'Düngemittel', datum: '2024-01-01', dateigroesse: '98 KB', dateiformat: 'pdf', produkt: 'NPK 15-15-15' },
  { id: '8', name: 'Sicherheitsdatenblatt Glyphosat 360', typ: 'deklaration', kategorie: 'Pflanzenschutz', datum: '2024-01-01', dateigroesse: '425 KB', dateiformat: 'pdf', produkt: 'Glyphosat 360' },
  { id: '9', name: 'Futtermittel-Deklaration MLF 18%', typ: 'deklaration', kategorie: 'Futtermittel', datum: '2024-06-01', dateigroesse: '112 KB', dateiformat: 'pdf', produkt: 'Milchleistungsfutter' },
  
  // Rechnungen
  { id: '10', name: 'Rechnung R-2024-0567', typ: 'rechnung', kategorie: 'Rechnung', datum: '2024-11-15', dateigroesse: '78 KB', dateiformat: 'pdf' },
  { id: '11', name: 'Rechnung R-2024-0542', typ: 'rechnung', kategorie: 'Rechnung', datum: '2024-11-01', dateigroesse: '82 KB', dateiformat: 'pdf' },
  
  // Lieferscheine
  { id: '12', name: 'Lieferschein LS-2024-1234', typ: 'lieferschein', kategorie: 'Lieferschein', datum: '2024-11-20', dateigroesse: '45 KB', dateiformat: 'pdf' },
  { id: '13', name: 'Lieferschein LS-2024-1198', typ: 'lieferschein', kategorie: 'Lieferschein', datum: '2024-11-10', dateigroesse: '42 KB', dateiformat: 'pdf' },
]

const typConfig: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  'naehrstoff': { label: 'Nährstoffbilanz', icon: <BarChart3 className="h-4 w-4" />, color: 'bg-emerald-100 text-emerald-800' },
  'analyse': { label: 'Analyse', icon: <Beaker className="h-4 w-4" />, color: 'bg-blue-100 text-blue-800' },
  'deklaration': { label: 'Deklaration', icon: <ScrollText className="h-4 w-4" />, color: 'bg-purple-100 text-purple-800' },
  'rechnung': { label: 'Rechnung', icon: <FileText className="h-4 w-4" />, color: 'bg-amber-100 text-amber-800' },
  'vertrag': { label: 'Vertrag', icon: <FileText className="h-4 w-4" />, color: 'bg-gray-100 text-gray-800' },
  'lieferschein': { label: 'Lieferschein', icon: <File className="h-4 w-4" />, color: 'bg-cyan-100 text-cyan-800' },
  'sonstiges': { label: 'Sonstiges', icon: <File className="h-4 w-4" />, color: 'bg-gray-100 text-gray-800' },
}

const formatIcons: Record<string, React.ReactNode> = {
  'pdf': <FileText className="h-8 w-8 text-red-500" />,
  'csv': <FileSpreadsheet className="h-8 w-8 text-green-500" />,
  'xlsx': <FileSpreadsheet className="h-8 w-8 text-emerald-500" />,
}

export default function PortalDokumente() {
  const [loading, setLoading] = useState(true)
  const [dokumente, setDokumente] = useState<Dokument[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('alle')
  const [selectedJahr, setSelectedJahr] = useState<string>('alle')

  useEffect(() => {
    const timer = setTimeout(() => {
      setDokumente(mockDokumente)
      setLoading(false)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  const filteredDokumente = dokumente.filter((d) => {
    const matchesSearch = d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.kategorie.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesTab = activeTab === 'alle' || d.typ === activeTab
    const matchesJahr = selectedJahr === 'alle' || (d.jahr && d.jahr.toString() === selectedJahr)
    return matchesSearch && matchesTab && matchesJahr
  })

  const availableYears = [...new Set(dokumente.filter(d => d.jahr).map(d => d.jahr))].sort((a, b) => (b || 0) - (a || 0))

  if (loading) {
    return <DokumenteSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold">Dokumente</h1>
        <p className="text-muted-foreground">Alle Ihre Dokumente zum Download</p>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="cursor-pointer transition-all hover:shadow-md" onClick={() => setActiveTab('naehrstoff')}>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
                <BarChart3 className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {dokumente.filter(d => d.typ === 'naehrstoff').length}
                </p>
                <p className="text-sm text-muted-foreground">Nährstoffbilanzen</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer transition-all hover:shadow-md" onClick={() => setActiveTab('analyse')}>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-100 p-2 text-blue-600">
                <Beaker className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {dokumente.filter(d => d.typ === 'analyse').length}
                </p>
                <p className="text-sm text-muted-foreground">Analysen</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer transition-all hover:shadow-md" onClick={() => setActiveTab('deklaration')}>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-purple-100 p-2 text-purple-600">
                <ScrollText className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {dokumente.filter(d => d.typ === 'deklaration').length}
                </p>
                <p className="text-sm text-muted-foreground">Deklarationen</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer transition-all hover:shadow-md" onClick={() => setActiveTab('alle')}>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-gray-100 p-2 text-gray-600">
                <FolderOpen className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{dokumente.length}</p>
                <p className="text-sm text-muted-foreground">Gesamt</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col gap-4 md:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Dokument suchen..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={selectedJahr} onValueChange={setSelectedJahr}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Jahr wählen" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="alle">Alle Jahre</SelectItem>
            {availableYears.map((jahr) => (
              <SelectItem key={jahr} value={jahr?.toString() || ''}>
                {jahr}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="flex-wrap">
          <TabsTrigger value="alle">Alle</TabsTrigger>
          <TabsTrigger value="naehrstoff">Nährstoffbilanzen</TabsTrigger>
          <TabsTrigger value="analyse">Analysen</TabsTrigger>
          <TabsTrigger value="deklaration">Deklarationen</TabsTrigger>
          <TabsTrigger value="rechnung">Rechnungen</TabsTrigger>
          <TabsTrigger value="lieferschein">Lieferscheine</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-4">
          {filteredDokumente.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <FolderOpen className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Keine Dokumente gefunden</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-3">
              {filteredDokumente.map((dokument) => {
                const typ = typConfig[dokument.typ]
                return (
                  <Card key={dokument.id} className="transition-all hover:shadow-md">
                    <CardContent className="flex items-center gap-4 p-4">
                      <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-muted">
                        {formatIcons[dokument.dateiformat]}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{dokument.name}</p>
                        <div className="flex flex-wrap items-center gap-2 mt-1">
                          <Badge className={`${typ.color} gap-1`}>
                            {typ.icon}
                            {typ.label}
                          </Badge>
                          <span className="text-sm text-muted-foreground">{dokument.kategorie}</span>
                          {dokument.produkt && (
                            <span className="text-sm text-muted-foreground">• {dokument.produkt}</span>
                          )}
                        </div>
                      </div>
                      <div className="hidden sm:flex flex-col items-end gap-1 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {dokument.datum}
                        </span>
                        <span>{dokument.dateigroesse}</span>
                      </div>
                      <Button className="gap-2 shrink-0">
                        <Download className="h-4 w-4" />
                        <span className="hidden sm:inline">Download</span>
                      </Button>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

function DokumenteSkeleton() {
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
      <div className="flex gap-4">
        <Skeleton className="h-10 flex-1" />
        <Skeleton className="h-10 w-[150px]" />
      </div>
      <div className="space-y-3">
        {[...Array(6)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-14 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

