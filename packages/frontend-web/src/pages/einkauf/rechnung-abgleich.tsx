import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Rechnungsabgleich aus der ScreenDefinition `einkauf/rechnung-abgleich-liste`. */
export default function EinkaufRechnungAbgleichTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="einkauf/rechnung-abgleich-liste" testId="screen-einkauf/rechnung-abgleich-liste" />
  )
}
