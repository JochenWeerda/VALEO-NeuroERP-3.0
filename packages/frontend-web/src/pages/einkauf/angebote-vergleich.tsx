import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Angebotsvergleich aus der ScreenDefinition `einkauf/angebote-vergleich-liste`. */
export default function EinkaufAngeboteVergleichTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="einkauf/angebote-vergleich-liste" testId="screen-einkauf/angebote-vergleich-liste" />
  )
}
