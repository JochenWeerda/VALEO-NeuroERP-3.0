import { lazy, Suspense } from 'react'
import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from '../intake/domain-runtime'

const Konditionssystem = lazy(() => import('./konditionssystem-surface'))

const PRICING_FIELDS: Record<string, string[]> = {
  'konditionen/konditionssystem': ['preisliste_count', 'rabattgruppe_count', 'individualpreis_count'],
}

/** Nur feste native Pricing-Vertraege duerfen Fach-Oberflaechen mounten. */
export function PricingWorkbench({ contract, plan }: SpecializedComponentProps): JSX.Element {
  if (
    !plan
    || plan.specialized?.type !== 'pricing_workbench'
    || plan.specialized.id !== contract.id
    || (plan.screenId !== contract.id && !plan.screenId.startsWith('tenant/'))
    || !Object.prototype.hasOwnProperty.call(PRICING_FIELDS, contract.id)
  ) {
    return <p role="alert">Pricing-Arbeitsplatz ist nicht verfügbar.</p>
  }
  return (
    <DomainContractBoundary plan={plan} fields={PRICING_FIELDS[contract.id]}>
      <Suspense fallback={<p role="status">Pricing-Arbeitsplatz wird geladen…</p>}>
        <Konditionssystem />
      </Suspense>
    </DomainContractBoundary>
  )
}
