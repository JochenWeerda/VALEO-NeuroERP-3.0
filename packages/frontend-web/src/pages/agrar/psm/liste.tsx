import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `agrar/psm-liste`; Spalten und Aktionen stehen in der Definition. */
export default function PsmListePage(): JSX.Element {
  return <NativeListPage screenId="agrar/psm-liste" testId="screen-agrar/psm-liste" />
}
