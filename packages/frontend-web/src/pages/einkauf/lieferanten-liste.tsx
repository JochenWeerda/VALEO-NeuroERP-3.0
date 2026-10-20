import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Lieferanten aus der ScreenDefinition `einkauf/lieferanten`; dieselbe Quelle wie die Objektmaske `einkauf/supplier`. */
export default function LieferantenListePage(): JSX.Element {
  return <NativeListPage screenId="einkauf/lieferanten" testId="screen-einkauf/lieferanten" />
}
