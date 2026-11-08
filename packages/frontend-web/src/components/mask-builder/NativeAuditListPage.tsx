import { useMemo, useState } from 'react'
import { Input } from '@/components/ui/input'
import { useScreenDefinition } from '@/lib/api/masks'
import { UniversalMaskRenderer } from './UniversalMaskRenderer'
import { useUniversalMaskRuntime } from './runtime/useUniversalMaskRuntime'

/** Context-bound read-only audit table; filter fields are declared by the screen. */
export function NativeAuditListPage({ screenId, entityId }: { screenId: string; entityId?: string }): JSX.Element {
  const schemaQuery = useScreenDefinition(screenId)
  const context = entityId?.trim()
  const runtime = useUniversalMaskRuntime({ screenId, schema: schemaQuery.data, entityId: context, completeClientTables: true, enabled: Boolean(context && schemaQuery.data) })
  const [filters, setFilters] = useState<Record<string, string>>({})
  const tableKey = runtime.plan ? Object.keys(runtime.plan.tablesByKey)[0] : undefined
  const table = tableKey ? runtime.plan?.tablesByKey[tableKey] : undefined
  const columns = table?.columns.filter(column => column.filterable) ?? []
  const tables = useMemo(() => {
    if (!tableKey) return runtime.tableRows
    const rows = (runtime.filteredTableRows[tableKey] ?? []).filter(row => Object.entries(filters).every(([key, value]) =>
      !value || String(row[key] ?? '').toLowerCase().includes(value.toLowerCase())))
    return { ...runtime.tableRows, [tableKey]: rows }
  }, [runtime.tableRows, runtime.filteredTableRows, tableKey, filters])

  if (!context) return <p role="status">Bitte einen Vorgang auswählen, um das Protokoll anzuzeigen.</p>
  if (schemaQuery.isLoading || runtime.isTableLoading) return <p role="status">Protokoll wird geladen…</p>
  if (schemaQuery.error || !runtime.plan) return <p role="alert">Protokoll konnte nicht geladen werden.</p>
  return <div data-testid={`screen-${screenId}`}>
    <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
      {columns.map(column => <Input key={column.key} aria-label={`Filter ${column.label}`} placeholder={`Filter ${column.label}`}
        value={filters[column.key] ?? ''} onChange={event => setFilters(previous => ({ ...previous, [column.key]: event.target.value }))} />)}
    </div>
    <UniversalMaskRenderer plan={runtime.plan} entityId={context} data={runtime.entityData} tables={tables}
      messages={runtime.messages} onRetry={() => { void runtime.refetch() }} flowSpineCatalog={runtime.flowSpineCatalog}
      lookupBindings={runtime.lookupBindings} />
  </div>
}
