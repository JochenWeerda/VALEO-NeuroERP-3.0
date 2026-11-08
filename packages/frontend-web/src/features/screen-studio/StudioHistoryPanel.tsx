import { useState } from 'react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { useScreenDefinition } from '@/lib/api/masks'

function AuditMask({ draftId, comparisonId, onSelect }: {
  draftId: string
  comparisonId?: string
  onSelect?: (_id: string) => void
}): JSX.Element {
  const screenId = comparisonId ? 'platform/studio-history-diff' : 'platform/studio-history'
  const schema = useScreenDefinition(screenId)
  const runtime = useUniversalMaskRuntime({
    screenId, entityId: comparisonId ?? draftId, schema: schema.data, enabled: Boolean(schema.data),

  })
  if (schema.isLoading) return <p>Historie wird geladen…</p>
  if (schema.error || !runtime.plan) return <p role="alert">Historienmaske konnte nicht geladen werden.</p>
  return <UniversalMaskRenderer plan={runtime.plan} data={runtime.entityData} tables={runtime.tableRows}
    messages={runtime.messages} tableTotals={runtime.tableTotals} tableQueryStates={runtime.tableQueryStates}
    onTableQueryChange={runtime.setTableQuery} onRetry={() => { void runtime.refetch() }}
    onAction={(action, row) => { if (action === 'compare' && typeof row.id === 'string') onSelect?.(row.id) }} />
}

export function StudioHistoryPanel({ draftId }: { draftId: string }): JSX.Element {
  const [comparisonId, setComparisonId] = useState<string>()
  return <section data-testid="studio-history" aria-label="Studio-Historie" className="col-span-full">
    <AuditMask draftId={draftId} onSelect={setComparisonId} />
    {comparisonId && <AuditMask key={comparisonId} draftId={draftId} comparisonId={comparisonId} />}
  </section>
}
