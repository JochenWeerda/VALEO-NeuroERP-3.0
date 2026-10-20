import { Navigate, useLocation } from '@/app/routing/typed-router'

/**
 * Kundenanlage laeuft seit 20.10.2026 ueber die Studio-Kundenakte (``crm/customer-360``, ``creation``);
 * alte Einstiege ``/verkauf/kunde/neu`` und ``/verkauf/kunde-neu`` leiten dorthin.
 */
export default function KundeNeuPage(): JSX.Element {
  const location = useLocation()
  return <Navigate to={`/crm/kunden/neu${location.search}`} replace />
}
