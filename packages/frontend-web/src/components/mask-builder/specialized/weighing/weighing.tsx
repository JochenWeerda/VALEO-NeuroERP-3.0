import type { SpecializedComponentProps } from '../types'
import { DomainContractBoundary } from '../intake/domain-runtime'
import ScalesSurface from './scales-surface'
import ScaleCreateSurface from './scale-create-surface'
import TicketsSurface from './tickets-surface'

export function Weighing({ contract, plan }: SpecializedComponentProps): JSX.Element {
  if (!plan || plan.specialized?.id !== contract.id || plan.specialized.type !== contract.type
    || (plan.screenId !== contract.id && !plan.screenId.startsWith('tenant/'))) return <p role="alert">Waagenvertrag ist nicht verfügbar.</p>
  if (contract.id === 'waage/neu') return <DomainContractBoundary plan={plan} fields={['standort', 'typ', 'max_kapazitaet']}><ScaleCreateSurface plan={plan} /></DomainContractBoundary>
  if (['waage/liste', 'waage/waagen-liste'].includes(contract.id)) return <DomainContractBoundary plan={plan} fields={['id', 'standort', 'typ', 'maxKapazitaet', 'letzteEichung', 'naechsteEichung', 'status', 'letztes_eichdatum', 'naechste_eichfaelligkeit', 'eichamt', 'zertifikat_nr', 'importScaleId', 'importFile', 'fehlerToleranz', 'importRaw', 'importError', 'importRetryCount']}><ScalesSurface plan={plan} /></DomainContractBoundary>
  if (['waage/wiegungen', 'waage/wiegungen-liste'].includes(contract.id)) return <DomainContractBoundary plan={plan} fields={['ticketNumber', 'scaleId', 'vehiclePlate', 'grossWeight', 'tareWeight', 'moisturePct', 'impuritiesPct', 'selectedTicketId', 'selectedContractId']}><TicketsSurface plan={plan} /></DomainContractBoundary>
  return <p role="alert">Unbekannter Waagenvertrag.</p>
}
