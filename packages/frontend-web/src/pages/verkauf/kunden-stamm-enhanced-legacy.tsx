import { Navigate, useParams } from '@/app/routing/typed-router'

/**
 * Alte URL /verkauf/kunden-stamm-enhanced: Detail landet in der nativen Akte,
 * Neuanlage bleibt auf /verkauf/kunden-stamm.
 */
export default function KundenStammEnhancedRedirect(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (id) {
    return <Navigate to={`/crm/kunden/${id}`} replace />
  }
  return <Navigate to="/verkauf/kunden-stamm" replace />
}
