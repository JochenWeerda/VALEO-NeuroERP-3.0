import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Bestellvorschlaege aus der ScreenDefinition `einkauf/bestellvorschlaege-liste`. */
export default function EinkaufBestellvorschlaegeTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="einkauf/bestellvorschlaege-liste" testId="screen-einkauf/bestellvorschlaege-liste" />
  )
}
