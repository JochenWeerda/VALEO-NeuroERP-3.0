import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Disposition: der Bestellvorschlag rechnet aus echtem Bestand und Meldebestand (ops_disposition war eine
 * handgepflegte Scheinliste, Nutzerentscheidung 04.11.2026). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="einkauf/bestellvorschlaege-liste" testId="screen-disposition/liste" />
}
