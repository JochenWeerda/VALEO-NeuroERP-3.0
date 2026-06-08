import { Navigate, useParams } from '@/app/routing/react-router-compat'

/**
 * Kanonische Kundenpflege: /verkauf/kunden-stamm (bzw. kunde/neu).
 * Alte URL /verkauf/kunden-stamm-enhanced leitet um, damit keine zweite „Version“ der Maske existiert.
 */
export default function KundenStammEnhancedRedirect(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (id) {
    return <Navigate to={`/verkauf/kunden-stamm/${id}`} replace />
  }
  return <Navigate to="/verkauf/kunden-stamm" replace />
}
