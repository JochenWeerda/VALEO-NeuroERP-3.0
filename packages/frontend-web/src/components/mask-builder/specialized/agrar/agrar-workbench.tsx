import { lazy, Suspense, type ComponentType, type LazyExoticComponent } from 'react'
import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from '../intake/domain-runtime'

const Schlagkartei = lazy(() => import('./schlagkartei-surface'))
const MilchviehKarte = lazy(() => import('./milchvieh-karte-surface'))
const ErnteAnnahme = lazy(() => import('./ernte-annahme-surface'))
const Abrechnung = lazy(() => import('./abrechnung-surface'))

const AGRAR_FIELDS: Record<string, string[]> = {
  'agrar/kunden-schlagkartei': ['kunden_nr', 'schlag_count', 'massnahme_count', 'gesamt_flaeche_ha'],
  'agrar/milchvieh-karte': ['feature_count'],
  'agrar/ernte-annahme-erfassung': ['acceptance_number', 'customer_id', 'release_status', 'delivery_date'],
  'annahme/abrechnung': ['settlement_count'],
}

const SURFACE_BY_ID: Record<string, LazyExoticComponent<ComponentType>> = {
  'agrar/kunden-schlagkartei': Schlagkartei,
  'agrar/milchvieh-karte': MilchviehKarte,
  'agrar/ernte-annahme-erfassung': ErnteAnnahme,
  'annahme/abrechnung': Abrechnung,
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
  const Surface = SURFACE_BY_ID[contract.id]
  return (
    <DomainContractBoundary plan={plan} fields={AGRAR_FIELDS[contract.id]}>
      <Suspense fallback={<p role="status">Agrar-Arbeitsplatz wird geladen…</p>}>
        <Surface />
      </Suspense>
    </DomainContractBoundary>
  )
}
