/**
 * Kundenportal - Dokumente
 * 
 * Download-Center für alle Kundendokumente
 * Nährstoffbilanzen, Analysen, Deklarationen etc.
 */

import { useState } from 'react'
import { usePortalDokumente, usePortalLieferscheinCompliance } from '@/lib/api/portal'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { NativeSelect } from '@/components/ui/native-select'
import {
  Search,
  Download,
  FileText,
  FileSpreadsheet,
  File,
  Calendar,
  FolderOpen,
  BarChart3,
  Beaker,
  ScrollText,
  AlertTriangle,
  ShieldCheck,
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

function inferDokumentTyp(name: string, kategorie: string): Dokument['typ'] {
  const x = `${name} ${kategorie}`.toLowerCase()
  if (x.includes('naehrstoff')) return 'naehrstoff'
  if (x.includes('analyse')) return 'analyse'
  if (x.includes('deklaration')) return 'deklaration'
  if (x.includes('rechnung')) return 'rechnung'
  if (x.includes('vertrag')) return 'vertrag'
  if (x.includes('lieferschein') || x.includes('delivery') || x.includes(' dl-') || x.includes(' ls-')) return 'lieferschein'
  return 'sonstiges'
}


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
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('alle')
  const [selectedJahr, setSelectedJahr] = useState<string>('alle')

  const { data: portalDokumente = [], isLoading, isError, error, refetch } = usePortalDokumente()
  const { data: psmLieferscheine = [], isError: isPsmDocsError, error: psmDocsError } = usePortalLieferscheinCompliance()
  const dokumente: Dokument[] = portalDokumente.map((d) => {
    const ext = d.typ.toLowerCase()
    const dateiformat: Dokument['dateiformat'] = ext === 'csv' || ext === 'xlsx' ? ext : 'pdf'
    return {
      id: d.id,
      name: d.name,
      typ: inferDokumentTyp(d.name, d.kategorie),
      kategorie: d.kategorie,
      datum: d.datum,
      dateigroesse: `${d.groesse} KB`,
      dateiformat,
      jahr: Number(d.datum.slice(0, 4)),
    }
  })

  const filteredDokumente = dokumente.filter((d) => {
    const matchesSearch = d.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.kategorie.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesTab = activeTab === 'alle' || d.typ === activeTab
    const matchesJahr = selectedJahr === 'alle' || (d.jahr && d.jahr.toString() === selectedJahr)
    return matchesSearch && matchesTab && matchesJahr
  })

  const availableYears = [...new Set(dokumente.filter(d => d.jahr).map(d => d.jahr))].sort((a, b) => (b || 0) - (a || 0))

  if (isLoading) {
    return <DokumenteSkeleton />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
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
        <NativeSelect
          value={selectedJahr}
          onValueChange={setSelectedJahr}
          placeholder="Jahr waehlen"
          options={[{ value: 'alle', label: 'Alle Jahre' }, ...availableYears.map((jahr) => ({ value: jahr?.toString() || '', label: String(jahr) }))]}
        />
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

      <Card>
        <CardContent className="p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">PSM-Lieferschein Nachweise</h3>
            <Badge variant="secondary">{psmLieferscheine.length} Belege</Badge>
          </div>
          {isPsmDocsError && (
            <div className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {(psmDocsError as Error)?.message || 'PSM-Lieferscheine konnten nicht geladen werden.'}
            </div>
          )}
          {psmLieferscheine.slice(0, 10).map((ls) => {
            const compliance = ls.psmCompliance
            const missing = compliance?.missingMandatoryFields ?? []
            const hinweise = compliance?.hinweise ?? []
            const ok = Boolean(compliance?.compliant)
            return (
              <div key={ls.number} className="rounded-lg border p-3 space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="font-medium">{ls.number}</div>
                  <Badge className={ok ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}>
                    {ok ? <ShieldCheck className="mr-1 h-3 w-3" /> : <AlertTriangle className="mr-1 h-3 w-3" />}
                    {ok ? 'Konform' : 'Pruefen'}
                  </Badge>
                </div>
                <div className="grid gap-2 text-sm sm:grid-cols-4">
                  <div>N: <span className="font-medium">{Number(ls.totalNutrientNKg ?? 0).toFixed(3)} kg</span></div>
                  <div>P2O5: <span className="font-medium">{Number(ls.totalNutrientP2o5Kg ?? 0).toFixed(3)} kg</span></div>
                  <div>CO2e: <span className="font-medium">{Number(ls.totalCo2eKg ?? 0).toFixed(3)} kg</span></div>
                  <div>ADR: <span className="font-medium">{Number(compliance?.adrPunkte ?? 0).toFixed(1)}</span></div>
                </div>
                <div className="text-xs text-muted-foreground">
                  Lieferant: {ls.supplierName || '-'} • Sachkunde: {compliance?.sachkundeStatus || '-'} • SDB: {compliance?.sdsMitgeliefert || '-'}
                </div>
                {missing.length > 0 && (
                  <div className="text-xs text-red-600">
                    Fehlende Pflichtangaben: {missing.join(' | ')}
                  </div>
                )}
                {hinweise.length > 0 && (
                  <div className="text-xs text-amber-700">
                    Hinweise: {hinweise.join(' | ')}
                  </div>
                )}
              </div>
            )
          })}
        </CardContent>
      </Card>
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

