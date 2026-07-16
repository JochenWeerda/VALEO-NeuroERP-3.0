import { useNavigate } from '@tanstack/react-router'
import { AlertTriangle, CalendarClock, Printer } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { useScreenDefinition } from '@/lib/api/masks'
import { getAxiosErrorMessage } from '@/lib/api-client'
import type { FeedingPlanInstruction, FeedingPlanVersion } from '@/lib/api/feeding-plans'

function amount(value: number | null | undefined): string {
  return value == null ? 'unbekannt' : `${Number(value).toLocaleString('de-DE', { maximumFractionDigits: 3 })} kg`
}

export function FeedingPlanDetail({ versionId }: { versionId: string }): JSX.Element {
  const navigate = useNavigate()
  const schemaQuery = useScreenDefinition('agrar/feeding-plan', { enabled: Boolean(versionId) })
  const runtime = useUniversalMaskRuntime({
    screenId: 'agrar/feeding-plan', entityId: versionId, schema: schemaQuery.data,
    enabled: Boolean(versionId) && schemaQuery.data?.adapter?.temporary === false,
  })
  const plan = runtime.entityData as unknown as FeedingPlanVersion | undefined
  const instructions = (runtime.tableRows.instructions ?? plan?.instructions ?? []) as unknown as FeedingPlanInstruction[]

  function handleAction(actionKey: string): void {
    if (actionKey === 'print_plan') window.print()
    if (actionKey === 'open_mobile') void navigate({ to: '/futtermittel/fuetterungsdokumentation-mobil' })
  }

  if (schemaQuery.error || runtime.entityError) return <p className="p-4" role="alert">{getAxiosErrorMessage(schemaQuery.error ?? runtime.entityError)}</p>
  if (!runtime.plan) return <p className="p-4 text-sm text-muted-foreground">Fuetterungsplan wird geladen...</p>

  return <div data-testid="feeding-plan-detail" data-runtime="native">
    <div className="print:hidden">
      {plan?.plan_status === 'stale' ? <div className="flex items-center gap-2 border-b border-status-warning/30 bg-status-warning/10 px-4 py-2 text-sm" role="status"><AlertTriangle className="h-4 w-4" />Dieser Plan ist veraltet und nur als Nachweis lesbar.</div> : null}
      {plan?.plan_status === 'scheduled' ? <div className="flex items-center gap-2 border-b bg-muted px-4 py-2 text-sm" role="status"><CalendarClock className="h-4 w-4" />Dieser Plan ist geplant und gilt ab {new Date(plan.valid_from).toLocaleDateString('de-DE')}.</div> : null}
      <UniversalMaskRenderer
        plan={runtime.plan} data={runtime.entityData} entityId={versionId}
        tables={runtime.tableRows} tableQueryStates={runtime.tableQueryStates} tableTotals={runtime.tableTotals}
        lookupBindings={runtime.lookupBindings} onTableQueryChange={runtime.setTableQuery}
        overlay={runtime.userOverlay} onOverlayChange={runtime.updateUserOverlay} onOverlayReset={runtime.resetUserOverlay}
        onAction={(key) => handleAction(key)}
      />
    </div>
    {plan ? <section className="hidden print:block" data-testid="feeding-plan-print">
      <header className="mb-6 border-b pb-4"><h1 className="text-2xl font-bold">Fuetterungsplan · {plan.group_name}</h1><p>Planversion {plan.version_no} · {plan.id}</p><p>Quelle {plan.source_ration_version_id}</p><p>Gueltig {plan.valid_from} bis {plan.valid_until ?? 'offen'} · Druckstand {new Date().toLocaleString('de-DE')}</p></header>
      <table className="w-full border-collapse text-sm"><thead><tr><th>Folge</th><th>Futtermittel</th><th>kg FM/Tier</th><th>Dosierziel</th><th>Delta</th></tr></thead><tbody>{instructions.map((row) => <tr key={row.id}><td>{row.sequence}</td><td>{row.feed_name ?? row.feed_id}</td><td>{amount(row.kg_fm_per_animal)}</td><td>{amount(row.target_batch_kg)}</td><td>{amount(row.rounding_delta_kg)}</td></tr>)}</tbody></table>
      <footer className="mt-6 flex items-center gap-2 text-xs"><Printer className="h-4 w-4" />Browserdruck: im Druckdialog „Als PDF speichern“ waehlen.</footer>
    </section> : null}
  </div>
}
