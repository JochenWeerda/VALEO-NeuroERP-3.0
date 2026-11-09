import { Navigate } from '@/app/routing/typed-router'

/** Alte Einstiegsseite ohne eigene Maske (screenId unbekannt): fuehrt auf die Wissensbasis. */
export default function Page(): JSX.Element {
  return <Navigate to="/wissen/wissensbasis" replace />
}
