import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from './domain-runtime'
import RegistrationSurface from './registration-surface'
import QualitySurface from './quality-surface'
import QueueSurface from './queue-surface'

export function Intake({ contract, plan }: SpecializedComponentProps): JSX.Element {
  if (!plan || plan.specialized?.id !== contract.id || plan.specialized.type !== contract.type
    || (plan.screenId !== contract.id && !plan.screenId.startsWith('tenant/'))) return <p role="alert">Annahmevertrag ist nicht verfügbar.</p>
  switch (contract.id) {
    case 'annahme/lkw-registrierung':
      return <DomainContractBoundary plan={plan} fields={['kennzeichen', 'lieferant', 'lieferscheinNr', 'articleId', 'artikel', 'ankunftszeit', 'prioritaet', 'attachmentIds']}><RegistrationSurface plan={plan} /></DomainContractBoundary>
    case 'annahme/qualitaets-check':
      return <DomainContractBoundary plan={plan} fields={['lieferscheinNr', 'artikel', 'feuchtigkeit', 'protein', 'verunreinigung', 'fremdgeruch', 'schaedlinge', 'farbe', 'bemerkungen', 'ergebnis']}><QualitySurface plan={plan} /></DomainContractBoundary>
    case 'annahme/warteschlange':
      return <DomainContractBoundary plan={plan} fields={['kennzeichen', 'lieferant', 'artikel', 'status', 'ankunft', 'wartezeit', 'lieferschein_nr']}><QueueSurface plan={plan} /></DomainContractBoundary>
    default: return <p role="alert">Unbekannter Annahmevertrag.</p>
  }
}
