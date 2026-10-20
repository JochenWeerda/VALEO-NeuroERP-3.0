import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Kreditoren aus der ScreenDefinition `finance/kreditoren-liste`; Zeilen oeffnen die native Objektmaske. */
export default function KreditorenListePage(): JSX.Element {
  return <NativeListPage screenId="finance/kreditoren-liste" testId="screen-finance/kreditoren-liste" />
}
