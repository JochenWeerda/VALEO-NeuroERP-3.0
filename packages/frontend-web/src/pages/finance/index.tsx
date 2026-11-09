import { Navigate } from '@/app/routing/typed-router'

/** Alte Einstiegsseite ohne eigene Maske (screenId unbekannt): fuehrt auf das Abschluss-Cockpit der Finanzbuchhaltung. */
export default function Page(): JSX.Element {
  return <Navigate to="/fibu" replace />
}
