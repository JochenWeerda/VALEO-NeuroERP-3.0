import { lazy, Suspense } from 'react'
import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from '../intake/domain-runtime'

const Materialfluss = lazy(() => import('./materialfluss-surface'))

const LAGER_FIELDS: Record<string, string[]> = {
  'lager/materialfluss': ['warehouse_id', 'node_count', 'edge_count'],
}

/** Nur feste native Lager-Vertraege duerfen Fach-Oberflaechen mounten. */
export function LagerWorkbench({ contract, plan }: SpecializedComponentProps): JSX.Element {
  if (
    !plan
    || plan.specialized?.type !== 'lager_workbench'
    || plan.specialized.id !== contract.id
    || (plan.screenId !== contract.id && !plan.screenId.startsWith('tenant/'))
    || !Object.prototype.hasOwnProperty.call(LAGER_FIELDS, contract.id)
  ) {
    return <p role="alert">Lager-Arbeitsplatz ist nicht verfügbar.</p>
  }
  return (
    <DomainContractBoundary plan={plan} fields={LAGER_FIELDS[contract.id]}>
      <Suspense fallback={<p role="status">Lager-Arbeitsplatz wird geladen…</p>}>
        <Materialfluss />
      </Suspense>
    </DomainContractBoundary>
  )
}
