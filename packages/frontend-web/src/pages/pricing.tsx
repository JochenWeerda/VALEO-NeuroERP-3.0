import { Navigate } from '@/app/routing/typed-router'

/** Alte Einstiegsseite ohne eigene Maske (screenId unbekannt): fuehrt auf die Konditionen. */
export default function Page(): JSX.Element {
  return <Navigate to="/preise/konditionen" replace />
}
