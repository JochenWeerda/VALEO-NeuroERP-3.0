import { DocumentControlScopePage } from './DocumentControlScopePage'

/** Belegkontrolle ueber alle Ausnahmetypen; dieselbe Seite wie die gespeicherten L3-Sichten. */
export default function BelegKontrollePage(): JSX.Element {
  return <DocumentControlScopePage screenId="auswertungen/beleg-kontrolle" testId="beleg-kontrolle" />
}
