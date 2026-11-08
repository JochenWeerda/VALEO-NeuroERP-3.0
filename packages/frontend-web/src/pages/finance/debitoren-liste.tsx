import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Debitoren aus der ScreenDefinition `finance/debitoren-liste`; Zeilen oeffnen die native Objektmaske. */
export default function DebitorenListePage(): JSX.Element {
  return <NativeListPage screenId="finance/debitoren-liste" testId="screen-finance/debitoren-liste" />
}
