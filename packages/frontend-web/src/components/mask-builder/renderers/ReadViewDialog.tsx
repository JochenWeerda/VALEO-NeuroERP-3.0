import { useMemo } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { auth } from '@/lib/auth'
import { tenantFromToken } from '@/lib/tenant-from-token'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import type { ScreenActionDefinition, ScreenDefinition } from '../schema'

export function useReadViewIdentity(): string {
  const { user } = useAuth()
  const tenant = tenantFromToken(auth.getAccessToken())
  return tenant && user?.sub ? JSON.stringify([tenant, user.sub]) : ''
}

export function readViewEndpoint(action: ScreenActionDefinition, row: Record<string, unknown>): string {
  const template = action.readView?.endpoint
  if (!template || !/^\/api\/v1\/(?:[A-Za-z0-9_-]+|\{[A-Za-z_][A-Za-z0-9_]*\})(?:\/(?:[A-Za-z0-9_-]+|\{[A-Za-z_][A-Za-z0-9_]*\}))*\/?$/.test(template)) {
    throw new Error('Der Leseweg ist nicht gültig.')
  }
  if ((template.match(/\{[^{}]+\}/g) ?? []).length > 1) throw new Error('Ein eindeutiger Objektbezug ist erforderlich.')
  return template.replace(/\{([^{}]+)\}/g, (_, key: string) => {
    if (/(?:^|_)(tenant|mandant|actor|user|agent)(?:_|$)/i.test(key)) throw new Error('Identitätsauswahl ist nicht zulässig.')
    const value = row[key === 'entity_id' ? 'id' : key]
    if (!['string', 'number'].includes(typeof value) || !String(value).trim() || (typeof value === 'number' && !Number.isFinite(value)) || ['.', '..'].includes(String(value))) {
      throw new Error('Die Kennung für diese Ansicht fehlt oder ist ungültig.')
    }
    return encodeURIComponent(String(value))
  })
}

export function ReadViewDialog({ screenId, action, row, identity, allowed, onClose }: {
  screenId: string; action: ScreenActionDefinition; row: Record<string, unknown>
  identity: string; allowed: boolean; onClose: () => void
}): JSX.Element {
  const currentIdentity = useReadViewIdentity()
  let endpoint = ''
  try { endpoint = readViewEndpoint(action, row) } catch { /* Fail closed before any request. */ }
  const authorized = Boolean(identity && identity === currentIdentity && allowed && endpoint)
  const tableKey = `readView-${action.key}`
  const definition = useMemo<ScreenDefinition>(() => ({
    schemaVersion: 1, id: screenId, domain: 'platform', mode: 'list', title: action.label,
    adapter: { type: 'native', sourceId: screenId, temporary: false },
    layout: { floorplan: 'worklist', density: 'compact', contextRail: 'none', tableProfile: 'audit' },
    tables: [{ key: tableKey, label: action.label, columns: action.readView?.columns ?? [],
      pageSize: 25, virtualized: true, rowHeight: 40, rowActions: [] }],
    actions: [],
  }), [screenId, action, endpoint, tableKey])
  const runtime = useUniversalMaskRuntime({ screenId, schema: definition, enabled: authorized, tenantId: currentIdentity, tabEndpoints: { [tableKey]: endpoint }, entityId: String(row.id ?? '') })
  return <Dialog open onOpenChange={open => { if (!open) onClose() }}>
    <DialogContent className="max-h-[90vh] overflow-auto sm:max-w-5xl">
      <DialogHeader><DialogTitle>{action.label}</DialogTitle>
        <DialogDescription>Lesende Ansicht zum ausgewählten Eintrag.</DialogDescription>
      </DialogHeader>
      {!authorized ? <p role="alert">Diese Ansicht ist im aktuellen Benutzer- und Mandantenkontext nicht verfügbar.</p>
        : runtime.isTableLoading ? <p role="status">Daten werden geladen…</p>
          : runtime.plan ? <UniversalMaskRenderer plan={runtime.plan} data={runtime.entityData}
            tables={runtime.tableRows} tableTotals={runtime.tableTotals} tableQueryStates={runtime.tableQueryStates}
            onTableQueryChange={runtime.setTableQuery} messages={runtime.messages}
            onRetry={() => { void runtime.refetch() }} /> : <p role="alert">Leseansicht konnte nicht aufgebaut werden.</p>}
    </DialogContent>
  </Dialog>
}
