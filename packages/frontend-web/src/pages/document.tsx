import { Navigate } from '@/app/routing/typed-router'

/** Alte Einstiegsseite ohne eigene Maske (screenId unbekannt): fuehrt auf die Dokumentenablage. */
export default function Page(): JSX.Element {
  return <Navigate to="/dokumente/ablage" replace />
}
