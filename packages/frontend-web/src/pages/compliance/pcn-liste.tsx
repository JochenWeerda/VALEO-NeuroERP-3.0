import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `compliance/pcn-liste`; Spalten und Aktionen stehen in der Definition. */
export default function PcnListePage(): JSX.Element {
  return <NativeListPage screenId="compliance/pcn-liste" testId="screen-compliance/pcn-liste" />
}
