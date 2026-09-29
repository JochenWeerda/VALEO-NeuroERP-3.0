import { useMemo, useRef, useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useTouchDevice } from '@/hooks/useTouchDevice'
import { AlertCircle, FileDown, Plus, Search } from 'lucide-react'
import { useReklamationen, type Reklamation } from '@/lib/api/misc-modules'
import { readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
import { WorkflowProcessBand } from '@/components/workflow/WorkflowProcessBand'
import { saveFlowSpineResumeCheckpoint } from '@/lib/api/flow-spines'
import { useToast } from '@/hooks/use-toast'

export default function ReklamationenPage(): JSX.Element {
  const navigate = useNavigate()
  const isTouch = useTouchDevice()
  const { toast } = useToast()
  const [searchParams] = useSearchParams()
  const searchInputRef = useRef<HTMLInputElement | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [pendingPath, setPendingPath] = useState<string | null>(null)
  const { data: reklamationen, isLoading } = useReklamationen()
  const workflowContext = readWorkflowEntryContext(searchParams)

  const persistNavigateWithWorkflowResume = async (targetPath: string, resumeNodeId: string): Promise<void> => {
    const query = workflowContext ? searchParams.toString() : ''
    const target = `${targetPath}${query ? `?${query}` : ''}`
    if (workflowContext?.process && workflowContext.instanceId) {
      await saveFlowSpineResumeCheckpoint(workflowContext.process, workflowContext.instanceId, {
        resume_node_id: resumeNodeId,
        resume_route: target,
        resume_payload: {
          screen: targetPath.includes('/neu') ? 'complaint-create' : 'complaint-detail',
          targetPath,
          workflowCase: workflowContext.caseNumber || undefined,
        },
        business_status: 'reklamation_in_bearbeitung',
        action_label: `Reklamation fortsetzen: ${targetPath}`,
      })
    }
    navigate(target)
  }

  const handleOpen = async (targetPath: string, resumeNodeId: string): Promise<void> => {
    if (pendingPath) return
    setPendingPath(targetPath)
    try {
      await persistNavigateWithWorkflowResume(targetPath, resumeNodeId)
    } catch {
      toast({
        variant: 'destructive',
        title: 'Reklamation konnte nicht geöffnet werden',
        description: 'Bitte erneut versuchen.',
      })
    } finally {
      setPendingPath(null)
    }
  }

  const list = useMemo(() => {
    const items = reklamationen ?? []
    if (!searchTerm.trim()) {
      return items
    }
    const term = searchTerm.trim().toLowerCase()
    return items.filter((reklamation) =>
      [reklamation.nummer, reklamation.kunde, reklamation.grund, reklamation.artikel]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(term)),
    )
  }, [reklamationen, searchTerm])

  const neu = list.filter((r) => r.status === 'neu').length
  const inBearbeitung = list.filter((r) => r.status === 'in-bearbeitung').length
  const hochprio = list.filter((r) => r.prioritaet === 'hoch' && r.status !== 'geloest' && r.status !== 'abgelehnt').length

  const fallkopf = useMemo(() => {
    return {
      status: neu > 0 ? `${neu} neue Reklamation(en)` : inBearbeitung > 0 ? 'Bearbeitung läuft' : 'Keine offenen Fälle',
      statusColor: neu > 0 || hochprio > 0
        ? 'text-status-error border-status-error/40 bg-status-error/10'
        : inBearbeitung > 0
          ? 'text-status-warning border-status-warning/40 bg-status-warning/10'
          : 'text-status-success border-status-success/40 bg-status-success/10',
      rueckstand: neu > 0 ? `${neu} unbearbeitete Reklamation(en)` : 'Kein Rückstand',
      risikobild: hochprio > 0 ? `${hochprio} mit hoher Priorität — SLA beachten` : 'Kein erhöhtes Risiko',
      naechsteSammelaktion: neu > 0 ? 'Neue Reklamationen sichten und zuweisen' : inBearbeitung > 0 ? 'Laufende Fälle prüfen' : 'Keine dringende Aktion',
    }
  }, [neu, inBearbeitung, hochprio])

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => { void handleOpen('/qualitaet/reklamation/neu', 'complaint') },
    onSearch: () => searchInputRef.current?.focus(),
  })
  useKeyboardShortcuts(shortcuts)

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Reklamations-Nr.',
      render: (r: Reklamation) => (
        <button
          type="button"
          onClick={() => { void handleOpen(`/qualitaet/reklamation/${r.id}`, 'complaint') }}
          disabled={pendingPath === `/qualitaet/reklamation/${r.id}`}
          className="min-h-11 font-medium text-primary touch-manipulation"
        >
          {r.nummer}
        </button>
      ),
    },
    {
      key: 'kunde' as const,
      label: 'Kunde',
      render: (r: Reklamation) => (
        <div>
          <div className="font-medium">{r.kunde}</div>
          <div className="text-sm text-muted-foreground">{r.artikel}</div>
        </div>
      ),
    },
    { key: 'grund' as const, label: 'Grund' },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (r: Reklamation) => new Date(r.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'prioritaet' as const,
      label: 'Priorität',
      render: (r: Reklamation) => (
        <Badge variant={r.prioritaet === 'hoch' ? 'destructive' : r.prioritaet === 'normal' ? 'secondary' : 'outline'}>
          {r.prioritaet === 'hoch' ? 'Hoch' : r.prioritaet === 'normal' ? 'Normal' : 'Niedrig'}
        </Badge>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (r: Reklamation) => (
        <Badge variant={r.status === 'geloest' ? 'outline' : r.status === 'abgelehnt' ? 'destructive' : 'default'}>
          {r.status === 'neu' ? 'Neu' : r.status === 'in-bearbeitung' ? 'In Bearbeitung' : r.status === 'geloest' ? 'Gelöst' : 'Abgelehnt'}
        </Badge>
      ),
    },
  ]

  if (isLoading) {
    return (
      <PageSurface data-page-surface="reklamationen-loading" contentClassName="space-y-4">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-64" />
      </PageSurface>
    )
  }

  const handleExport = (): void => {
    const header = 'Nummer;Kunde;Artikel;Grund;Datum;Prioritaet;Status\n'
    const esc = (value: unknown) => `"${String(value ?? '').replace(/"/g, '""')}"`
    const rows = list
      .map((entry) =>
        [
          entry.nummer,
          entry.kunde,
          entry.artikel,
          entry.grund,
          entry.datum,
          entry.prioritaet,
          entry.status,
        ].map(esc).join(';'),
      )
      .join('\n')
    const blob = new Blob([header + rows], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `Reklamationen_${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <PageSurface data-page-surface="reklamationen" contentClassName="space-y-6">
      {workflowContext ? (
        <WorkflowProcessBand context={workflowContext} />
      ) : null}

      <PageSection>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold md:text-3xl">Reklamationen</h1>
            <p className="text-muted-foreground">Beschwerden sichten, zuweisen, lösen</p>
          </div>
          <Button
            onClick={() => { void handleOpen('/qualitaet/reklamation/neu', 'complaint') }}
            disabled={pendingPath === '/qualitaet/reklamation/neu'}
            className="min-h-touch gap-2 touch-manipulation"
          >
            <Plus className="h-4 w-4" />
            Neue Reklamation
          </Button>
        </div>
      </PageSection>

      {neu > 0 && (
        <Card className="border-status-error/40 bg-status-error/10">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-status-error">
              <AlertCircle className="h-5 w-5" />
              <span className="font-semibold">{neu} neue Reklamation(en)</span>
            </div>
          </CardContent>
        </Card>
      )}

      <PageSection title="Suche und Liste">
        <div className="space-y-4">
          <div className="flex flex-wrap gap-4">
            <div className="relative min-w-[18rem] flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                ref={searchInputRef}
                aria-label="Suche Reklamationen"
                placeholder="Nummer, Kunde, Grund oder Artikel suchen"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>

          <Card>
            <CardContent className="pt-6">
              <DataTable data={list} columns={columns} />
            </CardContent>
          </Card>
        </div>
      </PageSection>

      {!isTouch ? (
      <Card className={`border ${fallkopf.statusColor}`}>
        <CardContent className="pt-4 pb-3 text-sm space-y-1">
          <div className="font-semibold">Reklamationen: {fallkopf.status}</div>
          <div>Rückstand: {fallkopf.rueckstand}</div>
          <div>Risikobild: {fallkopf.risikobild}</div>
          <div>Nächste Sammelaktion: {fallkopf.naechsteSammelaktion}</div>
        </CardContent>
      </Card>
      ) : null}

      {!isTouch ? (
      <PageSection title="Statuslage">
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Reklamationen Gesamt</CardTitle></CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-muted-foreground" />
                <span className="text-2xl font-bold">{list.length}</span>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Neu</CardTitle></CardHeader>
            <CardContent><span className="text-2xl font-bold text-status-error">{neu}</span></CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">In Bearbeitung</CardTitle></CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-status-warning">{list.filter((r) => r.status === 'in-bearbeitung').length}</span>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gelöst</CardTitle></CardHeader>
            <CardContent>
              <span className="text-2xl font-bold text-status-success">{list.filter((r) => r.status === 'geloest').length}</span>
            </CardContent>
          </Card>
        </div>
      </PageSection>
      ) : null}

      {!isTouch ? <KeyboardShortcutBar shortcuts={shortcuts} /> : null}
    </PageSurface>
  )
}
