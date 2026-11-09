import { Navigate } from '@/app/routing/typed-router'

/** Alte Seite ohne eigene Maske (screenId unbekannt, nicht verlinkt): fuehrt auf die Erfassung der Erntekampagne. */
export default function Page(): JSX.Element {
  return <Navigate to="/agrar/ernte-kampagne-erfassung" replace />
}
