import { lazy, Suspense } from 'react'
import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from '../intake/domain-runtime'

const Schlagkartei = lazy(() => import('./schlagkartei-surface'))
const MilchviehKarte = lazy(() => import('./milchvieh-karte-surface'))

const AGRAR_FIELDS: Record<string, string[]> = {
  'agrar/kunden-schlagkartei': ['kunden_nr', 'schlag_count', 'massnahme_count', 'gesamt_flaeche_ha'],
  'agrar/milchvieh-karte': ['feature_count'],
}

/** Nur feste native Agrar-Vertraege duerfen Fach-Oberflaechen mounten. */
export function AgrarWorkbench({ contract, plan }: SpecializedComponentProps): JSX.Element {
  if (
    !plan
    || plan.specialized?.type !== 'agrar_workbench'
    || plan.specialized.id !== contract.id
    || (plan.screenId !== contract.id && !plan.screenId.startsWith('tenant/'))
    || !Object.prototype.hasOwnProperty.call(AGRAR_FIELDS, contract.id)
  ) {
    return <p role="alert">Agrar-Arbeitsplatz ist nicht verfügbar.</p>
  }
  const fields = AGRAR_FIELDS[contract.id]
  const Surface = contract.id === 'agrar/kunden-schlagkartei' ? Schlagkartei : MilchviehKarte
  return (
    <DomainContractBoundary plan={plan} fields={fields}>
      <Suspense fallback={<p role="status">Agrar-Arbeitsplatz wird geladen…</p>}>
        <Surface />
      </Suspense>
    </DomainContractBoundary>
  )
}
