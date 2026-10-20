import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Bestellungen aus der ScreenDefinition `einkauf/bestellungen`; dieselbe Quelle wie die Objektmaske. */
export default function BestellungenListePage(): JSX.Element {
  return <NativeListPage screenId="einkauf/bestellungen" testId="screen-einkauf/bestellungen" />
}
