import { useMemo, useState } from 'react'
import { usePortalDokumente, usePortalLieferscheinCompliance } from '@/lib/api/portal'
import { buildDocumentRecord, buildDocumentWorkspace } from '@/lib/professional-workspaces'
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
import {
  NextActionPanel,
} from '@/components/workflow'

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
  const text = `${name} ${kategorie}`.toLowerCase()
  if (text.includes('naehrstoff')) return 'naehrstoff'
  if (text.includes('analyse')) return 'analyse'
  if (text.includes('deklaration')) return 'deklaration'
  if (text.includes('rechnung')) return 'rechnung'
  if (text.includes('vertrag')) return 'vertrag'
  if (text.includes('lieferschein') || text.includes('delivery') || text.includes(' dl-') || text.includes(' ls-')) return 'lieferschein'
  return 'sonstiges'
}

const typConfig: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  naehrstoff: { label: 'Naehrstoffbilanz', icon: <BarChart3 className="h-4 w-4" />, color: 'bg-emerald-100 text-emerald-800' },
  analyse: { label: 'Analyse', icon: <Beaker className="h-4 w-4" />, color: 'bg-blue-100 text-blue-800' },
  deklaration: { label: 'Deklaration', icon: <ScrollText className="h-4 w-4" />, color: 'bg-purple-100 text-purple-800' },
  rechnung: { label: 'Rechnung', icon: <FileText className="h-4 w-4" />, color: 'bg-amber-100 text-amber-800' },
  vertrag: { label: 'Vertrag', icon: <FileText className="h-4 w-4" />, color: 'bg-gray-100 text-gray-800' },
  lieferschein: { label: 'Lieferschein', icon: <File className="h-4 w-4" />, color: 'bg-cyan-100 text-cyan-800' },
  sonstiges: { label: 'Sonstiges', icon: <File className="h-4 w-4" />, color: 'bg-gray-100 text-gray-800' },
}

const formatIcons: Record<string, React.ReactNode> = {
  pdf: <FileText className="h-8 w-8 text-red-500" />,
  csv: <FileSpreadsheet className="h-8 w-8 text-green-500" />,
  xlsx: <FileSpreadsheet className="h-8 w-8 text-emerald-500" />,
}

export default function PortalDokumente(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('alle')
  const [selectedJahr, setSelectedJahr] = useState<string>('alle')

  const { data: portalDokumente = [], isLoading, isError, error, refetch } = usePortalDokumente()
  const { data: psmLieferscheine = [], isError: isPsmDocsError, error: psmDocsError } = usePortalLieferscheinCompliance()

  const dokumente: Dokument[] = portalDokumente.map((document) => {
    const ext = document.typ.toLowerCase()
    const dateiformat: Dokument['dateiformat'] = ext === 'csv' || ext === 'xlsx' ? ext : 'pdf'
    return {
      id: document.id,
      name: document.name,
      typ: inferDokumentTyp(document.name, document.kategorie),
      kategorie: document.kategorie,
      datum: document.datum,
      dateigroesse: `${document.groesse} KB`,
      dateiformat,
      jahr: Number(document.datum.slice(0, 4)),
    }
  })

  const documentRecords = useMemo(
    () =>
      dokumente.map((document) =>
        buildDocumentRecord({
          id: document.id,
          name: document.name,
          category: document.kategorie,
          type: document.typ,
          date: document.datum,
          sizeLabel: document.dateigroesse,
          owner: 'Portal',
          source: 'Portal',
        }),
      ),
    [dokumente],
  )

  const filteredDokumente = dokumente.filter((document) => {
    const matchesSearch = document.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      document.kategorie.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesTab = activeTab === 'alle' || document.typ === activeTab
    const matchesJahr = selectedJahr === 'alle' || (document.jahr && document.jahr.toString() === selectedJahr)
    return matchesSearch && matchesTab && matchesJahr
  })

  const filteredRecords = documentRecords.filter((record) => filteredDokumente.some((document) => document.id === record.id))
  const workspace = buildDocumentWorkspace(filteredRecords)
  const availableYears = [...new Set(dokumente.filter((document) => document.jahr).map((document) => document.jahr))].sort((a, b) => (b || 0) - (a || 0))
  const psmOpenIssues = psmLieferscheine.filter((entry) => entry.psmCompliance && entry.psmCompliance.compliant === false)
  const hasDocumentStopper = psmOpenIssues.length > 0 || workspace.total === 0
  const nextPortalAction = psmOpenIssues.length > 0
    ? 'Offene PSM-Hinweise zuerst pruefen und passenden Lieferschein oder Nachweis oeffnen.'
    : workspace.total === 0
      ? 'Dokumentfilter zuruecksetzen oder fehlendes Dokument beim Service anfragen.'
      : workspace.nextAction
  const documentStatusText = psmOpenIssues.length > 0
    ? `${psmOpenIssues.length} Hinweis(e) brauchen Ihre Pruefung.`
    : workspace.total === 0
      ? 'Keine passenden Dokumente in der aktuellen Auswahl.'
      : `${workspace.total} Dokument(e) sind fuer Sie verfuegbar.`

  if (isLoading) {
    return <DokumenteSkeleton />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Dokumente</h1>
        <p className="text-muted-foreground">Ihre Dokumente, Downloads und Hinweise zu Lieferscheinen oder Nachweisen</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <NextActionPanel
          title="Naechster sinnvoller Schritt"
          action={nextPortalAction}
          tone={hasDocumentStopper ? 'amber' : 'emerald'}
        />
        <Card>
          <CardContent className="space-y-2 p-4">
            <p className="text-sm font-semibold">Dokumentenstatus</p>
            <p className="text-sm text-muted-foreground">{documentStatusText}</p>
            <p className="text-xs text-muted-foreground">
              Nutzen Sie Suche, Jahr und Dokumenttyp, um schnell zum passenden Download zu kommen.
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="cursor-pointer transition-all hover:shadow-md" onClick={() => setActiveTab('naehrstoff')}>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
                <BarChart3 className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{dokumente.filter((document) => document.typ === 'naehrstoff').length}</p>
                <p className="text-sm text-muted-foreground">Naehrstoffbilanzen</p>
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
                <p className="text-2xl font-bold">{workspace.evidenceCount}</p>
                <p className="text-sm text-muted-foreground">Nachweisrelevant</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="transition-all hover:shadow-md">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-amber-100 p-2 text-amber-600">
                <AlertTriangle className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{psmOpenIssues.length}</p>
                <p className="text-sm text-muted-foreground">PSM-Offenpunkte</p>
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
                <p className="text-2xl font-bold">{workspace.total}</p>
                <p className="text-sm text-muted-foreground">Gesamt</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <Card>
          <CardContent className="grid gap-3 p-4 md:grid-cols-3">
            <div className="rounded-lg border p-4">
              <div className="text-sm text-muted-foreground">Vorgangsbelegte Dokumente</div>
              <div className="mt-2 text-2xl font-bold">{workspace.workflowCount}</div>
              <div className="mt-1 text-sm text-muted-foreground">Direkt an Lieferschein, Rechnung oder Vertrag angedockt</div>
            </div>
            <div className="rounded-lg border p-4">
              <div className="text-sm text-muted-foreground">Wiedervorlagen</div>
              <div className="mt-2 text-2xl font-bold">{workspace.followUpCount}</div>
              <div className="mt-1 text-sm text-muted-foreground">Ablauf- oder Nachweisdokumente mit Pruefpflicht</div>
            </div>
            <div className="rounded-lg border p-4">
              <div className="text-sm text-muted-foreground">Naechste Aktion</div>
              <div className="mt-2 font-semibold">{workspace.nextAction}</div>
              <div className="mt-1 text-sm text-muted-foreground">
                {workspace.latestDate ? `Letzter Eingang: ${new Date(workspace.latestDate).toLocaleDateString('de-DE')}` : 'Noch keine Dokumentbewegung'}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="space-y-3 p-4">
            <div className="flex items-center gap-2 font-semibold">
              <ShieldCheck className="h-4 w-4 text-emerald-600" />
              Compliance-Spur
            </div>
            {isPsmDocsError ? (
              <div className="text-sm text-red-600">{(psmDocsError as Error)?.message || 'PSM-Compliance nicht erreichbar'}</div>
            ) : (
              psmLieferscheine.slice(0, 3).map((entry) => (
                <div key={entry.number} className="rounded-lg border p-3 text-sm">
                  <div className="font-medium">{entry.number}</div>
                  <div className="text-muted-foreground">{entry.supplierName || 'ohne Lieferant'} am {entry.date}</div>
                  <div className="mt-1">
                    <Badge variant={entry.psmCompliance?.compliant ? 'outline' : 'destructive'}>
                      {entry.psmCompliance?.compliant ? 'vollstaendig' : 'Nachweis pruefen'}
                    </Badge>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

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

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="flex-wrap">
          <TabsTrigger value="alle">Alle</TabsTrigger>
          <TabsTrigger value="naehrstoff">Naehrstoffbilanzen</TabsTrigger>
          <TabsTrigger value="analyse">Analysen</TabsTrigger>
          <TabsTrigger value="deklaration">Deklarationen</TabsTrigger>
          <TabsTrigger value="rechnung">Rechnungen</TabsTrigger>
          <TabsTrigger value="lieferschein">Lieferscheine</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="mt-4">
          {filteredDokumente.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <FolderOpen className="mb-4 h-12 w-12 text-muted-foreground" />
                <p className="text-muted-foreground">Keine Dokumente gefunden</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-3">
              {filteredDokumente.map((dokument) => {
                const typ = typConfig[dokument.typ]
                const record = filteredRecords.find((entry) => entry.id === dokument.id)
                return (
                  <Card key={dokument.id} className="transition-all hover:shadow-md">
                    <CardContent className="flex items-center gap-4 p-4">
                      <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-muted">
                        {formatIcons[dokument.dateiformat]}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate font-medium">{dokument.name}</p>
                        <div className="mt-1 flex flex-wrap items-center gap-2">
                          <Badge className={`${typ.color} gap-1`}>
                            {typ.icon}
                            {typ.label}
                          </Badge>
                          {record ? <Badge variant="outline">{record.objectKind}: {record.objectRef}</Badge> : null}
                          <span className="text-sm text-muted-foreground">{dokument.kategorie}</span>
                          {dokument.produkt ? <span className="text-sm text-muted-foreground">- {dokument.produkt}</span> : null}
                        </div>
                        {record ? <div className="mt-2 text-sm text-muted-foreground">{record.followUp}</div> : null}
                      </div>
                      <div className="hidden flex-col items-end gap-1 text-sm text-muted-foreground sm:flex">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {dokument.datum}
                        </span>
                        <span>{dokument.dateigroesse}</span>
                      </div>
                      <Button className="shrink-0 gap-2">
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

function DokumenteSkeleton(): JSX.Element {
  return (
    <div className="space-y-6">
      <Skeleton className="h-16 w-72" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, index) => (
          <Skeleton key={index} className="h-28 rounded-xl" />
        ))}
      </div>
      <Skeleton className="h-14 w-full" />
      <div className="grid gap-3">
        {[...Array(6)].map((_, index) => (
          <Skeleton key={index} className="h-24 rounded-xl" />
        ))}
      </div>
    </div>
  )
}
