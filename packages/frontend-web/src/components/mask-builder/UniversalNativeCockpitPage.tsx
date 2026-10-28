import { useEffect } from 'react'
import { AlertCircle } from 'lucide-react'
import { useSearchParams } from '@/app/routing/typed-router'
import { readWorkflowEntryContext } from '@/components/workflow/WorkflowEntryBanner'
import { WorkflowProcessBand } from '@/components/workflow/WorkflowProcessBand'
import type { RenderPlan } from './render-plan/types'
import { evaluateListExperience } from './runtime/list-experience'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { useScreenDefinition } from '@/lib/api/masks'

const EMPTY_PERMISSIONS: string[] = []

function ListWorkflowBand(): JSX.Element | null {
  const [searchParams] = useSearchParams()
  const context = readWorkflowEntryContext(searchParams)
  return context ? <WorkflowProcessBand context={context} /> : null
}

/**
 * UniversalNativeCockpitPage (UIX-061): rendert einen cockpit-Workspace als
 * rollenbasierte Startseite. Kein Entity — die Seite kompiliert die
 * ScreenDefinition ueber den zentralen UniversalMaskRuntime zu einem RenderPlan
 * (KPI-Summary + Kachel-Grid) und navigiert ueber die Kacheln in die jeweiligen
 * Prozessmasken. Damit gelten Overlays, Berechtigungen und Compiler-Gates auch
 * fuer Cockpits und nicht nur fuer Objektmasken.
 */
export function UniversalNativeCockpitPage({
  screenId,
  testId,
  onAction,
  onRowSelect,
  onListData,
  permissions = EMPTY_PERMISSIONS,
}: {
  screenId: string
  testId?: string
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  onRowSelect?: (row: Record<string, unknown>) => void
  onListData?: (rows: Record<string, unknown>[], plan: RenderPlan) => void
  permissions?: string[]
}): JSX.Element {
  const schemaQuery = useScreenDefinition(screenId)
  const runtime = useUniversalMaskRuntime({
    screenId,
    schema: schemaQuery.data,
    enabled: Boolean(schemaQuery.data),
    permissions,
  })
  const plan = runtime.plan
  const firstKey = plan ? Object.keys(plan.tablesByKey)[0] : undefined
  const firstRows = firstKey && plan?.listExperience ? runtime.filteredTableRows[firstKey] : undefined
  useEffect(() => {
    if (plan && firstRows && onListData) onListData(firstRows, plan)
  }, [plan, firstRows, onListData])
  const experience = plan?.listExperience
  const result = experience && firstRows ? evaluateListExperience(experience, firstRows) : undefined

  if (schemaQuery.isLoading) {
    return (
      <div className="px-4 py-3 text-sm text-muted-foreground md:px-8" data-testid={`${testId ?? 'cockpit'}-loading`}>
        Workspace wird geladen…
      </div>
    )
  }

  if (schemaQuery.error || !plan) {
    return (
      <div
        className="flex items-start gap-2 px-4 py-3 text-sm text-destructive md:px-8"
        role="alert"
        data-testid={`${testId ?? 'cockpit'}-error`}
      >
        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
        <span>Workspace konnte nicht geladen werden.</span>
      </div>
    )
  }

  return (
    <div data-testid={testId ?? `native-cockpit-${screenId.replace('/', '-')}`} data-runtime="native-cockpit">
      {experience?.workflowResume && <ListWorkflowBand />}
      <UniversalMaskRenderer
        plan={plan}
        flowSpineCatalog={runtime.flowSpineCatalog}
        data={runtime.entityData}
        tables={runtime.tableRows}
          messages={runtime.messages}
          onRetry={() => { void runtime.refetch() }}
        tableQueryStates={runtime.tableQueryStates}
        tableTotals={runtime.tableTotals}
        onTableQueryChange={runtime.setTableQuery}
        onOverlayChange={runtime.updateUserOverlay}
        onOverlayReset={runtime.resetUserOverlay}
        lookupBindings={runtime.lookupBindings}
        onAction={onAction}
        onRowSelect={onRowSelect}
      />
      {experience && result && <section aria-label="Listenübersicht" className="space-y-2 px-4 py-3">
        <dl className="grid grid-cols-2 gap-x-6 gap-y-2 md:grid-cols-3 xl:grid-cols-6">{experience.aggregates.map(a => <div key={a.key}><dt className="text-sm text-muted-foreground">{a.label}</dt><dd className="font-semibold">{result.counts[a.key]}</dd></div>)}</dl>
        {result.notice && <p role="status">{result.notice}</p>}
        {result.insights.length > 0 && <dl className="grid gap-x-6 gap-y-2 md:grid-cols-2 xl:grid-cols-3">{result.insights.map(line => <div key={line.label}><dt className="font-medium">{line.label}</dt><dd>{line.text}</dd></div>)}</dl>}
      </section>}
    </div>
  )
}
