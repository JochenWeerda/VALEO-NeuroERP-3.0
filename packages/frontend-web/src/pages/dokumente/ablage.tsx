import { useCallback, useMemo, useRef, useState, type ChangeEvent } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { useDokumenteAblage, type Dokument } from '@/lib/api/betrieb'
import { buildDocumentRecord, buildDocumentWorkspace } from '@/lib/professional-workspaces'
import { summarizeDocumentEvidence } from '@/lib/domain-depth'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { OperationalCaseHeader } from '@/components/workflow/OperationalCaseHeader'
import { OperationalContextPanel } from '@/components/workflow/OperationalContextPanel'
import { OperationalTimeline } from '@/components/workflow/OperationalTimeline'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { AlertTriangle, FileDown, FileText, Search, Upload } from 'lucide-react'
import { normalizeOperationalStatus } from '@/lib/operational-status'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { toast } from '@/hooks/use-toast'

const OBJECT_KIND_ROUTES: Record<string, string> = {
  Lieferschein: '/sales/lieferungen-liste',
  Rechnung: '/verkauf/rechnungen',
  Kontrakt: '/kontrakte',
  Bestellung: '/einkauf/bestellungen-liste',
}

function LoadingSkeleton(): JSX.Element {
  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div><Skeleton className="mt-2 h-8 w-56" /><Skeleton className="mt-2 h-4 w-32" /></div>
        <Skeleton className="h-11 w-32" />
      </div>
      <Card><CardHeader><Skeleton className="h-5 w-24" /></CardHeader><CardContent><div className="flex gap-4"><Skeleton className="h-11 w-full" /><Skeleton className="h-11 w-24" /></div></CardContent></Card>
      <Card><CardContent className="pt-6"><Skeleton className="h-64 w-full" /></CardContent></Card>
    </div>
  )
}

function ErrorState({ error, onRetry }: { error: Error | null; onRetry: () => void }): JSX.Element {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <AlertTriangle className="mb-4 h-12 w-12 text-status-error" />
      <h2 className="mb-2 text-xl font-semibold text-status-error">Backend nicht erreichbar</h2>
      <p className="mb-4 text-muted-foreground">
        {error?.message || 'Die Dokumenten-Daten konnten nicht geladen werden.'}
      </p>
      <Button onClick={onRetry} variant="outline" className="min-h-touch gap-2 touch-manipulation">
        <FileText className="h-4 w-4" />Erneut versuchen
      </Button>
    </div>
  )
}

function downloadTextFile(filename: string, body: string): void {
  const blob = new Blob([body], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

export default function DokumentenAblagePage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const [searchTerm, setSearchTerm] = useState('')
  const [pendingKeys, setPendingKeys] = useState<Set<string>>(() => new Set())
  const pendingRef = useRef<Set<string>>(new Set())
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { data: dokumente = [], isLoading, isError, error, refetch } = useDokumenteAblage()

  const documentRecords = useMemo(
    () =>
      dokumente.map((dokument) =>
        buildDocumentRecord({
          id: dokument.id,
          name: dokument.name,
          category: dokument.kategorie,
          type: dokument.typ,
          date: dokument.hochgeladen,
          sizeLabel: `${dokument.groesse} KB`,
          owner: dokument.benutzer,
          source: 'Ablage',
        }),
      ),
    [dokumente],
  )

  const filteredDokumente = useMemo(() => {
    if (!searchTerm) return dokumente
    const term = searchTerm.toLowerCase()
    return dokumente.filter((dokument) =>
      dokument.name.toLowerCase().includes(term) ||
      dokument.kategorie.toLowerCase().includes(term),
    )
  }, [dokumente, searchTerm])

  const filteredRecords = useMemo(
    () => documentRecords.filter((record) => filteredDokumente.some((document) => document.id === record.id)),
    [documentRecords, filteredDokumente],
  )
  const workspace = useMemo(() => buildDocumentWorkspace(filteredRecords), [filteredRecords])
  const evidenceSummary = useMemo(() => summarizeDocumentEvidence(filteredRecords), [filteredRecords])

  const withPending = useCallback(async (key: string, work: () => void | Promise<void>): Promise<void> => {
    if (pendingRef.current.has(key)) return
    pendingRef.current.add(key)
    setPendingKeys(new Set(pendingRef.current))
    try {
      await work()
    } finally {
      pendingRef.current.delete(key)
      setPendingKeys(new Set(pendingRef.current))
    }
  }, [])

  const handleDownload = useCallback((dokument: Dokument): void => {
    void withPending(`download:${dokument.id}`, () => {
      const record = filteredRecords.find((entry) => entry.id === dokument.id)
      const body = [
        'VALEO NeuroERP — Dokument-Metadaten',
        `Name: ${dokument.name}`,
        `Typ: ${dokument.typ}`,
        `Kategorie: ${dokument.kategorie}`,
        `Groesse: ${dokument.groesse} KB`,
        `Hochgeladen: ${dokument.hochgeladen}`,
        `Benutzer: ${dokument.benutzer}`,
        record ? `Objekt: ${record.objectKind} ${record.objectRef}` : '',
        '',
        'Die Ablage liefert noch keine Datei-URL. Es wurde ein Metadaten-Text exportiert.',
      ].filter((line) => line.length > 0).join('\n')
      const safeName = dokument.name.replace(/[^\w.-]+/g, '_').replace(/^_+|_+$/g, '') || dokument.id
      downloadTextFile(`${safeName}.txt`, body)
      toast({
        title: 'Metadaten heruntergeladen',
        description: `${dokument.name}: keine Datei-URL am Server, daher Metadaten-Text.`,
      })
    })
  }, [filteredRecords, withPending])

  const handleExport = useCallback((): void => {
    void withPending('export', () => {
      if (filteredDokumente.length === 0) {
        toast({
          title: 'Keine Daten',
          description: 'Es gibt keine Dokumente zum Exportieren.',
          variant: 'destructive',
        })
        return
      }
      const rows = [
        ['Name', 'Typ', 'Kategorie', 'Groesse_KB', 'Hochgeladen', 'Benutzer', 'Objekt'],
        ...filteredDokumente.map((dokument) => {
          const record = filteredRecords.find((entry) => entry.id === dokument.id)
          return [
            dokument.name,
            dokument.typ,
            dokument.kategorie,
            String(dokument.groesse),
            dokument.hochgeladen,
            dokument.benutzer,
            record ? `${record.objectKind} ${record.objectRef}` : '',
          ]
        }),
      ]
      const csv = rows.map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(';')).join('\n')
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `dokumente-export-${new Date().toISOString().split('T')[0]}.csv`
      link.click()
      URL.revokeObjectURL(url)
      toast({
        title: 'Export erfolgreich',
        description: `${filteredDokumente.length} Einträge wurden exportiert.`,
      })
    })
  }, [filteredDokumente, filteredRecords, withPending])

  const handleOpenObject = useCallback((dokument: Dokument): void => {
    const record = filteredRecords.find((entry) => entry.id === dokument.id)
    if (!record || record.objectRef === 'nicht zugeordnet') {
      toast({
        title: 'Kein Vorgang',
        description: `${dokument.name} ist keinem fachlichen Objekt zugeordnet.`,
        variant: 'destructive',
      })
      return
    }
    const route = OBJECT_KIND_ROUTES[record.objectKind]
    if (!route) {
      toast({
        title: 'Keine Maske',
        description: `${record.objectKind} ${record.objectRef} hat noch keine Zielmaske.`,
        variant: 'destructive',
      })
      return
    }
    navigate(route)
  }, [filteredRecords, navigate])

  const handleUploadClick = useCallback((): void => {
    fileInputRef.current?.click()
  }, [])

  const handleUploadChange = useCallback((event: ChangeEvent<HTMLInputElement>): void => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    toast({
      title: 'Upload nicht am Server',
      description: `${file.name} ist gewählt. GET /api/v1/dokumente hat noch keinen Upload-Endpunkt.`,
      variant: 'destructive',
    })
  }, [])

  if (isError && !isLoading) {
    return <ErrorState error={error} onRetry={refetch} />
  }

  if (isLoading) return <LoadingSkeleton />

  const columns = [
    {
      key: 'name' as const,
      label: 'Dokument',
      render: (dokument: Dokument) => {
        const record = filteredRecords.find((entry) => entry.id === dokument.id)
        return (
          <div>
            <div className="font-medium">{dokument.name}</div>
            <div className="mt-1 flex flex-wrap gap-2">
              <Badge variant="outline">{dokument.typ}</Badge>
              {record ? <Badge variant="outline">{record.objectKind}: {record.objectRef}</Badge> : null}
            </div>
          </div>
        )
      },
    },
    { key: 'kategorie' as const, label: 'Kategorie' },
    { key: 'groesse' as const, label: 'Groesse', render: (dokument: Dokument) => `${dokument.groesse} KB` },
    {
      key: 'hochgeladen' as const,
      label: 'Hochgeladen',
      render: (dokument: Dokument) => {
        const record = filteredRecords.find((entry) => entry.id === dokument.id)
        return (
          <div>
            <div>{new Date(dokument.hochgeladen).toLocaleDateString('de-DE')}</div>
            <div className="text-sm text-muted-foreground">{dokument.benutzer}</div>
            {record && !isTouch ? <div className="text-xs text-muted-foreground">{record.followUp}</div> : null}
          </div>
        )
      },
    },
    {
      key: 'actions' as const,
      label: 'Aktionen',
      render: (dokument: Dokument) => {
        const record = filteredRecords.find((entry) => entry.id === dokument.id)
        const downloadPending = pendingKeys.has(`download:${dokument.id}`)
        return (
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              className="min-h-touch touch-manipulation"
              disabled={downloadPending}
              onClick={() => handleDownload(dokument)}
            >
              {downloadPending ? 'Laedt…' : 'Download'}
            </Button>
            {record?.objectRef && record.objectRef !== 'nicht zugeordnet' ? (
              <Button
                variant="ghost"
                className="min-h-touch touch-manipulation"
                onClick={() => handleOpenObject(dokument)}
              >
                Zum Vorgang
              </Button>
            ) : null}
          </div>
        )
      },
    },
  ]

  const gesamtGroesse = filteredDokumente.reduce((sum, dokument) => sum + dokument.groesse, 0)
  const operationalStatus = normalizeOperationalStatus(
    evidenceSummary.evidenceRisk === 'hoch' ? 'eskaliert' : filteredRecords.length > 0 ? 'in_pruefung' : 'offen',
  )
  const contextSections = [
    {
      title: 'Nachweislage',
      items: [
        { label: 'Nachweisrelevant', value: `${workspace.evidenceCount}` },
        { label: 'Wiedervorlagen', value: `${workspace.followUpCount}` },
        { label: 'Ohne Objektbezug', value: `${evidenceSummary.unassignedCount}` },
      ],
    },
    {
      title: 'Vorgangsbezug',
      items: [
        { label: 'Workflow-Belege', value: `${workspace.workflowCount}` },
        { label: 'Naechste Aktion', value: evidenceSummary.nextAction },
        { label: 'Arbeitsbild', value: workspace.nextAction },
      ],
    },
  ]
  const timelineItems = [
    { label: filteredRecords.length > 0 ? 'Dokumentraum geladen' : 'Noch keine Dokumente', detail: `${filteredRecords.length} Dokumente im aktuellen Filterraum.` },
    { label: workspace.latestDate ? 'Letzte Dokumentbewegung vorhanden' : 'Noch keine Bewegung', detail: workspace.latestDate ? new Date(workspace.latestDate).toLocaleDateString('de-DE') : 'Kein letzter Eingang vorhanden.' },
    { label: 'Naechster Nachweisschritt', detail: evidenceSummary.nextAction },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Dokumenten-Ablage</h1>
          <p className="text-muted-foreground">Nachweise suchen, herunterladen und dem Vorgang zuordnen</p>
        </div>
        <Button className="min-h-touch gap-2 touch-manipulation" onClick={handleUploadClick}>
          <Upload className="h-4 w-4" />Hochladen
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          className="sr-only"
          aria-hidden="true"
          tabIndex={-1}
          onChange={handleUploadChange}
        />
      </div>
      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Suche Dokumente"
                placeholder="Suche nach Dokument, Vorgang oder Kategorie..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button
              variant="outline"
              className="min-h-touch gap-2 touch-manipulation"
              data-global-button-handler="ignore"
              disabled={pendingKeys.has('export')}
              onClick={handleExport}
            >
              <FileDown className="h-4 w-4" />Export
            </Button>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardContent className="pt-6">
          <DataTable data={filteredDokumente} columns={columns} emptyMessage="Keine Dokumente im aktuellen Suchraum." />
        </CardContent>
      </Card>
      {!isTouch ? (
        <>
          <OperationalCaseHeader
            title="Dokumenten-Nachweise steuern"
            description="Nachweisrisiko, Wiedervorlagen und fehlender Objektbezug bleiben neben der Ablage als ein Fall sichtbar."
            status={operationalStatus}
            owner="Dokumentenablage / Fachbereich"
            blocker={evidenceSummary.unassignedCount > 0 ? 'Ein Teil der Dokumente ist noch keinem fachlichen Objekt sauber zugeordnet.' : null}
            nextAction={evidenceSummary.nextAction}
            caseLabel="Dokumenten-Nachweisfall"
            tags={['Dokumente', 'Nachweis']}
          />
          <div className="grid gap-4 lg:grid-cols-[1.35fr_1fr]">
            <OperationalTimeline title="Nachweisverlauf" items={timelineItems} />
            <OperationalContextPanel title="Nachweiskontext" sections={contextSections} />
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Dokumente Gesamt</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-muted-foreground" />
                  <span className="text-2xl font-bold">{workspace.total}</span>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Speicherplatz</CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-2xl font-bold">{gesamtGroesse} KB</span>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Nachweisrelevant</CardTitle>
              </CardHeader>
              <CardContent>
                <span className="text-2xl font-bold">{workspace.evidenceCount}</span>
              </CardContent>
            </Card>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Nachweisrisiko</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-lg font-semibold">{evidenceSummary.evidenceRisk}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Ohne Objektbezug</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{evidenceSummary.unassignedCount}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Naechster Nachweisschritt</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm font-semibold">{evidenceSummary.nextAction}</div>
              </CardContent>
            </Card>
          </div>
          <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
            <Card>
              <CardHeader>
                <CardTitle>Arbeitsbild</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-3">
                <div className="rounded-lg border p-4">
                  <div className="text-sm text-muted-foreground">Vorgangsbelege</div>
                  <div className="mt-2 text-2xl font-bold">{workspace.workflowCount}</div>
                  <div className="mt-1 text-sm text-muted-foreground">Direkt zuordenbare Belege fuer Lieferschein, Rechnung oder Kontrakt</div>
                </div>
                <div className="rounded-lg border p-4">
                  <div className="text-sm text-muted-foreground">Wiedervorlagen</div>
                  <div className="mt-2 text-2xl font-bold">{workspace.followUpCount}</div>
                  <div className="mt-1 text-sm text-muted-foreground">Ablauf- oder Nachweisdokumente mit Pruefbedarf</div>
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
              <CardHeader>
                <CardTitle>Offene Hinweise</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                {filteredRecords.slice(0, 4).map((record) => (
                  <div key={record.id} className="rounded-lg border p-3">
                    <div className="font-medium">{record.name}</div>
                    <div className="text-muted-foreground">{record.objectKind}: {record.objectRef}</div>
                    <div className="mt-1 text-muted-foreground">{record.followUp}</div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </>
      ) : null}
    </div>
  )
}
