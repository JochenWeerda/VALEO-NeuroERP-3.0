import { lazy, Suspense } from 'react'
import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from '../intake/domain-runtime'

const FahrzeugVertiefung = lazy(() => import('./fahrzeug-vertiefung-surface'))

const FLEET_FIELDS: Record<string, string[]> = {
  'fuhrpark/fahrzeug-vertiefung': ['fahrzeug_id', 'status', 'schaden_offen', 'bussgeld_offen'],
}

/** Nur feste native Fuhrpark-Vertraege duerfen Fach-Oberflaechen mounten. */
export function FleetWorkbench({ contract, plan }: SpecializedComponentProps): JSX.Element {
  if (
    !plan
    || plan.specialized?.type !== 'fleet_workbench'
    || plan.specialized.id !== contract.id
    || (plan.screenId !== contract.id && !plan.screenId.startsWith('tenant/'))
    || !Object.prototype.hasOwnProperty.call(FLEET_FIELDS, contract.id)
  ) {
    return <p role="alert">Fuhrpark-Arbeitsplatz ist nicht verfügbar.</p>
  }
  return (
    <DomainContractBoundary plan={plan} fields={FLEET_FIELDS[contract.id]}>
      <Suspense fallback={<p role="status">Fuhrpark-Arbeitsplatz wird geladen…</p>}>
        <FahrzeugVertiefung />
      </Suspense>
    </DomainContractBoundary>
  )
}
