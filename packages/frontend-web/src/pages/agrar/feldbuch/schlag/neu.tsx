import { Navigate } from '@/app/routing/typed-router'

/** Alte Seite ohne eigene Maske (screenId unbekannt, nicht verlinkt): fuehrt auf die Schlagkartei. */
export default function Page(): JSX.Element {
  return <Navigate to="/agrar/feldbuch/schlagkartei" replace />
}
